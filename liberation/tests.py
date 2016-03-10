# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from importlib import import_module
import itertools
import mailbox
import os
import os.path
import shutil
import tempfile

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import urlresolvers
from django.core.urlresolvers import reverse

from inboxen import models
from inboxen.tests import factories
from inboxen.utils import override_settings
from liberation import tasks
from liberation.forms import LiberationForm


class LiberateTestCase(test.TestCase):
    """Test account liberating"""
    def setUp(self):
        self.user = factories.UserFactory()
        self.inboxes = factories.InboxFactory.create_batch(2, user=self.user)
        self.emails = factories.EmailFactory.create_batch(5, inbox=self.inboxes[0])
        self.emails.extend(factories.EmailFactory.create_batch(5, inbox=self.inboxes[1]))

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject", data="ßssss!")

        self.tmp_dir = tempfile.mkdtemp()
        self.mail_dir = os.path.join(self.tmp_dir, "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_liberate(self):
        """Run through all combinations of compressions and mailbox formats"""
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            for storage, compression in itertools.product(LiberationForm.STORAGE_TYPES, LiberationForm.COMPRESSION_TYPES):
                form_data = {"storage_type": str(storage[0]), "compression_type": str(compression[0])}
                form = LiberationForm(self.user, data=form_data)
                self.assertTrue(form.is_valid())
                form.save()

                # delete liberation now we're done with it and refetch user
                models.Liberation.objects.all().delete()
                self.user = get_user_model().objects.get(id=self.user.id)

                # TODO: check Liberation model actually has correct archive type

    def test_liberate_inbox(self):
        result = tasks.liberate_inbox(self.mail_dir, self.inboxes[0].id)
        self.assertIn("folder", result)
        self.assertIn("ids", result)
        self.assertTrue(os.path.exists(os.path.join(self.mail_dir, '.' + result["folder"])))

        email_ids = models.Email.objects.filter(inbox=self.inboxes[0]).values_list("id", flat=True)
        self.assertItemsEqual(email_ids, result["ids"])

    def test_liberate_message(self):
        inbox = tasks.liberate_inbox(self.mail_dir, self.inboxes[0].id)["folder"]
        email = self.inboxes[0].email_set.all()[0]
        ret_val = tasks.liberate_message(self.mail_dir, inbox, email.id)
        self.assertEqual(ret_val, None)

        ret_val = tasks.liberate_message(self.mail_dir, inbox, 10000000)
        self.assertEqual(ret_val, hex(10000000)[2:])

    def test_liberate_collect_emails(self):
        tasks.liberate_collect_emails(None, self.mail_dir, {"user": self.user.id, "path": self.mail_dir, "tarname": self.mail_dir + ".tar.gz", "storage_type": "0", "compression_type": "0"})

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir, "storage_type": "0", "compression_type": "0"})


class LiberateNewUserTestCase(test.TestCase):
    """Liberate a new user, with no data"""
    def setUp(self):
        self.user = get_user_model().objects.create(username="atester")

        self.tmp_dir = tempfile.mkdtemp()
        self.mail_dir = os.path.join(self.tmp_dir, "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.mail_dir, ignore_errors=True)

    def test_liberate(self):
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            form = LiberationForm(self.user, data={"storage_type": 0, "compression_type": 0})
            self.assertTrue(form.is_valid())
            form.save()

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir, "storage_type": "0", "compression_type": "0"})


class LiberateViewTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-liberate")

    def test_form_bad_data(self):
        params = {"storage_type": 180, "compression_type": 180}
        form = LiberationForm(user=self.user, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        params = {"storage_type": 1, "compression_type": 1}
        form = LiberationForm(user=self.user, data=params)

        self.assertTrue(form.is_valid())

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)


class LiberationDownloadViewTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.tmp_dir = tempfile.mkdtemp()

        assert self.client.login(username=self.user.username, password="123456")

    def test_sendfile_no_liberation(self):
        response = self.client.get(reverse("user-liberate-get"))
        self.assertEqual(response.status_code, 404)

    def test_default_backend(self):
        module = import_module(settings.SENDFILE_BACKEND)
        self.assertTrue(hasattr(module, "sendfile"))  # function that django-senfile
        self.assertTrue(hasattr(module.sendfile, "__call__"))  # callable

    @override_settings(SENDFILE_BACKEND="sendfile.backends.xsendfile")
    def test_sendfile(self):
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            self.user.liberation.path = "test.txt"
            self.user.liberation.save()

            self.assertEqual(os.path.join(self.tmp_dir, "test.txt"), self.user.liberation.path)

            file_obj = open(self.user.liberation.path, "wb")
            file_obj.write("hello\n")
            file_obj.close()

            response = self.client.get(reverse("user-liberate-get"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, "")
            self.assertEqual(response["Content-Type"], "application/x-gzip")
            self.assertEqual(response["Content-Disposition"], 'attachment; filename="liberated_data.tar.gz"')
            self.assertEqual(response["X-Sendfile"], os.path.join(self.tmp_dir, "test.txt"))

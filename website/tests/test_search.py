# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from django import test
from django.core import urlresolvers

from inboxen.tests import factories


class SearchViewTestCase(test.TestCase):
    def setUp(self):
        super(SearchViewTestCase, self).setUp()
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-search", kwargs={"q": "cheddär"})

    def test_context(self):
        response = self.client.get(self.get_url())
        self.assertIn("search_results", response.context)
        self.assertItemsEqual(response.context["search_results"], ["emails", "inboxes"])

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertIn(u"There are no Inboxes or emails containing <em>cheddär</em>", response.content.decode("utf-8"))

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

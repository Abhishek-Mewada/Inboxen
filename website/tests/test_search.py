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
from django.contrib.auth import get_user_model
from django.core import urlresolvers

from inboxen import models

class SearchViewTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(SearchViewTestCase, self).setUp()
        self.user = get_user_model().objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-search", kwargs={"q":"cheddar"})

    def test_context(self):
        response = self.client.get(self.get_url())
        self.assertIn("search_results", response.context)
        self.assertItemsEqual(response.context["search_results"], ["emails", "inboxes"])

    def test_content(self):
        response = self.client.get(self.get_url())
        self.assertIn("There are no Inboxes or emails containing <em>cheddar</em>", response.content)

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

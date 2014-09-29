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

from blog import models

BODY = """
Hey there!
==========

This is a test post:

* A list item
* And another

Bye!
"""
SUBJECT = """A Test Post For You And Me"""

class BlogTestCase(test.TestCase):
    fixtures = ['inboxen_blog_testdata.json']

    def test_blog_index(self):
        url = urlresolvers.reverse("blog")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_blog_post(self):
        user = get_user_model().objects.get(username="isdabizda")
        user.is_staff = True
        user.save()

        login = self.client.login(username=user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

        models.BlogPost.objects.create(author=user, subject=SUBJECT, draft=False, body=BODY)
        post = models.BlogPost.objects.latest("date")
        self.assertEqual(post.subject, SUBJECT)
        self.assertEqual(post.body, BODY)

    def test_feeds(self):
        response_rss = self.client.get(urlresolvers.reverse("blog-feed-rss"))
        response_atom = self.client.get(urlresolvers.reverse("blog-feed-atom"))

        self.assertEqual(response_rss.status_code, 200)
        self.assertEqual(response_atom.status_code, 200)
        self.assertNotEqual(response_rss.content, response_atom.content)
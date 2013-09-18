##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.contrib.auth.models import User

from inboxen.models import UserProfile

def null_user():
    try:
        user = User.objects.get(username__exact='Melon')
    except User.DoesNotExist:
        user = User.objects.create_user('Melon', '', '')
        user.set_unusable_password()
        user.save()
    
    return user

def user_profile(user):
    """ Gets or creates a user profile """
    try:
        return UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # doesn't exist
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        return user_profile



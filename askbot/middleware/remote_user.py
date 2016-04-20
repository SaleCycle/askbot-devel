import logging
import os
import urllib
from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.files import File
from avatar.models import Avatar
from avatar.conf import settings as avatar_settings

class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_X_AUTH_EMAIL'

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if self.force_logout_if_no_header and request.user.is_authenticated:
                self._remove_invalid_user(request)
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            #if request.user.get_username() == self.clean_username(username, request):
            if request.user.get_username() == username[:username.find("@")]:
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            if user.email != username:
                user.email = username
                user.email_isvalid = True
                user.first_name = request.META['HTTP_X_AUTH_GIVEN_NAME']
                user.last_name = request.META['HTTP_X_AUTH_FAMILY_NAME']
                user.real_name = user.first_name + ' ' + user.last_name
                user.save()

            # If there's no avatar directory for this user on disk, retrieve the avatar from google
            # and set as primary
            if not os.path.exists("/var/askbot-site/askbot/upfiles/avatars/" + username[:username.find("@")]):
                result = urllib.urlretrieve(request.META['HTTP_X_AUTH_PICTURE'])
                avatar = Avatar(user=user, primary=True)
                avatar.avatar.save("/var/askbot-site/askbot/upfiles/avatars/" + username[:username.find("@")], File(open(result[0])))
                avatar.save()
                sizes = avatar_settings.AVATAR_AUTO_GENERATE_SIZES
                for size in sizes:
                    avatar.create_thumbnail(size)
                user.avatar_type = 'a'
                user.clear_avatar_urls()
                user.save()

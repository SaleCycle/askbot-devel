from django.contrib.auth.backends import RemoteUserBackend

class CustomRemoteUserBackend(RemoteUserBackend):
    def clean_username(self, username):
        return username[:username.find("@")]


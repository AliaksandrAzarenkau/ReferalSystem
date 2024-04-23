from django.contrib.auth.backends import ModelBackend
from user.models import UserProfile


class AuthBackend(ModelBackend):
    def authenticate(self, username=None):
        try:
            return UserProfile.objects.get(phone_number=username)
        except UserProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return None

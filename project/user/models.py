from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.db import models


class UserProfileManager(BaseUserManager):
    def create_user(self, phone_number, own_invite_code=None, activated_invite_code=None, last_login=None):
        if not phone_number:
            raise ValueError('Need to provide phone number')
        user = self.model(phone_number=phone_number, own_invite_code=own_invite_code,
                          activated_invite_code=activated_invite_code)
        user.save()
        return user


class UserProfile(AbstractBaseUser):
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='User_phone_number')
    own_invite_code = models.CharField(max_length=6, unique=True, verbose_name='User_own_invite_code')
    activated_invite_code = models.CharField(max_length=6, blank=True, verbose_name='User_own_invite_code')
    last_login = models.DateTimeField(default=timezone.now, verbose_name='Last login')
    password = models.CharField(default='0')  # Для аутентификации

    objects = UserProfileManager()

    def __str__(self):
        return self.phone_number

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['own_invite_code']

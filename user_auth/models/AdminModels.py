from django.db import models
from django.utils.translation import gettext_lazy as _


class Admin(models.Model):
    user = models.OneToOneField('user_auth.User', on_delete=models.CASCADE, unique=True, related_name='admin')
    created_at = models.DateTimeField(_('date created'), auto_now_add=True)

    def __str__(self):
        return self.user.email

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email

    def gender(self):
        return self.user.gender

    def personal_phone_number(self):
        return self.user.personal_phone_number

    def birthday(self):
        return self.user.birthday

    def location(self):
        return self.user.location

    def about_me(self):
        return self.user.about_me

    def image(self):
        return self.user.image.url

    def account_photo(self):
        return self.user.image.url

    def full_name(self):
        return self.user.full_name()

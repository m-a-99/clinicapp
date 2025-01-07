import requests
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    """ User manager """

    def _create_user(self, email, password=None, **extra_fields):
        """Creates and returns a new user using an email address"""
        if not email:  # check for an empty email
            raise AttributeError("User must set an email address")
        else:  # normalizes the provided email
            email = self.normalize_email(email)

        # create user
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hashes/encrypts password
        user.save(using=self._db)  # safe for multiple databases
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Creates and returns a new user using an email address"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_staffuser(self, email, password=None, **extra_fields):
        """Creates and returns a new staffuser using an email address"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and returns a new superuser using an email address"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


def email_to_string(email):
    email_as_list = email.split('@')
    first_part_of_email = email_as_list[0]
    second_part_of_email_as_list = email_as_list[1].split('.')
    return first_part_of_email + '_' + second_part_of_email_as_list[0] + '_' + second_part_of_email_as_list[1]


class User(AbstractBaseUser, PermissionsMixin):
    def email_as_string(self):
        return email_to_string(self.email)

    def upload_user_image(self, filename):
        return 'users/{}/personal_images/{}'.format(self.email_as_string(), filename)

    class Gender(models.TextChoices):
        unknown = "unknown", "unknown"
        Male = "Male", "Male"
        Female = "Female", "Female"

    """ Custom user model """
    email = models.EmailField(
        _('Email Address'),
        max_length=255,
        unique=True,
        help_text='Ex: example@example.com',
        error_messages={
            'unique': _("البريد الالكتروني المدخل مستخدم من قبل شخص أخر ، يرجى إدخال بريد إخر."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_updated = models.DateTimeField(
        _('Last Updated'), auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.unknown,
    )
    image = models.FileField(
        upload_to=upload_user_image,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    personal_phone_number = models.CharField(
        max_length=255,
        null=True,
        unique=True,
        error_messages={
            'unique': _("رقم الهاتف الشخصي المدخل مستخدم من قبل شخص أخر ، يرجى إدخال رقم آخر."),
        },
    )
    birthday = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def account_type(self):
        try:
            doctor = self.doctor
            return 'Doctor'
        except:
            try:
                patient = self.patient
                return 'Patient'
            except:
                try:
                    admin = self.admin
                    return 'Admin'
                except:
                    return 'not specified'

    def status(self):
        try:
            doctor = self.doctor
            status_labels = ["Rejected", "Accepted", "Pending"]
            return status_labels[int(doctor.status)]
        except:
            try:
                patient = self.patient
                return "Accepted"
            except:
                try:
                    admin = self.admin
                    return "Accepted"
                except:
                    return "Rejected"

    def status_message(self):
        try:
            doctor = self.doctor
            return doctor.status_message
        except:
            return None

    def __str__(self):
        return self.email

    def personal_ID(self):
        if self.account_type() == "Doctor":
            return self.doctor.personal_ID
        else:
            return None

    def work_phone_number(self):
        if self.account_type() == "Doctor":
            return self.doctor.work_phone_number
        else:
            return None

    def specialization(self):
        if self.account_type() == "Doctor":
            return self.doctor.specialization
        else:
            return None

    def years_of_experience(self):
        if self.account_type() == "Doctor":
            return self.doctor.years_of_experience
        else:
            return None

    def marital_status(self):
        if self.account_type() == "Doctor":
            return self.doctor.marital_status
        else:
            return None

    def account_photo(self):
        return self.image.url

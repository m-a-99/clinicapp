from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Doctor(models.Model):
    def upload_doctor_medical_licence(self, filename):
        return 'doctors/{}/medical_licences/{}'.format(self.user.email_as_string(), filename)

    def upload_doctor_face_photo(self, filename):
        return 'doctors/{}/face_photos/{}'.format(self.user.email_as_string(), filename)

    class MaritalStatus(models.TextChoices):
        unknown = "unknown", "unknown"
        Married = "Married", "Married"
        Widowed = "Widowed", "Widowed"
        Divorced = "Divorced", "Divorced"
        Single = "Single", "Single"

    class Status(models.IntegerChoices):
        Pending = 2, "Pending"
        Accepted = 1, "Accepted"
        Rejected = 0, "Rejected"

    user = models.OneToOneField('user_auth.User', on_delete=models.CASCADE, unique=True, related_name='doctor')
    specialization = models.CharField(max_length=255, default='not specified')
    work_phone_number = models.CharField(
        max_length=255,
        null=True,
        unique=True,
        error_messages={
            'unique': _("رقم هاتف العمل المدخل مستخدم من قبل شخص أخر ، يرجى إدخال رقم آخر."),
        },
    )
    years_of_experience = models.IntegerField(default=0)
    personal_ID = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        error_messages={
            'unique': _("الرقم المدني المدخل مستخدم من قبل شخص أخر ، يرجى إدخال رقم آخر."),
        },
    )
    face_photo = models.FileField(
        upload_to=upload_doctor_face_photo,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    marital_status = models.CharField(
        max_length=10,
        choices=MaritalStatus.choices,
        default=MaritalStatus.unknown,
    )
    medical_licence = models.FileField(
        upload_to=upload_doctor_medical_licence,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.Pending,
    )
    status_message = models.TextField(blank=True, null=True)
    department = models.ForeignKey('web.Department', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_('date created'), auto_now_add=True)

    def __str__(self):
        return self.user.email

    def department_details(self):
        from web.serializers import DepartmentSerializer
        return DepartmentSerializer(self.department).data

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


class Education(models.Model):
    def upload_doctor_education_medical_certificate(self, filename):
        return 'doctors/{}/medical_certificates/{}/{}'.format(
            self.doctor.user.email_as_string(),
            f"{self.university}_{self.degree}",
            filename
        )

    doctor = models.OneToOneField('user_auth.Doctor', on_delete=models.CASCADE, related_name='education')
    university = models.CharField(max_length=255, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    time_period = models.CharField(max_length=255, null=True, blank=True)
    certificate = models.FileField(
        upload_to=upload_doctor_education_medical_certificate,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    created_at = models.DateTimeField(_('date created'), auto_now_add=True)

    def __str__(self):
        return self.doctor.user.email

    def medical_licence(self):
        return self.doctor.medical_licence


class WorkExperience(models.Model):
    def upload_doctor_work_experience_certificate(self, filename):
        return 'doctors/{}/work_experience_certificates/{}'.format(
            self.doctor.user.email_as_string(),
            filename
        )

    doctor = models.ForeignKey('user_auth.Doctor', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    time_period = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    certificate = models.FileField(
        upload_to=upload_doctor_work_experience_certificate,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    created_at = models.DateTimeField(_('date created'), auto_now_add=True)

    def __str__(self):
        return self.doctor.user.email

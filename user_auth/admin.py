from django.contrib import admin
from .models import (
    User,
    Doctor,
    Patient,
    MedicalHistory,
    Education,
    WorkExperience,
    Admin,
)


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor')


class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(MedicalHistory, MedicalHistoryAdmin)
admin.site.register(Education)
admin.site.register(WorkExperience, WorkExperienceAdmin)
admin.site.register(Admin)

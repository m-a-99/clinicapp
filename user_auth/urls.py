from django.urls import path
from knox import views as knox_views
from .views import (
    RegisterAPI,
    LoginAPI,
    CheckLogin,
    change_password,

    # User Views
    UserBasicInfo,
    UserProfileInfo,
    UserProfileDetails,

    # Doctor Views
    DoctorEditGeneralInfo,
    DoctorEditPersonalInfo,
    DoctorEditEducationInfo,
    DoctorEditWorkExperience,
    DoctorCreateWorkExperience,
    DoctorDeleteWorkExperience,

    # Patient Views
    PatientEditGeneralInfo,
    PatientEditMedicalHistory,
    PatientCreateMedicalHistory,
    PatientDeleteMedicalHistory,

    # Admin Views
    PendingDoctors,
    RejectedDoctors,
    UpdateDoctorStatus,
)

urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('logout/', knox_views.LogoutView.as_view()),
    path('logoutall/', knox_views.LogoutAllView.as_view()),
    path('change/password/', change_password),
    path('check/login/', CheckLogin.as_view()),

    # User API's
    path('user/get/basic/info/', UserBasicInfo.as_view()),
    path('user/get/profile/info/', UserProfileInfo.as_view()),
    path('user/get/profile/details/', UserProfileDetails.as_view()),

    # Doctor API's
    path('doctor/edit/general/info/', DoctorEditGeneralInfo.as_view()),
    path('doctor/edit/personal/info/', DoctorEditPersonalInfo.as_view()),
    path('doctor/edit/education/info/', DoctorEditEducationInfo.as_view()),
    path('doctor/edit/work/experience/', DoctorEditWorkExperience.as_view()),
    path('doctor/create/work/experience/', DoctorCreateWorkExperience.as_view()),
    path('doctor/delete/work/experience/', DoctorDeleteWorkExperience.as_view()),

    # Patient API's
    path('patient/edit/general/info/', PatientEditGeneralInfo.as_view()),
    path('patient/edit/medical/history/', PatientEditMedicalHistory.as_view()),
    path('patient/create/medical/history/', PatientCreateMedicalHistory.as_view()),
    path('patient/delete/medical/history/', PatientDeleteMedicalHistory.as_view()),

    # Admin API's
    # path('get/pending/doctors/', PendingDoctors.as_view()),
    # path('get/rejected/doctors/', RejectedDoctors.as_view()),
    path('update/doctor/status/', UpdateDoctorStatus.as_view()),

]

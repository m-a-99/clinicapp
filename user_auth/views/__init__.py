from .UserAuthenticationViews import (
    RegisterAPI,
    LoginAPI,
    CheckLogin,
    change_password,
    UserBasicInfo,
    UserProfileInfo,
    UserProfileDetails,

    # Admin API's
    PendingDoctors,
    RejectedDoctors,
    UpdateDoctorStatus,
)
from .DoctorViews import (
    DoctorEditGeneralInfo,
    DoctorEditPersonalInfo,
    DoctorEditEducationInfo,
    DoctorEditWorkExperience,
    DoctorCreateWorkExperience,
    DoctorDeleteWorkExperience,
)

from .PatientViews import (
    PatientEditGeneralInfo,
    PatientEditMedicalHistory,
    PatientCreateMedicalHistory,
    PatientDeleteMedicalHistory,

)

__all__ = [
    # User Authentication Views
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

    # Admin API's
    PendingDoctors,
    RejectedDoctors,
    UpdateDoctorStatus,
]

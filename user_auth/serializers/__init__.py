from .UserAuthenticationSerializers import (
    RegisterSerializer,
    UserSerializer,
    UserBasicInfoSerializer,
    UserBasicDetailsSerializer,

)
from .DoctorSerializers import (
    DoctorProfileInfoSerializer,
    DoctorGeneralInfoSerializer,
    DoctorPersonalInfoSerializer,
    DoctorEducationInfoSerializer,
    DoctorWorkExperienceSerializer,
    DoctorBasicDetailsSerializer,
    DoctorBasicAndEducationDetailsSerializer,
    DoctorBasicAndPersonalDetailsSerializer,

)

from .PatientSerializers import (
    PatientProfileInfoSerializer,
    PatientGeneralInfoSerializer,
    PatientMedicalHistorySerializer,
    PatientBasicDetailsSerializer,
)

__all__ = [
    # User Authentication Serializers
    RegisterSerializer,
    UserSerializer,

    # User Serializers
    UserBasicInfoSerializer,
    UserBasicDetailsSerializer,

    # Doctor Serializers
    DoctorProfileInfoSerializer,
    DoctorGeneralInfoSerializer,
    DoctorPersonalInfoSerializer,
    DoctorEducationInfoSerializer,
    DoctorWorkExperienceSerializer,
    DoctorBasicDetailsSerializer,
    DoctorBasicAndEducationDetailsSerializer,
    DoctorBasicAndPersonalDetailsSerializer,

    # DoctorEditGeneralInfoSerializer,

    # Patient Serializers
    PatientProfileInfoSerializer,
    PatientGeneralInfoSerializer,
    PatientMedicalHistorySerializer,
    PatientBasicDetailsSerializer,
]

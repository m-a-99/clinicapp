from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.files.storage import FileSystemStorage

from ..models import (
    User,
    Doctor,
    Education,
    WorkExperience,
)


def upload_user_image(email_as_string, filename):
    return 'users/{}/personal_images/{}'.format(email_as_string, filename)


class DoctorGeneralInfoSerializer(serializers.ModelSerializer):
    work_phone_number = serializers.CharField(required=False)
    specialization = serializers.CharField(required=False)
    years_of_experience = serializers.IntegerField(min_value=0, required=False)

    class Meta:
        model = User
        fields = [
            'account_type',
            'email',
            'first_name',
            'last_name',
            'birthday',
            'gender',
            'work_phone_number',
            'image',
            'about_me',
            'specialization',
            'years_of_experience',
        ]

        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'birthday': {'required': False},
            'gender': {'required': False},
            'work_phone_number': {'required': False},
            'image': {'required': False},
            'about_me': {'required': False},
            'specialization': {'required': False},
            'years_of_experience': {'required': False},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ['specialization', 'years_of_experience', 'work_phone_number']:
                instance.doctor.__setattr__(attr, value)
            else:
                setattr(instance, attr, value)
        if instance.doctor.status == 0:
            instance.doctor.status = 2
        instance.save()
        instance.doctor.save()
        return instance


class DoctorPersonalInfoSerializer(serializers.ModelSerializer):
    personal_phone_number = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())],
                                                  required=False)
    location = serializers.CharField(required=False)

    class Meta:
        model = Doctor
        fields = [
            'personal_phone_number',
            'personal_ID',
            'face_photo',
            'marital_status',
            'location',
        ]
        extra_kwargs = {
            'personal_phone_number': {'required': False},
            'personal_ID': {'required': False},
            'face_photo': {'required': False},
            'marital_status': {'required': False},
            'location': {'required': False},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ['personal_phone_number', 'location']:
                instance.user.__setattr__(attr, value)
            else:
                setattr(instance, attr, value)
        if instance.status == 0:
            instance.status = 2
        instance.user.save()
        instance.save()
        return instance


class DoctorEducationInfoSerializer(serializers.ModelSerializer):
    medical_licence = serializers.FileField(required=False)

    class Meta:
        model = Education
        fields = [
            'university',
            'degree',
            'time_period',
            'certificate',
            'medical_licence',
        ]
        extra_kwargs = {
            'university': {'required': False},
            'degree': {'required': False},
            'time_period': {'required': False},
            'certificate': {'required': False},
            'medical_licence': {'required': False},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ['medical_licence']:
                setattr(instance.doctor, attr, value)
            else:
                setattr(instance, attr, value)
        if instance.doctor.status == 0:
            instance.doctor.status = 2
        instance.doctor.save()
        instance.save()
        return instance


class DoctorWorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = [
            'id',
            'title',
            'time_period',
            'body',
            'certificate',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if instance.doctor.status == 0:
            instance.doctor.status = 2
        instance.doctor.save()
        instance.save()
        return instance

    def create(self, validated_data):
        def upload_doctor_work_experience_certificate(doctor, filename):
            return 'doctors/{}/work_experience_certificates/{}'.format(
                doctor.user.email_as_string(),
                filename
            )

        doctor = self.context['request'].user.doctor
        title = validated_data['title']
        time_period = validated_data['time_period']
        body = validated_data['body']
        certificate = validated_data['certificate']

        # image url settings
        fs = FileSystemStorage()
        filename = fs.save(upload_doctor_work_experience_certificate(doctor, certificate.name), certificate)
        uploaded_file_url = fs.url(filename)
        certificate_url = str(uploaded_file_url)[7:]

        work_experience = WorkExperience.objects.create(
            doctor=doctor,
            title=title,
            time_period=time_period,
            body=body,
            certificate=certificate_url,
        )
        if work_experience:
            if work_experience.doctor.status == 0:
                work_experience.doctor.status = 2
            work_experience.doctor.save()
            return work_experience
        else:
            msg = 'لم يتم الإنشاء.'
            raise serializers.ValidationError(msg, code='authorization')


class DoctorProfileInfoSerializer(serializers.ModelSerializer):
    general = serializers.SerializerMethodField('get_general')
    personal_info = serializers.SerializerMethodField('get_personal_info')
    education = serializers.SerializerMethodField('get_education')
    work_experiences = serializers.SerializerMethodField('get_work_experiences')

    def get_general(self, obj):
        return DoctorGeneralInfoSerializer(obj, context={'request': self.context.get('request')}).data

    def get_personal_info(self, obj):
        return DoctorPersonalInfoSerializer(obj.doctor, context={'request': self.context.get('request')}).data

    def get_education(self, obj):
        def get_medical_licence_full_url(self, obj):
            image_url = obj.doctor.medical_licence.url
            request = self.context.get('request')
            return request.build_absolute_uri(image_url)

        try:
            education = obj.doctor.education
            return DoctorEducationInfoSerializer(education, context={'request': self.context.get('request')}).data
        except:
            return {
                'university': None,
                'degree': None,
                'time_period': None,
                'certificate': None,
                'medical_licence': get_medical_licence_full_url(self, obj),
            }

    def get_work_experiences(self, obj):
        work_experiences = obj.doctor.workexperience_set.all()
        return DoctorWorkExperienceSerializer(work_experiences, many=True,
                                              context={'request': self.context.get('request')}).data

    class Meta:
        model = User
        fields = [
            'general',
            'personal_info',
            'education',
            'work_experiences',
            'status',
            'status_message',
        ]


class DoctorBasicDetailsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_user_id', read_only=True)
    image = serializers.SerializerMethodField('get_doctor_image_full_url', read_only=True)

    def get_doctor_image_full_url(self, obj):
        doctor_image = obj.user.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(doctor_image)

    def get_user_id(self, obj):
        return obj.user.id

    class Meta:
        model = Doctor
        fields = [
            'id',
            'full_name',
            'image',
        ]
        read_only_fields = ['id']


class DoctorBasicAndEducationDetailsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_user_id', read_only=True)
    image = serializers.SerializerMethodField('get_doctor_image_full_url', read_only=True)
    university = serializers.SerializerMethodField('get_doctor_university', read_only=True)
    degree = serializers.SerializerMethodField('get_doctor_degree', read_only=True)

    def get_doctor_image_full_url(self, obj):
        doctor_image = obj.user.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(doctor_image)

    def get_user_id(self, obj):
        return obj.user.id

    def get_doctor_university(self, obj):
        try:
            return obj.education.university
        except:
            return None

    def get_doctor_degree(self, obj):
        try:
            return obj.education.degree
        except:
            return None

    class Meta:
        model = Doctor
        fields = [
            'id',
            'full_name',
            'image',
            'specialization',
            'university',
            'degree',
        ]
        read_only_fields = ['id']


class DoctorBasicAndPersonalDetailsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_user_id', read_only=True)
    image = serializers.SerializerMethodField('get_doctor_image_full_url', read_only=True)
    degree = serializers.SerializerMethodField('get_doctor_degree', read_only=True)

    def get_doctor_image_full_url(self, obj):
        doctor_image = obj.user.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(doctor_image)

    def get_user_id(self, obj):
        return obj.user.id

    def get_doctor_degree(self, obj):
        try:
            return obj.education.degree
        except:
            return None

    class Meta:
        model = Doctor
        fields = [
            'id',
            'first_name',
            'last_name',
            'image',
            'department_details',
            'location',
            'degree',
            'status',
            'status_message',
             'specialization',
        ]

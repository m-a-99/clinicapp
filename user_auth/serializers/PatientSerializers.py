from rest_framework import serializers
from ..models import (
    User,
    Patient,
    MedicalHistory,
)


class PatientGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'account_type',
            'email',
            'first_name',
            'last_name',
            'birthday',
            'gender',
            'image',
            'about_me',
            'location',
            'personal_phone_number',
        ]
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'birthday': {'required': False},
            'gender': {'required': False},
            'image': {'required': False},
            'about_me': {'required': False},
            'location': {'required': False},
            'personal_phone_number': {'required': False},
        }


class PatientMedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = [
            'id',
            'title',
            'time_period',
            'body',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        patient = self.context['request'].user.patient
        title = validated_data['title']
        time_period = validated_data['time_period']
        body = validated_data['body']

        medical_history = MedicalHistory.objects.create(
            patient=patient,
            title=title,
            time_period=time_period,
            body=body,
        )
        if medical_history:
            return medical_history
        else:
            msg = 'لم يتم الإنشاء.'
            raise serializers.ValidationError(msg, code='authorization')


class PatientProfileInfoSerializer(serializers.ModelSerializer):
    general = serializers.SerializerMethodField('get_general')
    medical_histories = serializers.SerializerMethodField('get_medical_histories')

    def get_general(self, obj):
        return PatientGeneralInfoSerializer(obj, context=self.context).data

    def get_medical_histories(self, obj):
        medical_histories = obj.patient.medicalhistory_set.all()
        return PatientMedicalHistorySerializer(medical_histories, many=True, context=self.context).data

    class Meta:
        model = User
        fields = [
            'general',
            'medical_histories',
        ]


class PatientBasicDetailsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_user_id', read_only=True)
    image = serializers.SerializerMethodField('get_patient_image_full_url', read_only=True)

    def get_patient_image_full_url(self, obj):
        patient_image = obj.user.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(patient_image)

    def get_user_id(self, obj):
        return obj.user.id

    class Meta:
        model = Patient
        fields = [
            'id',
            'full_name',
            'image',
        ]
        read_only_fields = ['id']

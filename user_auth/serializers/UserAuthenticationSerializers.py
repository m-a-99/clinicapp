from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import (
    User,
    Doctor,
    Patient,
)


class RegisterSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(['Doctor', 'Patient'])
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'type',
            'email',
            'password',
            'confirm_password',
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'type': {'required': True},
            'email': {'required': True},
            'password': {
                'write_only': True,
                'required': True
            },
            'confirm_password': {
                'write_only': True,
                'required': True
            },
        }

    def create(self, validated_data):
        first_name = validated_data['first_name'] if 'first_name' in validated_data else ""
        last_name = validated_data['last_name'] if 'last_name' in validated_data else ""
        type = validated_data['type']
        email = validated_data['email']
        password = validated_data['password']
        confirm_password = validated_data['confirm_password']

        if password == "":
            msg = _('يرجى إدخال كلمة المرور')
            raise serializers.ValidationError(msg, code='authorization')

        if password != confirm_password:
            msg = _('كلمات المرور المدخلة غير متطابقة.')
            raise serializers.ValidationError(msg, code='authorization')

        if len(password) < 8:
            msg = _('كلمة المرور قصيرة جدا ، يجب أن لا تقل كلمة المرور عن 8 حروف أو أرقام.')
            raise serializers.ValidationError(msg, code='authorization')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        if user:
            if type == 'Doctor':
                profile = Doctor.objects.create(
                    user=user,
                )
            elif type == 'Patient':
                profile = Patient.objects.create(
                    user=user
                )
            else:
                msg = _('لم يتم التسجيل.')
                raise serializers.ValidationError(msg, code='authorization')
            return user

        else:
            msg = _('لم يتم التسجيل.')
            raise serializers.ValidationError(msg, code='authorization')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'account_photo',
            'email',
        ]


class UserBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'account_type',
            'status',
            'status_message',
            'email',
            'first_name',
            'last_name',
            'location',
            'image',
            'gender',
            'birthday',
        ]


class UserBasicDetailsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_user_image_full_url', read_only=True)

    def get_user_image_full_url(self, obj):
        user_image = obj.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(user_image)

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'image',
            'account_type',
        ]
        read_only_fields = ['id']

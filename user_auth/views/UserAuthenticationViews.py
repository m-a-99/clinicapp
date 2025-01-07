import datetime
import pytz
from rest_framework import generics
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from knox.views import LoginView as KnoxLoginView
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from ..permissions import IsDoctor, IsPatient, IsAdmin, IsDoctorRegardlessStatus
from ..models import (
    User,
    Doctor,
)
from knox.models import AuthToken


class RegisterAPI(generics.GenericAPIView):
    from ..serializers.UserAuthenticationSerializers import RegisterSerializer
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from ..serializers.UserAuthenticationSerializers import UserSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class MyAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            check_user = get_object_or_404(User, email=email)
        except:
            msg = _('البريد الإلكتروني المدخل غير صحيح.')
            raise serializers.ValidationError(msg, code='authorization')
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('كلمة المرور المدخلة غير صحيحة')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('يرجى التأكد من إدخال البريد الإلكتروني وكلمة المرور.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class LoginAPI(KnoxLoginView):
    permission_classes = [AllowAny]
    template_name = 'user_auth/login_page.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, format=None):
        serializer = MyAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)
        # return HttpResponseRedirect('http://localhost:3000/')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        user = User.objects.get(pk=request.user.id)
    except:
        return JsonResponse(status=404, data={'status': False, "message": "User Not Found"})
    try:
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']
    except:
        msg = _('يرجى التأكد من إدخال جميع الحقول.')
        raise serializers.ValidationError(msg, code='authorization')

    if not user.check_password(old_password):
        msg = _('كلمة المرور القديمة المدخلة غير صحيحة')
        raise serializers.ValidationError(msg, code='authorization')
    elif new_password != confirm_new_password:
        msg = _('كلمات المرور المدخلة غير متطابقة.')
        raise serializers.ValidationError(msg, code='authorization')
    if len(new_password) < 8:
        msg = _('كلمة المرور قصيرة جدا ، يجب أن لا تقل كلمة المرور عن 8 حروف أو أرقام.')
        raise serializers.ValidationError(msg, code='authorization')
    elif old_password == new_password:
        msg = _('كلمة المرور القديمة لا يمكن أن تكون هي كلمة المرور الجديدة، يرجى إختيار كلمة أخرى.')
        raise serializers.ValidationError(msg, code='authorization')
    else:
        user.set_password(new_password)
        user.save()
        # update_session_auth_hash(request, user)
        return JsonResponse(status=201, data={'status': True, "message": "تم تغيير كلمة المرور بنجاح"})


class UserBasicInfo(generics.RetrieveAPIView):
    from ..serializers import UserBasicInfoSerializer
    serializer_class = UserBasicInfoSerializer
    permission_classes = [IsAuthenticated, IsDoctorRegardlessStatus | IsPatient | IsAdmin]

    def get_object(self):
        return self.request.user


class UserProfileInfo(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsDoctorRegardlessStatus | IsPatient]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user.account_type() == "Doctor":
            from ..serializers import DoctorProfileInfoSerializer
            serializer = DoctorProfileInfoSerializer(instance, context={'request': self.request})
            return Response(serializer.data)
        elif self.request.user.account_type() == "Patient":
            from ..serializers import PatientProfileInfoSerializer
            serializer = PatientProfileInfoSerializer(instance, context={'request': self.request})
            return Response(serializer.data)

        else:
            return None


class UserProfileDetails(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsDoctorRegardlessStatus | IsPatient | IsAdmin]

    def get_object(self):
        try:
            user_id = int(self.request.GET["user_id"])
        except:
            return 0
        try:
            user = User.objects.get(id=user_id)
            return user
        except:
            return 1

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالمستخدم",
                },
                status=400
            )
        elif instance == 1:
            return Response(
                {
                    'status': False,
                    'msg': "المستخدم الذي تحاول عرض المعلومات الخاصة به غير موجود",
                },
                status=404
            )
        else:
            if instance.account_type() == "Doctor":
                from ..serializers import DoctorProfileInfoSerializer
                serializer = DoctorProfileInfoSerializer(instance, context={'request': self.request})
                return Response(serializer.data)
            elif instance.account_type() == "Patient":
                from ..serializers import PatientProfileInfoSerializer
                serializer = PatientProfileInfoSerializer(instance, context={'request': self.request})
                return Response(serializer.data)
            else:
                return Response(
                    {
                        'status': False,
                        'msg': "المستخدم الذي تحاول عرض المعلومات الخاصة به غير موجود",
                    },
                    status=404
                )


class PendingDoctors(generics.ListAPIView):
    from user_auth.serializers import DoctorBasicAndEducationDetailsSerializer
    serializer_class = DoctorBasicAndEducationDetailsSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Doctor.objects.filter(status=2)


class RejectedDoctors(generics.ListAPIView):
    from user_auth.serializers import DoctorBasicAndEducationDetailsSerializer
    serializer_class = DoctorBasicAndEducationDetailsSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Doctor.objects.filter(status=0)


from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


class UpdateDoctorStatus(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        try:
            doctor_user_id = int(self.request.POST["id"])
            status = int(self.request.POST["status"])
            status_message = self.request.POST.get("status_message")
        except:
            return 0, -1, -1
        try:
            doctor = User.objects.get(id=doctor_user_id).doctor
        except:
            return 1, 0, 0
        return doctor, status, status_message

    def update(self, request, *args, **kwargs):
        instance, status, status_message = self.get_object()
        if instance == 0 or status not in [0, 1]:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى التأكد من إرسال البيانات المطلوبة",
                },
                status=400
            )
        elif instance == 1:
            return Response(
                {
                    'status': False,
                    'msg': "الدكتور الذي تحاول التعديل عليه غير موجود",
                },
                status=404
            )
        else:
            if status == 0:
                if instance.status == 0:
                    return Response(
                        {
                            'status': False,
                            'msg': "الدكتور الذي تحاول رفضه ،  مرفوض من قبل",
                        },
                        status=400
                    )
                else:
                    instance.status = 0
                    if status_message:
                        instance.status_message = status_message
                    instance.save()
                    msg_html = render_to_string('user_auth/reject.html',
                                                {'doctor_full_name': instance.user.full_name,
                                                 'date': datetime.datetime.today().date(),
                                                 'admin_status_message': status_message})
                    subject, from_email, to = 'Rejected As Doctor in E-Clinic System Website', settings.EMAIL_HOST_USER, instance.user.email
                    text_content = 'This is an important message.'
                    html_content = msg_html
                    mssg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    mssg.attach_alternative(html_content, "text/html")
                    mssg.send()
                    return Response(
                        {
                            'status': True,
                            'msg': "تم رفض الدكتور بنجاح",
                            'status_message': status_message,
                            'doctor_id': int(instance.user.id),
                        },
                        status=201
                    )
            elif status == 1:
                if instance.status == 1:
                    return Response(
                        {
                            'status': False,
                            'msg': "الدكتور الذي تحاول قبوله ،  مقبول من قبل",
                        },
                        status=400
                    )
                else:
                    instance.status = 1
                    if status_message:
                        instance.status_message = status_message
                    instance.save()
                    return Response(
                        {
                            'status': True,
                            'msg': "تم قبول الدكتور بنجاح",
                            'status_message': status_message,
                            'doctor_id': int(instance.user.id),
                        },
                        status=201
                    )


class CheckLogin(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        try:
            user_id = int(self.request.GET["user_id"])
        except:
            return -1, -1

        return AuthToken.objects.filter(
            user__id=user_id,
            expiry__gt=datetime.datetime.now().replace(tzinfo=pytz.UTC)
        ).exists(), user_id

    def retrieve(self, request, *args, **kwargs):
        instance, user_id = self.get_object()
        if instance == -1:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالمستخدم",
                },
                status=400
            )
        else:
            return Response(
                {
                    'is_login': instance,
                    'user_id': user_id,
                },
                status=201
            )

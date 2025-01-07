from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsPatient
from rest_framework.response import Response

from ..models import (
    User,
    Patient,
    MedicalHistory,
)


class PatientEditGeneralInfo(generics.UpdateAPIView):
    from ..serializers import PatientGeneralInfoSerializer
    serializer_class = PatientGeneralInfoSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    queryset = User.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class PatientEditMedicalHistory(generics.UpdateAPIView):
    from ..serializers import PatientMedicalHistorySerializer
    serializer_class = PatientMedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            medical_history_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            obj = self.request.user.patient.medicalhistory_set.get(id=medical_history_id)
        except:
            return 1
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response({
                'status': False,
                'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر المراد التعديل عليه",
            },
                status=400
            )
        if instance == 1:
            return Response({
                'status': False,
                'msg': "العنصر الذي تحاول التعديل عليه غير موجود",
            },
                status=404
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class PatientCreateMedicalHistory(generics.CreateAPIView):
    from ..serializers import PatientMedicalHistorySerializer
    serializer_class = PatientMedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsPatient]


class PatientDeleteMedicalHistory(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            medical_history_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            medical_history = MedicalHistory.objects.get(pk=medical_history_id, patient=self.request.user.patient)
            return medical_history
        except:
            return 1

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0:
            return Response({
                'status': False,
                'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر المراد حذفه",
            },
                status=400
            )
        if instance == 1:
            return Response({
                'status': False,
                'msg': "العنصر الذي تحاول حذفه غير موجود",
            },
                status=404
            )
        else:
            instance_id = instance.id
            self.check_object_permissions(self.request, instance)
            self.perform_destroy(instance)
            return Response({
                'status': True,
                'msg': "تم حذف العنصر بنجاح",
                'id': instance_id,
            },
                status=201
            )

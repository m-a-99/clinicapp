from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Room
from user_auth.models import User
from rest_framework.response import Response
from user_auth.permissions import IsPatient, IsDoctor
class GetContacts(generics.ListAPIView):
    from .serializers import RoomSerializer
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsDoctor|IsPatient]
    pagination_class = None

    def get_queryset(self):
        rooms = Room.objects.filter(users=self.request.user)
        return rooms

    # def list(self, request, *args, **kwargs):
    #     query = self.get_queryset()
    #     queryset = self.filter_queryset(query)
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

class GetRoomMembers(generics.RetrieveAPIView):
    from .serializers import PartnerSerializer
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated, IsDoctor|IsPatient]

    #  error Doc
    # {
    #     0 : 'room id not passed',
    #     1 : 'room id 404',
    #
    # }
    def get_object(self):
        try:
            room_id = self.kwargs.get('room_id')
        except:
            return 0
        try:
            room = Room.objects.get(id=room_id,users_=self.request.user)
        except:
            return 1

        return room

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0:
            return Response({
                'status': False,
                'msg': "يرجى التأكد من إرسال البيانات المطلوبة (room_id)",
            },
                status=400
            )
        if instance == 1:
            return Response(
                status=404,
                data={
                    'status': False,
                    'msg': "الغرفة التي تحاول عرضها غير موجودة",
                },

            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
class GetAddContactsList(generics.ListAPIView):
    from .serializers import PartnerSerializer
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated, IsDoctor|IsPatient]
    pagination_class = None

    def get_queryset(self):
        contacts = [d['users__id'] for d in list(Room.objects.filter(users=self.request.user,type='p2p').values('users__id'))]
        not_contacts = User.objects.exclude(id__in=contacts).exclude(id=self.request.user.id)
        return not_contacts
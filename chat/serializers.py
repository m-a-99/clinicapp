from rest_framework import serializers
from .models import Room
from user_auth.models import User

class RoomSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_room_name')
    photo = serializers.SerializerMethodField('get_room_photo')

    def get_room_name(self,obj):
        room_type = obj.type
        if room_type == 'p2p':
            request = self.context.get('request')
            current_user = request.user
            return (obj.users.exclude(id=current_user.id))[0].full_name()
        else:
            return obj.name

    def get_room_photo(self, obj):
        room_type = obj.type
        request = self.context.get('request')
        if room_type == 'p2p':
            current_user = request.user
            image_url = (obj.users.exclude(id=current_user.id))[0].image.url
            return request.build_absolute_uri(image_url)
        else:
            return request.build_absolute_uri(obj.photo.url)

    class Meta:
        model = Room
        fields = ['id','name','type','photo']


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','full_name']



from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save,pre_delete,post_delete,pre_save,m2m_changed
from django.dispatch import receiver



class Room(models.Model):
    def upload_room_photo(self, filename):
        return 'chat/rooms/{}/photos/{}'.format(self.id, filename)

    class Type(models.TextChoices):
        p2p = 'p2p', "p2p"
        group = 'group', "group"
    users = models.ManyToManyField('user_auth.User')
    name = models.CharField(max_length=255,null=True,blank=True)
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.p2p,
    )
    photo = models.FileField(
        upload_to=upload_room_photo,
        default='/default_images/default_image_for_all_models.jpeg'
    )
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    def __str__(self):
        return f"{self.id}"
    def f(self):
        return self.users.count()


class Messages(models.Model):
    room = models.ForeignKey('chat.Room',on_delete=models.CASCADE)
    body = models.TextField(null=True,blank=True)
    send_time = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    def __str__(self):
        return self.id


@receiver(m2m_changed, sender=Room.users.through)
def change_room_type(sender, action, instance, **kwargs):
    if action in ['post_add','post_remove']:
        room = instance
        if (room.users.count() > 2) and (room.type == 'p2p'):
            room.type = 'group'
            room.save()
        if (room.users.count() in [1,2]) and (room.type == 'group'):
            room.type = 'p2p'
            room.save()

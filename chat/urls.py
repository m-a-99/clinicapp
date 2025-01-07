from django.urls import path
from .views import (
    GetContacts,
    GetRoomMembers,
    GetAddContactsList,
)
urlpatterns = [
    path('get/contacts/', GetContacts.as_view()),
    path('get/room/members/<int:room_id>/', GetRoomMembers.as_view()),
    path('get/add/contacts/list/', GetAddContactsList.as_view()),

]

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from user_auth.permissions import IsDoctor, IsPatient, IsAdmin
from rest_framework.response import Response
import os
from django.http import FileResponse, HttpResponse
from rest_framework import filters
from django.db.models import Q

from .models import (
    Department,
    Question,
    QuestionFile,
    File,
    Discussion,
    Blog,
    Comment,
)
from user_auth.models import Doctor, User


# def MissParameters():
#         return Response({
#             'status': False,
#             'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
#         },
#             status=400
#         )
#
# def NotFound():
#         return Response(
#             {
#             'status': False,
#             'msg': "العنصر الذي تحاول التعديل عليه غير موجود",
#             },
#             status=404
#         )

def dummy_secure_media_directory(request, file):
    try:
        print("a" * 100)

        print(file)
        document = File.objects.get(path=f'files/{file}')
        question = QuestionFile.objects.get(file_id=document.id).question
        print("a" * 100)

        # user_email_as_string = file.split('/')[0]
        # if (user_email_as_string == request.user.email_as_string()):
        users_access = []
        if question.to_doctor:
            users_access.append(question.to_doctor.user)
        else:
            if question.department:
                department_doctors = Doctor.objects.filter(department_id=question.department.id, status=1)
                for doctor in department_doctors:
                    users_access.append(doctor.user)
            else:
                users_access = ['ALL_DOCTORS']
        print(users_access)
        print((('ALL_DOCTORS' in users_access) and (request.user.account_type() == 'Doctor')) or \
              (request.user in users_access) or \
              (request.user == question.patient.user))
        if (('ALL_DOCTORS' in users_access) and (request.user.account_type() == 'Doctor')) or \
                (request.user in users_access) or \
                (request.user == question.patient.user):
            file_path = os.path.join(os.getcwd(), 'media/files/', file)
            file_opened = open(file_path, 'rb')
            response = FileResponse(file_opened)
            return response
        else:
            return HttpResponse(status=403)
    except:
        return HttpResponse(status=403)


class Departments(generics.ListAPIView):
    from .serializers import DepartmentSerializer
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient | IsAdmin]
    pagination_class = None

    def get_queryset(self):
        # departmets_test_lest = ["COVID-19",
        #  "Allergist",
        #  "Anesthesiologist-resuscitator",
        #  "Venereologist",
        #  "Gastroenterologist",
        #  "Hematologist",
        #  "Geneticist",
        #  "Hepatologist",
        #  "Gynecologist",
        #  "Homeopathist",
        #  "Dermatologist",
        #  "Pediatric gastroenterologist",
        #  "Pediatric gynecologist",
        #  "Children's dermatologist",
        #  "Children's infectious disease specialist",
        #  "Pediatric cardiologist",
        #  "Children's ENT",
        #  "Children's neurologist",
        #  "Pediatric Nephrologist",
        #  "Children's ophthalmologist",
        #  "Child psychologist",
        #  "Children's pulmonologist",
        #  "Pediatric rheumatologist",
        #  "Pediatric urologist",
        #  "Pediatric surgeon",
        #  "Pediatric endocrinologist",
        #  "Nutritionist",
        #  "Immunologist",
        #  "Infectionist",
        #  "Cardiologist",
        #  "Clinical psychologist",
        #  "Clinical psychologist",
        #  "Cosmetologist",
        #  "Speech therapist",
        #  "Lore",
        #  "Medical lawyer",
        #  "Mammologist",
        #  "Expert in narcology"]
        # for departmet in departmets_test_lest :
        #     new_department = Department.objects.create(name=departmet)
        departments = Department.objects.all()
        return departments


class CreateQuestion(generics.CreateAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsPatient]


class EditQuestion(generics.UpdateAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            question_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            question = Question.objects.get(id=question_id, patient=self.request.user.patient)
        except:
            return 1
        self.check_object_permissions(self.request, question)
        return question

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
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


class DeleteQuestion(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            question_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            question = Question.objects.get(pk=question_id, patient=self.request.user.patient)
            return question
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
        elif instance == 1:
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


class QuestionDetails(generics.RetrieveAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            question_id = self.request.GET[self.lookup_field]
        except:
            return 0
        try:
            question = Question.objects.get(id=question_id)
            return question
        except:
            return 1

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
                    'status': False,
                    'msg': "العنصر الذي تحاول عرض تفاصيله غير موجود",
                },
                status=404
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuestionDiscussions(generics.ListAPIView):
    from .serializers import DiscussionSerializer
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]

    def get_queryset(self):
        try:
            question_id = self.request.GET["question_id"]
        except:
            return 0
        try:
            question_discussions = Question.objects.get(id=question_id).discussion_set.all().order_by('-created_at')
        except:
            return 1
        return question_discussions

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        print("1" * 100)
        if query == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if query == 1:
            return Response(
                {
                    'status': False,
                    'msg': "العنصر الذي تحاول عرض تفاصيله غير موجود",
                },
                status=404
            )
        print('2' * 100)
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CreateDiscussion(generics.CreateAPIView):
    from .serializers import DiscussionSerializer
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]


class EditDiscussion(generics.UpdateAPIView):
    from .serializers import DiscussionSerializer
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            discussion_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            discussion = Discussion.objects.get(id=discussion_id, user=self.request.user)
        except:
            return 1
        # self.check_object_permissions(self.request, discussion)
        return discussion

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
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


class DeleteDiscussion(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            discussion_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            discussion = Discussion.objects.get(pk=discussion_id, user=self.request.user)
            return discussion
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
        elif instance == 1:
            return Response({
                'status': False,
                'msg': "العنصر الذي تحاول حذفه غير موجود",
            },
                status=404
            )
        else:
            instance_id = instance.id
            # self.check_object_permissions(self.request, instance)
            self.perform_destroy(instance)
            return Response({
                'status': True,
                'msg': "تم حذف العنصر بنجاح",
                'id': instance_id,

            },
                status=201
            )


class CreateBlog(generics.CreateAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsDoctor]


class EditBlog(generics.UpdateAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    lookup_field = 'id'

    def get_object(self):
        try:
            blog_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            blog = Blog.objects.get(id=blog_id, doctor=self.request.user.doctor)
        except:
            return 1
        self.check_object_permissions(self.request, blog)
        return blog

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
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


class DeleteBlog(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsDoctor]
    lookup_field = 'id'

    def get_object(self):
        try:
            blog_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            blog = Blog.objects.get(pk=blog_id, doctor=self.request.user.doctor)
            return blog
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
        elif instance == 1:
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


class BlogDetails(generics.RetrieveAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            blog_id = self.request.GET[self.lookup_field]
        except:
            return 0
        try:
            blog = Blog.objects.get(id=blog_id)
            return blog
        except:
            return 1

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
                    'status': False,
                    'msg': "العنصر الذي تحاول عرض تفاصيله غير موجود",
                },
                status=404
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogComments(generics.ListAPIView):
    from .serializers import CommentSerializer
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]

    def get_queryset(self):
        try:
            blog_id = self.request.GET["blog_id"]
        except:
            return 0
        try:
            blog_comments = Blog.objects.get(id=blog_id).comment_set.all().order_by('-created_at')
        except:
            return 1
        return blog_comments

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if query == 1:
            return Response(
                {
                    'status': False,
                    'msg': "العنصر الذي تحاول عرض تفاصيله غير موجود",
                },
                status=404
            )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CreateComment(generics.CreateAPIView):
    from .serializers import CommentSerializer
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]


class EditComment(generics.UpdateAPIView):
    from .serializers import CommentSerializer
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            comment_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            comment = Comment.objects.get(id=comment_id, user=self.request.user)
        except:
            return 1
        # self.check_object_permissions(self.request, discussion)
        return comment

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
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


class DeleteComment(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    lookup_field = 'id'

    def get_object(self):
        try:
            comment_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            comment = Comment.objects.get(pk=comment_id, user=self.request.user)
            return comment
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
        elif instance == 1:
            return Response({
                'status': False,
                'msg': "العنصر الذي تحاول حذفه غير موجود",
            },
                status=404
            )
        else:
            instance_id = instance.id
            # self.check_object_permissions(self.request, instance)
            self.perform_destroy(instance)
            return Response({
                'status': True,
                'msg': "تم حذف العنصر بنجاح",
                'id': instance_id,
            },
                status=201
            )


class BlogLike(generics.CreateAPIView):
    from .serializers import BlogLikeSerializer
    serializer_class = BlogLikeSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status, done, msg = self.perform_create(serializer)
        if status == 0 and done:
            return Response(
                {
                    'status': True,
                    'action': 'dislike',
                    'msg': msg,
                },
                status=201
            )
        elif status == 0 and not done:
            return Response(
                {
                    'status': False,
                    'action': 'dislike',
                    'msg': msg,
                },
                status=400
            )
        elif status == 1 and done:
            return Response(
                {
                    'status': True,
                    'action': 'like',
                    'msg': msg,
                },
                status=201
            )
        elif status == 1 and not done:
            return Response(
                {
                    'status': False,
                    'action': 'like',
                    'msg': msg,
                },
                status=400
            )

    def perform_create(self, serializer):
        return serializer.save()


class DepartmentQuestions(generics.ListAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'body',
        'patient__user__first_name',
        'patient__user__last_name',
        'to_doctor__user__first_name',
        'to_doctor__user__last_name',
        'to_doctor__department__name',
        'department__name'
    ]

    def get_queryset(self):
        try:
            department_id = self.request.GET["department_id"]
            # dumm implementation i will change it later
            if not department_id == 'all':
                try:
                    department_id = int(department_id)
                except:
                    return 1
        except:
            return 0
        if department_id == 'all':
            department_questions = Question.objects.all().order_by('-created_at')
        elif not (department_id > 0):
            return 1
        else:
            if not Department.objects.filter(id=department_id).exists():
                return 1
            else:
                department_questions = Question.objects.filter(department_id=department_id).order_by('-created_at')
        return department_questions

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if query == 1:
            return Response(
                {
                    'status': False,
                    'msg': "القسم الذي تحاول عرض الأسئلة الخاصة به غير موجود",
                },
                status=404
            )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentsDoctors(generics.ListAPIView):
    from .serializers import DepartmentDoctorsSerializer
    serializer_class = DepartmentDoctorsSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    pagination_class = None

    def get_queryset(self):
        return Department.objects.all()


class PersonalQuestions(generics.ListAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'body',
        'patient__user__first_name',
        'patient__user__last_name',
        'to_doctor__user__first_name',
        'to_doctor__user__last_name',
        'to_doctor__department__name',
        'department__name'
    ]

    def get_queryset(self):
        return Question.objects.filter(patient=self.request.user.patient)


class AllBlogs(generics.ListAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'doctor__user__first_name',
        'doctor__user__last_name',
        'body',
        'doctor__department__name'
    ]

    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')


class Doctors(generics.ListAPIView):
    from user_auth.serializers import DoctorBasicAndPersonalDetailsSerializer
    serializer_class = DoctorBasicAndPersonalDetailsSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsPatient | IsAdmin]

    def get_queryset(self):

        try:
            department_id = str(self.request.GET["department_id"])
            if not department_id == 'all' and not department_id.isdigit():
                return 1
        except:
            department_id = 'all'
        if department_id == 'all':
            status = self.request.GET.get("status")
            if status and str(status) in ["0", "1", "2"]:
                criterion2 = Q(status=int(status))
            else:
                criterion2 = Q(id__gt=0)
            print(status)
            department_doctors = Doctor.objects.filter(criterion2)
        elif not (int(department_id) > 0) or not Department.objects.filter(id=int(department_id)).exists():
            return 1
        else:
            criterion1 = Q(department_id=int(department_id))
            status = self.request.GET.get("status")
            if status and str(status) in ["0", "1", "2"]:
                criterion2 = Q(status=int(status))
            else:
                criterion2 = Q(id__gt=0)
            print(status)
            department_doctors = Doctor.objects.filter(criterion1 & criterion2)
        return department_doctors

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        if query == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if query == 1:
            return Response(
                {
                    'status': False,
                    'msg': "القسم الذي تحاول عرض الأسئلة الخاصة به غير موجود",
                },
                status=404
            )
        queryset = self.filter_queryset(query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PersonalBlogs(generics.ListAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'doctor__user__first_name',
        'doctor__user__last_name',
        'body',
        'doctor__department__name'
    ]

    def get_queryset(self):
        return Blog.objects.filter(doctor=self.request.user.doctor).order_by('-created_at')


from django_filters.rest_framework import DjangoFilterBackend


class QuestionFilter(generics.ListAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'body',
        'patient__user__first_name',
        'patient__user__last_name',
        'to_doctor__user__first_name',
        'to_doctor__user__last_name',
        'to_doctor__department__name',
        'department__name'
    ]
    queryset = Question.objects.all()


class BlogFilter(generics.ListAPIView):
    from .serializers import BlogSerializer
    serializer_class = BlogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'doctor__user__first_name',
        'doctor__user__last_name',
        'body',
        'doctor__department__name'
    ]
    queryset = Blog.objects.all()


class CreateDepartment(generics.CreateAPIView):
    from .serializers import DepartmentSerializer
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class EditDepartment(generics.UpdateAPIView):
    from .serializers import DepartmentSerializer
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def get_object(self):
        try:
            department_id = self.request.POST[self.lookup_field]
        except:
            return 0
        try:
            department = Department.objects.get(id=department_id)
        except:
            return 1
        return department

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance == 0:
            return Response(
                {
                    'status': False,
                    'msg': "يرجى إرسال المعرف (id) الخاص بالعنصر",
                },
                status=400
            )
        if instance == 1:
            return Response(
                {
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


class UpdateDoctorDepartment(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        try:
            doctor_user_id = int(self.request.POST["doctor"])
            new_department_id = int(self.request.POST["department"])
        except:
            return 0, 0
        try:
            doctor = User.objects.get(id=doctor_user_id).doctor
        except:
            return 1, 1
        try:
            department = Department.objects.get(id=new_department_id)
        except:
            return 2, 2
        return doctor, department

    def update(self, request, *args, **kwargs):
        instance, new_department = self.get_object()
        if instance == 0:
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
        elif instance == 2:
            return Response(
                {
                    'status': False,
                    'msg': "القسم الذي تحاول إضافته للدكتور غير موجود",
                },
                status=404
            )
        else:
            instance.department = new_department
            instance.save()
            return Response(
                {
                    'status': True,
                    'msg': "تم إضافة القسم إلى الدكتور بنجاح",
                    'doctor_id': int(instance.id),
                    'department_id': int(instance.department.id),
                },
                status=201
            )


class DoctorDirectedQuestions(generics.ListAPIView):
    from .serializers import QuestionSerializer
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'body',
        'patient__user__first_name',
        'patient__user__last_name',
        'to_doctor__user__first_name',
        'to_doctor__user__last_name',
        'to_doctor__department__name',
        'department__name'
    ]

    def get_queryset(self):
        return Question.objects.filter(to_doctor=self.request.user.doctor)

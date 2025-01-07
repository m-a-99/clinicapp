from django.contrib import admin
from .models import (
    Question,
    Discussion,
    Blog,
    Comment,
    BlogLike,
    File,
    QuestionFile,
    # DiscussionFile,
    BlogFile,
    Department,
)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'patient', 'files')


class QuestionFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'file', 'patient')

    def patient(self, instance):
        try:
            return instance.question.patient
        except:
            return 'ERROR!!'


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'body')


# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id','username','email','full_name','mobile')
#
#     def email(self,instance):
#         try:
#             return instance.user.email
#         except :
#             return 'ERROR!!'
#
#

admin.site.register(Question, QuestionAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(BlogLike)
admin.site.register(File, FileAdmin)
admin.site.register(QuestionFile, QuestionFileAdmin)
# admin.site.register(DiscussionFile)
admin.site.register(BlogFile)
admin.site.register(Department, DepartmentAdmin)

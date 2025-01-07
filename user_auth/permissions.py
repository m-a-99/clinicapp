from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    message = '''You do not have permission to perform this action, for one of the reasons :
    1-User type Must Be Doctor
    2-User Must Have Permission To Edit This Object
    '''

    def has_permission(self, request, view):
        try:
            user = request.user.doctor
            if user.status != 1:
                return False
            else:
                return True
        except:
            return False

    def has_object_permission(self, request, view, obj):
        try:
            doctor = request.user.doctor
            if doctor == obj.doctor:
                return True
            else:
                return False
        except:
            return False


class IsDoctorRegardlessStatus(BasePermission):
    message = '''You do not have permission to perform this action, for one of the reasons :
    1-User type Must Be Doctor
    2-User Must Have Permission To Edit This Object
    '''

    def has_permission(self, request, view):
        try:
            user = request.user.doctor
            return True
        except:
            return False


class IsPatient(BasePermission):
    message = '''You do not have permission to perform this action, for one of the reasons :
    1-User type Must Be Patient
    2-User Must Have Permission To Edit This Object
    '''

    def has_permission(self, request, view):
        try:
            user = request.user.patient
        except:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        try:
            patient = request.user.patient
            if patient == obj.patient:
                return True
            else:
                return False
        except:
            return False


class IsAdmin(BasePermission):
    message = '''You do not have permission to perform this action, for one of the reasons :
    1-User type Must Be Admin
    2-User Must Have Permission To Edit This Object
    '''

    def has_permission(self, request, view):
        try:
            user = request.user.admin
        except:
            return False
        return True

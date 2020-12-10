from datetime import datetime
from django.shortcuts import get_list_or_404, get_object_or_404

from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions, status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    ListAPIView,
    DestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.projects.serializers import InvoiceTimelineHistorySerializer, ClaimTimelineHistorySerializer
from .models import User
from apps.licenses.models import License, Enterprise, EnterpriseLicense, LicenseHistory, UserLicense
from apps.projects.models import EnterpriseProjectRole, Invoice, Claims, InvoiceTimelineHistory, ClaimTimelineHistory, \
    ActivitySchedule, ClaimsSchedule
from apps.licenses.serializers import (
    LicenseSerializer,
    EnterpriseSerializer,
    UserLicenseSerializer,
    EnterpriseLicenseSerializer,
    LicenseHistorySerializer,
    ActiveEnterpriseLicenseSerializer,
    ActiveUserLicenseSerializer
    )
from .serializers import (
    UserRegisterSerializer,
    UserConfirmRegistrationSerializer,
    ProfileSerializer,
    MemberSerializer,
    EnterpriseRoleSerializer,
    EnterpriseRoleViewSerializer,
)


class RegisterView(CreateAPIView):
    """
    Register a new user.
    Send a verification link to provided email address.
    """

    permission_classes = [permissions.AllowAny]  # Or anon users can't register
    serializer_class = UserRegisterSerializer


register_view = RegisterView.as_view()  # noqa


class ConfirmRegistrationView(GenericAPIView):
    """
    Verify email of registered user and finish the registration process
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = UserConfirmRegistrationSerializer

    def dispatch(self, *args, **kwargs):
        return super(ConfirmRegistrationView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Email has been verified")})


conf_register_view = ConfirmRegistrationView.as_view()


class UserProfileView(RetrieveUpdateAPIView):
    """
    Retrieve / Update a user
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        try:
            user_id = self.kwargs.get("user_id")
            return User.objects.get(id=user_id)
        except:
            return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

user_profile_view = UserProfileView.as_view()


class DeleteProfileView(DestroyAPIView):
    """
    Remove account,
    Will erase data includint projects, invoices, claims, memebers ..etc
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        if instance.is_enterprise_member:
            raise ValidationError("Can't delete member profile. Please contact enterprise admin")
        instance.delete()


delete_profile_view = DeleteProfileView.as_view()


class ListUserLicensesView(ListAPIView):
    """
    List/Create licenses
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = LicenseSerializer

    def get_queryset(self):
        if self.request.user.is_enterprise_admin:
            return []
        else:
            queryset = License.objects.filter(is_active=True)
            return queryset


list_user_licenses_view = ListUserLicensesView.as_view()


class CreateEnterpriseMember(ListCreateAPIView):
    """
    List and create enterprise members
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = MemberSerializer
    queryset = License.objects.all()

    def get_queryset(self):
        cur_user = self.request.user
        if cur_user.is_enterprise_member:
            return User.objects.filter(created_by=cur_user.created_by, is_active=True).exclude(id=cur_user.id)
        members = User.objects.filter(created_by=cur_user, is_active=True)
        return members

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


create_enterprise_member_view = CreateEnterpriseMember.as_view()

class DeleteEnterpriseMember(DestroyAPIView):
    """
    Delete enterprise members
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = MemberSerializer

    def change_ownership(self, member_id):
        try:
            member = User.objects.get(id=member_id)
            invoices = Invoice.objects.filter(created_by=member)
            claims = Claims.objects.filter(created_by= member)
            e_admin = member.created_by
            if (e_admin != member) and (member.is_enterprise_admin == False):
                invoices.update(created_by = e_admin)
                claims.update(created_by = e_admin)
                return {"detail": "All roles of this user is assigned to Enterprise admin.","status": True}
            else:
                return {"detail": "Delete Enterprise Admin","status": True}
        except:
            return {"detail": "This user cannot be deleted until all roles are reassigned.","status": False}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        member_id = self.kwargs["member_id"]
        delete_status = self.kwargs["status"]
        delete_possibility = self.change_ownership(member_id)
        if delete_possibility['status'] and delete_status == 'delete':
            self.perform_destroy(instance)
            return Response(delete_possibility["detail"], status=status.HTTP_200_OK)
        elif delete_possibility['status'] and delete_status == 'falsedelete':
            instance.is_active = False
            instance.save()
            return Response(delete_possibility["detail"], status=status.HTTP_200_OK)
        else:
            return Response(delete_possibility["detail"], status=status.HTTP_406_NOT_ACCEPTABLE)


    def get_object(self):
        member_id = self.kwargs["member_id"]
        return get_object_or_404(User,pk=member_id)

delete_enterprise_member_view = DeleteEnterpriseMember.as_view()



class ListEnterpriseLicensesView(ListAPIView):

    """
    List/Create licenses
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = EnterpriseSerializer
    queryset = Enterprise.objects.filter(is_active=True)


list_enterprise_licenses_view = ListEnterpriseLicensesView.as_view()

class ActiveLicenseView(ListAPIView):
    """
    Verify email of registered user and finish the registration process
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActiveEnterpriseLicenseSerializer

    def get_queryset(self):
        if self.request.user.is_enterprise_admin:
            queryset = EnterpriseLicense.objects.filter(user=self.request.user.id, expiry__gte=datetime.now())
            return queryset
        else:
            self.serializer_class = ActiveUserLicenseSerializer
            queryset = UserLicense.objects.filter(user=self.request.user, expiry__gte=datetime.now())
            return queryset

active_licenses_view = ActiveLicenseView.as_view()


class ListLicensesHistoryView(ListAPIView):
    """
    List/Create licenses
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LicenseHistorySerializer
    queryset = LicenseHistory.objects.all()

    def get_queryset(self):
        queryset = LicenseHistory.objects.filter(user=self.request.user).order_by('-payment_date')
        return queryset

list_licenses_history_view = ListLicensesHistoryView.as_view()

class EnterpriseRoleView(CreateAPIView):
    """
    List and create enterprise member roles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EnterpriseRoleSerializer

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        project = instance.project
        instance.member.user_projects.add(instance.project)
        schedules = ActivitySchedule.objects.all().order_by("activity_category", "schedule_order")
        claimschedules = ClaimsSchedule.objects.all().order_by("activity_category", "schedule_order")
        # get invoice scheduled activity types
        for schedule in schedules:
            for n in range(1, 8):
                attr_name = f"activity_{n}"
                if hasattr(schedule, attr_name):
                    activity_type = getattr(schedule, attr_name)
                    if activity_type:
                        project.settings.create(
                            event=activity_type, category=schedule.activity_category, schedule=schedule,
                            project_user=instance.member
                        )
        # get claim scheduled activity types
        for schedule in claimschedules:
            for n in range(1, 6):
                attr_name = f"activity_{n}"
                if hasattr(schedule, attr_name):
                    activity_type = getattr(schedule, attr_name)
                    if activity_type:
                        project.claimsettings.create(
                            event=activity_type, category=schedule.activity_category, schedule=schedule,
                            project_user=instance.member
                        )

create_enterprise_role_view = EnterpriseRoleView.as_view()


class EnterpriseRoleListView(ListAPIView):
    """
    List and create enterprise member roles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EnterpriseRoleViewSerializer

    def get_queryset(self):
        try:
            roles = get_list_or_404(EnterpriseProjectRole,created_by=self.request.user)
        except:
            roles = EnterpriseProjectRole.objects.filter(member=self.request.user)
        return roles

list_enterprise_project_role_view = EnterpriseRoleListView.as_view()

class EnterpriseRoleUpdateView(DestroyAPIView):
    """
    delete enterprise member roles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EnterpriseRoleSerializer

    def get_object(self):
        role_id = self.kwargs["role_id"]
        user = EnterpriseProjectRole.objects.get(pk=role_id)
        user.member.user_projects.remove(user.project)
        user.project.settings.filter(project_user=user.member).delete()
        user.project.claimsettings.filter(project_user=user.member).delete()
        return get_object_or_404(EnterpriseProjectRole,pk=role_id)

update_enterprise_role_view = EnterpriseRoleUpdateView.as_view()

class EnterpriseRoleListbyProject(ListAPIView):
    """
    list enterprise member roles by project
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EnterpriseRoleSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return EnterpriseProjectRole.objects.filter(project=project_id)

list_enterprise_role_view = EnterpriseRoleListbyProject.as_view()


class UserInvoiceHistory(ListAPIView):
    """
    list enterprise member invoice action history
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = InvoiceTimelineHistorySerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        actions = InvoiceTimelineHistory.objects.filter(updated_by=get_object_or_404(User.objects.all(), id=user_id))
        return actions

user_invoicehistory_view = UserInvoiceHistory.as_view()


class UserClaimHistory(ListAPIView):
    """
    list enterprise member claim action history
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ClaimTimelineHistorySerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        actions = ClaimTimelineHistory.objects.filter(updated_by=get_object_or_404(User.objects.all(), id=user_id))
        return actions

user_claimhistory_view = UserClaimHistory.as_view()

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode as uid_decoder
from rest_auth.serializers import (
    LoginSerializer as BaseLoginSerializer,
    PasswordResetConfirmSerializer as BasePasswordResetConfirmSerializer,
    PasswordResetSerializer as BasePasswordResetSerializer,
    PasswordChangeSerializer as BasePasswordChangeSerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .forms import PpastUserCreationForm as UserCreationForm,PpastMemberCreationForm
from .models import User, UserType
from apps.projects.models import EnterpriseProjectRole, Project

UserModel = get_user_model()


class LoginSerializer(BaseLoginSerializer):
    # make email mandatory
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)


class PasswordResetSerializer(BasePasswordResetSerializer):
    def get_email_options(self):
        return {
            "email_template_name": "registration/password_reset_email.txt",
            "html_email_template_name": "registration/password_reset_email.html",
        }


class PasswdResetConfirmSerializer(BasePasswordResetConfirmSerializer):
    new_password1 = serializers.CharField(max_length=128, trim_whitespace=False)
    new_password2 = serializers.CharField(max_length=128, trim_whitespace=False)


class PasswordChangeSerializer(BasePasswordChangeSerializer):
    old_password = serializers.CharField(max_length=128, trim_whitespace=False)
    new_password1 = serializers.CharField(max_length=128, trim_whitespace=False)
    new_password2 = serializers.CharField(max_length=128, trim_whitespace=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    email = serializers.EmailField(max_length=128)
    first_name = serializers.CharField(max_length=128)
    last_name = serializers.CharField(max_length=128)
    password1 = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)
    is_enterprise_admin = serializers.BooleanField(default=True)
    is_enterprise_member = serializers.BooleanField(default=False, required=False)
    company_name = serializers.CharField(max_length=64)
    address = serializers.CharField()
    phone_number = serializers.CharField(max_length=16)
    postal_code = serializers.CharField(max_length=64)
    city = serializers.CharField(max_length=64)
    country = serializers.CharField(max_length=64)
    province = serializers.CharField(max_length=64)
    user_creation_form_class = UserCreationForm

    def validate(self, attrs):
        self.user_creation_form = self.user_creation_form_class(data=attrs)
        if not self.user_creation_form.is_valid():
            raise serializers.ValidationError(self.user_creation_form.errors)

        return attrs

    def validate_email(self, email):
        if UserModel.objects.filter(email__iexact=email).count() > 0:
            raise serializers.ValidationError("Email already exists")
        return email.lower()

    def save(self):
        user = self.user_creation_form.save()
        # deactivate user till email is verified
        user.is_active = False
        user.save()
        return user


class UserConfirmRegistrationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_text(uid_decoder(attrs["uid"]))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({"uid": ["Invalid value"]})

        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise ValidationError({"token": ["Invalid value"]})

        return attrs

    def save(self):
        self.user.is_active = True
        self.user.save()
        return self.user


class ProfileSerializer(serializers.ModelSerializer):
    # not a required for every update
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_staff = serializers.BooleanField(required=False, read_only=True)
    is_enterprise_admin = serializers.BooleanField(required=False)
    is_enterprise_member = serializers.BooleanField(required=False)

    class Meta:
        model = UserModel
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_enterprise_admin", "is_enterprise_member", "company_name", "address", "phone_number", "postal_code", "city", "country", "province")




class MemberSerializer(serializers.ModelSerializer):
    is_enterprise_member = serializers.BooleanField()
    user_creation_form_class = PpastMemberCreationForm


    def validate_email(self, email):
        if UserModel.objects.filter(email__iexact=email).count() > 0:
            raise serializers.ValidationError("Email already exists")
        return email.lower()

    class Meta:
        model = User
        fields = ( "id","username","first_name", "last_name", "email","is_active","is_enterprise_member")
       
        read_only_fields = ("created_by","password1", "password2")

class ProjectNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ("id", "name", "location", "owner_name")



class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = "__all__"

class EnterpriseRoleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField( many=False,queryset=UserType.objects.all(), slug_field='code')
    class Meta:
        model = EnterpriseProjectRole
        fields = ("id", "role", "member", "project")


class EnterpriseRoleViewSerializer(serializers.ModelSerializer):
    project = ProjectNameSerializer(read_only=True)
    created_by = ProfileSerializer(read_only=True)
    role = UserTypeSerializer(read_only=True)
    class Meta:
        model = EnterpriseProjectRole
        fields = ("id", "role", "member", "created_by", "project")

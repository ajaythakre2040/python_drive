from rest_framework import serializers
from auth_system.models import User, Role
from auth_system.utils.validators import validate_custom_password
from ..utils.sanitize import no_html_validator

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, required=False)  
    primary_mobile_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "primary_mobile_number",
            "password",
            "full_name",
            "gender",
            "dob",
            "email_id",
            "role",
        ]

        def validate_old_password(self, value):
            return value.strip()

    def validate_role(self, value):
        role_code = value.upper()
        role = Role.objects.filter(code=role_code, is_active=True).first()
        if not role:
            raise serializers.ValidationError(f"Role '{value}' is invalid or inactive")
        return role

    def validate_primary_mobile_number(self, value):
        value = no_html_validator(value)
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Mobile number must be 10 digits")
        if User.objects.filter(primary_mobile_number=value).exists():
            raise serializers.ValidationError("Mobile number already registered")
        return value

    def create(self, validated_data):
        role = validated_data.pop("role", None)
        password = validated_data.pop("password")
        user = User.all_objects.create_user(**validated_data, role=role, password=password)
        return user
class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        return validate_custom_password(value)
class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        return validate_custom_password(value)
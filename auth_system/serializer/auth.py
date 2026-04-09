from rest_framework import serializers
from auth_system.models import User
from auth_system.utils.password_validation import validate_custom_password
from ..utils.sanitize import no_html_validator
from ..utils.email_validations import check_email
from ..utils.register_validation import validate_full_name, validate_dob, validate_mobile_number

#================================ Register============================#
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    primary_mobile_number = serializers.CharField(required=True)
    secondary_mobile_number = serializers.CharField(required=False, allow_blank=True)
    email_id = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = "__all__"

    # =========================
    # 🔹 COMMON UNIQUE CHECK
    # =========================
    def _check_unique(self, field, value, role, message):
        if value and role:
            if User.all_objects.filter(**{field: value, "role": role}).exists():
                raise serializers.ValidationError(message)

    # =========================
    # 🔹 FIELD VALIDATIONS
    # =========================

    def validate_full_name(self, value):
        value = no_html_validator(value)
        return validate_full_name(value)

    def validate_primary_mobile_number(self, value):
        value = validate_mobile_number(value)
        role = self.context.get("role")

        self._check_unique("primary_mobile_number", value,role,"Mobile number already registered for this role")
        return value

    def validate_secondary_mobile_number(self, value):
        if value:
            return validate_mobile_number(value)
        return value

    def validate_email_id(self, value):
        if not value:
            return None

        value = no_html_validator(value)
        value = check_email(value)

        role = self.context.get("role")

        self._check_unique("email_id",value,role,"Email already registered for this role")
        return value

    def validate_dob(self, value):
        return validate_dob(value)

    def validate_password(self, value):
        validate_custom_password(value)
        return value

    # =========================
    # 🔹 CROSS FIELD VALIDATION
    # =========================
    def validate(self, data):
        primary = data.get("primary_mobile_number")
        secondary = data.get("secondary_mobile_number")

        if primary and secondary and primary == secondary:
            raise serializers.ValidationError({
                "secondary_mobile_number": "Primary and Secondary mobile cannot be same."
            })

        return data

    # =========================
    # 🔹 CREATE USER
    # =========================
    def create(self, validated_data):
        role = self.context.get("role")
        password = validated_data.pop("password")

        # Force role from context (security)
        validated_data.pop("role", None)

        user = User.all_objects.create_user(
            **validated_data,
            role=role,
            password=password
        )

        return user
#=========================================Change password=====================================#
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_custom_password(value)
        return value

#=========================================Reset password=====================================#
class ForgetPasswordSerializer(serializers.Serializer):
    primary_mobile_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email_id = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    new_password = serializers.CharField(write_only=True, required=False)
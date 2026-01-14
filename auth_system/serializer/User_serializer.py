from rest_framework import serializers
from auth_system.models import User, Role
from ..utils.validators import validate_custom_password


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    role = serializers.CharField(write_only=True)

    password = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "full_name",
            "primary_mobile_number",
            "password",
            "role",
            "email_id",
            "gender",
            "dob",
            "current_address",
            "permanent_address",
        ]
        read_only_fields = ["user_id"]

    def validate_password(self, value):
        return validate_custom_password(value)

    def validate_role(self, value):
        role_code = value.upper()
        role = Role.objects.filter(code=role_code,is_active=True).first()

        if not role:
            raise serializers.ValidationError(f"Role '{value}' is invalid or inactive.")
        return role  

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role", None)

        user = User.all_objects.create_user(password=password,role=role,**validated_data)
        return user

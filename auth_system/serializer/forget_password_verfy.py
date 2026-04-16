from rest_framework import serializers
from auth_system.utils.password_validation import validate_custom_password

class VerifyOTPAndForgetPasswordSerializer(serializers.Serializer):
    primary_mobile_number = serializers.CharField(required=False, allow_blank=True)
    email_id = serializers.EmailField(required=False, allow_blank=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        mobile = data.get("primary_mobile_number")
        email = data.get("email_id")

        if not mobile and not email:
            raise serializers.ValidationError("Either primary_mobile_number or email_id is required")
        return data
    
    def validate_new_password(self, value):
        validate_custom_password(value)
        return value
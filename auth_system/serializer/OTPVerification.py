from rest_framework import serializers
from auth_system.utils.sanitize import no_html_validator

class SendOTPSerializer(serializers.Serializer):
    otp_type = serializers.ChoiceField(choices=["mobile", "email"])
    mobile_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, data):
        otp_type = data.get("otp_type")
        mobile_number = data.get("mobile_number")
        email = data.get("email")

        if otp_type == "mobile" and not mobile_number:
            raise serializers.ValidationError({"mobile_number": "Mobile number is required for mobile OTP"})
        if otp_type == "email" and not email:
            raise serializers.ValidationError({"email": "Email is required for email OTP"})
        return data

class VerifyOTPSerializer(serializers.Serializer):
    otp_id = serializers.UUIDField() 
    otp = serializers.CharField(validators=[no_html_validator])

class RESENDOTPSerializer(serializers.Serializer):
    otp_id = serializers.UUIDField()  

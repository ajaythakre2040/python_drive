from rest_framework import serializers
from ..utils.mpin_validation import validate_mpin

class ForgetMPINSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    new_mpin = serializers.CharField(max_length=4, min_length=4)

    def validate_new_mpin(self, value):
        validate_mpin(value)
        return value
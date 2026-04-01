from rest_framework import serializers

class ForgetMPINSerializer(serializers.Serializer):
    new_mpin = serializers.CharField(max_length=4, min_length=4)
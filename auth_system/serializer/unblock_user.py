from rest_framework import serializers
from ..models.unblock_history import UserBlockHistory

class UnblockUserSerializer(serializers.ModelSerializer):
    email_id = serializers.EmailField(required=True)
    primary_mobile_number = serializers.CharField(required=True, max_length=10)

    class Meta:
        model = UserBlockHistory
        fields = ['email_id', 'primary_mobile_number']
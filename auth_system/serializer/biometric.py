from  rest_framework import serializers
from ..models import User_security

class UserSecuritySerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.user_id',read_only = True)

    class Meta:
        model = User_security
        fields = "__all__"
        read_only_fields = ['created_at','created_by', 'updated_by',]
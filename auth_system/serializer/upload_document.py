from rest_framework import serializers
from ..models import User_Documents

class DocumentUploadSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.user_id',read_only=True)


    class Meta:
        model = User_Documents
        fields = "__all__"

    read_only_fields = ['user_id','is_aadhaar_verified', 'is_dl_verified', 'is_pan_verified','is_rc_verified', 'is_insurance_verified', 'is_selfie_verified']
    
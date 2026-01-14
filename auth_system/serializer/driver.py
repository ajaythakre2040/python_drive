from rest_framework import serializers
from ..models.driver import Driver_Document
class DriverDocumentSerializer(serializers.ModelSerializer):
    driver = serializers.ReadOnlyField(source="driver.user_id")

    class Meta:
        model = Driver_Document
        fields = "__all__"
        read_only_fields = (
            "driver", "is_verified", "created_by", "updated_by", "deleted_by",
            "created_at", "updated_at", "deleted_at"
        )

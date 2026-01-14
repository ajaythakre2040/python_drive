from rest_framework import serializers
from ..models.vehicle import Vehicle
from ..utils.sanitize import no_html_validator


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    rc_number = serializers.CharField(validators=[no_html_validator])
    
    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("owner","created_by","updated_by","deleted_by",)

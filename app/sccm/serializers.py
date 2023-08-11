from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description']


class SCCMSerializer(serializers.Serializer):
    MachineName = serializers.CharField()
    LastLogon = serializers.DateTimeField()
    CPUType = serializers.CharField()
    OperatingSystem = serializers.CharField()
    OSVesionBuild = serializers.CharField()
    LastLogonUser = serializers.CharField()
    Description = serializers.CharField(required=False, allow_null=True)
    Model = serializers.CharField()
    ResourceID = serializers.IntegerField()
    SystemDriveSize = serializers.CharField(required=False, allow_null=True)
    SystemDriveFree = serializers.CharField(required=False, allow_null=True)
    LastTimeAgentTalkedToServer = serializers.DateTimeField() # Corresponds to "ws.LastHWScan"
    TPMVersion = serializers.CharField()
    TPMActivated = serializers.BooleanField()  # Assuming it's boolean; if not use IntegerField
    TPMEnabled = serializers.BooleanField()
    TPMOwned = serializers.BooleanField()
    SecureBoot = serializers.BooleanField()
    UEFI = serializers.BooleanField()
    LastBootTime = serializers.DateTimeField()
    SystemDrive = serializers.CharField()
    SystemDriveEncryption = serializers.BooleanField()
    ComputerType = serializers.CharField()
    PrimaryUser = serializers.CharField()
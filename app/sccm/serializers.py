from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description']


class SCCMSerializer(serializers.Serializer):
    MachineName = serializers.CharField()
    Model = serializers.CharField()
    ResourceID = serializers.IntegerField()
    Description = serializers.CharField(required=False, allow_null=True)
    SystemDrive = serializers.CharField()
    SystemDriveEncryption = serializers.IntegerField()
    ComputerType = serializers.CharField()
    LastLogon = serializers.DateTimeField()
    CPUType = serializers.CharField()
    OperatingSystem = serializers.CharField()
    SystemDriveSize = serializers.CharField(required=False, allow_null=True)
    SystemDriveFree = serializers.CharField(required=False, allow_null=True)
    PrimaryUser = serializers.CharField()
    LastLogonUser = serializers.CharField()
    LastHWScan = serializers.DateTimeField()
    LastBootTime = serializers.DateTimeField()
    TPMVersion = serializers.CharField()
    TPMActivated = serializers.IntegerField()
    TPMEnabled = serializers.IntegerField()
    TPMOwned = serializers.IntegerField()
    SecureBoot = serializers.IntegerField()
    UEFI = serializers.IntegerField()
    OSVesionBuild = serializers.CharField()

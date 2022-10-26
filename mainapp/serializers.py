from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Account


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class BalanceSerializer(Serializer):
    account = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    def create(self, validated_data):
        return validated_data


class TransferSerializer(Serializer):
    payer = serializers.CharField(max_length=255)
    recipient = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    def create(self, validated_data):
        return validated_data


class TransferRequestSerializer(Serializer):
    account = serializers.CharField(max_length=255)
    income_outcome = serializers.BooleanField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        return validated_data


class TransferHistorySerializer(Serializer):
    account_id = serializers.CharField(max_length=255)
    income_outcome = serializers.CharField(max_length=10)
    merchant_account = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    date = serializers.DateTimeField()

    def create(self, validated_data):
        return validated_data

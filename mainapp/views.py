from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.response import Response
from .serializers import (
    AccountSerializer,
    BalanceSerializer,
    TransferSerializer,
    TransferRequestSerializer,
    TransferHistorySerializer,
)
from decimal import Decimal
from .custom_functions import update_balance, create_money_transfer, convert_url_filters
from .custom_exceptions import AccountDoesNotExistError, MoneyIsNotEnoughError
from mainapp.models import Account, Transfer
from django.http import HttpResponse


class AccountView(APIView):
    """View for creating a bank account"""

    permission_classes = (IsAuthenticated,)

    def post(self, request) -> HttpResponse:
        serializer = AccountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(status=HTTP_201_CREATED)


class BalanceView(APIView):
    """View for adding balance of an account"""

    permission_classes = (IsAuthenticated,)

    def post(self, request) -> HttpResponse:
        serializer = BalanceSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save()

        if Decimal(request.data.get("amount")) == 0:
            error_message = {"error": ["the amount should be more than 0."]}
            return Response(error_message, status=HTTP_400_BAD_REQUEST)

        try:
            update_balance(dict(serializer.data))
        except AccountDoesNotExistError:
            error_message = {"error": ["the account doesn't exist."]}
            return Response(error_message, status=HTTP_404_NOT_FOUND)
        else:
            return Response(status=HTTP_201_CREATED)


class TransferView(APIView):
    """View for creating a money transfer to another account"""

    permission_classes = (IsAuthenticated,)

    def post(self, request) -> HttpResponse:
        serializer = TransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save()

        if Decimal(request.data.get("amount")) == 0:
            error_message = {"error": ["the amount should be more than 0."]}
            return Response(error_message, status=HTTP_400_BAD_REQUEST)

        if serializer.data.get("payer") == serializer.data.get("recipient"):
            error_message = {"error": ["payer and the recipient must be different"]}
            return Response(error_message, status=HTTP_400_BAD_REQUEST)

        try:
            create_money_transfer(dict(serializer.data))
        except AccountDoesNotExistError:
            error_message = {"error": ["there isn't recipient or payer."]}
            return Response(error_message, status=HTTP_404_NOT_FOUND)
        except MoneyIsNotEnoughError:
            error_message = {"error": ["the money isn't enough"]}
            return Response(error_message, status=HTTP_400_BAD_REQUEST)
        else:
            return Response(status=HTTP_201_CREATED)


class TransferHistoryView(APIView):
    """View for retrieving information about all money transactions of an account"""

    permission_classes = (IsAuthenticated,)

    def get(self, request) -> HttpResponse:
        url_filters = request.GET.lists()

        # retrieving filters from url and creating dict with filters
        # for further getting info from db
        serializer_url_filters = {_[0]: _[1][0] for _ in url_filters}
        valid_filters = TransferRequestSerializer(data=serializer_url_filters)

        if not valid_filters.is_valid():
            return Response(valid_filters.errors, status=HTTP_400_BAD_REQUEST)
        valid_filters.save()

        # converting filters in appropriate format for retrieving
        # historical information from db
        filters = convert_url_filters(valid_filters)

        if "account_id_id" not in filters:
            error_message = {"error": ["the account doesn't exist."]}
            return Response(error_message, status=HTTP_404_NOT_FOUND)

        transfer = Transfer.objects.filter(**filters)
        transfer_history = TransferHistorySerializer(transfer, many=True)
        requested_account = valid_filters.data.get("account")
        account = Account.objects.get(account=requested_account)
        return Response(
            [{"balance": account.balance}, transfer_history.data],
            status=HTTP_200_OK,
        )

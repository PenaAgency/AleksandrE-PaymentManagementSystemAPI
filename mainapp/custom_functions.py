from django.db import transaction
from .models import Account, Transfer
from decimal import Decimal
from django.db.models import Q
import datetime
import pytz
from .custom_exceptions import AccountDoesNotExistError, MoneyIsNotEnoughError
from typing import Dict


def update_balance(request_info: Dict) -> None:
    """ The function contains logic for updating balance of account """

    amount = Decimal(request_info.get("amount"))

    with transaction.atomic():
        account_name = request_info.get("account")
        # fmt: off
        account = Account.objects.select_for_update().filter(
            account=account_name
        )
        # fmt: on

        if not account:
            raise AccountDoesNotExistError

        account[0].balance += amount
        account[0].save()

        # creating data for making historical information about transaction
        request_info = request_info | {
            "account_id": account[0].id,
            "income_outcome": True,
        }
        create_transfer_info(request_info)


def create_money_transfer(request_info: Dict) -> None:
    """ The function contains logic for creating a money transaction """

    amount = Decimal(request_info.get("amount"))

    with transaction.atomic():
        payer_name = request_info.get("payer")
        recipient_name = request_info.get("recipient")
        accounts = Account.objects.select_for_update().filter(
            Q(account=payer_name) | Q(account=recipient_name)
        )

        # len(accounts) < 2 when payer or recipient doesn't exist
        if len(accounts) < 2:
            raise AccountDoesNotExistError

        # acc_ordered_dict - creating dictionary from query to get info about account
        # with the key, where key - account_name
        acc_ordered_dict = {account.account: account for account in accounts}
        payer = acc_ordered_dict.get(payer_name)
        recipient = acc_ordered_dict.get(recipient_name)

        if payer.balance < amount:
            raise MoneyIsNotEnoughError

        payer.balance -= amount
        payer.save()
        recipient.balance += amount
        recipient.save()

        # creating data for making historical information about transaction
        request_info = request_info | {
            "payer_id": payer.id,
            "recipient_id": recipient.id,
            "income_outcome": False,
        }
        create_transfer_info(request_info)


def create_transfer_info(request_info: Dict) -> None:
    """
    if income_outcome is True - a history is created for
    account that received the money.

    if income_outcome is False - a history is created for
    account to which the money was transferred and for
     account from which the transfer was made
    """

    if request_info.get("income_outcome"):
        Transfer.objects.create(
            account_id_id=request_info.get("account_id"),
            income_outcome=True,
            amount=request_info.get("amount"),
        )
    else:
        Transfer.objects.bulk_create(
            [
                Transfer(
                    account_id_id=request_info.get("payer_id"),
                    merchant_account=request_info.get("recipient"),
                    income_outcome=False,
                    amount=request_info.get("amount"),
                ),
                Transfer(
                    account_id_id=request_info.get("recipient_id"),
                    merchant_account=request_info.get("payer"),
                    income_outcome=True,
                    amount=request_info.get("amount"),
                ),
            ]
        )


def convert_url_filters(filters: Dict) -> Dict:
    """
    transforming url filters in appropriate format for retrieving
    and filtering history info about requested account

    this function performs next steps:
    - transforms time, stored in str formats to datatime objects
    in iso 8061 format
    - transforms account_name into account_id for retrieving info
    from db
    - check if the income_outcome argument is in request
    """

    valid_filters = {}

    account = Account.objects.filter(account=filters.data.get("account"))
    if account:
        valid_filters["account_id_id"] = account[0].id

    if "income_outcome" in filters.data:
        valid_filters["income_outcome"] = filters.data.get("income_outcome")

    if "date_from" in filters.data:
        date_from = datetime.datetime.strptime(
            filters.data.get("date_from"), "%Y-%m-%dT%H:%M:%SZ"
        )
        date_from = pytz.utc.localize(date_from)
        valid_filters["date__gte"] = date_from

    if "date_to" in filters.data:
        date_to = datetime.datetime.strptime(
            filters.data.get("date_to"), "%Y-%m-%dT%H:%M:%SZ"
        )
        date_to = pytz.utc.localize(date_to)
        valid_filters["date__lte"] = date_to

    return valid_filters

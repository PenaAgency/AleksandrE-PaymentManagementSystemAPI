from django.db import models


class Account(models.Model):
    """Actual information about balance"""

    account = models.CharField("ID", max_length=255, unique=True)
    balance = models.DecimalField("balance", max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["account"]),
        ]

    def __str__(self):
        return self.account


class Transfer(models.Model):
    """
    History information about money transfers

    merchant account - the account to which or from which
    the money was transferred

    income_outcome:
    - true - deposit
    - false - spending money
    """

    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    income_outcome = models.BooleanField()
    merchant_account = models.CharField("ID", max_length=255)
    amount = models.DecimalField("amount", max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["account_id"]),
        ]

    def __str__(self):
        return self.account_id

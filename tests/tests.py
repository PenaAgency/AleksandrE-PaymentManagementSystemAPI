from rest_framework.test import APIClient
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
import pytest


@pytest.fixture
def client():
    user = User.objects.create_user(username="user", password="userqwerty")
    token = Token.objects.create(user=user)
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.mark.django_db
class TestAccountView:
    def test_create_bank_account(self, client):
        data = {"account": "account"}
        response = client.post("/api/user/create-account", data=data)
        assert response.status_code == HTTP_201_CREATED

    def test_create_bank_account_if_account_exist(self, client):
        data = {"account": "account"}
        response = client.post("/api/user/create-account", data=data)
        response = client.post("/api/user/create-account", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_bank_account_if_account_exist_error_message(self, client):
        data = {"account": "account"}
        response = client.post("/api/user/create-account", data=data)
        response = client.post("/api/user/create-account", data=data)
        error_message = {"account": ["account with this ID already exists."]}
        assert json.loads(response.content) == error_message

    def test_create_bank_account_without_json_data(self, client):
        response = client.post("/api/user/create-account")
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_bank_account_without_json_data_error_message(self, client):
        response = client.post("/api/user/create-account")
        error_message = {"account": ["This field is required."]}
        assert json.loads(response.content) == error_message

    @pytest.mark.parametrize("data", [{}, {"wrong_field": "account"}])
    def test_create_bank_account_wrong_json_data(self, client, data):
        response = client.post("/api/user/create-account", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("data", [{}, {"wrong_field": "account"}])
    def test_create_bank_account_wrong_json_data_error(self, client, data):
        response = client.post("/api/user/create-account", data=data)
        error_message = {"account": ["This field is required."]}
        assert json.loads(response.content) == error_message


@pytest.mark.django_db
class TestBalanceView:
    def test_update_balance(self, client):
        data = {"account": "account"}
        client.post("/api/user/create-account", data=data)
        data = {"account": "account", "amount": 10}
        response = client.post("/api/user/update-balance", data=data)
        assert response.status_code == HTTP_201_CREATED

    def test_update_balance_without_json_data(self, client):
        data = {"account": "account"}
        client.post("/api/user/create-account", data=data)
        response = client.post("/api/user/update-balance")
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_update_balance_without_json_data_error_message(self, client):
        data = {"account": "account"}
        client.post("/api/user/create-account", data=data)
        response = client.post("/api/user/update-balance")
        error_message = {
            "account": ["This field is required."],
            "amount": ["This field is required."],
        }
        assert json.loads(response.content) == error_message

    @pytest.mark.parametrize(
        "data",
        [
            {},
            {"account": "account"},
            {"amount": 10},
            {"account": "account", "amount": 0},
            {"account": "account", "amount": -10},
        ],
    )
    def test_update_balance_with_wrong_json_data(self, client, data):
        create_account_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_data)
        response = client.post("/api/user/update-balance", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        ("data", "expected_result"),
        [
            (
                {},
                {
                    "account": ["This field is required."],
                    "amount": ["This field is required."],
                },
            ),
            ({"account": "account"}, {"amount": ["This field is required."]}),
            ({"amount": 10}, {"account": ["This field is required."]}),
            (
                {"account": "account", "amount": 0},
                {"error": ["the amount should be more than 0."]},
            ),
            (
                {"account": "account", "amount": -10},
                {
                    # fmt: off
                    "amount": [
                        "Ensure this value is greater than or equal to 0."
                    ]
                    # fmt: on
                },
            ),
        ],
    )
    def test_update_balance_with_wrong_json_data_error_message(
        self, client, data, expected_result
    ):
        create_account_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_data)
        response = client.post("/api/user/update-balance", data=data)
        assert json.loads(response.content) == expected_result

    def test_update_balance_account_does_not_exist(self, client):
        data = {"account": "account", "amount": 10}
        response = client.post("/api/user/update-balance", data=data)
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_update_balance_account_does_not_exist_error_message(self, client):
        data = {"account": "account", "amount": 10}
        response = client.post("/api/user/update-balance", data=data)
        error_message = {"error": ["the account doesn't exist."]}
        assert json.loads(response.content) == error_message


@pytest.mark.django_db
class TestTransferView:
    def test_create_transfer(self, client):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        transfer_data = {
            "payer": "account_1",
            "recipient": "account_2",
            "amount": 10.00,
        }
        response = client.post("/api/user/create-transfer", data=transfer_data)
        assert response.status_code == HTTP_201_CREATED

    def test_create_transfer_without_json_data(self, client):
        response = client.post("/api/user/create-transfer")
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_transfer_without_json_data_error_message(self, client):
        response = client.post("/api/user/create-transfer")
        error_message = {
            "payer": ["This field is required."],
            "recipient": ["This field is required."],
            "amount": ["This field is required."],
        }
        assert json.loads(response.content) == error_message

    @pytest.mark.parametrize(
        ("data"),
        [
            {},
            {"recipient": "account_2", "amount": 10},
            {"payer": "account_1", "amount": 10},
            {"payer": "account_1", "recipient": "account_2"},
            {"payer": "account_1", "recipient": "account_2", "amount": -10},
            {"payer": "account_1", "recipient": "account_2", "amount": 0},
        ],
    )
    def test_create_transfer_with_wrong_json_data(self, client, data):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        response = client.post("/api/user/create-transfer", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        ("data", "expected_result"),
        [
            (
                {},
                {
                    "payer": ["This field is required."],
                    "recipient": ["This field is required."],
                    "amount": ["This field is required."],
                },
            ),
            (
                {"recipient": "account_2", "amount": 10},
                {
                    "payer": ["This field is required."],
                },
            ),
            (
                {"payer": "account_1", "amount": 10},
                {
                    "recipient": ["This field is required."],
                },
            ),
            (
                {
                    "payer": "account_1",
                    "recipient": "account_2",
                },
                {
                    "amount": ["This field is required."],
                },
            ),
            (
                # fmt: off
                {"payer": "v1", "recipient": "v2", "amount": -10},
                {
                    "amount": [
                        "Ensure this value is greater than or equal to 0."
                    ]
                },
                # fmt: on
            ),
            (
                {"payer": "v1", "recipient": "v2", "amount": 0},
                {"error": ["the amount should be more than 0."]},
            ),
        ],
    )
    def test_create_transfer_with_wrong_json_data_error_message(
        self, client, data, expected_result
    ):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        response = client.post("/api/user/create-transfer", data=data)
        assert json.loads(response.content) == expected_result

    @pytest.mark.parametrize(
        "data",
        [
            {"payer": "account", "recipient": "wrong_account", "amount": 10},
            {"payer": "wrong_account", "recipient": "account", "amount": 10},
        ],
    )
    def test_create_transfer_accounts_does_not_exist(self, client, data):
        create_account_1_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_1_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        response = client.post("/api/user/create-transfer", data=data)
        assert response.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        ("data", "expected_result"),
        [
            (
                {"payer": "account", "recipient": "wrong", "amount": 10},
                {"error": ["there isn't recipient or payer."]},
            ),
            (
                {"payer": "wrong", "recipient": "account", "amount": 10},
                {"error": ["there isn't recipient or payer."]},
            ),
        ],
    )
    def test_create_transfer_accounts_does_not_exist_error_message(
        self, client, data, expected_result
    ):
        create_account_1_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_1_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        response = client.post("/api/user/create-transfer", data=data)
        assert json.loads(response.content) == expected_result

    def test_create_transfer_accounts_match(self, client):
        data = {"payer": "account", "recipient": "account", "amount": 100}
        response = client.post("/api/user/create-transfer", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_transfer_accounts_match_error_message(self, client):
        data = {"payer": "account", "recipient": "account", "amount": 100}
        response = client.post("/api/user/create-transfer", data=data)
        result = {"error": ["payer and the recipient must be different"]}
        assert json.loads(response.content) == result

    def test_create_transfer_money_is_not_enough(self, client):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        data = {"payer": "account_1", "recipient": "account_2", "amount": 100}
        response = client.post("/api/user/create-transfer", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_transfer_money_is_not_enough_error_message(self, client):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_data = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_data)
        data = {"payer": "account_1", "recipient": "account_2", "amount": 100}
        response = client.post("/api/user/create-transfer", data=data)
        expected_result = {"error": ["the money isn't enough"]}
        assert json.loads(response.content) == expected_result


@pytest.mark.django_db
class TestTransferHistoryView:
    @pytest.mark.parametrize(
        "request_url_filters",
        [
            "?account=account&"
            "date_from=2020-01-01T00:00&"
            "date_to=2040-01-01T00:00:00&"
            "income_outcome=true",
            "?account=account&"
            "date_from=2020-01-01T00:00&"
            "date_to=2040-01-01T00:00:00&"
            "income_outcome=false",
        ],
    )
    def test_get_transfer_history(self, client, request_url_filters):
        create_account_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_data)
        update_balance_data = {"account": "account", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_data)
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        assert response.status_code == HTTP_200_OK

    def test_get_transfer_history_of_created_account_message(self, client):
        create_account_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_data)
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url_filters = "?account=account&"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        expected_result = [{"balance": 0.0}, []]
        assert json.loads(response.content) == expected_result

    def test_get_transfer_history_with_added_balance_message(self, client):
        create_account_data = {"account": "account"}
        client.post("/api/user/create-account", data=create_account_data)
        update_balance_account = {"account": "account", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_account)
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url_filters = "?account=account&"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        date = json.loads(response.content)[1][0].get("date")
        expected_result = [
            {"balance": 10.0},
            [
                {
                    "account_id": "account",
                    "income_outcome": "True",
                    "merchant_account": "",
                    "amount": "10.00",
                    "date": f"{date}",
                }
            ],
        ]
        assert json.loads(response.content) == expected_result

    def test_get_transfer_history_with_url_flter_message(self, client):
        create_account_1_data = {"account": "account_1"}
        client.post("/api/user/create-account", data=create_account_1_data)
        create_account_2_data = {"account": "account_2"}
        client.post("/api/user/create-account", data=create_account_2_data)
        update_balance_1_account = {"account": "account_1", "amount": 10}
        client.post("/api/user/update-balance", data=update_balance_1_account)
        create_transfer_data = {
            "payer": "account_1",
            "recipient": "account_2",
            "amount": 5.00,
        }
        client.post("/api/user/create-transfer", data=create_transfer_data)
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url_filters = "?account=account_1&income_outcome=true"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        date = json.loads(response.content)[1][0].get("date")
        expected_result = [
            {"balance": 5.0},
            [
                {
                    "account_id": "account_1",
                    "income_outcome": "True",
                    "merchant_account": "",
                    "amount": "10.00",
                    "date": f"{date}",
                },
            ],
        ]
        assert json.loads(response.content) == expected_result

    def test_get_transfer_history_when_account_does_not_exist(self, client):
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url_filters = "?account=wrong_account"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_get_transfer_history_url_filters_is_not_valid(self, client):
        request_url_endpoint = "/api/user/get-transfer-history"
        request_url_filters = "?account=wrong_account"
        request_url = request_url_endpoint + request_url_filters
        response = client.get(request_url)
        assert response.status_code == HTTP_404_NOT_FOUND

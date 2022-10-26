## The application is designed to demonstrate interaction with customers bank accounts

## The application performs the following operations:

- creating bank account
- updating balance of a client
- transfer money to other bank account
- requesting operations on bank account

## In development:
#### - deploying application on the server

## the stack of technologies:
#### - Django and Django Rest Framework for creating API
#### - Postgres for database


## to run the application with docker:

#### - move to the root directory of project where the docker-compose file is located.
#### - run the next command for creating and running docker image:
#### $ docker-compose up

## to run the application without docker:

#### - clone the repository from https://github.com/Aleks-E/PaymentManagementSystemAPI
#### - install python 3.9
#### install dependencies:
#### - move to folders with the project
#### - run command:
#### $ pip install -r requirements.txt
#### $ python manage.py runserver

## You can interact with the application as follows:

### python code:
    import requests
    
    # API endpoints:
    CREATE_ACCOUNT = "api/user/create-account"
    UPDATE_BALANCE = "api/user/update-balance/api/user/update-balance"
    CREATE_TRANSFER = "api/user/create-transfer"
    GET_TRANSFER_HISTORY = api/user/get-transfer-history
    
        # url filters for getting history:   
            # account=<account>     
            # date_from=<date>
            # date_to=<date>
            # income_outcome=<income_outcome>
            
            # 'income_outcome' should be true or false 
            # 'date_from', 'date_to' should be in iso 8061 format


## At first you need create user ang get token:

### create user:
    data = {
         'username': 'user',
         'password': 'userqwerty'
         }
    requests.post('http://<localhost>/api/auth/users/', data=data)

### login and create token:
    data = {
        'username': 'user', 
        'password': 'userqwerty'
        }
    response = requests.post('http://<localhost>/api/auth-token/token/login/', data=data)
    token = response.json().get('auth_token')
    headers = {r"Authorization": f"Token {token}"}

## Interraction with API:

### create bank account:
    data = {"account": "account_2"}
    requests.post(f'http://<localhost>/{CREATE_ACCOUNT}', headers=headers, data=data)

### update balance:
    data = {
        "account": "account", 
        "amount": 100.05
        }
    requests.post(f'http://<localhost>/{UPDATE_BALANCE}', headers=headers, data=data)

### create transfer:
    # create account_1:
    data = {
        "account": 
        "account_1"
        }
    requests.post(f'http://<localhost>/{CREATE_ACCOUNT}', headers=headers, data=data)
    
    # create account_2:
    data = {
        "account": 
        "account_2"
        }
    requests.post(f'http://<localhost>/{CREATE_ACCOUNT}', headers=headers, data=data)
    
    # update balance for account_1:
    data = {
        "account": "account_1", 
        "amount": 100.05
        }
    requests.post(f'http://<localhost>/{UPDATE_BALANCE}', headers=headers, data=data)
    
    # create transfer:
    data = {
        "payer": "account_1", 
        "recipient": "account_2", 
        "amount": 50}
    requests.post(f'http://<localhost>/api/user/{CREATE_TRANSFER}', headers=headers, data=data)

### get transfer history:
    # url_filters:
    account = account_1
    data_from = '2020-01-01T00:00:00'
    date_to = '2022-01-01T00:00:00'
    income_outcome=true
  
    response = requests.get(f'http://<localhost>/{GET_TRANSFER_HISTORY}?account={account}&date_from={date_from}&date_to={data_to}&income_outcome={income_outcome}', headers=headers)
    
    data = response.json()

    # data:
    # [
    #     {
    #         "balance": 100.1
    #     },
    #     [
    #         {
    #             "account_id": "account_1",
    #             "income_outcome": "True",
    #             "merchant_account": "account_2",
    #             "amount": "100.05",
    #             "date": "2021-08-16T14:57:01.123627Z"
    #         },
    #         {
    #             "account_id": "account_1",
    #             "income_outcome": "True",
    #             "merchant_account": "account_2",
    #             "amount": "100.05",
    #             "date": "2021-08-16T14:57:02.761002Z"
    #         }
    #     ]
    # ]
    
## Logout and destroy token:
    data = {
        'username': 'user', 
        'password': 'userqwerty'
        }
    requests.post('http://<localhost>/api/auth-token/token/logout/', data=data, headers=headers)
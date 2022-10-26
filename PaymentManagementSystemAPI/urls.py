"""PaymentManagementSystemAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainapp.views import AccountView, BalanceView, TransferView, TransferHistoryView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("djoser.urls")),
    path("api/auth-token/", include("djoser.urls.authtoken")),
    path("api/user/create-account", AccountView.as_view()),
    path("api/user/update-balance", BalanceView.as_view()),
    path("api/user/create-transfer", TransferView.as_view()),
    path("api/user/get-transfer-history", TransferHistoryView.as_view()),
]

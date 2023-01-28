"""bikeShare URL Configuration

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
from django.urls import path
from sharesystem import views

urlpatterns = [
    path('', views.login, name='login'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('mapcust/', views.mapcust, name='mapcust'),
    path('mapopt/', views.mapopt, name='mapopt'),
    path('bikedetail/', views.bikedetail, name='bikedetail'),
    path('movebike/', views.movebike, name='movebike'),
    path('mapmag/', views.mapmag, name='mapmag'),
    path('reportdetail/', views.reportdetail, name='reportdetail'),
    path('account/', views.account, name='account'),
    path('report/defect/', views.report_defect, name='rd'),
    path('defect/', views.defect, name='defect'),
    path('order/', views.order, name='order'),
    path('order/detail/<int:order_id>/',views.order_detail),
    path('paybill/<int:order_id>/', views.pay_bill),
    path('recharge/', views.recharge),
    path('about/', views.about, name='about')
]

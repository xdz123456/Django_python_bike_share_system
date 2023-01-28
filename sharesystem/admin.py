from django.contrib import admin
from sharesystem.models import Defect, MyUser, Bike, Payment, Order

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Bike)
admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(Defect)
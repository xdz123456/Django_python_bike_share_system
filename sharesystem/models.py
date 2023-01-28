from django.db import models
import folium
from django.views.generic import TemplateView


class MyUser(models.Model):
    role_choices = (
        (0,"manager"),
        (1,"operator"),
        (2,"customer"),
    )
    state_choices = (
        (0,"idle"),
        (1,"riding"),
    )
    username = models.CharField(primary_key=True, max_length=20, unique=True)
    role = models.IntegerField(default=2, choices=role_choices)
    lng = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    user_state = models.IntegerField(default=0, choices=state_choices)    

    def __str__(self):
        return self.username


class Bike(models.Model):
    bike_id = models.AutoField(primary_key=True, unique=True)
    bike_state = models.IntegerField(default=0)
    lng = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return str(self.bike_id)


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True, unique=True)
    username = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    payment_time = models.DateTimeField()
    amount = models.FloatField()
    balance = models.FloatField()
    def __str__(self):
        return str(self.payment_id)


class Order(models.Model):
    # Need to Know
    # ForeignKey and PriKey
    status_choices = (
        (0,"ongoing"),
        (1,"unpaid"),
        (2,"finished"),
    )
    order_id = models.AutoField(primary_key=True, unique=True)
    username = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    rent_time = models.DateTimeField()
    duration = models.IntegerField(default=0)
    return_time = models.DateTimeField(null=True, blank=True)
    order_amount = models.FloatField(default=0)
    order_status = models.IntegerField(default=0, choices=status_choices)
    bike_id = models.ForeignKey(Bike, on_delete=models.CASCADE)
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.order_id)


class Defect(models.Model):
    defect_id = models.AutoField(primary_key=True, unique=True)
    username = models.ForeignKey(MyUser, on_delete= models.CASCADE)
    report_time = models.DateTimeField()
    description = models.CharField(max_length=200)
    bike_id = models.ForeignKey(Bike, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.defect_id)
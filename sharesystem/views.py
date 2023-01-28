from django.contrib.auth import authenticate
from django.db.models.fields import DateTimeField
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from pandas.core import frame
from sharesystem.models import Defect, MyUser, Payment
from sharesystem.models import Order, Bike
from django.http import HttpResponse
from django.utils import timezone
import datetime
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import math
from .utils import get_plot


def login(request):
    global name
    name = ""
    if request.method == 'POST':
        name = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=name, password=password)

        if user:
            myuser_object = MyUser.objects.filter(username=name).first()
            user_role = myuser_object.role
            if user_role == 0:
                return render(request, 'sharesystem/Welcome_MAG.html')
            elif user_role == 1:
                request.method = 'GET'
                return render(request, 'sharesystem/Welcome_OPT.html')
            elif user_role == 2:
                request.method = 'GET'
                return render(request, 'sharesystem/Welcome_CST.html')
        else:
            return render(request, 'sharesystem/ErrorLogin.html')

    # current_user = MyUser.objects.filter(username=name).get()
    # Input the bike data to the database
    # input_bike_data()

    return render(request, 'sharesystem/Login.html', {'username': name})


def register(request):
    if request.method == 'POST':
        name = request.POST.get('username', None)
        password = request.POST.get('password', None)
        exist = User.objects.filter(username=name).exists()
        if exist:
            return render(request, 'sharesystem/ErrorRegister.html')
        else:
            User.objects.create_user(username=name, password=password)
            current_user = MyUser(username=name)
            current_user.save()
            return render(request, 'sharesystem/RegisterSuccess.html')

    return render(request, 'sharesystem/Register.html')


def rent(bike_id, name):
    # Get current local date time
    dt = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    # Create a new order with given username, bike id and date time
    user = get_object_or_404(MyUser, username=name)
    bike = get_object_or_404(Bike, bike_id=bike_id)
    order = Order.objects.create(username=user, rent_time=dt, duration=0, bike_id=bike)
    order_id = order.order_id
    # Modify user_state to 1 (Riding)
    user.user_state = 1
    user.save()
    # Modify bike_state to 1(in use)
    bike.bike_state = 1
    bike.save()
    # Return the newly created order id and current user_state
    return order.order_id, user.user_state


def mapcust(request):
    global bike_id
    global order_id

    draw_the_map()
    generate_file_cust()

    user = get_object_or_404(MyUser, username=name)
    state = user.user_state
    rentflag = 0
    context = {'username': name, 'state': state, 'rentflag': rentflag}
    # If the user is riding, return the order_id 
    # (hide the Rent button and show the Return botton on the page)
    if state == 1:
        order = Order.objects.filter(username=name).order_by('-order_id').first()
        order_id = order.order_id
        context = {'username': name, 'state': state, 'rentflag': rentflag, 'order_id': order_id}

    # On click the "Rent" button, run 'POST' block
    if request.method == 'POST':
        # get bike_id from user input
        bike_id = request.POST.get('bike_id', None)
        # if the bike is idle, rent bike
        bike = get_object_or_404(Bike, bike_id=bike_id)
        if bike.bike_state == 0:
            order_id, state = rent(bike_id, name)
            context = {'username': name, 'state': state, 'bike_id': bike_id, 'order_id': order_id, 'rentflag': rentflag}
        # if the bike is in use, set rentflag to 0
        elif bike.bike_state == 1:
            rentflag = 1
            request.method = 'GET'
            context = {'username': name, 'state': state, 'rentflag': rentflag}
        elif bike.bike_state == 2:
            rentflag = 2
            request.method = 'GET'
            context = {'username': name, 'state': state, 'rentflag': rentflag}
        return render(request, 'sharesystem/template_map_cust.html', context)
    return render(request, 'sharesystem/template_map_cust.html', context)


def account(request):
    user = get_object_or_404(MyUser, username=name)
    payment_list = Payment.objects.filter(username=name).order_by('-payment_id')
    context = {'username': name, 'user': user, 'payment_list': payment_list}
    return render(request, 'sharesystem/Account.html', context)


def recharge(request):
    user = get_object_or_404(MyUser, username=name)
    # On click the 'Recharge' button, run 'POST' block
    if request.method == 'POST':
        # Get the amount from user input
        amount = request.POST.get('amount', None)
        # Add the amount to user balance
        user.balance = user.balance + int(amount)
        user.save()
        dt = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        # Create new payment with given user, payment_time, amount, balance
        Payment.objects.create(username=user, payment_time=dt, amount=amount, balance=user.balance)
        request.method = 'GET'
        return account(request)
    return render(request, 'sharesystem/Recharge.html')


def report_defect(request):
    context = {'username': name}
    # On click "Submit" button, run 'POST' block
    if request.method == 'POST':
        # Get bike id from user input
        bike_id = request.POST.get("bike_id", None)
        # If bike id doesn't exist, 404
        bike = get_object_or_404(Bike, bike_id=bike_id)
        bike.bike_state = 2
        bike.save()
        # Get description from user input
        description = request.POST.get('dftdsp', None)
        # Get current date time
        dt = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        user = MyUser.objects.filter(username=name).first()
        # Create a new defect with given username, bike_id, report_time and description
        Defect.objects.create(username=user, bike_id=bike, report_time=dt, description=description)
        request.method = 'GET'
        return defect(request)
    return render(request, 'sharesystem/ReportDefect.html', context)


def defect(request):
    defects = Defect.objects.filter(username=name).order_by('-defect_id')
    context = {'username': name, 'defects': defects}
    return render(request, 'sharesystem/Defect.html', context)


def order(request):
    orders = Order.objects.filter(username=name).order_by('-order_id')
    # Simultaneously calculate the duration and amount of ongoing orders
    for order in orders:
        if order.order_status == 0:
            now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
            duration = math.ceil((now - order.rent_time).seconds / 60)
            order.duration = duration
            amount = (math.ceil(duration / 60)) / 2
            order.order_amount = amount
            order.save()
    context = {'username': name, 'orders': orders}
    return render(request, 'sharesystem/Order.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    # Calculate the realtime duration and amount of ongoing orders
    if order.order_status == 0:
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        duration = math.ceil((now - order.rent_time).seconds / 60)
        order.duration = duration
        amount = (math.ceil(duration / 60)) / 2
        order.order_amount = amount
        order.save()
    context = {'order': order, 'username': name}
    # On click 'RETURN' button, run this block
    if request.method == 'POST':
        # Modify order_status to 1 (Unpaid)
        order.order_status = 1
        # Modify return_time to current local date time
        dt = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        order.return_time = dt
        # Calculate order duration
        delta = order.return_time - order.rent_time
        minutes = math.ceil(delta.seconds / 60)
        order.duration = minutes
        # Calculate order amount, 0.5 pound per hour
        hh = (math.ceil(minutes / 60)) / 2
        order.order_amount = hh
        order.save()
        # Modify user_state to 0(idle)
        user = get_object_or_404(MyUser, username=name)
        user.user_state = 0
        user.save()
        context = {'order_id': order_id, 'username': name}
        # Go to refreshed order detail page
        request.method = 'GET'
        return order_detail(request, order_id)
    return render(request, 'sharesystem/OrderDetail.html', context)


def pay_bill(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    context = {'order': order, 'username': name}
    # On click pay bill button, run 'POST' block
    if request.method == 'POST':
        # Get current local date time
        dt = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        # Create a payment object with given username, order_id, payment_time and amount
        user = get_object_or_404(MyUser, username=name)
        user.balance = user.balance - order.order_amount
        user.save()
        pay = Payment.objects.create(username=user, payment_time=dt, amount=-order.order_amount, balance=user.balance)
        # Modify order status to 2 (Finished)
        order.order_status = 2
        # Add order's payment_id 
        order.payment_id = pay
        order.save()
        # Return to order detail page
        request.method = 'GET'
        return order_detail(request, order.order_id)
    return render(request, 'sharesystem/PayBill.html', context)


def mapopt(request):
    global flag
    flag = 0
    global bike

    draw_the_map_manger()
    generate_file_opt()
    if request.method == 'POST':
        id = (request.POST.get('bike_id_input'))
        bike = get_object_or_404(Bike, bike_id=id)
        flag = 1
        context = {'username': name, 'bike': bike, 'flag': flag}
        request.method = 'GET'

    context = {'username': name, 'flag': flag}
    return render(request, 'sharesystem/template_map_opt.html', context)


def bikedetail(request):
    if request.method == 'POST':
        bike.bike_state = 0
        bike.save()
        context = {'username': name, 'bike': bike}
    context = {'username': name, 'bike': bike}
    return render(request, 'sharesystem/BikeDetail.html', context)


def movebike(request):
    if request.method == 'POST':
        lng = (request.POST.get('lng_input'))
        lat = (request.POST.get('lat_input'))
        bike.lng = lng
        bike.lat = lat
        bike.save()
        context = {'username': name, 'bike': bike}
        return render(request, 'sharesystem/BikeDetail.html', context)
    context = {'username': name, 'bike': bike}
    return render(request, 'sharesystem/MoveBike.html', context)


def mapmag(request):
    global startdate
    global enddate
    global userall
    global bikeall
    global paymentall
    global orderall
    global defectall
    draw_the_map_manger()
    generate_file_mag()
    if request.method == 'POST':
        startdate = (request.POST.get('startdate'))
        enddate = (request.POST.get('enddate'))

        ed = datetime.date(*map(int, enddate.split('-'))) + datetime.timedelta(days=1)
        userall = MyUser.objects.all()
        bikeall = Bike.objects.all()
        paymentall = Payment.objects.all()
        orderall = Order.objects.filter(rent_time__range=(startdate, ed))
        defectall = Defect.objects.filter(report_time__range=(startdate, ed))

        return reportdetail(request, startdate, enddate)
        # context = {'username': name}
        # return render(request, 'sharesystem/template_map_mag.html',context)
    date = datetime.date.today()
    context = {'username': name, 'date': date}
    return render(request, 'sharesystem/template_map_mag.html', context)


def reportdetail(request, startdate, enddate):
    # Add 1 day to the enddate, otherwise when the user choose 11.1~11.1, there'll be no orders
    # order=Order.objects.order_by('-order_id').first()
    # order_date = order.rent_time
    x = [x.return_time for x in orderall]
    y = [y.order_amount for y in orderall]

    number_of_manager = MyUser.objects.filter(role=0).count()
    number_of_operator = MyUser.objects.filter(role=1).count()
    number_of_custormer = MyUser.objects.filter(role=2).count()
    i = ["Manager", "Operator", "Customer"]
    j = [number_of_manager, number_of_operator, number_of_custormer]

    number_of_idle = Bike.objects.filter(bike_state=0).count()
    number_of_inuse = Bike.objects.filter(bike_state=1).count()
    number_of_broken = Bike.objects.filter(bike_state=2).count()
    m = ["Idle", "In use", "broken"]
    n = [number_of_idle, number_of_inuse, number_of_broken]
    k = ['green', 'blue', 'red']
    e = [0, 0, 0.3]

    # z = Payment.objects.filter(amount__range = (0,float('inf')))
    # f = Payment.objects.filter(amount__range = (float('-inf'),0))
    size = Payment.objects.all().count()
    List = []
    for index in range(size):
        List.append(str(index + 1))
    s = List
    z = []
    f = []
    for index_i in paymentall:
        z.append(index_i.amount)
        f.append(index_i.balance)

    frame_payment = pd.DataFrame({'Index': List, 'Amount': z})
    chart = get_plot(x, y, i, j, m, n, k, e, z, f, s, frame_payment)

    context = {'username': name, 'userall': userall, 'bikeall': bikeall, 'paymentall': paymentall, 'orderall': orderall,
               'defectall': defectall, 'chart': chart}
    return render(request, 'sharesystem/ReportDetail.html', context)


def about(request):
    return render(request, 'sharesystem/About.html')


def input_bike_data():
    csv_data = pd.read_csv('sharesystem/test.csv')
    csv_data_0 = csv_data.loc[csv_data['avi'] == 0]
    csv_data_1 = csv_data.loc[csv_data['avi'] == 1]

    for lat, lng, in zip(csv_data_0.lat, csv_data_0.log):
        current_bike = Bike(lng=lng, lat=lat, bike_state=0)
        current_bike.save()

    for lat, lng, in zip(csv_data_1.lat, csv_data_1.log):
        current_bike = Bike(lng=lng, lat=lat, bike_state=1)
        current_bike.save()


def draw_the_map():
    incidents = folium.map.FeatureGroup()
    marker_cluster = MarkerCluster()

    bikes_un_avi = Bike.objects.filter(bike_state=1)
    for bike_un_avi in bikes_un_avi:
        incidents.add_child(
            folium.CircleMarker(
                [bike_un_avi.lat, bike_un_avi.lng],
                radius=10,
                color='yellow',
                fill=True,
                popup='【InUse】\nBike_ID:' + str(bike_un_avi.bike_id) + "\nLNG:" + str(
                    round(bike_un_avi.lng, 2)) + "\nLAT:" + str(round(bike_un_avi.lat, 2)),
                fill_color='turquoise',
                fill_opacity=0.4
            )
        )

        folium.Marker(
            location=[bike_un_avi.lat, bike_un_avi.lng],
            color='yellow',
            popup='【InUse】\nBike_ID:' + str(bike_un_avi.bike_id) + "\nLNG:" + str(
                round(bike_un_avi.lng, 2)) + "\nLAT:" + str(round(bike_un_avi.lat, 2)),
            icon=None,
            #        popup=label,
        ).add_to(marker_cluster)

    bikes_avi = Bike.objects.filter(bike_state=0)
    for bike_avi in bikes_avi:
        incidents.add_child(
            folium.CircleMarker(
                [bike_avi.lat, bike_un_avi.lng],
                radius=10,
                color='dodgerblue',
                fill=True,
                popup='【Available】\n Bike_ID:' + str(bike_avi.bike_id) + "\nLOG:" + str(
                    round(bike_avi.lng, 2)) + "\nLAT:" + str(round(bike_avi.lat, 2)),
                fill_color='turquoise',
                fill_opacity=0.4
            )
        )

        folium.Marker(
            location=[bike_avi.lat, bike_un_avi.lng],
            color='dodgerblue',
            popup='【Available】\nBike_ID:' + str(bike_avi.bike_id) + "\nLOG:" + str(
                round(bike_avi.lng, 2)) + "\nLAT:" + str(round(bike_avi.lat, 2)),
            icon=None,
            #        popup=label,
        ).add_to(marker_cluster)

    Gla_map = folium.Map(location=[55.86, -4.251433], zoom_start=15)
    Gla_map.add_child(incidents)

    # Regional bike density

    # create a mark cluster object
    marker_cluster.add_to(Gla_map)
    # add marker_cluster to map
    Gla_map.add_child(marker_cluster)

    Gla_map.save("./templates/sharesystem/new_map.html")


def draw_the_map_manger():
    incidents = folium.map.FeatureGroup()
    marker_cluster = MarkerCluster()

    bikes_broken = Bike.objects.filter(bike_state=2)
    for bike_broken in bikes_broken:
        incidents.add_child(
            folium.CircleMarker(
                [bike_broken.lat, bike_broken.lng],
                radius=10,
                color='tomato',
                fill=True,
                popup='【Broken】\nBike_ID:' + str(bike_broken.bike_id) + "\nLNG:" + str(
                    round(bike_broken.lng, 2)) + "\nLAT:" + str(round(bike_broken.lat, 2)),
                fill_color='red',
                fill_opacity=0.4
            )
        )

        folium.Marker(
            location=[bike_broken.lat, bike_broken.lng],
            color='tomato',
            popup='【Broken】\nBike_ID:' + str(bike_broken.bike_id) + "\nLNG:" + str(
                round(bike_broken.lng, 2)) + "\nLAT:" + str(round(bike_broken.lat, 2)),
            icon=None,
            #        popup=label,
        ).add_to(marker_cluster)

    bikes_un_avi = Bike.objects.filter(bike_state=1)
    for bike_un_avi in bikes_un_avi:
        incidents.add_child(
            folium.CircleMarker(
                [bike_un_avi.lat, bike_un_avi.lng],
                radius=10,
                color='yellow',
                fill=True,
                popup='【InUse】\nBike_ID:' + str(bike_un_avi.bike_id) + "\nLNG:" + str(
                    round(bike_un_avi.lng, 2)) + "\nLAT:" + str(round(bike_un_avi.lat, 2)),
                fill_color='yellow',
                fill_opacity=0.4
            )
        )

        folium.Marker(
            location=[bike_un_avi.lat, bike_un_avi.lng],
            color='yellow',
            popup='【InUse】\nBike_ID:' + str(bike_un_avi.bike_id) + "\nLNG:" + str(
                round(bike_un_avi.lng, 2)) + "\nLAT:" + str(round(bike_un_avi.lat, 2)),
            icon=None,
            #        popup=label,
        ).add_to(marker_cluster)

    bikes_avi = Bike.objects.filter(bike_state=0)
    for bike_avi in bikes_avi:
        incidents.add_child(
            folium.CircleMarker(
                [bike_avi.lat, bike_un_avi.lng],
                radius=10,
                color='dodgerblue',
                fill=True,
                popup='【Available\nBike_ID: ' + str(bike_avi.bike_id) + "\nLNG:" + str(
                    round(bike_avi.lng, 2)) + "\nLAT:" + str(round(bike_avi.lat, 2)),
                fill_color='turquoise',
                fill_opacity=0.4
            )
        )

        folium.Marker(
            location=[bike_avi.lat, bike_un_avi.lng],
            color='dodgerblue',
            popup='【Available\nBike_ID:' + str(bike_avi.bike_id) + "\nLNG:" + str(
                round(bike_avi.lng, 2)) + "\nLAT:" + str(round(bike_avi.lat, 2)),
            icon=None,
            #        popup=label,
        ).add_to(marker_cluster)

    Gla_map = folium.Map(location=[55.86, -4.251433], zoom_start=15)
    Gla_map.add_child(incidents)

    # Regional bike density

    # create a mark cluster object
    marker_cluster.add_to(Gla_map)
    # add marker_cluster to map
    Gla_map.add_child(marker_cluster)

    Gla_map.save("./templates/sharesystem/new_map.html")


def generate_file_cust():
    old_file = open("./templates/sharesystem/new_map.html", "r")

    lines = old_file.readlines()
    new_file = open("./templates/sharesystem/template_map_cust.html", "w")

    total = "{% extends 'sharesystem/MapCst.html' %}\n"

    total += "{% block title_block %}\n"
    for i in range(24, 40):
        total += lines[i]
    total += "{% endblock %}\n"

    total += "{% block body_block %}\n"

    total += lines[44]

    total += "{% endblock %}\n"

    total += "{% block script_block %}\n"

    for i in range(47, len(lines)):
        total += lines[i]

    total += "\n{% endblock %}\n"

    new_file.write(total)

    old_file.close()
    new_file.close()


def generate_file_opt():
    old_file = open("./templates/sharesystem/new_map.html", "r")

    lines = old_file.readlines()
    new_file = open("./templates/sharesystem/template_map_opt.html", "w")

    total = "{% extends 'sharesystem/MapOpt.html' %}\n"

    total += "{% block title_block %}\n"
    for i in range(24, 40):
        total += lines[i]
    total += "{% endblock %}\n"

    total += "{% block body_block %}\n"

    total += lines[44]

    total += "{% endblock %}\n"

    total += "{% block script_block %}\n"

    for i in range(47, len(lines)):
        total += lines[i]

    total += "\n{% endblock %}\n"

    new_file.write(total)

    old_file.close()
    new_file.close()


def generate_file_mag():
    old_file = open("./templates/sharesystem/new_map.html", "r")

    lines = old_file.readlines()
    new_file = open("./templates/sharesystem/template_map_mag.html", "w")

    total = "{% extends 'sharesystem/MapMag.html' %}\n"

    total += "{% block title_block %}\n"
    for i in range(24, 40):
        total += lines[i]
    total += "{% endblock %}\n"

    total += "{% block body_block %}\n"

    total += lines[44]

    total += "{% endblock %}\n"

    total += "{% block script_block %}\n"

    for i in range(47, len(lines)):
        total += lines[i]

    total += "\n{% endblock %}\n"

    new_file.write(total)

    old_file.close()
    new_file.close()

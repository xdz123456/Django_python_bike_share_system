import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x,y,i,j,m,n,k,e,z,f,s,frame_payment):
    plt.switch_backend('AGG')
    figure, axis = plt.subplots(2, 2 ,figsize=(20,7))

    #plot1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
    #plot2 = plt.subplot2grid((3, 3), (0, 2), rowspan=3, colspan=2)
    #plot3 = plt.subplot2grid((3, 3), (1, 0), rowspan=2)
    #plot4 = plt.subplot2grid((3, 3), (1, 1), rowspan=2)

    #fig, axis[1, 1] = plt.subplots()
    #frame_payment['sign'] = frame_payment['Amount'] > 0

    #frame_payment['Amount'].plot(kind='bar', color=frame_payment.sign.map({True: (1.0, 0, 0, 0.7), False: (0, 0.6, 0, 0.7)}), axis=axis)

    axis[0, 0].plot(x, y, 'ro')
    axis[0, 0].set_title("order activity")
    axis[0, 0].set_xlabel("Date")
    axis[0, 0].set_ylabel("Pounds")

    axis[0, 1].bar(i,j)
    axis[0, 1].set_xlabel("Role")
    axis[0, 1].set_ylabel("Number")

    axis[1, 0].pie(n,labels = m, colors = k,explode = e, shadow=True, autopct='%1.1f%%', startangle=180)
    axis[1, 0].axis('equal')

    axis[1, 1].bar(s,z)
    axis[1, 1].set_xlabel("Role")
    axis[1, 1].set_ylabel("Number")

    graph = get_graph()
    return graph

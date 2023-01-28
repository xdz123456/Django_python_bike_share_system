import numpy as np
import pandas as pd
import random
import math


def generate_random_gps(base_log=None, base_lat=None, radius=None):
    radius_in_degrees = radius / 111300
    u = float(random.uniform(0.0, 1.0))
    v = float(random.uniform(0.0, 1.0))
    w = radius_in_degrees * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)
    longitude = y + base_log
    latitude = x + base_lat

    loga = '%.14f' % longitude
    lata = '%.14f' % latitude
    return loga, lata


np.random.seed(26)
log5 = np.zeros(200)
lat5 = np.zeros(200)

for i in range(50):
    Log, Lat = generate_random_gps(base_log=-4.2506, base_lat=55.8610, radius=10000)
    for n in range(4):
        log5[i * 4 + n], lat5[i * 4 + n] = generate_random_gps(base_log=float(Log), base_lat=float(Lat), radius=100)

a = np.random.randint(0, 2, size=len(log5))
data = {'log': log5,
        'lat': lat5,
        'avi': a}
df = pd.DataFrame(data)

df.to_csv("test.csv", index=False)

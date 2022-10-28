
import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

plt.style.use('fivethirtyeight')

index = count()

x =np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

def animate(i):
    a1 = random.randint(0, 5)
    a2 = random.randint(0, 5)
    b1 = random.randint(0, 5)
    b2 = random.randint(0, 5)
    c1 = random.randint(0, 5)
    c2 = random.randint(0, 5)

    y1 = a1 * (x ** 2) + b1 * x + c1     # **2 = ^2
    y2 = a2 * (x ** 2) + b2 * x + c2

    plt.cla()
    plt.plot(x, y1, label='Channel 1')
    plt.plot(x, y2, label='Channel 2')
    #plt.scatter(x3, x3, label='Intersection') # add the intersection coordinates

    plt.legend(loc='upper left')
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
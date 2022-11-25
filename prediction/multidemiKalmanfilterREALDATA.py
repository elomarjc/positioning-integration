# Multi dimensional Kalman filter
# https://gist.github.com/IshankGulati/d0a33cde4fe45cfedec0


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv(r"/Users/jacobel-omar/Desktop/Movement-data/UWPathForwardNBackward.csv")
shape = df.shape
UWBPositionsX = []
UWBPositionsY = []
index = 0

while index < shape[0]:
    UWBPositionsX.append(df.iloc[index, 0])
    UWBPositionsY.append(df.iloc[index, 1])
    index = index+1

print(UWBPositionsX)
plt.figure()
plt.scatter(UWBPositionsX, UWBPositionsY, label = "Measurements")
plt.legend()     # show a legend on the plot
plt.xlim(-5, 5)
plt.grid("True")


'''
#Define needed lists and matrix

UWBPositionsX = np.arange(31)
UWBPositionsY = np.array([])

#Create a sequence for the y values of the UWB

for number in range (31):

    if number <= 10:

       UWBPositionsY = np.append(UWBPositionsY, number)

    elif number > 10 and number < 20:

        UWBPositionsY = np.append(UWBPositionsY, 10)

    else:

       UWBPositionsY = np.append (UWBPositionsY, 10-(number-20))

plt.figure()
plt.scatter(UWBPositionsX, UWBPositionsY, label = "Measurements")
plt.legend()     # show a legend on the plot
plt.grid("True")
'''

#prediction list
x_p=np.array([])
y_p=np.array([])
x_print = np.array([])
y_print= np.array([])

# plotter function
def plotter(xMeasure, yMeasure, xEstimate, yEstimate, xPredict, yPredict):
    plt.figure()
    plt.scatter(xMeasure, yMeasure, label = "Measurements")
    plt.scatter(xEstimate, yEstimate, label = "Estimates")
    plt.scatter(xPredict, yPredict, label = "Predictions")
    plt.legend()     # show a legend on the plot
    plt.xlim(-5, 5)
    plt.grid("True")

# filter function
def kalman_filter(x, P, xList, yList):
    # prediction
    x = F.dot(x)
    P = F.dot(P).dot(F.transpose()) + Q

    x_e.append(x[0])
    y_e.append(x[3])
    print("Iteration number: ", 0, "\n", "p-value: ","\n", P, "\n", "x-value: ", x[0], "\n", "y-value: ", x[3], "\n")
    x_print=np.array([])
    y_print=np.array([])
    counter = 0
    for n in range(0, len(xList)):     # range(len(x_m)
        counter = counter+1
        # measurement update
        y = np.array([[xList[n]],[yList[n]]]) - H.dot(x)
        s = H.dot(P).dot(H.transpose()) + R
        K = P.dot(H.transpose()).dot(np.linalg.inv(s))
        x = x + K.dot(y)
        P = (np.identity(6) - K.dot(H)).dot(P) #.dot(np.identity(6)-K.dot(H)).transpose()+K.dot(R).dot(K.transpose())
        
        # prediction
        x = F.dot(x)
        P = F.dot(P).dot(F.transpose()) + Q
        
        # 3 predictions ahead of current esimation
        xTemp = x
        pTemp = P
        x_p=np.array([])
        y_p=np.array([])

        x_p = np.append(x_p, x[0])
        y_p = np.append(y_p, x[3])
        print("xTemp: ", xTemp) 
        print("x_list: ", xList) 
        print("y: ", y)   
        print("x_p first: ", x_p)    
        print("y_p first: ", y_p)     
        
        for n in range(9): # range 3 is equal to 4 predictions
            # measurement update step
            yTemp = np.array([[x_p[n]],[y_p[n]]]) - H.dot(xTemp)
            print("y_temp: ", yTemp)
            sTemp = H.dot(pTemp).dot(H.transpose()) + R
            kTemp = pTemp.dot(H.transpose()).dot(np.linalg.inv(sTemp))
            print("x_p later: ", x_p[0]) 
            print("y_p later: ", y_p[0])   
            
            xTemp = xTemp + kTemp.dot(yTemp)
            pTemp = (np.identity(6) - kTemp.dot(H)).dot(pTemp) #.dot(np.identity(6)-kTemp.dot(H)).transpose()+kTemp.dot(R).dot(kTemp.transpose())
            
            # time update step (prediction)
            xTemp = F.dot(xTemp)
            print("xTemp: ", xTemp)
            pTemp = F.dot(pTemp).dot(F.transpose()) + Q
            
            x_p = np.append(x_p, xTemp[0])
            y_p = np.append(y_p, xTemp[3])
            if counter == 22:
                x_print = np.append(x_print, x_p)
                y_print = np.append(y_print, y_p)
            else:
                pass
            #print("4 Predictions: ", "\n", "x-value: ", x_p, "\n", "y-value: ", y_p, "\n")

        x_e.append(x[0])
        y_e.append(x[3])
        
        print("4 Predictions: ", "\n", "x-value: ", x_p, "\n", "y-value: ", y_p, "\n")

    return x_p, y_p, x_print, y_print
        #print("Iteration number: ", n+1, "\n", "Measurement: ", "\n", np.array([[xList[n]],[yList[n]]]), "\n", "k-gain: ", "\n", K, "\n", "p-value: ","\n", P, "\n", "x-value: ", x[0], "\n", "y-value: ", x[3], "\n")
        #print("x-value: ", x[0], "\n", "y-value: ", x[3], "\n")
    #return x, P

#Measurements list
x_m=[-393.66,-375.93,-351.04,-328.96,-299.35,-273.36,-245.89,-222.58,-198.03,-174.17,-146.32,-123.72,-103.47,-78.23,-52.63,-23.34,25.96,49.72,76.94,95.38,119.83,144.01,161.84,180.56,201.42,222.62,239.4,252.51,266.26,271.75,277.4,294.12,301.23,291.8,299.89]
y_m=[300.4,301.78,295.1,305.19,301.06,302.05,300,303.57,296.33,297.65,297.41,299.61,299.6,302.39,295.04,300.09,294.72,298.61,294.64,284.88,272.82,264.93,251.46,241.27,222.98,203.73,184.1,166.12,138.71,119.71,100.41,79.76,50.62,32.99,2.14]

#Estimates list
x_e=[]
y_e=[]

#Definetions
dt=0.25 
sigma_a = 2  # variance in acceleration
sigma_xm, sigma_ym = 3, 3 # measurement uncertainty
p_u = 500 # initial uncertainty in p matrix

x = np.array([[0.],
            [0.],
            [0.],
            [0.],
            [0.],
            [0.]]) # initial state (location and velocity)
P = np.array([[p_u, 0., 0., 0., 0., 0.], 
            [0., p_u, 0., 0., 0., 0.],
            [0., 0., p_u, 0., 0., 0.],
            [0., 0., 0., p_u, 0., 0.],
            [0., 0., 0., 0., p_u, 0.],
            [0., 0., 0., 0., 0., p_u]]) # initial uncertainty

Q = np.array([[dt**4/4, dt**3/2, dt**2/2, 0., 0., 0.], 
            [dt**3/2, dt**2, dt, 0., 0.,0.],
            [dt**2/2, dt, 1, 0., 0., 0.],
            [0., 0., 0., dt**4/4, dt**3/2, dt**2/2],
            [0., 0.,  0., dt**3/2, dt**2, dt],
            [0.,0., 0., dt**2/2, dt, 1]])*sigma_a**2 # external motion - HARDCODED WITH sigma_a^2

F = np.array([[1., dt, 0.5*dt**2, 0., 0., 0.], 
              [0., 1., dt, 0., 0., 0.],
              [0., 0., 1., 0., 0., 0.],
              [0., 0., 0., 1., dt, 0.5*dt**2],
              [0., 0., 0., 0., 1., dt],
              [0., 0., 0., 0., 0., 1.]]) # next state function
H = np.array([[1., 0., 0., 0., 0., 0.], 
            [0., 0., 0., 1., 0., 0.]]) # measurement function
R = np.array([[sigma_xm**2,0],
            [0,sigma_ym**2]]) # measurement uncertainty


#Calling functions
x_p, y_p, x_print, y_print = kalman_filter(x, P, UWBPositionsX, UWBPositionsY)

print("-----------------")
print(x_print)
print("-----------------")

#Plot graphs
plotter(UWBPositionsX, UWBPositionsY, x_e, y_e, x_p,y_p)
#plotter(UWBPositionsX, UWBPositionsY, x_e[4:35], y_e[4:35], x_p,y_p)

plt.figure()
plt.plot(x_p, y_p)
plt.grid("True")
plt.xlim(-5, 5)

print("Final x values:", x_p)
print("Final y values:", y_p)

plt.figure()
plt.scatter(UWBPositionsX, UWBPositionsY, label = "Real data")
plt.scatter(x_print, y_print, label = "All predictions")
plt.grid("True")
plt.legend()
plt.xlim(-5, 5)
plt.show()       # function to show the plot

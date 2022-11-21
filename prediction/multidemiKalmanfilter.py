# Multi dimensional Kalman filter
# https://gist.github.com/IshankGulati/d0a33cde4fe45cfedec0


import numpy as np
import matplotlib.pyplot as plt

#prediction list
x_p=np.array([])
y_p=np.array([])

# plotter function
def plotter(xMeasure, yMeasure, xEstimate, yEstimate, xPredict, yPredict):
    plt.figure()
    plt.scatter(xMeasure, yMeasure, label = "Measurements")
    plt.scatter(xEstimate, yEstimate, label = "Estimates")
    plt.scatter(xPredict, yPredict, label = "Predictions")
    plt.legend()     # show a legend on the plot
    plt.grid("True")

# filter function
def kalman_filter(x, P, xList, yList):
    # prediction
    x = F.dot(x)
    P = F.dot(P).dot(F.transpose()) + Q

    x_e.append(x[0])
    y_e.append(x[3])
    print("Iteration number: ", 0, "\n", "p-value: ","\n", P, "\n", "x-value: ", x[0], "\n", "y-value: ", x[3], "\n")

    for n in range(0, len(xList)):     # range(len(x_m) 
        # measurement update
        y = np.array([[xList[n]],[yList[n]]]) - H.dot(x)
        s = H.dot(P).dot(H.transpose()) + R
        K = P.dot(H.transpose()).dot(np.linalg.inv(s))
        x = x + K.dot(y)
        P = (np.identity(6) - K.dot(H)).dot(P)
             
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
        print("x_list: ", xList) 
        print("y: ", y)   
        print("x_p first: ", x_p)    

        for n in range(3): # range 3 is equal to 4 predictions
            # measurement update
            yTemp = np.array([[x_p[n]],[y_p[n]]]) - H.dot(xTemp)
            print("y_temp: ", yTemp)
            sTemp = H.dot(pTemp).dot(H.transpose()) + R
            kTemp = pTemp.dot(H.transpose()).dot(np.linalg.inv(sTemp))
            print("x_p later: ", x_p) 
            #print("yTemp: ", yTemp)
    
            xTemp = xTemp + kTemp.dot(yTemp)
            pTemp = (np.identity(6) - kTemp.dot(H)).dot(pTemp)
                
            # prediction
            xTemp = F.dot(xTemp)
            pTemp = F.dot(pTemp).dot(F.transpose()) + Q
            
            x_p = np.append(x_p, xTemp[0])
            y_p = np.append(y_p, xTemp[3])
            #print("4 Predictions: ", "\n", "x-value: ", x_p, "\n", "y-value: ", y_p, "\n")

        x_e.append(x[0])
        y_e.append(x[3])
        
        print("4 Predictions: ", "\n", "x-value: ", x_p, "\n", "y-value: ", y_p, "\n")

    return x_p, y_p
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
dt=1
sigma_a = 0.2
sigma_xm, sigma_ym = 3, 3
p_u = 500 # uncertainty in p matrix

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
x_p, y_p = kalman_filter(x, P, x_m, y_m)

#Plot graphs
#plotter(x_m, y_m, x_e, y_e, x_p,y_p)
plotter(x_m, y_m, x_e[4:35], y_e[4:35], x_p,y_p)

plt.figure()
plt.plot(x_p, y_p)
plt.grid("True")

print("Final x values:", x_p)
print("Final y values:", y_p)

plt.show()       # function to show the plot
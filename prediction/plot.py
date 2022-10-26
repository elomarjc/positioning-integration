import matplotlib.pyplot as plt

def plotter(xCoords, yCoords):
    plt.figure()
    plt.scatter(xCoords, yCoords, label = "Human Path")
    plt.grid("True")
    plt.show()


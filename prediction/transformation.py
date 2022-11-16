import numpy as np
import math

def initializeLimits (width, length, robotbooty): #The limits of the area are defined on the robot frame
    topRightLimit = [width/2, 0-robotbooty]

    topLeftLimit = [-width/2, 0-robotbooty]

    bottomRightLimit = [width/2, -length-robotbooty]

    bottomLeftLimit = [-width/2, -length-robotbooty]

    return topRightLimit, topLeftLimit, bottomRightLimit, bottomLeftLimit


def personInNoPredictArea (topRightLimit, topLeftLimit, bottomRightLimit, bottomLeftLimit, personPosi): # since its a square, same X and Y will show twice    
    if (topRightLimit[0] > topLeftLimit[0]): #Check for x position
        if (personPosi[0] >= topLeftLimit[0] and personPosi[0] <= topRightLimit[0]):
            xIn = True
        else:
            xIn = False
    else:
        if (personPosi[0] <= topLeftLimit[0] and personPosi[0] >= topRightLimit[0]):
            xIn = True
        else:
            xIn = False
    
    if (topRightLimit[1] > bottomRightLimit[1]): #Check for Y position
        if (personPosi[1] <= topRightLimit[1] and personPosi[1] >= bottomRightLimit[1]):
            yIn = True
        else:
            yIn = False
    else:
        if (personPosi[1] >= topRightLimit[1] and personPosi[1] <= bottomRightLimit[1]):
            yIn = True
        else:
            yIn = False
    
    if (xIn and yIn):
        return True
    else:
        return False

def homogeneousTransformation (angle, pointToTransform, robotCoordenate): #pointToTransform and robotCoordenate are lists
    pointToTransformMatrix = np.array([])
    robotCoordenateMatrix = np.array([])
    
    for point in pointToTransform:
        pointToTransformMatrix = np.append(pointToTransformMatrix, point)
        
    pointToTransformMatrix = np.append(pointToTransformMatrix, 0) #Append 0 as z coordenate value
    pointToTransformMatrix = np.append(pointToTransformMatrix, 1) #Appended 1 to be able to multiply by de homogenous transform matrix
    pointToTransformMatrix = pointToTransformMatrix.transpose()
    
    for coordenate in robotCoordenate:
        robotCoordenateMatrix = np.append(robotCoordenateMatrix, coordenate)
    
    robotCoordenateMatrix = np.append(robotCoordenateMatrix, 0) #Append 0 as z coordenate value
    
    robotCoordenateMatrix = robotCoordenateMatrix*-1 #By definition of the transformation, to move from base frame to robot frame, we need to put robot frame "on top of" base frame
    
    angle = angle*math.pi/180 #Input angle is on deg, radians needed for the function
    
    rotationInZ = np.array([[math.cos(angle), -math.sin(angle), 0, 0], #Homogeneous transform only with rotation, positive rotation clockwise
                            [math.sin(angle), math.cos(angle), 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
    
    traslationXY = [[1, 0, 0, robotCoordenateMatrix[0]], #Homogenneous transform only with translation
                    [0, 1, 0, robotCoordenateMatrix[1]],
                    [0, 0, 1, robotCoordenateMatrix[2]],
                    [0, 0, 0, 1]]
    
    homogeneousTransformation = np.matmul(rotationInZ, traslationXY)
    try:
        transformationResult = np.matmul(homogeneousTransformation, pointToTransformMatrix)
        return [transformationResult[0], transformationResult[1]] #X and Y positions on robot frame
    except ValueError:
        print("------VALUE ERROR------")
        return [-100,-100]
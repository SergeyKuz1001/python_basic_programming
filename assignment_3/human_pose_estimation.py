import cv2
import numpy as np

def proto_file(model):
    if model is "COCO":
        return "pose/coco/pose_deploy_linevec.prototxt"
    elif model is "MPI":
        return "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
    else:
        return None

def weights_file(model):
    if model is "COCO":
        return "pose/coco/pose_iter_440000.caffemodel"
    elif model is "MPI":
        return "pose/mpi/pose_iter_160000.caffemodel"
    else:
        return None

def amount_points(model):
    if model is "COCO":
        return 18
    elif model is "MPI":
        return 15
    else:
        return None

def pose_pairs(model):
    if model is "COCO":
        return [[1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]]
    elif model is "MPI":
        return [[0,1],[1,2],[2,3],[3,4],[1,5],[5,6],[6,7],[1,14],[14,8],[8,9],[9,10],[14,11],[11,12],[12,13]]
    else:
        return None

def key_points(image, model):
    if model not in ["COCO", "MPI"]:
        return None

    protoFile = proto_file(model)
    weightsFile = weights_file(model)
    nPoints = amount_points(model)
    POSE_PAIRS = pose_pairs(model)

    imageWidth = image.shape[1]
    imageHeight = image.shape[0]
    threshold = 0.1

    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

    inWidth = 368
    inHeight = 368
    inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (inWidth, inHeight),
                              (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]

    points = []

    for i in range(nPoints):
        probMap = output[0, i, :, :]
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        x = (imageWidth * point[0]) / W
        y = (imageHeight * point[1]) / H

        if prob > threshold : 
            points.append((int(x), int(y)))
        else :
            points.append(None)

    return points

def image_with_skeleton(initial_image, key_points, pose_pairs):
    image = np.copy(initial_image)

    for pair in pose_pairs:
        partA = pair[0]
        partB = pair[1]
        if key_points[partA] and key_points[partB]:
            cv2.line(image, key_points[partA], key_points[partB], (0, 255, 255), 2)
    
    for point in key_points:
        if point != None:
            cv2.circle(image, point, 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    return image

def image_with_key_points(initial_image, key_points):
    image = np.copy(initial_image)

    for i in range(len(key_points)):
        point = key_points[i]
        if point != None:
            cv2.circle(image, point, 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(image, f"{i}", point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

    return image
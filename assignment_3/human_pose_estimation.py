import cv2
import numpy as np

models = {
    "COCO": {
        "proto_file": "pose/coco/pose_deploy_linevec.prototxt",
        "weights_file": "pose/coco/pose_iter_440000.caffemodel",
        "amount_points": 18,
        "pose_pairs": [
            [1,0],
            [1,2],
            [1,5],
            [2,3],
            [3,4],
            [5,6],
            [6,7],
            [1,8],
            [8,9],
            [9,10],
            [1,11],
            [11,12],
            [12,13],
            [0,14],
            [0,15],
            [14,16],
            [15,17]
        ]
    },
    "MPI": {
        "proto_file": "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt",
        "weights_file": "pose/mpi/pose_iter_160000.caffemodel",
        "amount_points": 15,
        "pose_pairs": [
            [0,1],
            [1,2],
            [2,3],
            [3,4],
            [1,5],
            [5,6],
            [6,7],
            [1,14],
            [14,8],
            [8,9],
            [9,10],
            [14,11],
            [11,12],
            [12,13]
        ]
    }
}


def pose_pairs(model):
    return models[model]["pose_pairs"]


def key_points(image, model):
    if model not in ["COCO", "MPI"]:
        return None

    proto_file = models[model]["proto_file"]
    weights_file = models[model]["weights_file"]
    amount_points = models[model]["amount_points"]

    image_width = image.shape[1]
    image_height = image.shape[0]
    threshold = 0.1

    net = cv2.dnn.readNetFromCaffe(proto_file, weights_file)

    in_width = 368
    in_height = 368
    inp_blob = cv2.dnn.blobFromImage(
        image, 1.0 / 255, (in_width, in_height),
        (0, 0, 0), swapRB=False, crop=False
    )

    net.setInput(inp_blob)

    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]

    points = []

    for i in range(amount_points):
        prob_map = output[0, i, :, :]
        min_val, prob, min_loc, point = cv2.minMaxLoc(prob_map)
        x = (image_width * point[0]) / W
        y = (image_height * point[1]) / H

        if prob > threshold:
            points.append((int(x), int(y)))
        else:
            points.append(None)

    return points


def image_with_skeleton(initial_image, key_points, pose_pairs):
    image = np.copy(initial_image)

    for pair in pose_pairs:
        partA = pair[0]
        partB = pair[1]
        if key_points[partA] and key_points[partB]:
            cv2.line(
                image, key_points[partA], key_points[partB],
                (0, 255, 255), 2
            )
    for point in key_points:
        if point is not None:
            cv2.circle(
                image, point, 8, (0, 0, 255),
                thickness=-1, lineType=cv2.FILLED
            )

    return image


def image_with_key_points(initial_image, key_points):
    image = np.copy(initial_image)

    for i in range(len(key_points)):
        point = key_points[i]
        if point is not None:
            cv2.circle(
                image, point, 8, (0, 255, 255),
                thickness=-1, lineType=cv2.FILLED
            )
            cv2.putText(
                image, f"{i}", point, cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2, lineType=cv2.LINE_AA
            )

    return image

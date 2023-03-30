from pathlib import Path

import blobconverter
import cv2
import depthai
import numpy as np
import json
from pyzbar.pyzbar import decode as qr_decode

def dump_json(object, filename):
  with open(filename, 'w') as f:
    json.dump(object, f)

def qr_decoder(img):
    try:
        gray_img = cv2.cvtColor(img, 0)
        qr = qr_decode(gray_img)[0]

        qrCodeData = qr.data.decode("utf-8")
        return qrCodeData
    except:
        return -1

# yolo v4 tiny label texts
labelMap = [
    "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
    "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
    "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
    "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
    "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
    "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
    "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
    "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
    "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
    "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
    "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
    "teddy bear",     "hair drier", "toothbrush"
]

# Pipeline tells DepthAI what operations to perform when running
pipeline = depthai.Pipeline()

# Using RGB camera as input
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(416, 416)
cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(depthai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.setFps(20)

# Manip images to match nn input size
qr_manip = pipeline.create(depthai.node.ImageManip)
qr_manip.initialConfig.setResize(384, 384)
qr_manip.initialConfig.setFrameType(depthai.RawImgFrame.Type.RGB888p)
cam_rgb.preview.link(qr_manip.inputImage)

# Person detection nn node
yolo_nn = pipeline.createYoloDetectionNetwork()
yolo_nn.setBlobPath(blobconverter.from_zoo(name='yolo-v4-tiny-tf', shaves=6))
yolo_nn.setIouThreshold(0.5)
yolo_nn.setNumClasses(80)
yolo_nn.setCoordinateSize(4)
yolo_nn.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319])
yolo_nn.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
yolo_nn.setNumInferenceThreads(2)
yolo_nn.input.setBlocking(False)
cam_rgb.preview.link(yolo_nn.input)

# QR code detection nn node
qr_detection_nn = pipeline.createMobileNetDetectionNetwork()
qr_detection_nn.setBlobPath(blobconverter.from_zoo(name="qr_code_detection_384x384", zoo_type="depthai", shaves=6))
qr_detection_nn.setConfidenceThreshold(0.5)
qr_manip.out.link(qr_detection_nn.input)

# RGB image output queue
xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# Person detection nn output queue
xout_person_nn = pipeline.createXLinkOut()
xout_person_nn.setStreamName("yolo_nn")
yolo_nn.out.link(xout_person_nn.input)

# QR code detection nn output queue
xout_qr_nn = pipeline.createXLinkOut()
xout_qr_nn.setStreamName("qr_nn")
qr_detection_nn.out.link(xout_qr_nn.input)

# Send pipeline to OAK camera
with depthai.Device(pipeline) as device:
    # Retrieve data queues
    q_rgb = device.getOutputQueue("rgb")
    q_yolo_nn = device.getOutputQueue("yolo_nn")
    q_qr_nn = device.getOutputQueue("qr_nn")

    frame = None
    floor_num = -1
    prev_n_yolo = 0
    n_yolo = 0
    yolo_detections = []
    text_yolo = "Total objects: 0"
    prev_n_qr = 0
    n_qr = 0
    qr_detections = []
    text_qr = "Current floor: 0"

    # Get bounding box from nn outputs
    def frameNorm(frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    print("Running CV...")
    # Main on-device application loop
    while True:
        # Get objects from queues
        in_rgb = q_rgb.tryGet()
        in_yolo_nn = q_yolo_nn.tryGet()
        in_qr_nn = q_qr_nn.tryGet()

        if in_rgb is not None:
            frame = in_rgb.getCvFrame()

        if in_yolo_nn is not None:
            yolo_detections = in_yolo_nn.detections
            prev_n_yolo = n_yolo
            if len(yolo_detections) - prev_n_yolo != 0:
                n_yolo = len(yolo_detections)
                text_yolo = "Total objects: " + str(n_yolo)

        if in_qr_nn is not None:
            qr_detections = in_qr_nn.detections
            prev_n_qr = n_qr
            if len(qr_detections) - prev_n_qr != 0:
                n_qr = len(qr_detections)

        # Fit both person and QR detection boxes to frames using OpenCV
        if frame is not None:
            qr_crop = frame
            detection_dict = {}
            for label in labelMap:
                detection_dict["floor"] = floor_num
                detection_dict[label] = {}
                detection_dict[label]["count"] = 0
                detection_dict[label]["boxes"] = []

            for detection in yolo_detections:
                bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                detection_dict[labelMap[detection.label]]["count"] += 1
                detection_dict[labelMap[detection.label]]["boxes"].append([detection.xmin, detection.ymin, detection.xmax, detection.ymax])
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255 - detection.label*3,  detection.label*3, 0), 2)
                cv2.putText(frame, labelMap[detection.label], (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255 -  detection.label*3,  detection.label*3, 0), 1, cv2.LINE_AA)

            for detection in qr_detections:
                bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                cv2.putText(frame, "QR " + str(int(detection.confidence * 100)) + "%", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                qr_crop = frame[min(bbox[1], bbox[3]):max(bbox[1], bbox[3]), min(bbox[0], bbox[2]):max(bbox[0], bbox[2])]
                if qr_decoder(qr_crop) != -1 and qr_decoder(qr_crop) != floor_num:
                    floor_num = qr_decoder(qr_crop)
                    detection_dict["floor"] = floor_num

            text_qr = "Current floor: " + str(detection_dict["floor"])

            cv2.putText(frame, text_yolo, (5, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, text_qr, (5, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            #Show frames on screen using OpenCV
            #cv2.imshow("preview", frame)

            detection_filename = "/home/pi/hcrcv/yolo-qr/hcrcv_detections.json"
            dump_json(detection_dict, detection_filename)

	# Press Q to close
        if cv2.waitKey(1) == ord('q'):
            break

#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# QSTOM-IT
# Aurélien Vannieuwenhuyze
# 26/04/2020
#---------------------------------------------------


import cv2
from naoqi import ALProxy
import os
import numpy as np
import tensorflow as tf
import qi
import argparse
import sys

# Detection de visages à l'aide du model Cafee Model Zoo
# http://caffe.berkeleyvision.org/model_zoo.html
prototxt_path = os.path.join('model_data/deploy.prototxt')
caffemodel_path = os.path.join('model_data/weights.caffemodel')
model = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)

#Chargement du modèle permettant de détecter le port du masque
modelMasque = tf.keras.models.load_model("QSTOMIT-MASQUE.model")

# camera = ALProxy("ALVideoDevice", "192.168.0.102", 9559)
# resolution = 2
# colorSpace = 11
#
# if not camera.isCameraStarted(0):
#     camera.startCamera(0)
# if not camera.isCameraOpen(0):
#     camera.openCamera(0)
#
# camera_top = camera.subscribeCamera("camera_top", 0, 2, 11, 5)

session = qi.Session()
try:
    session.connect("tcp://ilisa.local:9559")
except RuntimeError:
    print ("Cannot connect to Pepper")
    sys.exit(1)
camera = session.service("ALVideoDevice")
tts = session.service("ALTextToSpeech")
try:
    camera_top = camera.subscribeCamera("camera", 0, 2, 11, 30)
except RuntimeError:
    print ("Cannot connect to the camera")
    sys.exit(1)
# camera_top = camera.subscribeCamera("camera_top", 0, 2, 11, 15)


while True:

    image = camera.getImageRemote(camera_top)
    if image == None:
        print "Cannot capture"
        camera.closeCamera(0)
        camera.stopCamera(0)
        break
    elif image[6] == None:
        print "No image data string"
        camera.closeCamera(0)
        camera.stopCamera(0)
        break
    else:
        image = np.array(image[6])
        image = np.reshape(image, (480, 640, 3))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        model.setInput(blob)
        detections = model.forward()
        h = image.shape[0]
        w = image.shape[1]

        pM_counter = 0
        aM_counter = 0

        for i in range(0, detections.shape[2]):
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            confidence = detections[0, 0, i, 2]

            # If confidence > 0.5, save it as a separate file
            if (confidence > 0.5):
                frame = image[startY:endY, startX:endX]

                #Appel du modèle appris pour la detection de masque
                capture = cv2.resize(frame, (224, 224))
                capture = capture.reshape((1, capture.shape[0], capture.shape[1], capture.shape[2]))
                predict = modelMasque.predict(capture)
                pasDeMasque = predict[0][0]
                avecMasque = predict[0][1]

                if (pasDeMasque > avecMasque):
                    cv2.rectangle(image, (startX, startY), (endX, endY),(0, 0, 255), 2)
                    cv2.putText(image, "PAS DE MASQUE", (startX, startY-10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                    pM_counter += 1
                else:
                    cv2.rectangle(image, (startX, startY), (endX, endY),(0, 255, 0), 2)
                    cv2.putText(image, "OK", (startX, startY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)
                    aM_counter += 1


        # Affichage de l'image
        cv2.imshow('img', image)

    if pM_counter > aM_counter:
        # tts.say("Pas de Masque! Mettre votre masque s'il vous plaît")
        tts.say("Ponté la mascara goiton culiào")
    else:
        tts.say("Merci d'utiliser votre masque!")

    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

camera.unsubscribe(camera_top)
session.close()

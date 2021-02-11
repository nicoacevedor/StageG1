import cv2
import os
import numpy as np
import tensorflow as tf


# Detection de visages à l'aide du model Cafee Model Zoo
# http://caffe.berkeleyvision.org/model_zoo.html
prototxt_path = os.path.join('resources/deploy.prototxt')
caffemodel_path = os.path.join('resources/weights.caffemodel')
model = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)

#Chargement du modèle permettant de détecter le port du masque
modelMasque = tf.keras.models.load_model("resources/QSTOMIT-MASQUE.model")

class MyClass(GeneratedClass):
    def __init__(self):
        try: # disable autoBind
          GeneratedClass.__init__(self, False)
        except TypeError: # if NAOqi < 1.14
          GeneratedClass.__init__( self )
        self.camera = ALProxy("ALVideoDevice")

    def onLoad(self):
        # subscribe(cameraIndex, resolution, colorSpace, fps)
        # 0 -> camera top
        # 2 -> 480x640
        # 11 -> RGB
        self.camera_top = self.camera.subscribeCamera("camera_top", 0, 2, 11, 15)

    def onUnload(self):
        self.camera.unsubscribe(self.camera_top)

    def onInput_onStart(self):
        while True:
            image = self.camera.getImageRemote(self.camera_top)
            self.image_processing(image)
            k = cv2.waitKey(30) & 0xff
            if k==27:
                break

    def onInput_onStop(self):
        self.onUnload() #it is recommended to reuse the clean-up as the box is stopped
        self.onStopped() #activate the output of the


    def image_processing(self, image):
        if image == None:
            print "Cannot capture"
            self.camera.closeCamera(0)
            self.camera.stopCamera(0)
            return
        elif image[6] == None:
            print "No image data string"
            return
        else:
            image = np.array(image[6])
            image = np.reshape(image, (480, 640, 3))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            model.setInput(blob)
            detections = model.forward()

            h = image.shape[0]
            w = image.shape[1]

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

                    if (pasDeMasque >= 0.75):
                        self.useMasque("Mettre votre masque!")
                        cv2.rectangle(image, (startX, startY), (endX, endY),(0, 0, 255), 2)
                        cv2.putText(image, "PAS DE MASQUE", (startX, startY-10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                        cv2.putText(image, str(pasDeMasque*100)+"%", (endX, endY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                    elif (pasDeMasque > 0.5 and pasDeMasque < 0.75):
                        self.usedeMasque("Ajustez bien votre masque!")
                        cv2.rectangle(image, (startX, startY), (endX, endY),(0, 255, 255), 2)
                        cv2.putText(image, "MASQUE MAL AJUSTÉ", (startX, startY-10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                        cv2.putText(image, str(pasDeMasque*100)+"%", (endX, endY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                    else:
                        self.useMasque("Merci d'utiliser votre masque!")
                        cv2.rectangle(image, (startX, startY), (endX, endY),(0, 255, 0), 2)
                        cv2.putText(image, "OK", (startX, startY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)
                        cv2.putText(image, str(avecMasque*100)+"%", (endX, endY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)


            # Affichage de l'image
            cv2.imshow('img', image)
        return

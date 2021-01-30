from naoqi import ALProxy

cam = ALProxy("ALVideoDevice", "ilisa.local", 9559) # IP of the robot | port
# subscribeCamera(Name, CameraIndex, Resolution, ColorSpace, Fps)
# 640x480 | RGB | 30 fps
if not cam.isCameraOpen(0):
    cam.openCamera(0)
if not cam.isCameraOpen(1):
    cam.openCamera(1)

if not cam.isCameraStarted(0):
    cam.startCamera(0)
if not cam.isCameraStarted(1):
    cam.startCamera(1)

cam_top = cam.subscribeCamera("cam_top", 0, 2, 11, 30)
cam_bot = cam.subscribeCamera("cam_bot", 1, 2, 11, 30)

img_top = cam.getImageRemote(cam_top)
img_bot = cam.getImageRemote(cam_bot)
print type(img_top)

tts = ALProxy("ALTextToSpeech", "ilisa.local", 9559)
tts.say("Bonjour!")

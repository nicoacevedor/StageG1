from naoqi import ALProxy

cam = ALProxy("ALVideoDevice", "localhost", 45073) # IP of the robot | port
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
cam_bot = cam.subscribeCamera("cam_bot", 0, 2, 11, 30)

# img_top = cam.getImageLocal(cam_top)
# img_bot = cam.getImageLocal(cam_bot)

tts = ALProxy("ALTextToSpeech", "localhost", 45073)
tts.say("Hello World!")

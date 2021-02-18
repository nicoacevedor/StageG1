import qi

session = qi.Session()
session.connect("tcp://ilisa.local:9559")

seg = session.service("ALSegmentation3D")
print(seg.getBlobTrackingDistance())
mem = session.service("ALMemory")
l = mem.getData("Segmentation3D/TopOfTrackedBlob")
print(l)


session.close()

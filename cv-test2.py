# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from find_blue import find_blue
import time
import cv2

xres = 320
yres = 240
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (xres, yres)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(xres, yres))

# allow the camera to warmup
time.sleep(0.1)
i = 0
tstart = time.clock()
show_frame_rate = 10

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # find the feature we're looking for
    (x,y),(rx,ry,w,h) = find_blue(image)

    # if found the feature:
    if (x != -1):
        #print(x - (xres / 2))
        if (i % show_frame_rate == 0):
            # show the frame
            cv2.rectangle(image, (rx,ry), (rx+w, ry+h), (0, 255, 0), 2)
            cv2.circle(image, (x, y), 3, (0,0,255), -1)
            cv2.imshow("Frame", image)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    i = i+1
    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
print("last x", x)
print("fps: ", i / time.clock() - tstart)
cv2.destroyAllWindows()
print("out")

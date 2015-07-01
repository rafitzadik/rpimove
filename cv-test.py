# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

stop = False
while not stop:
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array

    # display the image on screen and wait for a keypress
    cv2.imshow("Image", image)
    key = cv2.waitKey(0) & 0xFF
    rawCapture.truncate(0)
    if key == ord('q'):
        stop = True

cv2.destroyAllWindows()
cv2.waitKey(1)
print("done")

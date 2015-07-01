import cv2
import numpy as np
import time

def find_blue(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([50, 50, 50])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blur = cv2.inRange(cv2.GaussianBlur(mask, (5,5), 0), 250, 255)
    #im2, contours, hierarchy = cv2.findContours(blur, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, hierarchy = cv2.findContours(blur, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return ((-1,-1),(-1,-1,-1,-1))
    largest_cnt = None
    largest_cnt_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (largest_cnt == None or area > largest_cnt_area):
            largest_cnt = cnt
            largest_cnt_area = area

    x,y,w,h = cv2.boundingRect(largest_cnt)
    
    return((x+w/2, y+h/2), (x,y,w,h))

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
    tstart = time.clock()
    i = 0
    while (1):
        _, frame = cap.read()
        (x,y),(rx,ry,w,h) = find_blue(frame)
        cv2.rectangle(frame, (rx,ry), (rx+w, ry+h), (0, 255, 0), 2)
        cv2.circle(frame, (x, y), 3, (0,0,255), -1)
        cv2.imshow('frame', frame)
        i=i+1
        k = cv2.waitKey(5) & 0xff
        if k == 27:
            break

    print("fps: ", i / time.clock() - tstart)
    cv2.destroyAllWindows()

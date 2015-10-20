import cv2
import numpy as np

MIN_MATCH_COUNT = 5

class findSymbol(object):
    def __init__(self, symbol_img_filename):
        self.img = cv2.imread(symbol_img_filename, 0)
        self.orb = cv2.ORB()
        #kp = self.orb.detect(img, None)
        self.kp1, self.des1 = self.orb.detectAndCompute(self.img,None)
        self.last_poly = None
        self.consistent_reading = 0

    def is_reasonable(self, poly_ar):
        #True if this is a reasonable transformation of a squarish rectangle
        #Right now, checks that it's a reasonable approximation of a square
        #Would be good to check against the geometry of the init image

        poly = poly_ar.tolist()
        print poly
        pts = [poly[0][0], poly[1][0], poly[2][0], poly[3][0]]
        print pts
        #is it generally clockwise? if not, return False.
        if not (pts[1][1] > pts[0][1] and pts[2][0] > pts[1][0] and 
                pts[3][1] < pts[2][1] and pts[0][0] < pts[3][0]):
            print('Not clockwise')
            return False
        #is the y axis on the left and right the same length to within 50%?
        y_ratio = float(pts[1][1] - pts[0][1]) / float(pts[2][1] - pts[3][1]) 
        if y_ratio < 0.5 or y_ratio > 1.5:
            print('y_ratio off:', y_ratio)
            return False
        x_ratio = float(pts[2][0] - pts[1][0]) / float(pts[3][0] - pts[0][0])
        if x_ratio < 0.5 or x_ratio > 1.5:
            print ('x_ratio off: ', x_ratio)
            return False
        #is it a square to within 50%?
        x_mean = float((pts[2][0] - pts[1][0]) + (pts[3][0] - pts[0][0])) / 2
        y_mean = float((pts[1][1] - pts[0][1]) + (pts[2][1] - pts[3][1])) / 2
        x_to_y = x_mean / y_mean
        if x_to_y < 0.5 or x_to_y > 1.5:
            print ('x_to_y off: ', x_to_y, ' x_mean: ', x_mean, ' y_mean: ', y_mean)
            return False
        return True

    def find(self,img2):
        #return: center, enclosing polygon, number of good matches, annotated image
        #kp = self.orb.detect(img2,None)
        kp2, des2 = self.orb.detectAndCompute(img2, None)
        if (des2 == None):
            return None, None, 0, img2
        
        FLANN_INDEX_LSH = 6
        
        index_params = dict(algorithm = FLANN_INDEX_LSH,
                            table_number = 6,
                            key_size = 12,
                            multi_probe_level = 1)
        search_params = dict(checks = 50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        #print 'orig descriptors:', len(self.des1), 'current: ', len(des2)
        matches = flann.knnMatch(self.des1, des2, k=2)
        print 'matches: ', len(matches)
        good = []
        if len(matches) < MIN_MATCH_COUNT:
            return None, None, 0, img2 #not enough matches, forget about "good"

        #print matches[0]
        for m in matches:
            if len(m) == 2 and m[0].distance < 0.7 * m[1].distance:
                good.append(m[0])
        print 'good: ', len(good)
        #cv2.drawKeypoints(img2, kp2, img2, color=(0,255,0),flags=0)
##        bf = cv2.BFMatcher(cv2.NORM_HAMMIN, crossCheck=True)
##        matches = bf.match(self.des1, des2)
##        matches = sorted(matches, key = lambda x:x.dstance)
##        good = matches [:MIN_MATCH_COUNT]

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([ self.kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            if (mask != None):
                matchesMask = mask.ravel().tolist()
                h,w = self.img.shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)
                #print np.int32(dst)
                #print len(img2)
                cv2.polylines(img2,[np.int32(dst)],1,(255,0,0))
                #print len(img2)
                centerx = int(sum([x for [[x,y]] in dst]) / len(dst))
                centery = int(sum([y for [[x,y]] in dst]) / len(dst))
                return [centerx,centery], np.int32(dst), len(good), img2
        return None, None, len(good), img2

if __name__ == "__main__":

    from picamera.array import PiRGBArray
    from picamera import PiCamera
    
    finder = findSymbol("gopigo-bw.jpg")

    camera = PiCamera()
    while True:
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format = 'bgr', use_video_port = True)
        image = rawCapture.array
        
        center, poly, num_good, img = finder.find(image)
        print("center: ", center)
        if (center != None):
            print("poly: ", poly)
            print("is_reasonable: ", finder.is_reasonable(poly))
        cv2.imshow('frame', img)
        if (cv2.waitKey(0) == ord('q')):
            break
        rawCapture.truncate(0)
    
##    cap = cv2.VideoCapture(0)
##    while (1):
##        _, frame = cap.read()
##        center, img = finder.find(frame)
##        if (center != None):
##            cv2.circle(img, (center[0],center[1]), 3, (0,0,255), -1)
##        cv2.imshow('frame', img)
##        k = cv2.waitKey(5) & 0xff
##        if k == 27:
##            break
##
    cv2.destroyAllWindows()
    cv2.waitKey(1)

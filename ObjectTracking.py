import cv2
import time
import numpy as np

cap = cv2.VideoCapture("video123.mp4")

tracker = cv2.TrackerMOSSE_create()
#tracker = cv2.TrackerCSRT_create()

success, img = cap.read()
bbox = cv2.selectROI("Tracking",img,False)

tracker.init(img,bbox)
bbox_array = np.zeros((1,4))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

flag = 0
init_val=0


def drawBox(img,bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    cv2.rectangle(img,(x,y),((x+w),(y+h)),(255,0,255),3,1)
    cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)


while cap.isOpened():
    timer = cv2.getTickCount()
    success, img = cap.read()

    if success:
        success1, bbox = tracker.update(img)
        if success1:
            drawBox(img,bbox)
        else:
            image = cv2.putText(img,"Lost",(75,75),cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)

        fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)

        time.sleep(1/fps)

        bbox = np.asarray(bbox)
        bbox_array = np.append(bbox_array, [bbox], axis=0)
        print(bbox[0]-init_val)
        distance = (bbox[0]-init_val)*0.0637 + 0.106

        cv2.putText(img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, str(distance), (75, 100), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Tracking", img)
        out.write(img)

        if flag == 0:
            if bbox[0] > 0:
                init_val = bbox[0]
                flag = 1


        if cv2.waitKey(1) & 0xff ==ord('q'):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

for i in range(len(bbox_array)):
    bbox_array[i] = bbox_array[i + 1]
    bbox_array[i, 0] -= init_val


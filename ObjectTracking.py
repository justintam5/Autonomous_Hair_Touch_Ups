import cv2
import time
import numpy as np
import csv

class TrackObject:
    cap = cv2.VideoCapture("VideoLast.mp4")

    tracker = cv2.TrackerMOSSE_create()
    #tracker = cv2.TrackerCSRT_create()

    success, img = cap.read()
    bbox = cv2.selectROI("Tracking",img,False)

    tracker.init(img,bbox)
    #bbox_array = np.zeros((1,4))
    distance_time_array = np.zeros((1,2))

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    flag = 0
    init_val=0
    init_time = time.time()
    movie_len = 32000


    def drawBox(img,bbox):
        x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        cv2.rectangle(img,(x,y),((x+w),(y+h)),(255,0,255),3,1)
        cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)


    while cap.isOpened():
        timer = cv2.getTickCount()
        success, img = cap.read()

        if success:
            bbox_success, bbox = tracker.update(img)
            if bbox_success:
                drawBox(img,bbox)

                bbox = np.asarray(bbox)
                distance = (bbox[0] - init_val) * 0.0637 + 0.106  # linear distance function
                distance_time = np.array([distance, time.time() - init_time])
                distance_time_array = np.append(distance_time_array, [distance_time], axis=0)

                if flag == 0:
                    if bbox[0] > 0:
                        init_val = bbox[0]
                        flag = 1
            else:
                image = cv2.putText(img,"Lost",(75,75),cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)

            fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)

            time.sleep(1/fps)

            cv2.putText(img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(img, str(distance), (75, 100), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow("Tracking", img)
            #out.write(img)

            if cv2.waitKey(1) & 0xff ==ord('q'):
                break
        else:
            break

    distance_time_array = np.delete(distance_time_array,0,0)
    distance_time_array = np.delete(distance_time_array,0,0)

    #add the linear time difference between actual movie length and measured length
    movie_diff = (movie_len-((time.time()-init_time)*1000))/1000
    for i in range(len(distance_time_array)):
        distance_time_array[i,1] += movie_diff*(i/len(distance_time_array))

    with open("TestLastVidData.csv","w+", newline='') as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(distance_time_array)







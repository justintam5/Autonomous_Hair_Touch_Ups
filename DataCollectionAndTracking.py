import serial
import numpy as np
import csv
from datetime import datetime
import cv2
import time

# data collection init variables
# declare serial communication variables and file paths
serial_port = 'COM3'    # com port
baud_rate = 57600
currentTime = str(datetime.now())
currentTime = currentTime.replace(':', '_')
pathRunningCsv = "%s_running.csv" % currentTime
pathCalibrationCsv = "%s_calibration.csv" % currentTime
ser = serial.Serial(serial_port, baud_rate)
ser.close()

# initialize arrays
arraycsv = np.zeros((1,7))
linetxt = np.zeros((1,7))
average = np.zeros(3)

flagData = 0    # flag for running different script during calibration and runtime (0 for calibration 1 for runtime)

calibrationTime = 6000000   # calibration time
runTime = 30000000      # runtime time

#Video capture init variables
cap = cv2.VideoCapture("video123.mp4")

tracker = cv2.TrackerMOSSE_create()
#tracker = cv2.TrackerCSRT_create()

success, img = cap.read()
bbox = cv2.selectROI("Tracking",img,False)

tracker.init(img,bbox)
bbox_array = np.zeros((1,4))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

flagVid = 0
init_val = 0

def drawBox(img,bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    cv2.rectangle(img,(x,y),((x+w),(y+h)),(255,0,255),3,1)
    cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

def readDataLine(init_time):
    linetxt = ser.readline()  # read first line
    linetxt = linetxt.decode("utf-8")  # ser.readline returns a binary, convert to string
    linetxt = [[int(i) for i in linetxt.split(',')]]  # put the line into a list seperated by commas
    linetxt = np.asarray(linetxt)  # convert list to numpy array
    linetxt[0, 6] -= init_time  # subtract off initial time from total time to get run time
    return linetxt

def ImageAndTracking():
    while cap.isOpened():
        timer = cv2.getTickCount()
        success, img = cap.read()

        if success:
            success1, bbox = tracker.update(img)
            if success1:
                drawBox(img, bbox)
            else:
                image = cv2.putText(img, "Lost", (75, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

            bbox = np.asarray(bbox)
            bbox_array = np.append(bbox_array, [bbox], axis=0)
            print(bbox[0] - init_val)
            distance = (bbox[0] - init_val) * 0.0637 + 0.106

            cv2.putText(img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(img, str(distance), (75, 100), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow("Tracking", img)
            out.write(img)

            if flagVid == 0:
                if bbox[0] > 0:
                    init_val = bbox[0]
                    flagVid = 1

            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        else:
            break


def data_collection(calibrationTime, runTime, flagData, average,arraycsv,linetxt):
    summ = np.zeros(3)

    # declare time for run time data or calibration data
    if flagData == 0:
        time = calibrationTime
        val = input("Please wait for tracker to finish calibrating, don't touch the tracker, hit enter to continue.")
    elif flagData == 1:
        time = runTime
        val = input("Tracker has been calibrated, hit enter to continue.")

    ser = serial.Serial(serial_port, baud_rate)     # start serial communication

    # compute initial time
    init_time = ser.readline()
    init_time = init_time.decode("utf-8")
    init_time = [[int(i) for i in init_time.split(',')]]
    init_time = np.asarray(init_time)
    init_time = init_time[0, 6]

    while linetxt[0,6] < time:
        linetxt = readDataLine(init_time)
        ImageAndTracking()

        if flagData == 1:   # subtract off average for run time
            for i in range(3):
                linetxt[0, i] -= average[i]
        else:   # sum accelerometer data during calibration for average calculation
            for i in range(3):
                summ[i] += linetxt[0, i]

        arraycsv = np.append(arraycsv, linetxt, axis=0)     # compute 2D array from each single line data
        print(linetxt)

    if flagData == 0:   #comment this block to get rid of average
        for i in range(3):
            average[i] = summ[i]/len(arraycsv)  # compute average of accelerometer data

    ser.close()     # close serial communication

    return arraycsv, average


def savefile(path):
    # a functin for simply saving files
    with open(path,"w+", newline='') as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(arraycsv)


if __name__ == '__main__':
    arraycsv = np.zeros((1, 7))
    linetxt = np.zeros((1, 7))

    cap = cv2.VideoCapture("video123.mp4")

    tracker = cv2.TrackerMOSSE_create()
    # tracker = cv2.TrackerCSRT_create()

    success, img = cap.read()
    bbox = cv2.selectROI("Tracking", img, False)

    tracker.init(img, bbox)
    bbox_array = np.zeros((1, 4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    # get calibration data
    arraycsv, average = data_collection(calibrationTime, runTime, flagData, average, arraycsv, linetxt)
    savefile(pathCalibrationCsv)

    flagData = 1    # set flag to 1 to setup for runtime
    print(average)
    arraycsv = np.zeros((1, 7))     # reinitialize arrays to zero for runtime
    linetxt = np.zeros((1, 7))

    # get runtime data
    arraycsv, average = data_collection(calibrationTime, runTime, flagData, average, arraycsv, linetxt)
    savefile(pathRunningCsv)
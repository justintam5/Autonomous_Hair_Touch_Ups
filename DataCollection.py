import serial
import numpy as np
import csv
from datetime import datetime

# declare serial communication variables and file paths
serial_port = 'COM3'    # com port
baud_rate = 57600
currentTime = str(datetime.now())
currentTime = currentTime.replace(':', '_')
pathRunningCsv = "%s_running.csv" % currentTime
pathCalibrationCsv = "%s_calibration.csv" % currentTime

# initialize arrays
arraycsv = np.zeros((1,7))
linetxt = np.zeros((1,7))
average = np.zeros(3)

flag = 0    # flag for running different script during calibration and runtime (0 for calibration 1 for runtime)

calibrationTime = 6000000   # calibration time
runTime = 12000000      # runtime time

def data_collection(calibrationTime, runTime, flag, average,arraycsv,linetxt):
    summ = np.zeros(3)

    # declare time for run time data or calibration data
    if flag == 0:
        time = calibrationTime
        val = input("Please wait for tracker to finish calibrating, don't touch the tracker, hit enter to continue.")
    elif flag == 1:
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
        linetxt = ser.readline()    # read first line
        linetxt = linetxt.decode("utf-8")  # ser.readline returns a binary, convert to string
        linetxt = [[int(i) for i in linetxt.split(',')]]    # put the line into a list seperated by commas
        linetxt = np.asarray(linetxt)   # convert list to numpy array
        linetxt[0, 6] -= init_time  # subtract off initial time from total time to get run time

        if flag == 1:   # subtract off average for run time
            for i in range(3):
                linetxt[0, i] -= average[i]
        else:   # sum accelerometer data during calibration for average calculation
            for i in range(3):
                summ[i] += linetxt[0, i]

        arraycsv = np.append(arraycsv, linetxt, axis=0)     # compute 2D array from each single line data
        print(linetxt)

    if flag == 0:   #comment this block to get rid of average
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

    # get calibration data
    arraycsv, average = data_collection(calibrationTime, runTime, flag, average, arraycsv, linetxt)
    savefile(pathCalibrationCsv)

    flag = 1    # set flag to 1 to setup for runtime
    print(average)
    arraycsv = np.zeros((1, 7))     # reinitialize arrays to zero for runtime
    linetxt = np.zeros((1, 7))

    # get runtime data
    arraycsv, average = data_collection(calibrationTime, runTime, flag, average, arraycsv, linetxt)
    savefile(pathRunningCsv)


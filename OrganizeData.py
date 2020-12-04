import numpy as np
import math
import csv

class OrganizeData:

    def __init__(self, vid_file='Test1VidData.csv', sensor_file='Test1Data.csv', data_set_number=1):

        self.vid_file = vid_file
        self.sensor_file = sensor_file

        self.data_set_number = data_set_number

        self.sensor_time_column = 3
        self.vid_time_column = 1

        self.sensor_cut_off_value = 0.5
        self.vid_cut_off_value = 0.2

    def read_csv(self):
        vid_array = np.genfromtxt(self.vid_file, delimiter=',')
        sensor_array = np.genfromtxt(self.sensor_file, delimiter=',')
        return vid_array, sensor_array

    def shift_start_data(self, vid_array, sensor_array):
        sensor_start_time, vid_start_time, time_diff = 0, 0, 0

        if sensor_array[1, self.sensor_time_column] > 1000:
            sensor_array[:, self.sensor_time_column] *= 1/1000000

        for i in range(len(sensor_array)):
            if abs(sensor_array[i, 0]) > self.sensor_cut_off_value:
                sensor_start_time = sensor_array[i, self.sensor_time_column]
                break

        for i in range(len(vid_array)):
            if abs(vid_array[i, 0]) > self.vid_cut_off_value:
                vid_start_time = vid_array[i, self.vid_time_column]
                break

        time_diff = abs(vid_start_time-sensor_start_time)

        if vid_start_time > sensor_start_time:
            for i in range(len(vid_array)):
                try:
                    while True:
                        vid_array[i, self.vid_time_column] -= time_diff
                        if vid_array[i, self.vid_time_column] < 0:
                            vid_array = np.delete(vid_array, i, 0)
                        else:
                            break
                except:
                    break
        else:
            for i in range(len(sensor_array)):
                try:
                    while True:
                        sensor_array[i, self.sensor_time_column] -= time_diff
                        if sensor_array[i, self.sensor_time_column] < 0:
                            sensor_array = np.delete(sensor_array, i, 0)
                        else:
                            break
                except:
                    break

        return vid_array, sensor_array

    def shift_end_data(self, vid_array, sensor_array):

        if vid_array[len(vid_array)-1, self.vid_time_column] > sensor_array[len(sensor_array)-1, self.sensor_time_column]:
            for i in range(len(vid_array)):
                try:
                    while True:
                        if vid_array[i, self.vid_time_column] > sensor_array[len(sensor_array)-1, self.sensor_time_column]:
                            vid_array = np.delete(vid_array, i, 0)
                        else:
                            break
                except:
                    break
            while vid_array[len(vid_array) - 1, self.vid_time_column] < sensor_array[len(sensor_array) - 1, self.sensor_time_column]:
                sensor_array = np.delete(sensor_array, len(sensor_array) - 1, 0)

        else:
            for i in range(len(sensor_array)):
                try:
                    while True:
                        if sensor_array[i, self.sensor_time_column] > vid_array[len(vid_array), 1]:
                            sensor_array = np.delete(sensor_array, i, 0)
                        else:
                            break
                except:
                    break

        return vid_array, sensor_array

    def reduce_frequency(self, vid_array, sensor_array):
        counter1, counter2 = 0, 0 # counter1 used for indexing vid_array counter2 used for counting elements with same time
        sum = np.zeros(self.sensor_time_column)

        # lets sensor times equal vid_array times then averages out accelerometer values for given time interval
        for i in range(len(sensor_array)):
            try:
                repeat = True
                while repeat:
                    if sensor_array[i, self.sensor_time_column] < vid_array[counter1, self.vid_time_column]:
                        sensor_array[i, self.sensor_time_column] = vid_array[counter1, self.vid_time_column]
                        for j in range(self.sensor_time_column):
                            sum[j] += sensor_array[i, j]
                        counter2 += 1
                        repeat = False
                    else:
                        if counter2 == 0:   # handles the case where the time interval of the video is smaller than sensors
                            sensor_array[i, self.sensor_time_column] = vid_array[counter1, self.vid_time_column]
                            repeat = False
                        else:
                            for j in range(self.sensor_time_column):
                                sensor_array[i-counter2:i, j] = sum[j] / counter2

                        counter1 += 1
                        counter2 = 0
                        sum[:] = 0

            except:
                break

        # deletes repeat values
        for i in range(len(sensor_array)):
            try:
                while True:
                    if math.isclose(sensor_array[i, self.sensor_time_column], sensor_array[i+1, self.sensor_time_column]):
                        sensor_array = np.delete(sensor_array, i+1, 0)
                    else:
                        break
            except:
                break

        return vid_array, sensor_array

    def combine_vid_sensor_print(self, vid_array, sensor_array):
        data = np.append(sensor_array,vid_array, 1)
        data = np.delete(data,data.shape[1]-1, 1)
        with open("CombinedSensorVidData%d.csv" % self.data_set_number, "w+", newline='') as my_csv:
            csvWriter = csv.writer(my_csv, delimiter=',')
            csvWriter.writerows(data)

    def combine_files(self, *args):
        with open('final_training_set.csv', 'w') as outfile:
            for names in args:
                with open(names) as infile:
                    outfile.write(infile.read())

if __name__ == '__main__':
    data = OrganizeData()
    vid_array, sensor_array = data.read_csv()
    vid_array, sensor_array = data.shift_start_data(vid_array, sensor_array)
    vid_array, sensor_array = data.shift_end_data(vid_array, sensor_array)
    vid_array, sensor_array = data.reduce_frequency(vid_array, sensor_array)
    data.combine_vid_sensor_print(vid_array, sensor_array)




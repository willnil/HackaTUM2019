#HACKATUM 2019
#TEAM DUT ME
#ROHDE & SCHWARZ CHALLENGE 
# This optimisation code does:
#   1. Optimisation on a break in measurement once a faulty DUT is identified
#   2. Optimisation to prioritise measurements that take the shortest duration first
#   3. Identification of the optimal time interval to recalibrate the tester for a specific seed.
#       Explanation: A company would only produce a specific number of types of DUTs (P) and would want to do a specific 
#       number of combinations of measurements (N). Since the recalibration time is regular if N and P are constant, 
#       this code identifies the optimal recalibration time, saves it in a json file aso that when similar conditions (N & P)
#       exist, the optimal recalibration time can be directly identified.

import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import sys  #
from initial_test import initial_test


def main():
    # yield 3 ==> ~90%
    # yield 4.4 ==> ~99.99%
    # my_dut = DUT(None,True,3.8)
    # my_dut = DUT()

    calibration_interval_arr = np.arange(50, 1360, 100)
    output_DUT_array = []
    seed = 9    #<<<INPUT SEED HERE
                #Seed is not deterministic, as in real life, there are specific Models of DUTs and specfic set of tests 

    def init_dut():
        dut_init = DUT(seed, True, 3)
        return dut_init

    data = {'component': []}
    failed_DUT_count_arr = []
    array_to_sort = []
    sorted_new_order = []
    i = 0
    best_calib = 0
    
    
    
    for calibration_interval in calibration_interval_arr: 
        error_count = 0
        t = 0
        i+= 1
        my_dut = init_dut()
        meastime, nmeas, nport, meas, ports, expyield = my_dut.info()

        print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ",
              expyield)
        print("Current Calibration Interval = ", calibration_interval)

        for x in range(10000):

            my_dut.new_dut()
            dut = {'dut_id': x, 'measurements': []}
            if x % calibration_interval == 0:
                my_dut.calibrate()
            for i in range(0, nmeas):
                if x == 0:
                    t, result, dist = my_dut.gen_meas_idx(i)
                    measurement = {}
                    measurement['m_id'] = i
                    measurement['m_time'] = meas[i].meas_time
                    measurement['m_result'] = dist  # measurement result
                    dut['measurements'].append(measurement)
                    sequence = range(0, nmeas)
                    array_to_sort.append(meas[i].meas_time)
                    new_order = list(zip(sequence, array_to_sort))

                if x > 1:
                    u = sorted_new_order[i][0] #Sort according to shortest meastime, refer to no. 2
                    t, result, dist = my_dut.gen_meas_idx(u)
                    measurement = {}
                    measurement['m_id'] = u
                    measurement['m_time'] = meas[u].meas_time
                    measurement['m_result'] = dist  # measurement result
                    dut['measurements'].append(measurement)
                    if dist > 1: #Break when one error detected, refer to no.1
                        break

            if x == 0:
                sorted_new_order = sorted(new_order, key=lambda tup: tup[1])

            t, res, dist = my_dut.get_result()
            dut['dut_result'] = res

            data['component'].append(dut)
            if not res:
                error_count += 1
            if t >= 86400:
                error_dut, error_meas = my_dut.get_errordutcount()
                output_DUT_array.append(x + 1 - (error_meas - error_dut))
                failed_DUT_count_arr.append(error_dut)
                break
                
                

        print("DUTs in a day ", x + 1 - (error_meas - error_dut), " ( ", error_count, " | ", error_dut, " | ",
              error_meas, " ) ==> ",
              (x + 1 - error_count) / (x + 1))

    # print results
    new_result = output_DUT_array[np.argmax(np.array(output_DUT_array))]
    old_result = initial_test(init_dut())
    best_calib = 50 + 100*output_DUT_array.index(new_result)
    print(" ")
    print("Best Calibration Interval for DUT model no.", seed, " is :", best_calib) #Finds best calibration, refer to no.3
    print("New Result: ", new_result)
    print("Old Result: ", old_result)
    improvement = ((new_result - old_result) / old_result)*100
    print("Percentage Improvement", improvement, "%")
    
    infoblock = [seed, best_calib]

    #Place for code to append infoblock to a json database of optimal recalibration intervall and corresponding seeds.
    #
    #
    #End of sub-block.
  
if __name__ == "__main__":
    # execute only if run as a script
    main()

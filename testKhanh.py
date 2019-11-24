# HACKATUM 2019
# TEAM DUT ME
# ROHDE & SCHWARZ CHALLENGE
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
from scipy.interpolate import interpolate
from initial_test import initial_test
import json
import sys


def main():

    # Khanh's Variables
    performance_arr = []
    wPerform = 5;
    wFalse = 1;

    # init empty array
    X = []
    Y = []
    d_cali_arr = np.arange(100, 1400, 50)
    data = {'component': []}
    error_dut_arr = []
    total_dut = []
    array_to_sort = []
    sorted_new_order = []
    seed = 9  # <<< INPUT SEED HERE
    # Seed is not deterministic, as in real life, there are specific Models of DUTs and specfic set of tests
    i = 0
    best_calib = 0

    def init_dut():
        # yield 3 ==> ~90%
        # yield 4.4 ==> ~99.99%
        # my_dut = DUT(None,True,3.8)
        # my_dut = DUT()
        dut_init = DUT(seed, True, 3)
        return dut_init

    for d_cali in d_cali_arr:
        error_count = 0
        t = 0
        i += 1
        my_dut = init_dut()
        meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
        print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ",
              expyield)
        print("current calibration interval = ", d_cali)

        for x in range(10000):
            my_dut.new_dut()
            dut = {'dut_id': x, 'measurements': []}

            # recalibration interval
            if x % d_cali == 0:
                my_dut.calibrate()

            for i in range(0, nmeas):
                if x == 0:
                    t, result, dist = my_dut.gen_meas_idx(i)
                    measurement = {'m_id': i, 'm_time': meas[i].meas_time, 'm_result': dist}
                    dut['measurements'].append(measurement)
                    sequence = range(0, nmeas)
                    array_to_sort.append(meas[i].meas_time)
                    new_order = list(zip(sequence, array_to_sort))

                if x > 1:
                    u = sorted_new_order[i][0]  # Sort according to shortest meastime, refer to no. 2
                    t, result, dist = my_dut.gen_meas_idx(u)
                    measurement = {'m_id': u, 'm_time': meas[u].meas_time, 'm_result': dist}
                    dut['measurements'].append(measurement) # Break when one error detected, refer to no.1
                    if dist > 1:
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
                total_dut.append(x + 1 - (error_meas - error_dut))
                error_dut_arr.append(error_meas-error_dut)
                break

            X.append(t)
            Y.append(dist)

        print("DUT in a day ", x + 1 - (error_meas - error_dut), " ( ", error_count, " | ", error_dut, " | ",
              error_meas, " ) ==> ", (x + 1 - error_count) / (x + 1))

        # Evaluating performance through amount of successful tested DUT and correctly faulty DUT
        performance_arr.append(x - error_count);

    # print results
    new_result = total_dut[np.argmax(np.array(total_dut))]
    old_result = initial_test(init_dut())
    best_calib = 50 + 100 * total_dut.index(new_result)
    print("Best Calibration Interval for DUT model no.", seed, " is :", best_calib)  # Finds best calibration, refer
    # to no.3
    print("DUT output after optimization per 24 h : ", new_result)
    print("DUT output before optimization per 24 h : ", old_result)
    improvement = ((new_result - old_result) / old_result)*100
    print("Percentage improvement [%]: ", improvement)

    infoblock = [seed, best_calib]

    # Place for code to append infoblock to a json database of optimal recalibration intervall and corresponding seeds.
    #
    #
    # End of sub-block.

    # write json log
    outfile = open('new_result.json', 'w')
    json.dump(sorted_new_order, outfile, indent=2)



    # Khanh Plot
    # Calculating cost function
    gewinn = []
    for i in range(len(d_cali_arr)):
        tmp = 5 * performance_arr[i] - total_dut[i]
        gewinn.append(tmp)

    # 1st Subplot
    fig, axs = plt.subplots(2, 1, constrained_layout=True)
    axs[0].plot(d_cali_arr, performance_arr, 'or', d_cali_arr, performance_arr, 'b-')
    axs[0].set_title('Amount of Tested DUT vs Wrong Measurements.')
    axs[0].set_xlabel('recalibration_interval')
    axs[0].set_ylabel('Performance', color='b')
    ax2 = axs[0].twinx()
    # plt.vlines(x = best_calib, ymin = min(output_DUT_array), ymax=max(output_DUT_array), color='blue')
    ax2.plot(d_cali_arr, error_dut_arr, 'o', d_cali_arr, error_dut_arr, '-')
    ax2.set_ylabel('failed_DUT', color='r')
    # ax2.set_ylim(0, 100)
    ax2.tick_params('y', colors='r')
    fig.tight_layout()

    # 2nd Subplot
    axs[1].plot(d_cali_arr, gewinn, 'g-', d_cali_arr, gewinn, 'o')
    axs[1].set_title('Profit depends on calibration interval')
    axs[1].set_xlabel('recalibration_interval')
    axs[1].set_ylabel('Profit', color='g')
    axs[1].tick_params('y', colors='g')
    axs[1].legend(['W1 * Performances - W2 * Wrong Measurements', 'W1 = %d, W2 = %d' % (wPerform, wFalse)])
    fig.tight_layout()

    # Screen Output
    plt.show();


if __name__ == "__main__":
    # execute only if run as a script
    main()
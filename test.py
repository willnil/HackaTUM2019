import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import json
import sys  #
from initial_test import initial_test


def main():
    # yield 3 ==> ~90%
    # yield 4.4 ==> ~99.99%
    # my_dut = DUT(None,True,3.8)
    # my_dut = DUT()

    calibration_interval_arr = np.arange(200, 1000, 50)
    output_DUT_array = []

    # Khanh's Variables
    performance_arr = []
    wPerform = 5;
    wFalse = 1;

    def init_dut():
        mySeed = 8
        dut_init = DUT(mySeed, True, 3)
        return dut_init

    data = {'component': []}
    failed_DUT_count_arr = []
    array_to_sort = []
    sorted_new_order = []

    for calibration_interval in calibration_interval_arr:
        error_count = 0
        t = 0
        my_dut = init_dut()
        meastime, nmeas, nport, meas, ports, expyield = my_dut.info()

        print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ",
              expyield)
        print("current calibration interval = ", calibration_interval)

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
                    u = sorted_new_order[i][0]
                    t, result, dist = my_dut.gen_meas_idx(u)
                    measurement = {}
                    measurement['m_id'] = u
                    measurement['m_time'] = meas[u].meas_time
                    measurement['m_result'] = dist  # measurement result
                    dut['measurements'].append(measurement)
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
                output_DUT_array.append(x + 1 - (error_meas - error_dut))
                failed_DUT_count_arr.append(error_dut)
                break

        print("DUT in a day ", x + 1 - (error_meas - error_dut), " ( ", error_count, " | ", error_dut, " | ",
              error_meas, " ) ==> ",
              (x + 1 - error_count) / (x + 1))

        # Evaluating performance through amount of successful tested DUT and correctly faulty DUT
        performance_arr.append(x - error_count);

    new_result = output_DUT_array[np.argmax(np.array(output_DUT_array))]
    old_result = initial_test(init_dut())
    best_calib = 200 + 50 * output_DUT_array.index(new_result)
    print("new result: ", new_result)
    print("old result: ", old_result)
    improvement = new_result / old_result
    print(improvement)
    print(best_calib)


        # plot results
    # Khanh

    # Calculating cost function
    gewinn = []
    for i in range(len(calibration_interval_arr)):
        tmp = 5 * performance_arr[i] - failed_DUT_count_arr[i]
        gewinn.append(tmp)

    # 1st Subplot
    fig, axs = plt.subplots(2, 1, constrained_layout=True)
    axs[0].plot(calibration_interval_arr, performance_arr, 'or', calibration_interval_arr, performance_arr, 'b-')
    axs[0].set_title('Amount of Tested DUT vs Wrong Measurements.')
    axs[0].set_xlabel('recalibration_interval')
    axs[0].set_ylabel('Performance', color='b')
    ax2 = axs[0].twinx()
    #plt.vlines(x = best_calib, ymin = min(output_DUT_array), ymax=max(output_DUT_array), color='blue')
    ax2.plot(calibration_interval_arr, failed_DUT_count_arr, 'o', calibration_interval_arr, failed_DUT_count_arr, '-')
    ax2.set_ylabel('failed_DUT', color='r')
    #ax2.set_ylim(0, 100)
    ax2.tick_params('y', colors='r')
    fig.tight_layout()

    # 2nd Subplot
    axs[1].plot(calibration_interval_arr, gewinn, 'g-', calibration_interval_arr, gewinn, 'o')
    axs[1].set_title('Profit depends on calibration interval')
    axs[1].set_xlabel('recalibration_interval')
    axs[1].set_ylabel('Profit', color='g')
    axs[1].tick_params('y', colors='g')
    axs[1].legend(['W1 * Performances - W2 * Wrong Measurements', 'W1 = %d, W2 = %d' % (wPerform, wFalse)])
    fig.tight_layout()

    # Screen Output
    plt.show();


    # End Khanh




if __name__ == "__main__":
    # execute only if run as a script
    main()

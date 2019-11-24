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

    calibration_interval_arr = np.arange(50, 1360, 100)
    output_DUT_array = []

    def init_dut():
        dut_init = DUT(4, True, 3)
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

        # plot results

    new_result = output_DUT_array[np.argmax(np.array(output_DUT_array))]
    old_result = initial_test(init_dut())
    print("new result: ", new_result)
    print("old result: ", old_result)
    improvement = new_result / old_result
    print(improvement)


if __name__ == "__main__":
    # execute only if run as a script
    main()

import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import json
import sys


def main():
    # yield 3 ==> ~90%
    # yield 4.4 ==> ~99.99%
    # my_dut = DUT(None,True,3.8)
    # my_dut = DUT()
    my_dut = DUT(None, True, 4.1)

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ",
          expyield)

    error_count = 0
    X = []
    Y = []
    t = 0

    data = {'component': []}

    for x in range(10000):
        my_dut.new_dut()
        dut = {'dut_id': x, 'measurements': []}

        if x % 500 == 0:
            my_dut.calibrate()

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            measurement = {'m_id': i, 'm_time': meas[i].meas_time, 'm_result': dist}
            dut['measurements'].append(measurement)

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ", t, "s ", x + 1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ",
          (x + 1 - error_count) / (x + 1))

    # write json log
    outfile = open('result.json', 'w')
    json.dump(data, outfile)

    # plot results
    timeAxis = [x / 3600. for x in X]
    plt.xlabel('time [h]')
    plt.plot(timeAxis, Y)
    plt.axhline(y=1., xmin=0, xmax=1, color='r')
    plt.show()


if __name__ == "__main__":
    # execute only if run as a script
    main()

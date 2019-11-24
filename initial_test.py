import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import json
import sys

def initial_test(my_dut):
    # yield 3 ==> ~90%
    # yield 4.4 ==> ~99.99%
    #my_dut = DUT(None,True,3.8)
    # my_dut = DUT()


    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)

    error_count = 0
    t = 0
    data= {}
    data['component']=[]
    for x in range(10000):
        my_dut.new_dut()
        dut = {}
        dut['dut_id'] = x
        dut['measurements']=[]

        if x % 500 == 0:
            my_dut.calibrate()

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        if not res:
            error_count += 1
        if t >= 86400:
            error_dut, error_meas = my_dut.get_errordutcount()
            return x + 1 - (error_meas - error_dut)





    # write json log
    outfile = open('result.json', 'w')
    json.dump(data, outfile)
    return()


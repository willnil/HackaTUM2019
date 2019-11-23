import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import math


        
def main():
    # yield 3 ==> ~90%
    # yield 4.4 ==> ~99.99%
    #my_dut = DUT(None,True,3.8)
    # my_dut = DUT()
    my_dut = DUT(1,True,4)

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)

    error_count = 0
    X = []
    Y = []
    t=0
    array_to_sort = []
    sorted_new_order = []
    

    data= {}
    data['component']=[]


    for x in range(10000):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]

        if x % 500 == 0:
            my_dut.calibrate()

        for i in range(0, nmeas):
            if x == 0:
                t, result, dist = my_dut.gen_meas_idx(i)
                measurement = {}
                measurement['m_id'] = i
                measurement['m_time'] = meas[i].meas_time
                measurement['m_result'] = dist    #measurement result 
                dut['measurements'].append(measurement)
                sequence = range(0, nmeas)
                array_to_sort.append(meas[i].meas_time)
                new_order = list(zip(sequence,array_to_sort))
                
            if x > 1:
                u = sorted_new_order[i][0]
                t, result, dist = my_dut.gen_meas_idx(u)
                measurement = {}
                measurement['m_id'] = u
                measurement['m_time'] = meas[u].meas_time
                measurement['m_result'] = dist    #measurement result 
                dut['measurements'].append(measurement)
                if dist > 1:
                    break

        if x == 0:
            sorted_new_order= sorted(new_order, key=lambda tup: tup[1])
    
        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res     

        data['component'].append(dut)
        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ",t, "s ", x+1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ", (x+1-error_count)/(x+1) )

    # write json log
    outfile = open('result.json', 'w')
    json.dump(data, outfile, indent = 2)
    
    outfile2 = open('meas.json', 'w')
    json.dump(sorted_new_order, outfile2, indent = 0)


    # plot results
    timeAxis = [x / 3600. for x in X]
    plt.xlabel('time [h]')
    plt.plot(timeAxis,Y)
    plt.axhline(y=1., xmin=0, xmax=1, color='r')
    plt.show()
    
if __name__ == "__main__":
    # execute only if run as a script
    main()

import math
import random
import numpy as np
from scipy.stats import random_correlation as rndcorr
#from RandomWalk import RandomWalk

class port:
    def __init__(self, x, recal_hours = None):
        self.idx = x
        self.random_generator = np.random.RandomState(x)
        self.longest_measurement_time = 0
        if recal_hours is not None:
            self.RecalTime = 60 * 60 * recal_hours
        else:
            self.RecalTime = 60 * 60 * 24 * 2  # 2 days for re-calibration

    def set_longest_meas_time(self, t):
        if t > self.longest_measurement_time:
            self.longest_measurement_time = t

    def get_port_error(self, t):
        linDrift = t/self.RecalTime * 0.1
        #portNoise = self.random_generator.chisquare(1) / 200.
        portNoise = self.random_generator.standard_normal() / 200;
        return linDrift + portNoise
        #return self.random_generator.get_next()


class meas:
    def __init__(self, x, port_a, port_b, meas_time):
        self.idx = x
        self.port_a = port_a
        self.port_b = port_b
        self.meas_time = meas_time
        self.meas_dist = 0
        #self.random_generator = np.random.RandomState(x)

class DUT:
    """
    DUT class represents a dedicated DUT based on stochastical behaviour

    Attributes
    ----------
    seed : optional
        seed for all random generators; if given, reproducible data will be generated
        if omitted, an internally generated random seed is used
    """
    def __init__(self, seed=None, usePort=True, expYield=None):
        """

        :param seed: optional
            if omitted, the seed is randomly generated internally

        init constructs a DUT with a random (equal distributed) number of 10 to 50 measurements "n"
        A random (equal distributed) number of 4,8,12,16,20 or 24  so called "ports"  "p" is generated. Each measurement
        is randomly associated to two not necessarily different ports.
        These ports contribute to the measurement error with a random drift.

        All measurements might be correlated through a nxn covariance matrix, generated through its n randomly
        generated eigenvalues.
        """
        if seed is not None:
            np.random.seed(seed)

        self.usePort = usePort
        self.exp_yield =  expYield if expYield is not None else np.random.randint(3, 4.4)
        self.numMeas = np.random.randint(10, 50)
        self.numPorts = np.random.randint(1, 6) * 4
        self.lastCal = 0
        self.DutMeasTime = 0
        self.dist_max = 0

        # list of ports with uncorrelated random walk generators
        self.ports = [port(count) for count in range(self.numPorts)]

        self.meas = [meas(count, np.random.randint(1, self.numPorts), np.random.randint(1, self.numPorts),
                          np.random.randint(50, 5000000)*1e-6) for count in range(self.numMeas)]
        for idx in range(self.numMeas):
            p_a = self.meas[idx].port_a
            p_b = self.meas[idx].port_b
            meas_time = self.meas[idx].meas_time
            self.ports[p_a].set_longest_meas_time( meas_time )
            self.ports[p_b].set_longest_meas_time( meas_time )
            self.DutMeasTime += meas_time

        # count used ports
        self.portcountused = 0
        for idx in range(self.numPorts):
            if self.ports[idx].longest_measurement_time > 0:
                self.portcountused += 1

        # generate random eigenvalues for covariance matrix ...
        self.meas_eigenvalue = np.random.random(self.numMeas)
        # ... and normalise it
        self.meas_eigenvalue *= self.numMeas / np.sum(self.meas_eigenvalue)
        # generate covariance matrix based on random eigenvector
        self.meas_cov = rndcorr.rvs(self.meas_eigenvalue)

        self.meas_noise = np.zeros((self.numMeas, self.numMeas))
        self.port_noise = np.zeros(self.numPorts)

        # instantiate p biased ports errors
        #self.ports = [RandomWalk(count) for count in range(self.numPorts)]

        # measurement time
        self.measurement_time = 0
        self.dT_newDut = 0.1
        self.dut_result = True
        self.meas_result = True

        self.errordutcount = 0
        self.errormeascount = 0

    def info(self):
        return self.DutMeasTime, self.numMeas, self.numPorts, self.meas, self.ports, self.exp_yield

    def new_dut(self):
        """
        Called whenever a new DUT is in the virtual handler
        :return:
        """
        # if previous DUT was errorneous add to count
        if self.dut_result == False:
            self.errordutcount += 1
        if self.meas_result == False:
            self.errormeascount += 1

        self.measurement_time += self.dT_newDut

        self.dut_result = True
        self.meas_result = True

        self.dist_max=0
        self.meas_noise = np.random.multivariate_normal(np.zeros(self.numMeas), self.meas_cov) / self.exp_yield
        for index in range(self.numPorts):
            self.port_noise[index] = self.ports[index].get_port_error(self.measurement_time - self.lastCal)

    def calibrate(self):
        caltime = 0
        # caltime is number of (used) ports times longest measurement at this port times standard used (OSM)
        # plus through (might be underestimated as per used port rather than per used port pair)
        for idx in range(self.numPorts):
            caltime += 4*self.ports[idx].longest_measurement_time
        # add 30 seconds per port for connecting
        caltime += self.portcountused * 30
        print("Calibration at ",self.measurement_time, " took ", caltime, " seconds.")
        self.measurement_time += caltime
        self.lastCal = self.measurement_time

    def gen_meas(self):
        """
        generate all measurements for the current DUT
        :return:
        """
        self.new_dut()
        for i in range(0, self.numMeas):
            t, result, dist = self.gen_meas_idx(i)
        return self.measurement_time, self.dut_result, self.dist_max

    def gen_meas_idx(self, idx):
        """
        generate individual measurement of the current DUT incrementing the allover measurement time
        :param idx:
        :return:
        """
        meas_result = True
        # chi-square of order k=1  #self.meas[idx].random_generator.chisquare(3) / 10.
        porta = self.port_noise[self.meas[idx].port_a]
        portb = self.port_noise[self.meas[idx].port_b]

        # DUT characteristic
        self.meas[idx].meas_dist = self.meas_noise[idx] ** 2
        self.measurement_time += self.meas[idx].meas_time
        if self.meas[idx].meas_dist > self.dist_max:
            self.dist_max = self.meas[idx].meas_dist
        if self.meas[idx].meas_dist > 1.0:
            self.dut_result = False
            self.meas_result = False
            meas_result = False

        # add influence of port calibration
        if self.usePort:
            self.meas[idx].meas_dist += porta + portb
            if self.meas[idx].meas_dist > 1.0:
                self.meas_result = False
                meas_result = False

        return self.measurement_time, meas_result, self.meas[idx].meas_dist

    def get_result(self):
        return self.measurement_time, self.meas_result, self.dist_max

    def get_time(self):
        return self.measurement_time

    def get_errordutcount(self):
        return self.errordutcount, self.errormeascount







# mq9 adapted from https://github.com/leech001/MQ9

import time
import math
from machine import ADC

class MQ:
    # Hardware Related Macros
    RL_VALUE = 10  # define the load resistance on the board, in kilo ohms
    RO_CLEAN_AIR_FACTOR = 9.83
    # RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO, which is derived from the chart in datasheet

    # Software Related Macros
    CALIBARAION_SAMPLE_TIMES = 50  # define how many samples you are going to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL = 500  # define the time interval(in milliseconds) between each sample in the calibration phase
    READ_SAMPLE_INTERVAL = 50  # define how many samples you are going to take in normal operation
    READ_SAMPLE_TIMES = 5  # define the time interval(in milliseconds) between each sample in normal operation

    # Application Related Macros
    GAS_LPG = 0
    GAS_CH4 = 1

    def __init__(self, ro=10):
        self.ro = ro
        self.adc = ADC(0)

        self.LPGCurve = [2.3, 0.21, -0.47]  # two points are taken from the curve.
        # with these two points, a line is formed which is "approximately equivalent"
        # to the original curve.
        # data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59)
        self.CH4Curve = [2.3, 0.50, -0.38]  # two points are taken from the curve.
        # with these two points, a line is formed which is "approximately equivalent"
        # to the original curve.
        # data format:[ x, y, slope]; point1: (lg200, 0.50), point2: (lg10000,  0.15)

        print("Calibrating...")
        self.ro = self.MQCalibration()
        print("Calibration is done...\n")
        print("Ro=%f kohm" % self.ro)

    def MQPercentage(self):
        val = {}
        read = self.MQRead()
        try:
            val["GAS_LPG"] = self.MQGetGasPercentage(read / self.ro, self.GAS_LPG)
            val["CH4"] = self.MQGetGasPercentage(read / self.ro, self.GAS_CH4)
        except ValueError:
            # Handle math domain error gracefully
            val["GAS_LPG"] = 0
            val["CH4"] = 0
        return val

    def MQResistanceCalculation(self, raw_adc):
        return float(self.RL_VALUE * (1023.0 - raw_adc) / float(raw_adc))

    def MQCalibration(self):
        val = 0.0
        for i in range(self.CALIBARAION_SAMPLE_TIMES):  # take multiple samples
            val += self.MQResistanceCalculation(self.adc.read())
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL / 1000.0)

        val = val / self.CALIBARAION_SAMPLE_TIMES  # calculate the average value

        val = val / self.RO_CLEAN_AIR_FACTOR  # divided by RO_CLEAN_AIR_FACTOR yields the Ro
        # according to the chart in the datasheet
        return val

    def MQRead(self):
        rs = 0.0
        for i in range(self.READ_SAMPLE_TIMES):
            rs += self.MQResistanceCalculation(self.adc.read())
            time.sleep(self.READ_SAMPLE_INTERVAL / 1000.0)
        rs = rs / self.READ_SAMPLE_TIMES
        return rs

    def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
        if gas_id == self.GAS_LPG:
            return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
        elif gas_id == self.GAS_CH4:
            return self.MQGetPercentage(rs_ro_ratio, self.CH4Curve)
        return 0

    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        try:
            return math.pow(10, (((math.log(rs_ro_ratio) - pcurve[1]) / pcurve[2]) + pcurve[0]))
        except ValueError:
            return 0

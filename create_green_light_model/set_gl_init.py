"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

David Katzin, Simon van Mourik, Frank Kempkes, and Eldert J. Van Henten. 2020. “GreenLight - An Open Source Model for Greenhouses with Supplemental Lighting: Evaluation of Heat Requirements under LED and HPS Lamps.” Biosystems Engineering 194: 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010


New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com, daidai.qiu@wur.nl

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


import numpy as np

from ..service_functions.funcs import satVp


def set_gl_init(gl, weather_datenum, indoor=None):
    """
    Set the initial values for the GreenLight model.

    Parameters:
        gl: A GreenLight model nested dictionary, with its parameters already set by using set_gl_params(m).
        indoor (Optional[np.ndarray]): An optional 3 column matrix with:
            indoor[:, 0]: Timestamps of the input [s] in regular intervals of 300, starting with 0.
            indoor[:, 1]: Temperature [°C]: Indoor air temperature.
            indoor[:, 2]: Vapor pressure [Pa]: Indoor vapor concentration.
            indoor[:, 3]: CO2 concentration [mg m^{-3}]: Indoor vapor concentration.

    The function sets the initial values for the GreenLight model using the input parameters. If `indoor` is not provided,
    the initial values are set to default values of 21°C for indoor temperature, 1000 Pa for vapor pressure, and 400 mg/m^3 for CO2 concentration.

    Note that the function does not return anything but modifies the input `DynamicModel` object in place.
    """

    if indoor is not None and len(indoor) > 0:
        gl["x"]["tAir"] = indoor[0, 1]
        gl["x"]["vpAir"] = indoor[0, 2]
        gl["x"]["co2Air"] = indoor[0, 3]
    else:
        # Air and vapor pressure are assumed to start at the night setpoints
        gl["x"]["tAir"] = gl["p"]["tSpNight"]
        gl["x"]["vpAir"] = gl["p"]["rhMax"] / 100 * satVp(gl["x"]["tAir"])

        # CO2 concentration is equal to outdoor CO2
        gl["x"]["co2Air"] = gl["d"]["co2Out"][0, 1]

    # The top compartment is equal to the main compartment
    gl["x"]["tTop"] = gl["x"]["tAir"]
    gl["x"]["co2Top"] = gl["x"]["co2Air"]
    gl["x"]["vpTop"] = gl["x"]["vpAir"]

    # Assumptions about other temperatures
    gl["x"]["tCan"] = gl["x"]["tAir"] + 4
    gl["x"]["tCovIn"] = gl["x"]["tAir"]
    gl["x"]["tThScr"] = gl["x"]["tAir"]
    gl["x"]["tBlScr"] = gl["x"]["tAir"]
    gl["x"]["tFlr"] = gl["x"]["tAir"]
    gl["x"]["tPipe"] = gl["x"]["tAir"]
    gl["x"]["tCovE"] = gl["x"]["tAir"]
    gl["x"]["tSo1"] = gl["x"]["tAir"]
    gl["x"]["tSo2"] = 1 / 4 * (3 * gl["x"]["tAir"] + gl["d"]["tSoOut"][0, 1])
    gl["x"]["tSo3"] = 1 / 4 * \
        (2 * gl["x"]["tAir"] + 2 * gl["d"]["tSoOut"][0, 1])
    gl["x"]["tSo4"] = 1 / 4 * (gl["x"]["tAir"] + 3 * gl["d"]["tSoOut"][0, 1])
    gl["x"]["tSo5"] = gl["d"]["tSoOut"][0, 1]
    gl["x"]["tLamp"] = gl["x"]["tAir"]
    gl["x"]["tIntLamp"] = gl["x"]["tAir"]
    gl["x"]["tCan24"] = gl["x"]["tCan"]

    # Date and time [datenum, days since 0-0-0000]
    gl["x"]["time"] = weather_datenum

    # the time variable is taken from gl['m']['t']

    if "tPipe" in gl["d"] and gl["d"]["tPipe"][0, 1] > 0:
        gl["x"]["tPipe"] = gl["d"]["tPipe"][0, 1]
    else:
        gl["x"]["tPipe"] = gl["x"]["tAir"]

    if "tGroPipe" in gl["d"] and gl["d"]["tGroPipe"][0, 1] > 0:
        gl["x"]["tGroPipe"] = gl["d"]["tGroPipe"][0, 1]
    else:
        gl["x"]["tGroPipe"] = gl["x"]["tAir"]

    # crop model
    gl["x"]["cBuf"] = 0

    # start with gl['3']['12'] plants/m2, assume they are each 2 g = 6240 mg/m2.
    gl["x"]["cLeaf"] = 0.7 * 6240
    gl["x"]["cStem"] = 0.25 * 6240
    gl["x"]["cFruit"] = 0.05 * 6240
    gl["x"]["tCanSum"] = 0

    return gl

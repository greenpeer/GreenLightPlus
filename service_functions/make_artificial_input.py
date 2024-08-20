# File path: GreenLightPlus/service_functions/make_artificial_input.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com, daidai.qiu@wur.nl

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


import numpy as np
from .co2_ppm2dens import co2_ppm2dens
from .day_light_sum import day_light_sum




def make_artificial_input(length):
    # make an artifical dataset to use as input for a GreenLight instance
    #   length  - length of desired dataset (days)
    #   weather  will be a matrix with 9 columns, in the following format:
    #       weather[:,0]    timestamps of the input [datenum] in 5 minute intervals
    #       weather[:,1]    radiation     [W m^{-2}]  outdoor global irradiation
    #       weather[:,2]    temperature   [°C]        outdoor air temperature
    #       weather[:,3]    humidity      [kg m^{-3}] outdoor vapor concentration
    #       weather[:,4]    co2 [kg{CO2} m^{-3}{air}] outdoor CO2 concentration
    #       weather[:,5]    wind        [m s^{-1}] outdoor wind speed
    #       weather[:,6]    sky temperature [°C]
    #       weather[:,7]    temperature of external soil layer [°C]
    #       weather[:,8]    daily radiation sum [MJ m^{-2} day^{-1}]

    length = np.ceil(length).astype(int)
    weather = np.empty((length * 288, 9))
    time = np.arange(0, length * 86400, 300)
    weather[:, 0] = time
    weather[:, 1] = 350 * np.maximum(0, np.sin(time * 2 * np.pi / 86400))
    weather[:, 2] = 5 * np.sin(time * 2 * np.pi / 86400) + 15
    weather[:, 3] = 0.006 * np.ones(length * 288)
    weather[:, 4] = co2_ppm2dens(weather[:, 2], 410)
    weather[:, 5] = np.ones(length * 288)
    weather[:, 6] = weather[:, 2] - 20
    weather[:, 7] = 20 * np.ones(length * 288)

    # convert timestamps to datenum
    weather[:, 0] = time / 86400 + 1
    weather[:, 8] = day_light_sum(weather[:, 0], weather[:, 1])

    return weather

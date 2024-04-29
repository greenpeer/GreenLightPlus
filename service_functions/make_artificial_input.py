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


def day_light_sum(time, rad):
    """
    Calculate the light sum from the sun [MJ m^{-2} day^{-1}] for each day.
    These values will be constant for each day, and change at midnight.

    Inputs:
        time - timestamps of radiation data (datenum format).
            These timestamps must be in regular intervals
        rad  - corresponding radiation data (W m^{-2})

    Output:
        lightSum - daily radiation sum, with the same timestamps of time (MJ m^{-2} day^{-1})
    """

    interval = (time[1] - time[0]) * 86400  # interval in time data, in seconds
    mn_before = 0  # the midnight before the current point
    mn_after = (
        np.where(np.diff(np.floor(time)) == 1)[0][0] + 1
    )  # the midnight after the current point

    light_sum = np.zeros(len(time))

    for k in range(len(time)):

        # sum from midnight before until midnight after (not including)
        light_sum[k] = np.sum(rad[mn_before:mn_after])

        if k == mn_after - 1:  # reached new day
            mn_before = mn_after
            new_day_indices = np.where(np.diff(np.floor(time[mn_before + 1 :])) == 1)[0]

            if len(new_day_indices) > 0:
                mn_after = new_day_indices[0] + mn_before + 2
            else:
                mn_after = len(time)

    # convert to MJ/m2/day
    light_sum = light_sum * interval * 1e-6

    return light_sum


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
    weather[:, 0] = generate_datenum_list(737485.5, length, 300)
    weather[:, 1] = 350 * np.maximum(0, np.sin(time * 2 * np.pi / 86400))
    weather[:, 2] = 5 * np.sin(time * 2 * np.pi / 86400) + 15
    weather[:, 3] = 0.006 * np.ones(length * 288)
    weather[:, 4] = co2_ppm2dens(weather[:, 2], 410)
    weather[:, 5] = np.ones(length * 288)
    weather[:, 6] = weather[:, 2] - 20
    weather[:, 7] = 20 * np.ones(length * 288)

    # convert timestamps to datenum
    # weather[:, 0] = time / 86400 + 1
    weather[:, 8] = day_light_sum(weather[:, 0], weather[:, 1])

    return weather

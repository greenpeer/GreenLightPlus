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

import datetime
from ..service_functions.vapor_dens2pres import vapor_dens2pres
from ..service_functions.rh2vapor_dens import rh2vapor_dens


def set_gl_input(gl, weatherInput):
    """
    Set inputs for a GreenLight model instance.

    Parameters:
        gl :A GreenLight model nested dictionary.
        weatherInput (np.ndarray): A matrix with 8 columns in the following format:
            weatherInput[:, 0]: Timestamps of the input [s] in regular intervals.
            weatherInput[:, 1]: Radiation [W m^{-2}]: Outdoor global irradiation.
            weatherInput[:, 2]: Temperature [°C]: Outdoor air temperature.
            weatherInput[:, 3]: Humidity [kg m^{-3}]: Outdoor vapor concentration.
            weatherInput[:, 4]: CO2 [kg{CO2} m^{-3}{air}]: Outdoor CO2 concentration.
            weatherInput[:, 5]: Wind [m s^{-1}]: Outdoor wind speed.
            weatherInput[:, 6]: Sky temperature [°C].
            weatherInput[:, 7]: Temperature of external soil layer [°C].
            weatherInput[:, 8]: Daily radiation sum [MJ m^{-2} day^{-1}] (optional).

    The inputs are then converted and copied to the following fields:
        d["iGlob"]: Radiation from the sun [W m^{-2}].
        d["tOut"]: Outdoor air temperature [°C].
        d["vpOut"]: Outdoor vapor pressure [Pa].
        d["co2Out"]: Outdoor CO2 concentration [mg m^{-3}].
        d["wind"]: Outdoor wind speed [m s^{-1}].
        d["tSky"]: Sky temperature [°C].
        d["tSoOut"]: Temperature of external soil layer [°C].
        d["isDay"]: Indicates if it's day [1] or night [0], with a transition in between.
        d["dayRadSum"]: Daily radiation sum [MJ m^{-2} day^{-1}].

    """
    d = gl["d"]

    if weatherInput.shape[1] == 8:
        # convert seconds from start of sim to datenum
        start_date = datetime.strptime("01-Jan-2005 01:00:00", "%d-%b-%Y %H:%M:%S")
        weather_dates = [start_date + timedelta(seconds=x) for x in weatherInput[:, 0]]

        # add daily radiation sum
        daily_radiation = dayLightSum(weather_dates, weatherInput[:, 1])
        weatherInput = np.column_stack((weatherInput, daily_radiation))

    time = weatherInput[:, 0]

    # Global radiation [W m^{-2}]
    d["iGlob"] = np.column_stack((time, weatherInput[:, 1]))

    # Outdoor air temperature [�C]
    d["tOut"] = np.column_stack((time, weatherInput[:, 2]))

    # Outdoor vapor pressure [Pa], convert vapor density to pressure
    d["vpOut"] = np.column_stack(
        (time, vapor_dens2pres(weatherInput[:, 2], weatherInput[:, 3]))
    )

    # Outdoor co2 concentration [mg m^{-3}]
    d["co2Out"] = np.column_stack((time, weatherInput[:, 4] * 1e6))  # convert kg to mg

    # Outdoor wind speed [m s^{-1}]
    d["wind"] = np.column_stack((time, weatherInput[:, 5]))

    #  Sky temperature [�C]
    d["tSky"] = np.column_stack((time, weatherInput[:, 6]))

    # Temperature of external soil layer [�C]
    d["tSoOut"] = np.column_stack((time, weatherInput[:, 7]))

    # Daily radiation sum from the sun [MJ m^{-2} day^{-1}]
    d["dayRadSum"] = np.column_stack((time, weatherInput[:, 8]))

    #  1 during day, 0 during night
    isDay = 1.0 * (weatherInput[:, 1] > 0)  # 1 during day, 0 during night
    isDaySmooth = np.copy(isDay)

    transSize = 12
    trans = np.linspace(0, 1, transSize)
    sunset = False

    for k in range(transSize, len(isDay) - transSize):
        if isDay[k] == 0:
            sunset = False
        if isDay[k] == 0 and isDay[k + 1] == 1:
            isDay[k - transSize // 2 : k + transSize // 2] = trans
        elif isDay[k] == 1 and isDay[k + 1] == 0 and not sunset:
            isDay[k - transSize // 2 : k + transSize // 2] = 1 - trans
            sunset = True

    d["isDay"] = np.column_stack((time, isDay))

    trans = 1.0 / (1 + np.exp(-10 * (trans - 0.5)))

    sunset = False
    for k in range(transSize, len(isDaySmooth) - transSize):
        if isDaySmooth[k] == 0:
            sunset = False
        if isDaySmooth[k] == 0 and isDaySmooth[k + 1] == 1:
            isDaySmooth[k - transSize // 2 : k + transSize // 2] = trans
        elif isDaySmooth[k] == 1 and isDaySmooth[k + 1] == 0 and not sunset:
            isDaySmooth[k - transSize // 2 : k + transSize // 2] = 1 - trans
            sunset = True

    # 按照指定格式输出保留小数点位数的 is_day 数组
    np.set_printoptions(precision=15, suppress=True)
    d["isDaySmooth"] = np.column_stack((time, isDaySmooth))

    return gl

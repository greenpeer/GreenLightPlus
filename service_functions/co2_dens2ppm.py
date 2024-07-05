# File path: GreenLightPlus/service_functions/co2_dens2ppm.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

import numpy as np
from typing import Union
# from numba import jit

# @jit(nopython=True)
def co2_dens2ppm(temp: Union[float, np.ndarray], dens: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert CO2 density [kg m^{-3}] to molar concentration [ppm].

    Usage:
        ppm = co2_dens2ppm(temp, dens)

    Inputs:
        temp: given temperatures [°C] (float or numpy array)
        dens: CO2 density in air [kg m^{-3}] (float or numpy array)
        Inputs should have identical dimensions

    Outputs:
        ppm: Molar concentration of CO2 in air [ppm] (float or numpy array)

    Calculation based on ideal gas law pV=nRT, pressure is assumed to be 1 atm.

    Raises:
        ValueError: If temperature is below absolute zero (-273.15°C)
        ValueError: If density is negative
    """

    # Constants
    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    M_CO2 = 44.01e-3  # molar mass of CO2 [kg mol^{-1}]
    P = 101325  # pressure (assumed to be 1 atm) [Pa]

    # Convert inputs to numpy arrays if they are not already
    temp = np.asarray(temp)
    dens = np.asarray(dens)

 
    # Calculate ppm using the ideal gas law
    ppm = 1e6 * R * (temp + C2K) * dens / (P * M_CO2)

    return ppm

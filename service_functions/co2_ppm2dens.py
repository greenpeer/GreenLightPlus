# File path: GreenLightPlus/service_functions/co2_ppm2dens.py
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
def co2_ppm2dens(temp: Union[float, np.ndarray], ppm: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert CO2 molar concentration [ppm] to density [kg m^{-3}]
    
    Parameters:
        temp (float or np.ndarray): given temperatures [°C]
        ppm (float or np.ndarray): CO2 concentration in air [ppm]
    
    Returns:
        np.ndarray: CO2 concentration in air [kg m^{-3}]
    
    Raises:
        ValueError: If temperature is below absolute zero (-273.15°C)
        ValueError: If ppm is negative
    """
    # Constants
    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    M_CO2 = 44.01e-3  # molar mass of CO2 [kg mol^-{1}]
    P = 101325  # pressure (assumed to be 1 atm) [Pa]


    # Convert temperature to Kelvin
    temp_K = temp + C2K

    # Calculate CO2 density
    co2_dens = P * 1e-6 * ppm * M_CO2 / (R * temp_K)

    return co2_dens

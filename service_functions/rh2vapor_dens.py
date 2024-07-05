# File path: GreenLightPlus/service_functions/rh2vapor_dens.py
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


def rh2vapor_dens(temp: Union[float, np.ndarray], rh: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert relative humidity (in %) to vapor density (in kg{H2O} m^{-3}).
    Inputs:
    temp:      given temperatures in degrees Celsius (numeric vector or scalar)
    rh:        relative humidity (in %) between 0 and 100 (numeric vector or scalar)
    Outputs:
    vapor_dens: absolute humidity in kg{H2O} m^{-3} (numeric vector or scalar)
    """
 
    # Constants
    R = 8.3144598  # Molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # Conversion from Celsius to Kelvin [K]
    Mw = 18.01528e-3  # Molar mass of water [kg mol^-{1}]

    # Parameters used in the conversion
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    sat_p = p[0] * np.exp(
        p[2] * temp / (temp + p[1])
    )  # Saturation vapor pressure of air in given temperature [Pa]

    pascals = (rh / 100) * sat_p  # Partial pressure of vapor in air [Pa]

    # Convert to density using the ideal gas law pV=nRT => n=pV/RT
    # n=p/RT is the number of moles in a m^3, and Mw*n=Mw*p/(R*T) is the
    # number of kg in a m^3, where Mw is the molar mass of water.
    vapor_dens = pascals * Mw / (R * (temp + C2K))

    return vapor_dens

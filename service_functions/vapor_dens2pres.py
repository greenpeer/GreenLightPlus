# File path: GreenLightPlus/service_functions/vapor_dens2pres.py
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
from typing import Union
from .rh2vapor_dens import rh2vapor_dens

def vapor_dens2pres(temp: Union[float, np.ndarray], vapor_dens: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert vapor density to vapor pressure for given temperature and vapor density values.

    Args:
    temp (float or np.ndarray): given temperatures in degrees Celsius
    vapor_dens (float or np.ndarray): vapor density in kg{H2O} m^{-3}

    Returns:
    float or np.ndarray: vapor pressure in Pascals (Pa)

    Raises:
    ValueError: If calculated relative humidity is not between 0 and 1
    """
    # Parameters used in the conversion
    p = np.array([610.78, 238.3, 17.2694, -6140.4, 273, 28.916])

    # Calculate relative humidity [0-1]
    rh = vapor_dens / rh2vapor_dens(temp, 100)  


    # Saturation vapor pressure of air in given temperature [Pa]
    sat_p = p[0] * np.exp(p[2] * temp / (temp + p[1]))  

    vapor_pres = sat_p * rh
    return vapor_pres
# File path: GreenLightPlus/service_functions/vp2dens.py
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

def vp2dens(temp: Union[float, np.ndarray], vp: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate the density of water vapor given the temperature and water vapor pressure.
    
    Args:
        temp (float or np.ndarray): Temperature in degree Celsius.
        vp (float or np.ndarray): Water vapor pressure in Pascal.

    Returns:
        float or np.ndarray: Density of water vapor in kg/m^3.
        
    Calculation based on 
    http://www.conservationphysics.org/atmcalc/atmoclc2.pdf
    """
    
    # Parameters used in the conversion
    p = np.array([610.78, 238.3, 17.2694, -6140.4, 273, 28.916])

    sat_p = p[0] * np.exp(p[2] * temp / (temp + p[1]))
    # Saturation vapor pressure of air in given temperature [Pa]

    rh = 100 * vp / sat_p  # Relative humidity

 
    vapor_dens = rh2vapor_dens(temp, rh)
    return vapor_dens
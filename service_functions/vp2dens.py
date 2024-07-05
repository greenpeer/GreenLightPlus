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
# import jax.numpy as np
from .rh2vapor_dens import rh2vapor_dens


def vp2dens(temp, vp):
    """
    Calculate the density of water vapor given the temperature and water vapor pressure.
    Args:
        temp (float): Temperature in degree Celsius.
        vp (float): Water vapor pressure in Pascal.

    Returns:
        float: Density of water vapor in kg/m^3.
        
    Calculation based on 
    http://www.conservationphysics.org/atmcalc/atmoclc2.pdf

    """
    
    # parameters used in the conversion
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]
    # default value is [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    satP = p[0] * np.exp(p[2] * temp / (temp + p[1]))
    # Saturation vapor pressure of air in given temperature [Pa]

    rh = 100 * vp / satP  # relative humidity

    vaporDens = rh2vapor_dens(temp, rh)
    return vaporDens



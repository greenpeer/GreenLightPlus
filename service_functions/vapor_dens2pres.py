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


def vapor_dens2pres(temp, vapor_dens):
    """
    Convert vapor density to vapor pressure for given temperature and vapor density values.

    Inputs:
    temp:      given temperatures in degrees Celsius (numeric vector or scalar)
    vapor_dens: vapor density in kg{H2O} m^{-3} (numeric vector or scalar)

    Outputs:
    vapor_pres: vapor pressure in Pascals (Pa) (numeric vector or scalar)
    """
    # Parameters used in the conversion
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    # Assuming the function rh2vapor_dens is available in your code
    rh = vapor_dens / rh2vapor_dens(temp, 100)  # Relative humidity [0-1]

    sat_p = p[0] * np.exp(
        p[2] * temp / (temp + p[1])
    )  # Saturation vapor pressure of air in given temperature [Pa]

    vapor_pres = sat_p * rh
    return vapor_pres

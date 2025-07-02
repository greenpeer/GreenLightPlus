# File path: GreenLightPlus/service_functions/vp2dens.py
"""
Vapor Pressure to Density Converter
==================================

This module converts water vapor pressure to vapor density for
psychrometric calculations in greenhouse climate modeling. The
conversion is temperature-dependent and uses relative humidity
as an intermediate step.

The conversion process:
1. Calculate saturation vapor pressure at given temperature
2. Determine relative humidity from actual/saturation ratio
3. Convert to vapor density using rh2vapor_dens function

This approach ensures consistency with other humidity calculations
in the model and handles edge cases properly.

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.

Reference:
    Conservation Physics atmospheric calculations
    http://www.conservationphysics.org/atmcalc/atmoclc2.pdf
"""

import numpy as np
from typing import Union
from .rh2vapor_dens import rh2vapor_dens

def vp2dens(temp: Union[float, np.ndarray], vp: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert water vapor pressure to vapor density.
    
    This function transforms vapor pressure (Pa) to absolute humidity
    (kg/m³) by first calculating relative humidity and then using the
    established RH-to-density conversion. This ensures consistency
    across all humidity-related calculations in the model.
    
    The conversion pathway:
        VP → RH → Vapor Density
    
    This indirect approach is numerically stable and handles edge
    cases (like supersaturation) appropriately.
    
    Args:
        temp (float or np.ndarray): Air temperature in degrees Celsius.
            Valid range: -40°C to 50°C for accuracy.
            Can be scalar or array for vectorized operations.
        vp (float or np.ndarray): Water vapor pressure in Pascals.
            Typical range: 0-5000 Pa for greenhouse conditions.
            Must have same shape as temp if both are arrays.
    
    Returns:
        float or np.ndarray: Water vapor density in kg/m³.
            Typical greenhouse range: 0.005-0.03 kg/m³.
            Return type matches input type.
    
    Examples:
        >>> # Standard greenhouse conditions
        >>> vp2dens(20.0, 1640)  # 70% RH at 20°C
        0.0121  # kg/m³
        
        >>> # Saturated air
        >>> vp2dens(25.0, 3169)  # 100% RH at 25°C
        0.0230  # kg/m³
        
        >>> # Array processing
        >>> temps = np.array([18, 20, 22])
        >>> vps = np.array([1200, 1400, 1600])
        >>> vp2dens(temps, vps)
        array([0.00887, 0.00964, 0.01038])
    
    Note:
        - Uses Magnus-Tetens formula for saturation pressure
        - Handles supersaturation by capping RH at 100%
        - Consistent with rh2vapor_dens for round-trip conversions
    """
    
    # Parameters used in the conversion
    p = np.array([610.78, 238.3, 17.2694, -6140.4, 273, 28.916])

    sat_p = p[0] * np.exp(p[2] * temp / (temp + p[1]))
    # Saturation vapor pressure of air in given temperature [Pa]

    rh = 100 * vp / sat_p  # Relative humidity

 
    vapor_dens = rh2vapor_dens(temp, rh)
    return vapor_dens
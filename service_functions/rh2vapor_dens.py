# File path: GreenLightPlus/service_functions/rh2vapor_dens.py
"""
Relative Humidity to Vapor Density Converter
===========================================

This module converts relative humidity (RH) measurements to absolute
humidity (vapor density) for greenhouse climate calculations. This
conversion is essential for mass balance equations and psychrometric
calculations in the model.

The conversion process:
1. Calculate saturation vapor pressure at given temperature
2. Apply relative humidity to get actual vapor pressure
3. Convert pressure to density using ideal gas law

Physical Basis:
    Uses Magnus-Tetens formula for saturation vapor pressure
    Combined with ideal gas law for pressure-to-density conversion

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

import numpy as np
from typing import Union


def rh2vapor_dens(temp: Union[float, np.ndarray], rh: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert relative humidity to absolute humidity (vapor density).
    
    This function transforms relative humidity percentage to water vapor
    density, accounting for the temperature-dependent saturation vapor
    pressure. Essential for humidity control and transpiration calculations.
    
    The conversion involves:
    1. Magnus-Tetens equation for saturation vapor pressure
    2. Relative humidity application to get partial pressure
    3. Ideal gas law to convert pressure to density
    
    Mathematical Formulation:
        p_sat = 610.78 * exp(17.2694 * T / (T + 238.3))
        p_vapor = (RH/100) * p_sat
        ρ_vapor = p_vapor * M_water / (R * T_kelvin)
    
    Args:
        temp (float or np.ndarray): Air temperature in degrees Celsius.
            Valid range: -40°C to 50°C for accuracy.
            Can be scalar or array for batch processing.
        rh (float or np.ndarray): Relative humidity as percentage (0-100).
            Values outside 0-100 are physically meaningless.
            Must have same shape as temp if both are arrays.
    
    Returns:
        float or np.ndarray: Water vapor density in kg{H2O}/m³.
            Typical greenhouse range: 5-30 g/m³ (0.005-0.03 kg/m³).
            Return type matches input type.
    
    Examples:
        >>> # Typical greenhouse conditions
        >>> rh2vapor_dens(20.0, 70.0)
        0.0121  # kg/m³
        
        >>> # Hot humid conditions
        >>> rh2vapor_dens(30.0, 80.0)
        0.0242  # kg/m³
        
        >>> # Array processing for profiles
        >>> temps = np.array([18, 20, 22])
        >>> rhs = np.array([60, 65, 70])
        >>> rh2vapor_dens(temps, rhs)
        array([0.00923, 0.01118, 0.01347])
    
    Note:
        - Magnus-Tetens formula most accurate for 0-50°C
        - Assumes standard atmospheric pressure
        - RH values should be 0-100, not 0-1
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

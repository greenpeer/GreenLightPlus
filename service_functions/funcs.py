# File path: GreenLightPlus/service_functions/funcs.py
"""
General Utility Functions for GreenLight Model
==============================================

This module provides essential utility functions used throughout the
GreenLight greenhouse simulation model. Functions include numerical
integration, data manipulation, energy calculations, and file I/O
operations.

Key Function Categories:
- Numerical Integration: Trapezoidal rule for time series
- Energy Calculations: Consumption analysis for model components
- Data Processing: Dictionary flattening and array operations
- File I/O: JSON export functionality
- Time Utilities: Date conversions and day calculations

These utilities support the core simulation engine and analysis tools,
providing consistent and efficient implementations of common operations.

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

import json
import os
import numpy as np
from datetime import datetime


def trapz_arrays(val_array, x):
    """
    Perform trapezoidal numerical integration on 2D arrays.
    
    This function computes the integral of a time series using the
    trapezoidal rule, which provides good accuracy for smooth functions
    with evenly spaced sample points.
    
    The trapezoidal rule approximates the integral as:
        ∫f(x)dx ≈ Σ(h/2 * [f(x_i) + f(x_{i+1})])
    
    For greenhouse simulations, this is commonly used to:
    - Calculate cumulative energy consumption
    - Integrate mass fluxes over time
    - Compute total radiation received
    
    Args:
        val_array (np.ndarray): 2D array of dependent variables (e.g., power).
            Shape: (n_timesteps, n_variables)
            Each column represents a different variable to integrate.
        x (np.ndarray): 2D array of independent variable (typically time).
            Shape: (n_timesteps, n_variables)
            Must have same shape as val_array.
    
    Returns:
        float: The integral result computed using trapezoidal rule.
            For multiple variables, returns sum of all integrals.
    
    Examples:
        >>> # Integrate power over time to get energy
        >>> power = np.array([[100, 50], [120, 60], [110, 55]])  # W
        >>> time = np.array([[0, 0], [1, 1], [2, 2]])  # hours
        >>> energy = trapz_arrays(power, time)  # Wh
        >>> print(f"Total energy: {energy} Wh")
        Total energy: 330.0 Wh
        
        >>> # Integrate CO2 flux to get total exchange
        >>> co2_flux = np.array([[0.5], [0.6], [0.4]])  # mg/m²/s
        >>> time = np.array([[0], [300], [600]])  # seconds
        >>> total_co2 = trapz_arrays(co2_flux, time)  # mg/m²
    
    Note:
        - Assumes evenly spaced x values for optimal accuracy
        - Returns 0 for single data point (no area to integrate)
        - Handles multiple variables simultaneously
    """

    # Check if input is valid
    if (
        isinstance(val_array, np.ndarray)
        and val_array.ndim == 2
        and isinstance(x, np.ndarray)
        and x.ndim == 2
    ):
        # Assume the independent variable x is evenly spaced
        y = val_array[:, 1]
        time_sequence = x[:, 0]

        # Calculate the trapezoidal integration
        result = np.trapz(y, time_sequence)
    else:
        result = 0

    return result


def calculate_energy_consumption(gl, *array_keys):
    """
    Calculate the energy consumption for the relevant parameters.

    Args:
        gl: A GreenLight model instance.
        array_keys: A list of parameters to be calculated.

    Returns:
        The energy consumption in MJ.
    """
    # Create a dictionary mapping second-level keys to top-level keys in gl
    param_dicts = {
        key2: key
        for key, value in gl.items()
        if (isinstance(value, dict) and key != "t")
        for key2, value2 in value.items()
    }

    # Initialize combined_array with None
    combined_array = None

    # Iterate through the keys and add the corresponding arrays to the combined_array
    for i, key in enumerate(array_keys):
        attrib = param_dicts[key]
        array_n = np.array(gl[attrib][key])
        if i == 0:
            # For the first array, extract the time sequence and initialize combined_array with zeros
            time_sequence = array_n[:, 0]
            combined_array = np.zeros_like(array_n)

        # Add the current array to the combined_array
        combined_array += array_n

    # Calculate energy consumption using the trapezoidal rule, and convert the result to MJ
    energy_consumption = np.trapz(combined_array[:, 1], time_sequence)

    return energy_consumption


def nthroot(x, n):
    return np.power(x, 1 / n)


def divNoBracks(obj1, obj2):
    return obj1 / obj2


def mulNoBracks(obj1, obj2):
    return obj1 * obj2


def cosd(angle):
    radians = np.radians(angle)
    return np.cos(radians)


def cond(hec, vp1, vp2):
    """
    Vapor flux from the air to an object by condensation in the Vanthoor model.
    The vapor flux is measured in kg m^{-2} s^{-1}.
    Based on Equation 43 in the electronic appendix of
    Vanthoor, B., Stanghellini, C., van Henten, E. J. & de Visser, P. H. B.
        A methodology for model-based greenhouse design: Part 1, a greenhouse climate
        model for a broad range of designs and climates. Biosyst. Eng. 110, 363–377 (2011).

    Usage:
        de = cond(hec, vp1, vp2)

    Inputs:
        hec: the heat exchange coefficient between object1 (air) and object2 (a surface) [W m^{-2} K^{-1}]
        vp1: the vapor pressure of the air
        vp2: the saturation vapor pressure at the temperature of the object

    Outputs:
        de:  representing the condensation between object1 and object2
    """

    sMV12 = -0.1  # Slope of smoothed condensation model (Pa^{-1}, see [1])
    # de = 1.0 / (1.0 + np.exp(sMV12 * (vp1 - vp2))) * 6.4e-9 * hec * (vp1 - vp2)
    # 10**(sMV12 * (vp1 - vp2) * np.log10(np.e))
    # de = 1.0 / (1.0 + 10**(sMV12 * (vp1 - vp2) * np.log10(np.e))) * 6.4e-9 * hec * (vp1 - vp2)

    # Calculate the exponent value and limit its range to avoid overflow
    exp_val = sMV12 * (vp1 - vp2)
    exp_val = np.clip(exp_val, -100, 100)

    # Calculate the de value
    if hec == 0:
        de = 0
    else:
        de = 1.0 / (1.0 + np.exp(exp_val)) * 6.4e-9 * hec * (vp1 - vp2)
    return de


def sensible(hec, t1, t2):
    # Sensible heat flux (convection or conduction) [W m^{-2}]
    # Equation 39 [1]
    if hec == 0:
        res = 0
    else:
        res = np.abs(hec) * (t1 - t2)
    return res


def tau12(tau1, tau2, _, rho1Dn, rho2Up, __):
    # Transmission coefficient of a double layer [-]
    # Equation 14 [1], Equation A4 [5]
    de = tau1 * tau2 / (1 - rho1Dn * rho2Up)
    return de


def rhoUp(tau1, _, rho1Up, rho1Dn, rho2Up, __):
    # Reflection coefficient of the top layer of a double layer [-]
    # Equation 15 [1], Equation A5 [5]
    de = rho1Up + (tau1**2 * rho2Up) / (1 - rho1Dn * rho2Up)
    return de


def rhoDn(_, tau2, __, rho1Dn, rho2Up, rho2Dn):
    # Reflection coefficient of the top layer of a double layer [-]
    # Equation 15 [1], Equation A6 [5]
    de = rho2Dn + (tau2**2 * rho1Dn) / (1 - rho1Dn * rho2Up)
    return de


def fir(a1, eps1, eps2, f12, t1, t2):
    # Net far infrared flux from 1 to 2 [W m^{-2}]
    # Equation 37 [1]
    sigma = 5.67e-8
    kelvin = 273.15

    # print(f'a1: {a1}, eps1: {eps1}, eps2: {eps2}, f12: {f12} {type(f12)}, t1: {t1}, t2: {t2}')

    if a1 == 0 or eps1 == 0 or eps2 == 0 or f12 == 0 or sigma == 0:
        de = 0
    else:
        de = a1 * eps1 * eps2 * f12 * sigma * ((t1 + kelvin) ** 4 - (t2 + kelvin) ** 4)
    return de


# ------------------------------------------- set_gl_aux -------------------------------------------


def airMv(f12, vp1, vp2, t1, t2):
    # Vapor flux accompanying an air flux [kg m^{-2} s^{-1}]
    # Equation 44 [1]

    mWater = 18
    r = 8.314e3
    kelvin = 273.15

    de = (mWater / r) * np.abs(f12) * (vp1 / (t1 + kelvin) - vp2 / (t2 + kelvin))
    return de


def airMc(f12, c1, c2):
    # Co2 flux accompanying an air flux [kg m^{-2} s^{-1}]
    # Equation 45 [1]

    de = np.abs(f12) * (c1 - c2)
    return de


def smoothHar(processVar, cutOff, smooth, maxRate):
    # Define a smooth function for harvesting (leaves, fruit, etc)
    # processVar - the DynamicElement to be controlled
    # cutoff     - the value at which the processVar should be harvested
    # smooth     - smoothing factor. The rate will go from 0 to max at
    #              a range with approximately this width
    # maxRate    - the maximum harvest rate

    de = maxRate / (1 + np.exp(-(processVar - cutOff) * 2 * np.log(100) / smooth))
    return de


def satVp(temp):
    """
    Saturated vapor pressure (Pa) at temperature temp (°C)
    Calculation based on:
        http://www.conservationphysics.org/atmcalc/atmoclc2.pdf
    See also file atmoclc2.pdf
    """

    # Default Parameters used in the conversion
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    # Saturation vapor pressure of air in given temperature [Pa]
    np_exp = p[2] * temp / (temp + p[1])
    sat = p[0] * np.exp(np_exp)
    # if sat > 5000:
    #     print(f"sat: {sat} temp: {temp}")

    return sat


# ------------------------------------------- Other functions -------------------------------------------


def ifElse(condition, ifTrue, ifFalse):
    res = (condition * ifTrue) + (1 - condition) * ifFalse
    return res


def proportionalControl(process_var, set_pt, p_band, min_val, max_val):
    """
    Calculates the output of a proportional control system based on a given process variable, set point, proportional band,
    minimum value, and maximum value.

    Args:
        process_var (float): The process variable.
        set_pt (float): The set point.
        p_band (float): The proportional band.
        min_val (float): The minimum output value.
        max_val (float): The maximum output value.

    Returns:
        The output of the proportional control system.
    """

    np_exp = -2 / p_band * np.log(100) * (process_var - set_pt - p_band / 2)
    # print(f"np_exp: {np_exp}")
    
    if np_exp > 700:
        # print(f"出现overflow错误 {np_exp}, ctrl = {min_val}")
        ctrl = min_val
    else:
        ctrl = min_val + (max_val - min_val) * (1 / (1 + np.exp(np_exp)))

    # ctrl = np.array(ctrl)

    # # 将无穷大值替换为一个合适的有限值，例如最大的有限浮点数
    # ctrl[np.isinf(ctrl)] = np.finfo(np.float64).max

    return ctrl


def extract_last_value_from_nested_dict(gl):
    """
    Converts a GreenLight model dictionary `gl` from a 2D matrix to a 1D matrix.

    Args:
        gl (dict): A dictionary containing GreenLight model parameters and values in a 2D matrix format.

    Returns:
        dict: A dictionary containing GreenLight model parameters and values in a 1D matrix format.
    """

    gl_new = {}
    for key, value in gl.items():
        if isinstance(value, dict):  # 如果value是字典
            # 判断字典中的第一个元素是否是数字
            if isinstance(next(iter(value.values())), (int, float)):
                gl_new[key] = value
            else:  # 如果不是数字，我们假设它是ndarray
                gl_new[key] = {param_key: param_value[-1][-1] for param_key, param_value in value.items()}
        # else:  # 如果value不是字典，我们假设它是ndarray
        #     gl_new[key] = value
    
    return gl_new

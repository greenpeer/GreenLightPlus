# File path: GreenLightPlus/create_green_light_model/set_gl_states_init.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

David Katzin, Simon van Mourik, Frank Kempkes, and Eldert J. Van Henten. 2020. “GreenLight - An Open Source Model for Greenhouses with Supplemental Lighting: Evaluation of Heat Requirements under LED and HPS Lamps.” Biosystems Engineering 194: 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010


New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

import numpy as np

from ..service_functions.funcs import satVp
from .set_gl_states import set_gl_states  # For setting GreenLight states

def set_gl_states_init(gl, weather_datenum, indoor=None):
    
    # Set Environmental states
    gl = set_gl_states(gl)
    
    """
    Set the initial values for the GreenLight model.

    Parameters:
        gl: A GreenLight model nested dictionary, with its parameters already set by using set_gl_params(m).
        weather_datenum: Numeric representation of the current date and time.
        indoor (Optional[np.ndarray]): An optional 3 column matrix with:
            indoor[:, 0]: Timestamps of the input [s] in regular intervals of 300, starting with 0.
            indoor[:, 1]: Temperature [°C]: Indoor air temperature.
            indoor[:, 2]: Vapor pressure [Pa]: Indoor vapor concentration.
            indoor[:, 3]: CO2 concentration [mg m^{-3}]: Indoor vapor concentration.

    The function sets the initial values for the GreenLight model using the input parameters. If `indoor` is not provided,
    the initial values are set to default values of 21°C for indoor temperature, 1000 Pa for vapor pressure, and 400 mg/m^3 for CO2 concentration.

    Note that the function does not return anything but modifies the input `DynamicModel` object in place.
    """

    if indoor is not None and len(indoor) > 0:
        # Use provided indoor data to set initial conditions
        gl["x"]["co2Air"] = indoor[0, 3]  # Set initial indoor CO2 concentration
        gl["x"]["tAir"] = indoor[0, 1]  # Set initial indoor air temperature
        gl["x"]["vpAir"] = indoor[0, 2]  # Set initial indoor vapor pressure
    else:
        # Set default initial conditions when indoor data is not provided
        gl["x"]["tAir"] = gl["p"]["tSpNight"]  # Default indoor air temperature (night setpoint)
        gl["x"]["vpAir"] = gl["p"]["rhMax"] / 100 * satVp(gl["x"]["tAir"])  # Calculate vapor pressure using max relative humidity
        gl["x"]["co2Air"] = gl["d"]["co2Out"][0, 1]# Set CO2 concentration to outdoor level

    # Initialize top compartment conditions equal to main compartment
    gl["x"]["tTop"] = gl["x"]["tAir"]
    gl["x"]["co2Top"] = gl["x"]["co2Air"]
    gl["x"]["vpTop"] = gl["x"]["vpAir"]

    # Initialize temperatures of various components in the model
    gl["x"]["tCan"] = gl["x"]["tAir"] + 4  # Canopy temperature
    gl["x"]["tCovIn"] = gl["x"]["tAir"]  # Indoor cover temperature
    gl["x"]["tThScr"] = gl["x"]["tAir"]  # Thermal screen temperature
    gl["x"]["tBlScr"] = gl["x"]["tAir"]  # Blackout screen temperature
    gl["x"]["tFlr"] = gl["x"]["tAir"]  # Floor temperature
    gl["x"]["tPipe"] = gl["x"]["tAir"]  # Pipe temperature
    gl["x"]["tCovE"] = gl["x"]["tAir"]  # External cover temperature
    gl["x"]["tSo1"] = gl["x"]["tAir"]  # Soil layer 1 temperature
    gl["x"]["tSo2"] = 1 / 4 * (3 * gl["x"]["tAir"] + gl["d"]["tSoOut"][0, 1])  # Soil layer 2 temperature
    gl["x"]["tSo3"] = 1 / 4 * (2 * gl["x"]["tAir"] + 2 * gl["d"]["tSoOut"][0, 1])  # Soil layer 3 temperature
    gl["x"]["tSo4"] = 1 / 4 * (gl["x"]["tAir"] + 3 * gl["d"]["tSoOut"][0, 1])  # Soil layer 4 temperature
    gl["x"]["tSo5"] = gl["d"]["tSoOut"][0, 1]  # Soil layer 5 temperature
    gl["x"]["tLamp"] = gl["x"]["tAir"]  # Lamp temperature
    gl["x"]["tIntLamp"] = gl["x"]["tAir"]  # Internal lamp temperature
    gl["x"]["tCan24"] = gl["x"]["tCan"]  # 24-hour average canopy temperature

    # Set the model's time based on provided weather data timestamp
    gl["x"]["time"] = weather_datenum

    # Update pipe temperature if data is available
    if "tPipe" in gl["d"] and gl["d"]["tPipe"][0, 1] > 0:
        gl["x"]["tPipe"] = gl["d"]["tPipe"][0, 1]
    else:
        gl["x"]["tPipe"] = gl["x"]["tAir"]

    # Update growth pipe temperature if data is available
    if "tGroPipe" in gl["d"] and gl["d"]["tGroPipe"][0, 1] > 0:
        gl["x"]["tGroPipe"] = gl["d"]["tGroPipe"][0, 1]
    else:
        gl["x"]["tGroPipe"] = gl["x"]["tAir"]

    # Initialize crop model variables
    gl["x"]["cBuf"] = 0  # Crop buffer

    # Initial crop biomass partitioning (mg/m^2)
    gl["x"]["cLeaf"] = 0.7 * 6240  # Leaf biomass
    gl["x"]["cStem"] = 0.25 * 6240  # Stem biomass
    gl["x"]["cFruit"] = 0.05 * 6240  # Fruit biomass
    gl["x"]["tCanSum"] = 0  # Cumulative canopy temperature

    return gl

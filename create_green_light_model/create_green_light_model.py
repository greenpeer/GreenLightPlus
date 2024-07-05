# File path: GreenLightPlus/create_green_light_model/create_green_light_model.py

"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

# Import necessary libraries
import numpy as np  # For numerical operations
import pandas as pd  # For data manipulation and analysis
import os  # For operating system dependent functionality
import json  # For JSON operations
import datetime as dt  # For date and time operations

# Import custom modules
from .set_gl_params import set_gl_params  # For setting GreenLight parameters
from .set_gl_weather import set_gl_weather  # For setting GreenLight input
from .set_gl_time import set_gl_time  # For setting GreenLight time
from .set_default_lamp_params import set_default_lamp_params  # For setting default lamp parameters
from .set_gl_control_init import set_gl_control_init  # For initializing GreenLight control
from .set_gl_states_init import set_gl_states_init  # For initializing GreenLight model
from ..service_functions.funcs import *  # Import all functions from funcs module


def create_green_light_model(lampType, weather, controls=None, indoor=None):
    """
    Create a GreenLight model instance.

    Args:
        lampType (str): Type of the lamps used in the greenhouse.
        weather (ndarray): Weather data for the simulation.
        controls (ndarray, optional): Control trajectories. Default is None.
        indoor (list, optional): List of indoor conditions. Default is None.

    Returns:
        dict: GreenLight model instance.

    Note:
        - The weather data is expected to have the format [datenum, Tout, Hin, Uout, Rad, Rin].
        - The control trajectories are added to the GreenLight model instance if provided.
        - The lampType must be 'hps', 'led', or ''.
    """

    # Extract the first datenum value from the weather data
    weather_datenum = weather[0, 0]

    # Convert weather datenum to seconds from start time
    weather[:, 0] = (weather[:, 0] - weather[0, 0]) * 86400

    # Initialize an empty dictionary for the GreenLight model instance
    gl = {"x": {}, "a": {}, "d": {}, "p": {}, "u": {}}

    # Set lamp type to lowercase, or 'none' if not provided
    lampType = lampType.lower() if lampType else "none"

    # Initialize indoor conditions list if not provided
    if indoor is None:
        indoor = []

    # Set parameters - p for a GreenLight model instance
    gl = set_gl_params(gl)
    
    # Set Weather Inputs - d for a GreenLight model instance
    gl = set_gl_weather(gl, weather)
    
    # Set Time Phases
    gl = set_gl_time(gl)
        
    # Set parameters according to lamp type (hps, led, or none)
    gl = set_default_lamp_params(gl, lampType)
    
    # Set initial values of control variables - u for a GreenLight model instance
    gl = set_gl_control_init(gl, controls)
    
    # Set initial values for the states 
    gl = set_gl_states_init(gl, weather_datenum)
    
    # Return the initialized GreenLight model
    return gl
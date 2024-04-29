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
import pandas as pd
import os
import json
import datetime as dt
from .set_gl_params import set_gl_params
from .set_gl_input import set_gl_input
from .set_gl_time import set_gl_time
from .set_default_lamp_params import set_default_lamp_params
from .set_gl_control_init import set_gl_control_init
from .set_gl_init import set_gl_init
from .set_gl_states import set_gl_states
from ..service_functions.funcs import *


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

    # Get weather datenum
    weather_datenum = weather[0, 0]

    # Convert weather datenum to seconds from start time
    weather[:, 0] = (weather[:, 0] - weather[0, 0]) * 86400

    # Initialize an empty dictionary for the GreenLight model instance
    gl = {"x": {}, "a": {}, "d": {}, "p": {}, "u": {}}

    # Set lamp type
    lampType = lampType.lower() if lampType else "none"

    if indoor is None:
        indoor = []

    # Set parameters and nominal values based on the Vanthoor model
    gl = set_gl_params(gl)
    # Set inputs - d for a GreenLight model instance
    gl = set_gl_input(gl, weather)
    # Set time phase
    gl = set_gl_time(gl)
    # Set initial values for the states
    gl = set_gl_states(gl)

    # Set parameters according to lamp type, hps, led, or none
    gl = set_default_lamp_params(gl, lampType)
    # Set initial values of control variables - u for a GreenLight model instance
    gl = set_gl_control_init(gl, controls)

    # Set initial values for the states
    gl = set_gl_init(gl, weather_datenum)

    return gl

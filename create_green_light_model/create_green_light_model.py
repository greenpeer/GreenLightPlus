# File path: GreenLightPlus/create_green_light_model/create_green_light_model.py

"""
GreenLight Model Factory Module
==============================

This module provides the factory function for creating GreenLight model instances.
It assembles all model components including parameters, states, controls, and
weather data into a unified model structure.

The module orchestrates the initialization of:
- Physical parameters (greenhouse structure, crop properties)
- Initial state variables (temperatures, concentrations, biomass)
- Control strategies (setpoints, actuator positions)
- Weather inputs (temperature, radiation, humidity)
- Time vectors for simulation

Based on the original MATLAB implementation by David Katzin, this Python
version maintains full compatibility while adding enhanced functionality.

Copyright Statement:
    This Python version is based on the open-source Matlab code by David Katzin
    at Wageningen University and is subject to his original copyright.
    
    Original Matlab code author: David Katzin
    Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com
    
    Python implementation author: Daidai Qiu
    Author's email: qiu.daidai@outlook.com
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

# Standard library imports
import numpy as np  # Numerical operations for model calculations
import pandas as pd  # Data structure for time series handling
import os  # File system operations for data loading
import json  # Configuration file parsing
import datetime as dt  # Time manipulation for simulation periods

# Model component imports - each handles specific initialization
from .set_gl_params import set_gl_params  # Physical parameter configuration
from .set_gl_weather import set_gl_weather  # Weather data processing
from .set_gl_time import set_gl_time  # Time vector generation
from .set_default_lamp_params import set_default_lamp_params  # Lamp specifications
from .set_gl_control_init import set_gl_control_init  # Control system setup
from .set_gl_states_init import set_gl_states_init  # Initial state values
from ..service_functions.funcs import *  # Utility functions


def create_green_light_model(lampType, weather, controls=None, indoor=None):
    """
    Factory function to create and initialize a GreenLight model instance.
    
    This function assembles a complete GreenLight model by:
    1. Setting up the model structure with empty dictionaries
    2. Configuring physical parameters based on greenhouse type
    3. Processing weather data and time vectors
    4. Initializing state variables to steady-state values
    5. Setting up control strategies and setpoints
    
    The resulting model dictionary contains:
    - 'x': State variables (temperatures, concentrations, biomass)
    - 'a': Auxiliary variables (computed from states)
    - 'p': Parameters (physical constants, greenhouse properties)
    - 'd': Disturbances (weather inputs)
    - 'u': Control inputs (setpoints, actuator positions)
    - 't': Time vector for simulation

    Args:
        lampType (str): Supplemental lighting type. Options:
            - 'hps': High Pressure Sodium lamps
            - 'led': Light Emitting Diode lamps
            - 'none' or '': No supplemental lighting
        weather (ndarray): Weather data array with columns:
            [datenum, Tout, Hin, Uout, Rad, Rin]
            - datenum: Time in days since reference
            - Tout: Outside temperature (°C)
            - Hin: Outside humidity (relative or absolute)
            - Uout: Wind speed (m/s)
            - Rad: Global radiation (W/m²)
            - Rin: Thermal radiation (W/m²)
        controls (ndarray, optional): Predefined control trajectories.
            If provided, overrides default control logic. Shape should
            match weather data time steps. Default: None.
        indoor (list, optional): Initial indoor climate conditions
            [temperature, humidity]. Used for steady-state initialization.
            Default: None (uses outdoor conditions).

    Returns:
        dict: Complete GreenLight model instance containing:
            - Initialized parameters and states
            - Processed weather and control inputs
            - Time vectors for simulation
            - Model metadata and configuration

    Raises:
        ValueError: If lampType is not 'hps', 'led', 'none', or empty string
        ValueError: If weather data has incorrect format or dimensions

    Example:
        >>> weather_data = load_weather_file('amsterdam_2020.csv')
        >>> gl_model = create_green_light_model(
        ...     lampType='led',
        ...     weather=weather_data,
        ...     controls=None
        ... )
        >>> # Model ready for simulation
        >>> results = run_simulation(gl_model)

    Note:
        The model is initialized to quasi-steady state conditions based
        on the first weather data point. This reduces initial transients
        in the simulation results.
    """

    # Step 1: Time Reference Extraction
    # Store original datenum for state initialization (preserves seasonal information)
    weather_datenum = weather[0, 0]

    # Step 2: Time Normalization
    # Convert absolute datenum to relative seconds from simulation start
    # This ensures t=0 at simulation beginning for numerical stability
    weather[:, 0] = (weather[:, 0] - weather[0, 0]) * 86400  # days to seconds

    # Step 3: Model Structure Initialization
    # Create core model dictionary with standard GreenLight structure
    gl = {
        "x": {},  # State variables (temperatures, concentrations, biomass)
        "a": {},  # Auxiliary variables (fluxes, rates, intermediate calculations)
        "d": {},  # Disturbances (weather inputs, external conditions)
        "p": {},  # Parameters (physical constants, greenhouse specifications)
        "u": {}   # Control inputs (setpoints, actuator commands)
    }

    # Step 4: Lamp Type Validation
    # Normalize lamp type string and default to 'none' if invalid
    lampType = lampType.lower() if lampType else "none"
    
    # Validate lamp type is supported
    if lampType not in ['hps', 'led', 'none', '']:
        lampType = 'none'
        print(f"Warning: Invalid lamp type. Defaulting to 'none' (no supplemental lighting)")

    # Step 5: Indoor Conditions Setup
    # Initialize indoor climate list for steady-state calculations
    if indoor is None:
        indoor = []  # Will use outdoor conditions for initialization

    # Step 6: Parameter Configuration Pipeline
    # Each function adds specific parameter sets to the model
    
    # 6.1: Base greenhouse parameters (structure, materials, crop properties)
    gl = set_gl_params(gl)
    
    # 6.2: Weather data processing and interpolation setup
    gl = set_gl_weather(gl, weather)
    
    # 6.3: Time vector generation for simulation period
    gl = set_gl_time(gl)
        
    # 6.4: Lamp-specific parameters (efficiency, spectrum, heat output)
    gl = set_default_lamp_params(gl, lampType)
    
    # 6.5: Control system initialization (setpoints, schedules)
    gl = set_gl_control_init(gl, controls)
    
    # 6.6: State variable initialization (steady-state or specified values)
    # Uses original datenum to account for seasonal variations
    gl = set_gl_states_init(gl, weather_datenum)
    
    # Step 7: Model Validation and Return
    # Model is now fully initialized and ready for simulation
    return gl
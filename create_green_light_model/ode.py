# GreenLightPlus/GreenLightPlus/create_green_light_model/ode.py
# ODE Solver Implementation for GreenLight Model
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

David Katzin, Simon van Mourik, Frank Kempkes, and Eldert J. Van Henten. 2020. “GreenLight - An Open Source Model for Greenhouses with Supplemental Lighting: Evaluation of Heat Requirements under LED and HPS Lamps.” Biosystems Engineering 194: 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010


New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com, daidai.qiu@wur.nl

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

# Import necessary modules and functions
from ..service_functions.funcs import *
from .set_gl_aux import set_gl_aux
from .set_gl_control import set_gl_control
from .set_gl_odes import set_gl_odes
import copy
import numpy as np
np.seterr(invalid="ignore", over="ignore")  # Set numpy to ignore invalid and overflow warnings

class ODESolver:
    """
    Custom ODE solver wrapper for GreenLight model integration.
    
    This class provides a specialized interface between the GreenLight model
    and scipy's ODE solvers. It handles:
    - Time-dependent input interpolation
    - State variable management
    - Auxiliary calculations at each time step
    - Control system updates
    
    The solver maintains model consistency by updating all interdependent
    variables at each integration step, ensuring physical relationships
    are preserved throughout the simulation.
    
    Attributes:
        gl (dict): Complete GreenLight model instance
        d (ndarray): Disturbance (weather) input matrix
        u (ndarray): Control input matrix
        prev_gl (dict): Previous model state for event detection
    """
    
    def __init__(self, d, u, gl):
        """
        Initialize ODE solver with model and input data.
        
        Args:
            d (ndarray): Disturbance matrix with weather data.
                Shape: (n_timesteps, n_disturbances)
                Columns include temperature, radiation, humidity, etc.
            u (ndarray): Control input matrix with setpoints.
                Shape: (n_timesteps, n_controls)
                Columns include heating, ventilation, lighting controls.
            gl (dict): Initialized GreenLight model instance containing:
                - 'x': State variables
                - 'p': Parameters
                - 't': Time vector
                - 'a': Auxiliary variables
        """
        self.gl = gl  # Complete model structure
        self.d = d  # Weather/disturbance inputs
        self.u = u  # Control inputs
        self.prev_gl = {}  # State history for event handling

    def convert_dict_to_array(self, data_dict):
        """
        Convert state dictionary to numpy array for ODE solver.
        
        Transforms the hierarchical state dictionary into a flat array
        format required by numerical integrators. Maintains consistent
        ordering for proper state reconstruction.
        
        Args:
            data_dict (dict): Dictionary with state variables as key-value pairs.
                Each value should be a numpy array of the same length.
                
        Returns:
            ndarray: 2D array with shape (n_timesteps, n_variables).
                Each column corresponds to one state variable.
                
        Raises:
            ValueError: If dictionary values have inconsistent shapes.
        """
        keys = list(data_dict.keys())  # Get all keys of the dictionary
        num_rows = data_dict[keys[0]].shape[0]  # Get number of rows from the first array
        
        # Check if all arrays have the same number of rows
        for key in keys:
            if data_dict[key].shape[0] != num_rows:
                raise ValueError("All arrays must have the same number of rows")
        
        # Build the result array
        result_array = data_dict[keys[0]]
        for key in keys[1:]:
            result_array = np.hstack((result_array, data_dict[key][:, 1:]))
        
        return result_array

    def sample_d(self, t):
        """
        Sample uncontrollable factor data at time t, handling boundary cases
        :param t: Sampling time
        :return: Sampling result
        """
        if t <= self.d[0, 0]:
            return self.d[0, 1:]  # If t is less than or equal to the minimum time, return the first row of data
        elif t >= self.d[-1, 0]:
            return self.d[-1, 1:]  # If t is greater than or equal to the maximum time, return the last row of data
        else:
            # Perform linear interpolation for each column
            return np.array([np.interp(t, self.d[:, 0], self.d[:, k]) for k in range(1, self.d.shape[1])])

    def sample_u(self, t):
        """
        Sample predefined control variables at time t, handling boundary cases
        :param t: Sampling time
        :return: Sampling result
        """
        if t <= self.u[0, 0]:
            return self.u[0, 1:]  # If t is less than or equal to the minimum time, return the first row of data
        elif t >= self.u[-1, 0]:
            return self.u[-1, 1:]  # If t is greater than or equal to the maximum time, return the last row of data
        else:
            # Perform linear interpolation for each column
            return np.array([np.interp(t, self.u[:, 0], self.u[:, k]) for k in range(1, self.u.shape[1])])

    def ode(self, t, x):
        """
        Solve the system of ordinary differential equations
        :param t: Current time step
        :param x: Array of current dependent variables
        :return: List of ODE values at the current time step
        """
        # Update x values in the gl dictionary
        self.gl["x"].update(zip(self.gl["x"].keys(), x))

        # Sample uncontrollable factors at time t
        d_sample = self.sample_d(t)
        self.gl["d"] = {key: value for key, value in zip(list(self.gl["d"].keys()), d_sample)}

        # If control variables are provided, sample them at time t
        if self.u is not None:
            u_sample = self.sample_u(t)
            self.gl["u"] = {key: value for key, value in zip(list(self.gl["u"].keys()), u_sample)}

        # Check if specific variables are inf and replace with previous value
        keys_to_check = ["tBlScr", "tThScr", "tIntLamp", "tCovIn", "time"]
        values_to_check = np.array([self.gl["x"][key] for key in keys_to_check])
        inf_indices = np.isinf(values_to_check)
        
        if np.any(inf_indices):
            for idx, key in enumerate(keys_to_check):
                if inf_indices[idx]:
                    self.gl["x"][key] = self.prev_gl["x"][key]

        # Initialize values of auxiliary variables
        self.gl = set_gl_aux(self.gl)

        # Calculate values of rule-based control variables
        self.gl = set_gl_control(self.gl)

        # Recalculate values of auxiliary variables
        self.gl = set_gl_aux(self.gl)

        # Calculate ODE values
        dx_list = set_gl_odes(self.gl)

        # Update prev_gl
        self.prev_gl["x"] = self.gl["x"].copy()

        return dx_list
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


from ..service_functions.funcs import *
from .set_gl_aux import set_gl_aux
from .set_gl_control import set_gl_control
from .set_gl_odes import set_gl_odes
import copy
import numpy as np
np.seterr(invalid="ignore", over="ignore")


class ODESolver:
    def __init__(self, d, u, gl):
        # Create interpolation functions for each column of d
        self.gl = gl  # Store the entire GreenLight model instance
        self.d = d  # Store the entire uncontrolled variables matrix
        self.u = u  # Store the entire control data variables matrix
        self.prev_gl = {}  # Store the previous GreenLight model instance
        self.d_keys = list(gl["d"].keys())

    def sample_d(self, t):
        """Sample data at time t, handling edges."""
        if t <= self.d[0, 0]:
            # print("Warning: t is less than the first time point in the data matrix.")
            # Use first row if t is less than the first time point
            return self.d[0, 1:]
        elif t >= self.d[-1, 0]:
            # print("Warning: t is greater than the last time point in the data matrix.")
            # Use last row if t is greater than the last time point
            return self.d[-1, 1:]
        else:
            # Use interpolation for each column
            return np.array([np.interp(t, self.d[:, 0], self.d[:, k]) for k in range(1, self.d.shape[1])])

    def sample_u(self, t, u):
        """Sample predefined controls at time t, handling edges."""
        if t <= u[0, 0]:
            # Use first row if t is less than the first time point
            return u[0, 1:]
        elif t >= u[-1, 0]:
            # Use last row if t is greater than the last time point
            return u[-1, 1:]
        else:
            # Use interpolation for each column
            u_sample = np.empty(u.shape[1] - 1)
            for k in range(1, u.shape[1]):
                if not np.isnan(u[0, k]):
                    u_sample[k - 1] = np.interp(t, u[:, 0], u[:, k])
                else:
                    u_sample[k - 1] = np.nan
            return u_sample

    def ode(self, t, x):
        """
        Solve a system of ODEs.

        Args:
            t (float): Current time step.
            x (np.ndarray): Array of current values of the dependent variables.
            gl (dict): Dictionary containing the current values of the independent variables, as well as any constants.

        Returns:
            list: List of the values of the ODEs at the current time step.
        """
        # Update the values in the dictionary
        self.gl["x"].update(zip(self.gl["x"].keys(), x))

        # Sample inputs at time t, d is uncontrolled factors, such as outdoor weather conditions
        d_sample = self.sample_d(t)
 
        # Update the values in the dictionary
        self.gl["d"] = {key: value for key,
                        value in zip(self.d_keys, d_sample)}

        # If controls are provided, sample them at time t
        if self.u is not None:
            # Sample controls at time t, u is controlled factors, such as heating, cooling, lighting, etc.
            u_sample = self.sample_u(t, self.u)
            # Update the values in the dictionary
            self.gl["u"].update(zip(self.gl["u"].keys(), u_sample))

        # Check if any of the values in the dictionary is inf, which may cause the ODE solver to fail
        keys_to_check = ["tBlScr", "tThScr", "tIntLamp", "tCovIn", "time"]
        values_to_check = np.array([self.gl["x"][key]
                                   for key in keys_to_check])

        # Check if any of the values is inf
        inf_indices = np.isinf(values_to_check)

        # If any of the values is inf, replace it with the previous value
        if np.any(inf_indices):
            for idx, key in enumerate(keys_to_check):
                if inf_indices[idx]:
                    self.gl["x"][key] = self.prev_gl["x"][key]

        # Calculate values of auxiliary variables, a
        set_gl_aux(self.gl)

        # Calculate values of rule-based controls, u
        set_gl_control(self.gl)

        # Calculate values of auxiliary variables, a
        set_gl_aux(self.gl)
 
        # Calculate values of ODEs
        dx_list = set_gl_odes(self.gl)

        # Update prev_gl
        # use shallow copy instead of deep copy
        self.prev_gl["x"] = self.gl["x"].copy()
        
        # print(f'self.gl["a"]["fVentRoof2"]: {self.gl["a"]["fVentRoof2"]}\n')


        return dx_list

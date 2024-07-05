"""
Copyright Statement:
This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.
Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com
New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com, daidai.qiu@wur.nl
This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

import os
import copy
import time as tm
import numpy as np
import pandas as pd

from datetime import datetime
from scipy.integrate import solve_ivp


from ..service_functions.funcs import *
from ..service_functions.cut_energy_plus_data import cut_energy_plus_data, cut_energy_plus_data_csv, cut_energy_plus_data_csv_extreme
from ..service_functions.make_artificial_input import make_artificial_input
from ..service_functions.funcs import (
    calculate_energy_consumption,
    extract_last_value_from_nested_dict,
)

from ..create_green_light_model.ode import ODESolver
from ..create_green_light_model.set_params4ha_world_comparison import (
    set_params4ha_world_comparison,
)
from ..create_green_light_model.create_green_light_model import create_green_light_model
from ..create_green_light_model.set_dep_params import set_dep_params
from ..create_green_light_model.change_res import change_res
from ..create_green_light_model.set_gl_aux import set_gl_aux
from ..service_functions.convert_epw2csv import convert_epw2csv


class GreenLightModel:
    """
    A class which allows for running simulations of greenhouse environments with supplemental lighting.

    Attributes:
        filename (str): The name of the output file for the model results (default is "").
        first_day (int): The initial day of the year (default is 1).
        lampType (str): The type of lamp to be used, either 'led' or 'hps' (default is 'led').
        isMature (bool): Whether start from mature stage (default is False).
        controls_file (str): Control trajectories file (default is None).
        epw_path (str): EPW file path (default is None).
        artificialWeather (bool): Whether to use artificial weather data (default is False).
        controls (numpy.ndarray): Control strategies data (default is None).
        u (numpy.ndarray): 'u' parameter matrix for the ODE solver (default is None).
        weather (numpy.ndarray): Weather data.
        elevation (float): Elevation parameter.
        gl (dict): GreenLight model data and parameters.
        d (numpy.ndarray): 'd' parameter matrix for the ODE solver.
    """

    def __init__(
        self,
        filename="",
        first_day=1,
        lampType="led",  # "led" or "hps" or "none"
        gl_params=None,  # Green light parameters
        isMature=False,  # Whether start from mature stage
        controls_file=None,  # Control trajectories file
        epw_path=None,  # EPW file path
        csv_path=None,  # CSV file path
    ):
        self.filename = filename
        self.first_day = first_day
        self.lampType = lampType
        self.isMature = isMature
        self.controls_file = controls_file
        self.epw_path = epw_path
        self.artificialWeather = False
        self.controls = None
        self.u = None
        self.csv_path = csv_path

    def prepare_data_and_params(self, season_length, start_row, end_row):
        """
        Prepares the data and parameters for the GreenLight model simulation.
        Handles the setting up of weather data paths, initializing model parameters,
        and setting up control strategies if provided.

        Args:
            season_length (int): The length of the simulation season.
            start_row (int): The starting index row for the weather data slicing.
            end_row (int): The ending index row for the weather data slicing.
        """
        if  self.csv_path is None:
            # Convert the EPW file to CSV format and get the path to the CSV file.
            path = convert_epw2csv(
                epw_path=self.epw_path,
                time_step=5, # Time step in minutes
            )
        else:
            path = self.csv_path
    
        # Normalize the lamp type input to lower case and set to 'none' if not 'hps' or 'led'.
        self.lampType = self.lampType.lower() if self.lampType.lower() in ["hps", "led"] else "none"

        # Load artificial weather data if the flag is set, or slice the real weather data as per the given rows.
        if self.artificialWeather:
            weather_data = make_artificial_input(5)[start_row:end_row]
        else:
            # Select which function to execute based on the file extension
            if os.path.splitext(path)[1] == ".mat":
                weather_data = cut_energy_plus_data(self.first_day, season_length, path)
            elif os.path.splitext(path)[1] == ".csv":
                weather_data = cut_energy_plus_data_csv(self.first_day, season_length, path)
            else:
                raise ValueError("Unsupported weather data file format")

        if start_row is not None and end_row is not None:
            weather_data = weather_data[start_row:end_row]

        # Store the weather data in the class instance.
        self.weather = weather_data

        # Set the elevation parameter based on the weather data or default it to 0.
        if self.weather.shape[0] > 0 and self.weather.shape[1] >= 10:
            self.elevation = self.weather[0, 9]
        else:
            self.elevation = 0
            print("Warning: weather data is not properly initialized.")

        # If a controls file is provided, read the control strategies and convert to numpy array.
        if self.controls_file is not None:
            controls = pd.read_csv(self.controls_file, header=None, skiprows=1)
            self.controls = controls.to_numpy()
            print(f"controls.shape: {self.controls.shape}")

        # Create the GreenLight model with the specified lamp type, weather data, and control strategies.
        self.gl = create_green_light_model(
            self.lampType, self.weather, self.controls)

        # Set parameters for the GreenLight model for comparison with HA-world.
        self.gl = set_params4ha_world_comparison(self.gl)

        # Set the elevation parameter in the GreenLight model.
        self.gl["p"]["hElevation"] = self.elevation

        # Set any model-dependent parameters.
        self.gl = set_dep_params(self.gl)

        # Prepare the 'd' parameter matrix from the GreenLight model for the ODE solver.
        d_arrays = list(self.gl["d"].values())
        time_column = d_arrays[0][:, 0:1]
        value_columns = [arr[:, 1:2] for arr in d_arrays]
        self.d = np.hstack([time_column, *value_columns])

        # Prepare the 'u' parameter matrix from the GreenLight model for the ODE solver, if controls are provided.
        if self.controls_file is not None:
            u_values = list(self.gl["u"].values())
            first_columns = u_values[0][:, :2]
            other_columns = [value[:, 1:2] for value in u_values[1:]]
            self.u = np.hstack((first_columns, *other_columns))

    def run_model(
        self,
        gl_params=None,
        season_length=1 / 24,
        season_interval=1 / 24 / 12,
        step=0,
        start_row=None,
        end_row=None,
        time_step=60
    ):
        """
        Runs the green light model and generates the results.

        Args:
            gl_params (dict): Green light parameters to be passed to the model (default is None).
            season_length (float): Length of the simulation season in days (default is 1/24).
            season_interval (float): Interval of the simulation season in days (default is 1/24/12).
            step (int): Current step of the simulation (default is 0).
            start_row (int): Starting row index for the weather data (default is None).
            end_row (int): Ending row index for the weather data (default is None).
            time_step (int): Time step for the final interpolation in seconds (default is 60).

        Returns:
            dict: A dictionary containing the results of the simulation.
        """
        if start_row is None or end_row is None:
            # Set the start and end rows for the weather data (each interval in the weather data is 5 minutes)
            rows_in_each_interval = int(season_interval * 12 * 24)
            start_row = step * rows_in_each_interval
            end_row = start_row + rows_in_each_interval

        # Prepare the data and parameters for the model
        self.prepare_data_and_params(season_length, start_row, end_row)

        if gl_params:
            # Convert the 2d ndarrays in the gl_params dictionary to 1d ndarrays
            gl_params = extract_last_value_from_nested_dict(gl_params)
            # Update the gl dictionary with the gl_params dictionary
            for key, value in gl_params.items():
                if isinstance(value, dict):
                    self.gl[key].update(value)
                else:
                    self.gl[key] = value

        # Start with a mature crop
        if self.isMature and step == 0:
            print("Start with a mature crop")
            self.gl["x"]["cFruit"] = 2.8e5  # Fruit dry matter weight [mg m^{-2}]
            self.gl["x"]["cLeaf"] = 0.9e5
            self.gl["x"]["cStem"] = 2.5e5
            self.gl["x"]["tCanSum"] = 3000

        # Set the options for the simulation
        time = self.gl["t"]

        # Set the initial states for the simulation
        initial_states = list(self.gl["x"].values())

        # Set the options for the solver
        options = {
            "atol": 1e-6,
            "rtol": 1e-3,
        }

        # Set the solver method
        solver = "BDF"

        # Create an instance of ODESolver
        solver_instance = ODESolver(self.d, self.u, self.gl)

        # Solve the differential equations and generate the results
        sol = solve_ivp(
            solver_instance.ode,
            time,
            initial_states,
            dense_output=True,
            method=solver,
            **options,
        )

        # Change the time resolution of the results, set the time step, and generate the model results
        self.gl = change_res(self.gl, self.d, sol, time_step)

        return self.gl
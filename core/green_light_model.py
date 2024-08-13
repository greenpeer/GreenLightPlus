# GreenLightPlus/GreenLightPlus/core/green_light_model.py

"""
Copyright Statement:

Author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


import os  # Import the os module for file and path operations
import copy  # Import the copy module for creating deep copies of objects
import time as tm  # Import the time module as tm for time-related operations
import numpy as np  # Import numpy for numerical operations
import pandas as pd  # Import pandas for data manipulation and analysis

from datetime import datetime  # Import datetime for date and time operations
from scipy.integrate import solve_ivp  # Import solve_ivp from scipy.integrate for solving initial value problems for ODE systems

# Import necessary functions and classes from service_functions and create_green_light_model modules
from ..service_functions.funcs import *
from ..service_functions.cut_energy_plus_data import cut_energy_plus_data, cut_energy_plus_data_csv, cut_energy_plus_data_csv_extreme
from ..service_functions.make_artificial_input import make_artificial_input
from ..service_functions.funcs import (
    calculate_energy_consumption,
    extract_last_value_from_nested_dict,
)
from ..create_green_light_model.ode import ODESolver
from ..create_green_light_model.set_params4ha_world_comparison import set_params4ha_world_comparison
from ..create_green_light_model.create_green_light_model import create_green_light_model
from ..create_green_light_model.set_dep_params import set_dep_params
from ..create_green_light_model.change_res import change_res
from ..create_green_light_model.set_gl_aux import set_gl_aux
from ..service_functions.convert_epw2csv import convert_epw2csv,check_csv

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
        lampType="led",         # "led" or "hps" or "none"
        gl_params=None,         # Change default parameters
        isMature=False,         # Whether start from mature stage
        controls_file=None,     # Control trajectories file
        epw_path=None,          # Weather EPW file path
        csv_path=None,          # Weather CSV file path
    ):
        # Initialize the filename attribute
        self.filename = filename
        # Set the first day of the simulation
        self.first_day = first_day
        # Set the type of lamp to be used
        self.lampType = lampType
        # Set whether to start from mature stage
        self.isMature = isMature
        # Set the path to the control trajectories file
        self.controls_file = controls_file
        # Set the path to the EPW file
        self.epw_path = epw_path
        # Initialize artificial weather flag to False
        self.artificialWeather = False
        # Initialize controls to None
        self.controls = None
        # Initialize u parameter matrix to None
        self.u = None
        # Set the path to the CSV file
        self.csv_path = csv_path

  
    def _get_weather_data_path(self):
            """
            Determines the path to the weather data file, converting EPW to CSV if necessary and checking the CSV file.

            Returns:
                str: The path to the weather data file.
            """
            if self.csv_path is None:
                print("Converting EPW file to CSV format...")
                print(f"EPW path: {self.epw_path}")
                # Convert EPW file to CSV format if CSV path is not provided
                return convert_epw2csv(epw_path=self.epw_path, time_step=5)
            else:
                # Check and process the provided CSV file with the desired timestep (e.g., 5 minutes)
                return check_csv(csv_path=self.csv_path, timestep=5)
          

    def _load_weather_data(self, path, season_length, start_row, end_row):
        """
        Loads weather data from the specified path, slicing it based on start and end rows.

        Args:
            path (str): The path to the weather data file.
            season_length (int): The length of the simulation season.
            start_row (int): The starting index row for slicing.
            end_row (int): The ending index row for slicing.

        Returns:
            np.ndarray: The sliced weather data.
        """
        # Normalize lamp type to lowercase, set to 'none' if not 'hps' or 'led'
        self.lampType = self.lampType.lower() if self.lampType.lower() in ["hps", "led"] else "none"

        # Check if artificial weather data should be used
        if self.artificialWeather:
            # Generate artificial weather data and slice it
            return make_artificial_input(5)[start_row:end_row]

        # Get the file extension of the weather data path
        ext = os.path.splitext(path)[1]
        # Load weather data based on file extension
        if ext == ".mat":
            weather_data = cut_energy_plus_data(self.first_day, season_length, path)
        elif ext == ".csv":
            weather_data = cut_energy_plus_data_csv(self.first_day, season_length, path)
        else:
            # Raise an error if the file format is not supported
            raise ValueError("Unsupported weather data file format")

        # Slice and return the weather data
        return weather_data[start_row:end_row]

    def _set_elevation(self):
        """
        Sets the elevation attribute based on the weather data.
        """
        # Check if weather data has sufficient rows and columns
        if self.weather.shape[0] > 0 and self.weather.shape[1] >= 10:
            # Set elevation to the value from the weather data
            self.elevation = self.weather[0, 9]
        else:
            # Set elevation to 0 if weather data is not properly initialized
            self.elevation = 0
            print("Warning: weather data is not properly initialized.")

    def _load_controls(self):
        """
        Loads control strategies from the control file if provided.
        """
        if self.controls_file is not None:
            # Read control strategies from the control file
            controls = pd.read_csv(self.controls_file, header=None, skiprows=1)
            # Convert controls to numpy array
            self.controls = controls.to_numpy()
            print(f"controls.shape: {self.controls.shape}")

    def _initialize_green_light_model(self):
        """
        Initializes the GreenLight model with the provided lamp type, weather data, and controls.
        """
        # Create the GreenLight model with the specified lamp type, weather data, and controls
        self.gl = create_green_light_model(self.lampType, self.weather, self.controls)
        # Set parameters for comparison with HA-world
        self.gl = set_params4ha_world_comparison(self.gl)
        # Set the elevation parameter in the GreenLight model
        self.gl["p"]["hElevation"] = self.elevation

    def _set_dependent_params(self):
        """
        Sets dependent parameters for the GreenLight model.
        """
        # Set dependent parameters in the GreenLight model
        self.gl = set_dep_params(self.gl)

    def _prepare_ode_parameters(self):
        """
        Prepares the 'd' and 'u' parameter matrices for the ODE solver.
        """
        # Extract 'd' parameter arrays from the GreenLight model
        d_arrays = list(self.gl["d"].values())
        # Extract time column and value columns from 'd' arrays
        time_column = d_arrays[0][:, 0:1]
        value_columns = [arr[:, 1:2] for arr in d_arrays]
        # Combine time column and value columns to form 'd' parameter matrix
        self.d = np.hstack([time_column, *value_columns])

        # Check if controls file is provided
        if self.controls_file is not None:
            # Extract 'u' parameter arrays from the GreenLight model
            u_values = list(self.gl["u"].values())
            # Extract first columns and other columns from 'u' arrays
            first_columns = u_values[0][:, :2]
            other_columns = [value[:, 1:2] for value in u_values[1:]]
            # Combine first columns and other columns to form 'u' parameter matrix
            self.u = np.hstack((first_columns, *other_columns))

    def _prepare_data_and_params(self, season_length, start_row, end_row):
        """
        Prepares the data and parameters for the GreenLight model simulation.
        Handles the setting up of weather data paths, initializing model parameters,
        and setting up control strategies if provided.

        Args:
            season_length (int): The length of the simulation season.
            start_row (int): The starting index row for the weather data slicing.
            end_row (int): The ending index row for the weather data slicing.
        """
        # Prepare weather data
        weather_data_path = self._get_weather_data_path()
        self.weather = self._load_weather_data(weather_data_path, season_length, start_row, end_row)
        
        # Process elevation
        self._set_elevation()

        # Load controls if provided
        self._load_controls()

        # Initialize GreenLight model
        self._initialize_green_light_model()

        # Set dependent parameters
        self._set_dependent_params()

        # Prepare parameter matrices for the ODE solver
        self._prepare_ode_parameters()

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
        # Check if start_row or end_row is not provided
        if start_row is None or end_row is None:
            # Set the start and end rows for the weather data (each interval in the weather data is 5 minutes)
            rows_in_each_interval = int(season_interval * 12 * 24)
            start_row = step * rows_in_each_interval
            end_row = start_row + rows_in_each_interval

        # Prepare the data and parameters for the model
        self._prepare_data_and_params(season_length, start_row, end_row)

        # Check if additional green light parameters are provided
        if gl_params:
            # Convert the 2d ndarrays in the gl_params dictionary to 1d ndarrays
            gl_params = extract_last_value_from_nested_dict(gl_params)
            # Update the gl dictionary with the gl_params dictionary
            for key, value in gl_params.items():
                if isinstance(value, dict):
                    self.gl[key].update(value)
                else:
                    self.gl[key] = value

        # Start with a mature crop if specified
        if self.isMature and step == 0:
            print("Start with a mature crop")
            # Set initial conditions for a mature crop
            # Fruit dry matter weight [mg m^{-2}]
            self.gl["x"]["cFruit"] = 2.8e5
            self.gl["x"]["cLeaf"] = 0.9e5
            self.gl["x"]["cStem"] = 2.5e5
            self.gl["x"]["tCanSum"] = 3000

        # Set the time range for the simulation
        time = self.gl["t"]

        # Set the initial states for the simulation
        initial_states = list(self.gl["x"].values())

        # Set the options for the ODE solver
        options = {
            "atol": 1e-6,  # Absolute tolerance
            "rtol": 1e-3,  # Relative tolerance
        }

        # Set the solver method
        solver = "BDF"  # Backward Differentiation Formula
        
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
        
        # Return the simulation results
        return self.gl

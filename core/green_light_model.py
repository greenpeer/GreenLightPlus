# GreenLightPlus/GreenLightPlus/core/green_light_model.py

"""
GreenLight Model Core Implementation
====================================

This module implements the core GreenLight greenhouse climate and crop growth model.
Based on the original MATLAB implementation by David Katzin et al. (2020), this
Python version provides enhanced functionality for greenhouse simulation and optimization.

The model integrates:
- Dynamic greenhouse climate simulation
- Crop growth and yield prediction
- Energy consumption calculations
- Supplemental lighting control (LED/HPS)
- Weather data integration

Copyright Statement:
    Author: Daidai Qiu
    Author's email: qiu.daidai@outlook.com
    Last Updated: July 2025
    
    This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.

References:
    Katzin, D., van Mourik, S., Kempkes, F., & van Henten, E. J. (2020).
    GreenLight - An open source model for greenhouses with supplemental lighting:
    Evaluation of heat requirements under LED and HPS lamps.
    Biosystems Engineering, 194, 61-81.
"""

# Standard library imports
import os  # File and path operations for weather data handling
import copy  # Deep copying of model states and parameters
import time as tm  # Performance timing and simulation timestamps
import numpy as np  # Numerical computations and array operations
import pandas as pd  # Data manipulation for weather and result analysis

# Scientific computing imports
from datetime import datetime  # Date/time handling for simulation periods
from scipy.integrate import solve_ivp  # ODE solver for dynamic system simulation

# Internal module imports - Service functions
from ..service_functions.funcs import *  # General utility functions
from ..service_functions.cut_energy_plus_data import (
    cut_energy_plus_data,  # MAT file weather data extraction
    cut_energy_plus_data_csv,  # CSV weather data extraction
    cut_energy_plus_data_csv_extreme  # Extreme weather scenario extraction
)
from ..service_functions.make_artificial_input import make_artificial_input  # Synthetic weather generation
from ..service_functions.funcs import (
    calculate_energy_consumption,  # Energy use calculations
    extract_last_value_from_nested_dict,  # Result extraction utilities
)
from ..service_functions.convert_epw2csv import convert_epw2csv, check_csv  # Weather format conversion

# Internal module imports - Model creation and configuration
from ..create_green_light_model.ode import ODESolver  # Custom ODE solver wrapper
from ..create_green_light_model.set_params4ha_world_comparison import set_params4ha_world_comparison  # Benchmark parameters
from ..create_green_light_model.create_green_light_model import create_green_light_model  # Model factory
from ..create_green_light_model.set_dep_params import set_dep_params  # Dependent parameter calculation
from ..create_green_light_model.change_res import change_res  # Time resolution adjustment
from ..create_green_light_model.set_gl_aux import set_gl_aux  # Auxiliary variable computation

class GreenLightModel:
    """
    Core GreenLight greenhouse climate and crop growth simulation model.
    
    This class provides a comprehensive simulation environment for greenhouse operations,
    integrating climate dynamics, crop growth, energy consumption, and supplemental
    lighting control. The model uses a system of ordinary differential equations (ODEs)
    to simulate the dynamic behavior of the greenhouse system.

    Key Features:
        - Multi-layer energy and mass balance calculations
        - Dynamic crop growth based on photosynthesis and respiration
        - Supplemental lighting simulation (LED/HPS)
        - Weather data integration (EPW, CSV, MAT formats)
        - Energy consumption tracking and optimization
        - Flexible control strategies for climate management

    Attributes:
        filename (str): Output filename for saving simulation results (default: "").
        first_day (int): Starting day of year for simulation (1-365, default: 1).
        lampType (str): Type of supplemental lighting - 'led', 'hps', or 'none' (default: 'led').
        isMature (bool): Initialize crop at mature stage if True (default: False).
        controls_file (str): Path to control strategy file (default: None).
        epw_path (str): Path to EPW weather data file (default: None).
        csv_path (str): Path to CSV weather data file (default: None).
        artificialWeather (bool): Use synthetic weather data if True (default: False).
        controls (numpy.ndarray): Control action time series (default: None).
        u (numpy.ndarray): Control input matrix for ODE solver (default: None).
        weather (numpy.ndarray): Processed weather data array.
        elevation (float): Site elevation in meters above sea level.
        gl (dict): Main model dictionary containing states, parameters, and results.
        d (numpy.ndarray): Disturbance (weather) input matrix for ODE solver.

    Example:
        >>> model = GreenLightModel(
        ...     first_day=91,  # Start April 1st
        ...     lampType='led',
        ...     epw_path='weather_data.epw'
        ... )
        >>> results = model.run_simulation(season_length=10, time_step=5)
    """

    def __init__(
        self,
        filename="",
        first_day=1,
        lampType="led",         # Supplemental lighting type: "led", "hps", or "none"
        gl_params=None,         # Custom parameter overrides for model configuration
        isMature=False,         # Initialize crop at mature development stage
        controls_file=None,     # Path to predefined control strategy file
        epw_path=None,          # EnergyPlus Weather (EPW) file path
        csv_path=None,          # Alternative CSV weather data file path
    ):
        """
        Initialize GreenLight model instance with specified configuration.

        This constructor sets up the greenhouse simulation environment with the
        specified parameters. Weather data can be provided in EPW, CSV, or MAT
        format, or synthetic weather can be generated.

        Args:
            filename (str, optional): Base filename for saving simulation results.
                Results will be saved as '{filename}_greenLight.mat'. Default: "".
            first_day (int, optional): Starting day of year (1-365) for simulation.
                Determines which part of annual weather data to use. Default: 1.
            lampType (str, optional): Type of supplemental lighting system.
                Options: 'led' (Light Emitting Diode), 'hps' (High Pressure Sodium),
                or 'none' (no supplemental lighting). Default: 'led'.
            gl_params (dict, optional): Custom parameter overrides for the model.
                Allows modification of default greenhouse parameters. Default: None.
            isMature (bool, optional): If True, initialize crop at mature stage
                (skips juvenile growth phase). Useful for steady-state analysis. Default: False.
            controls_file (str, optional): Path to file containing predefined
                control strategies for climate management. Default: None.
            epw_path (str, optional): Path to EnergyPlus Weather (EPW) file.
                Standard format for building energy simulation. Default: None.
            csv_path (str, optional): Path to CSV file with weather data.
                Alternative to EPW format. Default: None.

        Note:
            Either epw_path or csv_path must be provided for weather data,
            unless using artificial weather generation.
        """
        # Store output filename for result saving
        self.filename = filename
        
        # Set simulation start day (1-365)
        self.first_day = first_day
        
        # Configure supplemental lighting system type
        self.lampType = lampType
        
        # Set crop maturity initialization flag
        self.isMature = isMature
        
        # Store path to control strategy file
        self.controls_file = controls_file
        
        # Store weather data file paths
        self.epw_path = epw_path
        self.csv_path = csv_path
        
        # Initialize simulation configuration flags
        self.artificialWeather = False  # Flag for using synthetic weather
        self.controls = None  # Control action time series
        self.u = None  # Control input matrix for ODE solver

  
    def _get_weather_data_path(self):
            """
            Prepare weather data file path, handling format conversion if needed.
            
            This method determines the appropriate weather data source and ensures
            it's in the correct format for simulation. EPW files are automatically
            converted to CSV format with 5-minute time steps for compatibility
            with the ODE solver.

            The method handles two scenarios:
            1. EPW file provided: Converts to CSV with proper time resolution
            2. CSV file provided: Validates and adjusts time resolution if needed

            Returns:
                str: Absolute path to the processed weather data file (CSV format).
                     The file will have 5-minute resolution time steps.

            Raises:
                ValueError: If neither EPW nor CSV path is provided.
                FileNotFoundError: If the specified weather file doesn't exist.

            Note:
                The conversion process creates a new CSV file in the same directory
                as the source file, with '_5min' suffix added to the filename.
            """
            if self.csv_path is None:
                # EPW format provided - convert to CSV
                print("Converting EPW file to CSV format...")
                print(f"EPW path: {self.epw_path}")
                # Convert EPW to CSV with 5-minute time steps for numerical stability
                return convert_epw2csv(epw_path=self.epw_path, time_step=5)
            else:
                # CSV format provided - validate and adjust time resolution
                # Ensure CSV has consistent 5-minute intervals for ODE solver
                return check_csv(csv_path=self.csv_path, timestep=5)
          

    def _load_weather_data(self, path, season_length, start_row, end_row):
        """
        Load and preprocess weather data for simulation period.
        
        This method handles loading weather data from various sources and formats,
        including real weather files (MAT/CSV) or synthetic weather generation.
        The data is sliced to match the exact simulation period and time resolution.

        Weather data columns typically include:
        - Outdoor temperature (°C)
        - Outdoor relative humidity (%)
        - Global solar radiation (W/m²)
        - Direct and diffuse radiation components
        - Wind speed (m/s)
        - Sky temperature (°C)
        - Elevation and time information

        Args:
            path (str): File path to weather data (MAT or CSV format).
            season_length (int): Duration of growing season in days.
            start_row (int): Starting index for data extraction (inclusive).
            end_row (int): Ending index for data extraction (exclusive).

        Returns:
            np.ndarray: Weather data array with shape (n_timesteps, n_variables).
                Each row represents one time step (typically 5 minutes).
                Columns contain weather variables in standardized order.

        Raises:
            ValueError: If file format is not supported (.mat or .csv required).
            FileNotFoundError: If weather data file doesn't exist.
            IndexError: If requested time range exceeds available data.

        Side Effects:
            - Normalizes lampType attribute to lowercase
            - Validates lamp type is 'hps', 'led', or 'none'
        """
        # Normalize and validate lamp type specification
        self.lampType = self.lampType.lower() if self.lampType.lower() in ["hps", "led"] else "none"

        # Option 1: Use synthetic weather data for testing
        if self.artificialWeather:
            # Generate idealized weather patterns with 5-minute resolution
            return make_artificial_input(5)[start_row:end_row]

        # Option 2: Load real weather data from file
        ext = os.path.splitext(path)[1]
        
        # Load weather data using appropriate parser
        if ext == ".mat":
            # MATLAB format (legacy compatibility)
            weather_data = cut_energy_plus_data(self.first_day, season_length, path)
        elif ext == ".csv":
            # CSV format (standard for EnergyPlus)
            weather_data = cut_energy_plus_data_csv(self.first_day, season_length, path)
        else:
            # Unsupported format
            raise ValueError(f"Unsupported weather data file format: {ext}. Use .mat or .csv files.")

        # Extract requested time period and return
        return weather_data[start_row:end_row]

    def _set_elevation(self):
        """
        Extract and set site elevation from weather data.
        
        This method reads the elevation value from the weather data array,
        which is typically stored in column index 9 (0-based) of standard
        weather data formats. Elevation affects atmospheric pressure and
        consequently impacts various thermodynamic calculations in the model.

        The elevation is used for:
        - Atmospheric pressure calculations
        - Psychrometric property corrections
        - Heat transfer coefficient adjustments

        Note:
            Assumes weather data follows standard column ordering where
            column 9 contains elevation in meters above sea level.
            Falls back to 0m elevation if data is unavailable.
        """
        # Validate weather data dimensions
        if self.weather.shape[0] > 0 and self.weather.shape[1] >= 10:
            # Extract elevation from standard weather data column
            self.elevation = self.weather[0, 9]
        else:
            # Set elevation to 0 if weather data is not properly initialized
            self.elevation = 0
            print("Warning: weather data is not properly initialized.")

    def _load_controls(self):
        """
        Load predefined control strategies from external file.
        
        This method reads control action time series from a CSV file, allowing
        for reproducible simulations with specific control patterns. Control
        files typically contain setpoints and actuator commands for:
        - Heating/cooling systems
        - Ventilation rates
        - Screen positions
        - Supplemental lighting schedules
        - CO2 injection rates

        File Format:
            - CSV format without headers
            - First row is skipped (typically contains column descriptions)
            - Each row represents one time step
            - Columns represent different control variables

        Side Effects:
            - Sets self.controls as numpy array if file exists
            - Prints shape information for validation
        """
        if self.controls_file is not None:
            # Load control strategy time series from CSV
            controls = pd.read_csv(self.controls_file, header=None, skiprows=1)
            # Convert to numpy for efficient numerical operations
            self.controls = controls.to_numpy()
            print(f"Loaded control strategies: {self.controls.shape[0]} timesteps, {self.controls.shape[1]} control variables")

    def _initialize_green_light_model(self):
        """
        Initialize core GreenLight model structure and parameters.
        
        This method creates the main model dictionary (self.gl) that contains
        all model components organized in sub-dictionaries:
        - 'x': State variables (temperatures, concentrations, biomass)
        - 'a': Auxiliary variables (computed from states)
        - 'p': Parameters (physical constants, greenhouse properties)
        - 'd': Disturbances (weather inputs)
        - 'u': Control inputs (setpoints, actuator positions)

        The initialization process:
        1. Creates base model structure with specified lamp type
        2. Applies standard parameter set for comparison studies
        3. Sets site-specific elevation for pressure calculations

        Note:
            Uses parameters from Katzin et al. (2020) as baseline
            for reproducibility and comparison with published results.
        """
        # Build core model structure with specified configuration
        self.gl = create_green_light_model(self.lampType, self.weather, self.controls)
        
        # Apply standardized parameter set for benchmarking
        # These parameters enable comparison with published results
        self.gl = set_params4ha_world_comparison(self.gl)
        
        # Set site elevation for atmospheric pressure calculations
        self.gl["p"]["hElevation"] = self.elevation

    def _set_dependent_params(self):
        """
        Calculate and set derived parameters based on primary parameters.
        
        Many model parameters depend on other parameters through physical
        relationships. This method computes all dependent parameters to
        ensure consistency. Examples include:
        - Heat capacity calculations from material properties
        - View factors from greenhouse geometry
        - Optical properties from material specifications
        - Convection coefficients from dimensional analysis

        This step is crucial for maintaining physical consistency
        and must be called after any parameter modifications.
        """
        # Compute all dependent parameters from primary values
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
        Execute GreenLight greenhouse simulation for specified time period.
        
        This is the main simulation method that integrates the system of ODEs
        representing greenhouse climate dynamics and crop growth. The simulation
        can be run for periods ranging from hours to full growing seasons.

        The method performs:
        1. Weather data preparation and slicing
        2. Model initialization with parameters
        3. ODE integration using adaptive time stepping
        4. Post-processing and interpolation of results
        5. Energy consumption calculations

        Args:
            gl_params (dict, optional): Custom parameter overrides to modify
                default model parameters. Nested dictionary matching gl structure.
                Example: {'p': {'LAI': 3.5, 'plantDensity': 4}}. Default: None.
            season_length (float, optional): Total simulation duration in days.
                Common values: 1/24 (1 hour), 1 (1 day), 7 (1 week). Default: 1/24.
            season_interval (float, optional): Length of each simulation segment
                in days. Used for splitting long simulations. Default: 1/24/12 (5 min).
            step (int, optional): Current simulation step when running segmented
                simulations. Used to calculate data offsets. Default: 0.
            start_row (int, optional): Manual override for weather data start index.
                If None, calculated from step and season_interval. Default: None.
            end_row (int, optional): Manual override for weather data end index.
                If None, calculated from step and season_interval. Default: None.
            time_step (int, optional): Output time resolution in seconds for
                interpolation. Lower values give smoother results. Default: 60.

        Returns:
            dict: Comprehensive simulation results containing:
                - 'time': Time vector (days since start)
                - 'states': All state variables over time
                - 'controls': Control actions applied
                - 'weather': Weather conditions used
                - 'auxVars': Auxiliary calculated variables
                - 'energy': Energy consumption breakdown
                - 'yield': Cumulative crop yield
                - 'gl': Complete model dictionary with final values

        Example:
            >>> # Run 7-day simulation with hourly output
            >>> results = model.run_model(
            ...     season_length=7,
            ...     time_step=3600,
            ...     gl_params={'p': {'tSpNight': 18}}
            ... )
            >>> 
            >>> # Access results
            >>> temps = results['states']['tAir']
            >>> energy = results['energy']['totalElec']

        Note:
            For simulations longer than a few days, consider using
            smaller season_intervals to improve numerical stability.
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

# File path: GreenLightPlus/create_green_light_model/set_gl_weather.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

David Katzin, Simon van Mourik, Frank Kempkes, and Eldert J. Van Henten. 2020. "GreenLight - An Open Source Model for Greenhouses with Supplemental Lighting: Evaluation of Heat Requirements under LED and HPS Lamps." Biosystems Engineering 194: 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010

New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

import numpy as np  # Import NumPy for numerical operations
import datetime  # Import datetime module for date and time operations
from datetime import timedelta  # Import timedelta for time calculations
from ..service_functions.vapor_dens2pres import vapor_dens2pres  # Import function to convert vapor density to pressure
from ..service_functions.rh2vapor_dens import rh2vapor_dens  # Import function to convert relative humidity to vapor density
from ..service_functions.day_light_sum import day_light_sum  # Import function to calculate daily light sum

class GreenLightWeather:
    """
    A class to process and set weather inputs for the GreenLight greenhouse model.

    Attributes:
        gl (dict): A GreenLight model nested dictionary.
        p (dict): Parameters from the GreenLight model.
    """

    def __init__(self, gl):
        """
        Initialize the GreenLightWeather instance.

        Args:
            gl (dict): A GreenLight model nested dictionary.
        """
        self.gl = gl  # Store the GreenLight model dictionary
        self.p = gl["p"]  # Extract and store the parameters from the model

    def _process_weather_input(self, weatherInput):
        """
        Process the input weather data, adding daily radiation sum if needed.

        Args:
            weatherInput (np.ndarray): Raw weather input data.

        Returns:
            None
        """
        if weatherInput.shape[1] == 8:  # Check if weatherInput has 8 columns (missing daily radiation sum)
            # convert seconds from start of sim to datenum
            start_date = datetime.datetime.strptime("01-Jan-2005 01:00:00", "%d-%b-%Y %H:%M:%S")  # Define start date
            weather_dates = [start_date + timedelta(seconds=x) for x in weatherInput[:, 0]]  # Convert seconds to datetime objects

            # add daily radiation sum
            daily_radiation = day_light_sum(weather_dates, weatherInput[:, 1])  # Calculate daily radiation sum
            self.weatherInput = np.column_stack((weatherInput, daily_radiation))  # Add daily radiation sum as 9th column
        else:
            self.weatherInput = weatherInput  # Use input as is if it already has 9 columns

        self.time = self.weatherInput[:, 0]  # Extract time data from weatherInput

    def _set_weather_parameters(self):
        """
        Set various weather parameters in the GreenLight model dictionary.

        Returns:
            None
        """
        # Global radiation [W m^{-2}]
        self.gl["d"]["iGlob"] = np.column_stack((self.time, self.weatherInput[:, 1]))  # Store global radiation data

        # Outdoor air temperature [°C]
        self.gl["d"]["tOut"] = np.column_stack((self.time, self.weatherInput[:, 2]))  # Store outdoor temperature data

        # Outdoor vapor pressure [Pa], convert vapor density to pressure
        self.gl["d"]["vpOut"] = np.column_stack(
            (self.time, vapor_dens2pres(self.weatherInput[:, 2], self.weatherInput[:, 3]))
        )  # Convert vapor density to pressure and store

        # Outdoor co2 concentration [mg m^{-3}]
        self.gl["d"]["co2Out"] = np.column_stack((self.time, self.weatherInput[:, 4] * 1e6))  # Convert kg to mg and store CO2 concentration

        # Outdoor wind speed [m s^{-1}]
        self.gl["d"]["wind"] = np.column_stack((self.time, self.weatherInput[:, 5]))  # Store wind speed data

        # Sky temperature [°C]
        self.gl["d"]["tSky"] = np.column_stack((self.time, self.weatherInput[:, 6]))  # Store sky temperature data

        # Temperature of external soil layer [°C]
        self.gl["d"]["tSoOut"] = np.column_stack((self.time, self.weatherInput[:, 7]))  # Store external soil layer temperature data

        # Daily radiation sum from the sun [MJ m^{-2} day^{-1}]
        self.gl["d"]["dayRadSum"] = np.column_stack((self.time, self.weatherInput[:, 8]))  # Store daily radiation sum data

    def _calculate_day_night_indicators(self):
        """
        Calculate day/night indicators, including smooth transitions for sunrise and sunset.

        Returns:
            None
        """
        # 1 during day, 0 during night
        isDay = 1.0 * (self.weatherInput[:, 1] > 0)  # Create binary day/night indicator based on radiation
        isDaySmooth = np.copy(isDay)  # Create a copy for smooth transition

        transSize = 12  # Define transition size for smooth day/night change
        linear_transition = np.linspace(0, 1, transSize)  # Create linear transition array
        sunset = False  # Initialize sunset flag

        for k in range(transSize, len(isDay) - transSize):  # Iterate through isDay array
            if isDay[k] == 0:
                sunset = False  # Reset sunset flag when it's night
            if isDay[k] == 0 and isDay[k + 1] == 1:  # Sunrise condition
                isDay[k - transSize // 2 : k + transSize // 2] = linear_transition  # Apply sunrise transition
            elif isDay[k] == 1 and isDay[k + 1] == 0 and not sunset:  # Sunset condition
                isDay[k - transSize // 2 : k + transSize // 2] = 1 - linear_transition  # Apply sunset transition
                sunset = True  # Set sunset flag

        self.gl["d"]["isDay"] = np.column_stack((self.time, isDay))  # Store isDay data

        sigmoid_transition = 1.0 / (1 + np.exp(-10 * (linear_transition - 0.5)))  # Create sigmoid transition for smoother change

        sunset = False  # Reset sunset flag for isDaySmooth
        for k in range(transSize, len(isDaySmooth) - transSize):  # Iterate through isDaySmooth array
            if isDaySmooth[k] == 0:
                sunset = False  # Reset sunset flag when it's night
            if isDaySmooth[k] == 0 and isDaySmooth[k + 1] == 1:  # Sunrise condition
                isDaySmooth[k - transSize // 2 : k + transSize // 2] = sigmoid_transition  # Apply smooth sunrise transition
            elif isDaySmooth[k] == 1 and isDaySmooth[k + 1] == 0 and not sunset:  # Sunset condition
                isDaySmooth[k - transSize // 2 : k + transSize // 2] = 1 - sigmoid_transition  # Apply smooth sunset transition
                sunset = True  # Set sunset flag

        # Set output format for isDaySmooth with high precision
        np.set_printoptions(precision=15, suppress=True)  # Set NumPy print options for high precision
        self.gl["d"]["isDaySmooth"] = np.column_stack((self.time, isDaySmooth))  # Store isDaySmooth data

    def set_gl_weather(self, weatherInput):
        """
        Set weather inputs for a GreenLight model instance.

        Args:
            weatherInput (np.ndarray): A matrix with 8 or 9 columns in the following format:
                weatherInput[:, 0]: Timestamps of the input [s] in regular intervals.
                weatherInput[:, 1]: Radiation [W m^{-2}]: Outdoor global irradiation.
                weatherInput[:, 2]: Temperature [°C]: Outdoor air temperature.
                weatherInput[:, 3]: Humidity [kg m^{-3}]: Outdoor vapor concentration.
                weatherInput[:, 4]: CO2 [kg{CO2} m^{-3}{air}]: Outdoor CO2 concentration.
                weatherInput[:, 5]: Wind [m s^{-1}]: Outdoor wind speed.
                weatherInput[:, 6]: Sky temperature [°C].
                weatherInput[:, 7]: Temperature of external soil layer [°C].
                weatherInput[:, 8]: Daily radiation sum [MJ m^{-2} day^{-1}] (optional).

        Returns:
            dict: The updated GreenLight model dictionary with the following new fields:
                gl["d"]["iGlob"]: Radiation from the sun [W m^{-2}].
                gl["d"]["tOut"]: Outdoor air temperature [°C].
                gl["d"]["vpOut"]: Outdoor vapor pressure [Pa].
                gl["d"]["co2Out"]: Outdoor CO2 concentration [mg m^{-3}].
                gl["d"]["wind"]: Outdoor wind speed [m s^{-1}].
                gl["d"]["tSky"]: Sky temperature [°C].
                gl["d"]["tSoOut"]: Temperature of external soil layer [°C].
                gl["d"]["isDay"]: Indicates if it's day [1] or night [0], with a transition in between.
                gl["d"]["dayRadSum"]: Daily radiation sum [MJ m^{-2} day^{-1}].
        """
        self._process_weather_input(weatherInput)  # Process the input weather data
        self._set_weather_parameters()  # Set the weather parameters
        self._calculate_day_night_indicators()  # Calculate day/night indicators
        return self.gl  # Return the updated GreenLight model dictionary

def set_gl_weather(gl, weatherInput):
    """
    A wrapper function to set weather inputs for a GreenLight model instance.

    Args:
        gl (dict): A GreenLight model nested dictionary.
        weatherInput (np.ndarray): A matrix with weather data. See GreenLightWeather.set_gl_weather for details.

    Returns:
        dict: The updated GreenLight model dictionary. See GreenLightWeather.set_gl_weather for details on added fields.
    """
    gl_weather = GreenLightWeather(gl)  # Create a GreenLightWeather instance
    return gl_weather.set_gl_weather(weatherInput)  # Process weather data and return updated model



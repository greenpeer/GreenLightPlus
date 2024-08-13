# File path: GreenLightPlus/service_functions/convert_epw2csv.py
# GreenLightPlus/service_functions/convert_epw2csv.py
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.optimize import minimize
from scipy.interpolate import pchip_interpolate
import glob
from typing import Union, Tuple, List, Dict
from .rh2vapor_dens import rh2vapor_dens
from .co2_ppm2dens import co2_ppm2dens
from .rh2vapor_dens import rh2vapor_dens


def correct_hour_24(time_str):
    """
    Corrects '24:00' hour in a datetime string to '00:00' of the next day.
    This function handles the edge case where '24:00' is used to represent
    midnight of the following day. It adjusts such cases to '00:00' of the
    next day to maintain correct datetime formatting.

    Parameters:
    time_str (str): The datetime string in the format 'YYYY-MM-DD HH:MM'.

    Returns:
    str: The corrected datetime string in the format 'YYYY-MM-DD HH:MM'.
    """
    if time_str.endswith("24:00"):
        # Split the date and time parts
        date_part, *_ = time_str.split(" ")
        # Convert the date part to datetime and add one day
        corrected_date = pd.to_datetime(date_part) + pd.DateOffset(days=1)
        # Return the corrected datetime string with '00:00' time part
        return corrected_date.strftime("%Y-%m-%d 00:00")
    else:
        # If the time part is not '24:00', return the original time string
        return time_str



def relative_humidity_to_vapor_density(temperature: Union[float, np.ndarray], relative_humidity: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert relative humidity to vapor density.

    Args:
        temperature (float or np.ndarray): Temperature in Celsius.
        relative_humidity (float or np.ndarray): Relative humidity in percentage (0-100).

    Returns:
        float or np.ndarray: Vapor density in kg/m^3.
    """
    MOLAR_GAS_CONSTANT = 8.3144598  # J mol^{-1} K^{-1}
    CELSIUS_TO_KELVIN = 273.15  # K
    MOLAR_MASS_WATER = 18.01528e-3  # kg mol^{-1}
    SATURATION_PRESSURE_PARAMS = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    # Calculate saturation vapor pressure of air at given temperature [Pa]
    saturation_pressure = SATURATION_PRESSURE_PARAMS[0] * np.exp(
        SATURATION_PRESSURE_PARAMS[2] * temperature /
        (temperature + SATURATION_PRESSURE_PARAMS[1])
    )

    # Calculate partial pressure of vapor in air [Pa]
    partial_pressure = (relative_humidity / 100) * saturation_pressure

    # Convert to density using the ideal gas law: ρ = (P * M) / (R * T)
    vapor_density = partial_pressure * MOLAR_MASS_WATER / \
        (MOLAR_GAS_CONSTANT * (temperature + CELSIUS_TO_KELVIN))

    return vapor_density


def vapor_density_to_pressure(temperature: Union[float, np.ndarray], vapor_density: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert vapor density to vapor pressure.

    Args:
        temperature (float or np.ndarray): Temperature in Celsius.
        vapor_density (float or np.ndarray): Vapor density in kg/m^3.

    Returns:
        float or np.ndarray: Vapor pressure in Pascal.
    """
    SATURATION_PRESSURE_PARAMS = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]

    # Calculate relative humidity [0-1]
    relative_humidity = vapor_density / \
        relative_humidity_to_vapor_density(temperature, 100)

    # Calculate saturation vapor pressure of air at given temperature [Pa]
    saturation_pressure = SATURATION_PRESSURE_PARAMS[0] * np.exp(
        SATURATION_PRESSURE_PARAMS[2] * temperature /
        (temperature + SATURATION_PRESSURE_PARAMS[1])
    )

    # Calculate vapor pressure
    vapor_pressure = saturation_pressure * relative_humidity

    return vapor_pressure


def co2_ppm_to_density(temperature: Union[float, np.ndarray], ppm: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert CO2 molar concentration [ppm] to density [kg m^{-3}].

    Args:
        temperature (float or np.ndarray): Given temperatures in Celsius.
        ppm (float or np.ndarray): CO2 concentration in air [ppm].

    Returns:
        float or np.ndarray: CO2 concentration in air [kg m^{-3}].
    """
    MOLAR_GAS_CONSTANT = 8.3144598  # J mol^{-1} K^{-1}
    CELSIUS_TO_KELVIN = 273.15  # K
    MOLAR_MASS_CO2 = 44.01e-3  # kg mol^{-1}
    ATMOSPHERIC_PRESSURE = 101325  # Pa (assumed to be 1 atm)

    # Calculate CO2 density using the ideal gas law
    # ρ = (P * M) / (R * T) * (ppm * 10^-6)
    co2_density = (
        ATMOSPHERIC_PRESSURE * MOLAR_MASS_CO2 * ppm * 1e-6 /
        (MOLAR_GAS_CONSTANT * (temperature + CELSIUS_TO_KELVIN))
    )

    return co2_density


def read_epw_data(epw_path: str) -> pd.DataFrame:
    """
    Read an EPW (EnergyPlus Weather) file and return the corresponding pandas DataFrame.

    Args:
        epw_path (str): Path to the EPW file.

    Returns:
        pd.DataFrame: A DataFrame containing the EPW data with named columns.

    Raises:
        FileNotFoundError: If the specified EPW file does not exist.
        ValueError: If the number of columns in the EPW file doesn't match the expected number.
    """
    # Define column names for the EPW data
    column_names: List[str] = [
        "Year", "Month", "Day", "Hour", "Minute",
        "Data Source and Uncertainty Flags",
        "Dry Bulb Temperature (°C)",
        "Dew Point Temperature (°C)",
        "Relative Humidity (%)",
        "Atmospheric Station Pressure (Pa)",
        "Extraterrestrial Horizontal Radiation (J/m²)",
        "Extraterrestrial Direct Normal Radiation (J/m²)",
        "Horizontal Infrared Radiation Intensity (J/m²)",
        "Global Horizontal Radiation (J/m²)",
        "Direct Normal Radiation (J/m²)",
        "Diffuse Horizontal Radiation (J/m²)",
        "Global Horizontal Illuminance (lux)",
        "Direct Normal Illuminance (lux)",
        "Diffuse Horizontal Illuminance (lux)",
        "Zenith Luminance (klux)",
        "Wind Direction (deg)",
        "Wind Speed (m/s)",
        "Total Sky Cover (tenths)",
        "Opaque Sky Cover (tenths)",
        "Visibility (km)",
        "Ceiling Height (m)",
        "Present Weather Observation (code)",
        "Present Weather Codes (code)",
        "Precipitable Water (mm)",
        "Aerosol Optical Depth (km)",
        "Snow Depth (cm)",
        "Days Since Last Snowfall (day)",
        "Albedo",
        "Liquid Precipitation Depth (mm)",
        "Liquid Precipitation Quantity (hr)",
    ]

    # Check if the file exists
    if not os.path.isfile(epw_path):
        raise FileNotFoundError(f"The EPW file does not exist: {epw_path}")

    # Read the EPW file, skipping the header rows
    epw_data: pd.DataFrame = pd.read_csv(
        epw_path, skiprows=8, header=None, names=column_names)

    # Verify that the number of columns matches the expected number
    if len(column_names) != epw_data.shape[1]:
        raise ValueError(f"Expected {len(column_names)} columns, but found {epw_data.shape[1]} columns in the EPW file.")

    return epw_data


def preprocess_epw_data(epw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess weather data from an EPW file, including handling time columns and formatting.

    This function performs the following operations:
    1. Converts '60' minutes to '0'.
    2. Creates a 'DateTime' column from separate date and time columns.
    3. Removes individual date and time columns.
    4. Reorders columns to put 'DateTime' first.
    5. Corrects any '24:00' time to '00:00' of the next day.
    6. Converts 'DateTime' to pandas datetime type.

    Args:
        epw_data (pd.DataFrame): The input EPW data.

    Returns:
        pd.DataFrame: The preprocessed EPW data with a unified 'DateTime' column.
    """
    # Step 1: Convert '60' minutes to '0'
    epw_data["Minute"] = epw_data["Minute"].astype(str).replace("60", "0")

    # Step 2: Create 'DateTime' column by combining 'Year', 'Month', 'Day', 'Hour', 'Minute'
    epw_data["DateTime"] = (
        epw_data["Year"].astype(str) + "-"
        + epw_data["Month"].astype(str).str.zfill(2) + "-"
        + epw_data["Day"].astype(str).str.zfill(2) + " "
        + epw_data["Hour"].astype(str).str.zfill(2) + ":"
        + epw_data["Minute"].astype(str).str.zfill(2)
    )

    # Step 3: Remove individual date and time columns
    date_time_columns: List[str] = ["Year", "Month", "Day", "Hour", "Minute"]
    epw_data = epw_data.drop(columns=date_time_columns)

    # Step 4: Reorder columns to put 'DateTime' first
    columns: List[str] = ["DateTime"] + \
        [col for col in epw_data.columns if col != "DateTime"]
    epw_data = epw_data.reindex(columns=columns)

    # Step 5: Correct any '24:00' time to '00:00' of the next day
    epw_data["DateTime"] = epw_data["DateTime"].apply(correct_hour_24)

    # Step 6: Convert 'DateTime' to pandas datetime type
    epw_data["DateTime"] = pd.to_datetime(epw_data["DateTime"])

    return epw_data


def compute_additional_data(epw_data: pd.DataFrame, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Compute additional weather parameters such as vapor density, CO2 density, sky temperature, etc.

    Args:
        epw_data (pd.DataFrame): The preprocessed EPW data.
        df (pd.DataFrame): The raw EPW data.

    Returns:
        tuple: A tuple containing the computed additional data:
            - vaporDens (np.ndarray): Vapor density.
            - co2 (np.ndarray): CO2 density.
            - skyT (np.ndarray): Sky temperature.
            - soilT (np.ndarray): Soil temperature.
            - elevation (float): Elevation.
    """
    # Constants
    SIGMA = 5.6697e-8  # Stefan-Boltzmann constant
    KELVIN = 273.15  # Conversion from Celsius to Kelvin
    SECS_IN_MONTH = 86400 * 365 / 12  # Average number of seconds in a month

    # Define soilTsec function to calculate soil temperature based on time in seconds

    def soilTsec(sec: float) -> float:
        return s[0] * np.sin(2 * np.pi * sec / SECS_IN_MONTH / per + 2 * np.pi / s[2]) + s[3]

    # Define least squares cost function for sinusoidal fit
    def cost_function(b: np.ndarray) -> float:
        return np.sum((b[0] * np.sin(2 * np.pi * x / per + 2 * np.pi / b[2]) + b[3] - y) ** 2)

    # Extract elevation from the raw EPW data
    elevation = float(df.iloc[0, 0].split(",")[-1])

    # Extract relevant data columns from the preprocessed EPW data
    # Global horizontal radiation
    rad = epw_data["Global Horizontal Radiation (J/m²)"]
    temp = epw_data["Dry Bulb Temperature (°C)"]  # Dry bulb temperature
    rh = epw_data["Relative Humidity (%)"]  # Relative humidity
    # Sky radiation
    radSky = epw_data["Horizontal Infrared Radiation Intensity (J/m²)"]

    # Compute vapor density using temperature and relative humidity
    vaporDens = rh2vapor_dens(temp, rh) 

    # Compute CO2 density assuming a constant concentration of 410 ppm
    co2 = co2_ppm2dens(temp, 410)

    # Compute sky temperature from sky radiation
    skyT = (radSky / SIGMA) ** 0.25 - KELVIN

    # Soil temperature calculations
    soilT2 = df.iloc[3, 0].split(",")[1:]  # Extract soil temperature data
    soilT2 = soilT2[21:33]  # Select relevant indices for soil temperature
    y = np.array(soilT2, dtype=float)  # Convert to numpy array of floats
    # Generate x values for the soil temperature points
    x = np.linspace(0.5, 11.5, len(y))

    # Perform sinusoidal fit to the soil temperature data
    yz = y - np.max(y) + (np.max(y) - np.min(y)) / \
        2  # Normalize soil temperature data
    shifted_yz = np.roll(yz, 1)  # Shift the normalized data by one position
    crossings = np.where(yz * shifted_yz <= 0)[0]  # Find zero crossings
    zx = x[crossings]  # Get the x values at zero crossings
    # Calculate the period of the sinusoidal function
    per = 2 * np.mean(np.diff(zx))

    # Initial guess for the sinusoidal fit parameters
    initial_guess = [np.max(y) - np.min(y), per, -1, np.mean(y)]

    # Minimize the cost function to find the best fit parameters
    result = minimize(cost_function, initial_guess, method="Nelder-Mead")
    s = result.x  # Extract the fit parameters
    s[1] = per  # Update the period in the parameters

    # Calculate soil temperature over the year based on the fit
    # Get the start time from the EPW data
    startTime = epw_data["DateTime"].iloc[0]
    # Calculate seconds since the start of the year
    secsInYear = (startTime - datetime(startTime.year,
                  1, 1, 0, 0, 0)).total_seconds()
    # Generate time steps in seconds
    time_diff_seconds = np.arange(0, len(epw_data["DateTime"]) * 3600, 3600)
    # Calculate soil temperature for each time step
    soilT = soilTsec(secsInYear + time_diff_seconds)

    return vaporDens, co2, skyT, soilT, elevation  # Return the computed parameters


def combine_all_data(epw_data: pd.DataFrame, vaporDens: np.ndarray, co2: np.ndarray, skyT: np.ndarray, soilT: np.ndarray, elevation: float) -> pd.DataFrame:
    """
    Combine all weather parameters into a new DataFrame.

    Args:
        epw_data (pd.DataFrame): The preprocessed EPW data.
        vaporDens (np.ndarray): Vapor density.
        co2 (np.ndarray): CO2 density.
        skyT (np.ndarray): Sky temperature.
        soilT (np.ndarray): Soil temperature.
        elevation (float): Elevation.

    Returns:
        pd.DataFrame: A DataFrame containing the combined weather data.
    """
    # Calculate the interval in seconds (1 hour)
    interval = 3600

    # Split the global horizontal radiation data into daily segments
    daily_rad_splits = np.array_split(
        epw_data["Global Horizontal Radiation (J/m²)"], len(epw_data) / 24)

    # Calculate the daily radiation sum in MJ/m^2/day
    daily_rad_sum = [np.sum(day * interval * 1e-6) for day in daily_rad_splits]

    # Expand the daily sums to match the original hourly data length
    expanded_daily_rad_sum = np.repeat(daily_rad_sum, 24)

    # Shift the expanded sums by one hour to align with the next day
    expanded_daily_rad_sum_shifted = np.roll(expanded_daily_rad_sum, -1)
    expanded_daily_rad_sum_shifted[-1] = 0  # Set the last value to 0

    # Calculate vapor pressure from vapor density and temperature
    vapor_pressure = rh2vapor_dens(
        epw_data["Dry Bulb Temperature (°C)"], vaporDens)

    # Create a new DataFrame to combine all weather parameters
    data = pd.DataFrame({
        "DateTime": epw_data["DateTime"],
        "Outdoor global irradiation(W m⁻²)": epw_data["Global Horizontal Radiation (J/m²)"],
        "Outdoor air temperature(°C)": epw_data["Dry Bulb Temperature (°C)"],
        "Outdoor vapor concentration(kg m⁻³)": vaporDens,
        "Outdoor CO2 concentration(kg{CO2} m⁻³{air})": co2,
        "Outdoor wind speed(m s⁻¹)": epw_data["Wind Speed (m/s)"],
        "Sky temperature(°C)": skyT,
        "Temperature of external soil layer (°C)": soilT,
        "Daily light sum (MJ m⁻² day⁻¹)": expanded_daily_rad_sum_shifted,
        "Elevation (m)": elevation,
        "Outdoor vapor pressure (Pa)": vapor_pressure,
    })

    return data


def interpolate_to_hires(startTime: pd.Timestamp, data: pd.DataFrame, epw_data: pd.DataFrame, interval: int = 300) -> pd.DataFrame:
    """
    Interpolate data from 1-hour interval to a specified interval using pchip interpolation.

    Args:
        startTime (pd.Timestamp): The start time of the data.
        data (pd.DataFrame): The data to be interpolated.
        epw_data (pd.DataFrame): The preprocessed EPW data.
        interval (int, optional): The desired interval in seconds. Defaults to 300 (5 minutes).

    Returns:
        pd.DataFrame: The interpolated high-resolution data.
    """
    # Calculate the length of the EPW data
    length = len(epw_data["DateTime"])

    # Create an array of time differences for the original 1-hour interval data
    time_diff_seconds = np.arange(0, length * 3600, 3600)

    # Create an array of new time differences for the specified interval
    new_time_diff_seconds = np.arange(0, length * 3600, interval)

    # Generate new datetime values based on the specified interval
    new_datetimes = [
        startTime + pd.Timedelta(seconds=int(s)) for s in new_time_diff_seconds]

    # Create a new DataFrame to store the interpolated data at the specified interval
    hires_data = pd.DataFrame({"DateTime": new_datetimes})

    # Interpolate each column in the data DataFrame using pchip interpolation
    for column in data.columns[1:]:
        hires_data[column] = pchip_interpolate(
            time_diff_seconds, data[column].values, new_time_diff_seconds)

    return hires_data


def datestr_to_matlab_datenum(date_obj) -> float:
    """
    Convert a datetime or Timestamp object to MATLAB's datenum.

    Args:
        date_obj (datetime or pd.Timestamp): The date object to be converted.

    Returns:
        float: The MATLAB datenum corresponding to the input date.
    """
    # If the input is a pandas Timestamp, convert it to a datetime object
    if isinstance(date_obj, pd.Timestamp):
        date_obj = date_obj.to_pydatetime()

    # Calculate days from 0000/1/1 to the given date
    # MATLAB's datenum starts from 0000/1/1, and the year 0000 is considered a leap year (366 days)
    days_to_date = (date_obj - datetime(1, 1, 1)).days + 366

    # Calculate the fraction of the day represented by the hours, minutes, and seconds
    hours_fraction = (
        date_obj.hour / 24 + date_obj.minute / 1440 + date_obj.second / 86400
    )  # 86400 = 24*60*60 seconds in a day

    # Calculate MATLAB datenum
    # Adding 1 to account for MATLAB's datenum offset
    matlab_datenum = days_to_date + hours_fraction + 1

    return matlab_datenum


def convert_epw2csv(epw_path: str, time_step: int, out_folder: str = "data/energyPlus/inputs") -> str:
    """
    Convert EnergyPlus Weather (EPW) file to a CSV file with additional computed weather parameters.

    Args:
        epw_path (str): Path to the input EPW file.
        time_step (int): Time step in minutes for the output data.
        out_folder (str, optional): Output folder for the converted CSV file. Defaults to "data/energyPlus/inputs".

    Returns:
        str: Path to the output CSV file.
    """
    
    # # Extract filename without extension
    filename = os.path.splitext(os.path.basename(epw_path))[0]
    output_file = f"{out_folder}/{filename}_{time_step}.csv"

    # Check if output file already exists
    if os.path.isfile(output_file):
        return output_file
   
    # Create output folder if it doesn't exist
    os.makedirs(out_folder, exist_ok=True)

    # Read and preprocess weather data
    epw_data = read_epw_data(epw_path)
    epw_data = preprocess_epw_data(epw_data)

    # Read the raw EPW data again
    df = pd.read_csv(epw_path, delimiter="\t", header=None)

    # Compute additional weather parameters
    vaporDens, co2, skyT, soilT, elevation = compute_additional_data(
        epw_data, df)

    # Combine all weather parameters
    data = combine_all_data(epw_data, vaporDens, co2, skyT, soilT, elevation)

    # print("DateTime before: ", data["DateTime"].head())
    
    # Replace DateTime column with MATLAB datenum
    data["DateTime"] = data["DateTime"].apply(datestr_to_matlab_datenum)
    
    # print("DateTime after: ", data["DateTime"].head())
    
    # Save the combined weather data as a new CSV file
    data.to_csv(f"{out_folder}/{filename}.csv", index=False)

    # Generate high-resolution weather data with the specified time interval
    hires_data = interpolate_to_hires(
        epw_data["DateTime"].iloc[0], data, epw_data, interval=time_step * 60)

    # Replace DateTime column in high-resolution data with MATLAB datenum
    hires_data["DateTime"] = hires_data["DateTime"].apply(
        datestr_to_matlab_datenum)

    # Save the high-resolution weather data as a new CSV file
    hires_data.to_csv(output_file, index=False)
    
    print(f"High-resolution weather data saved to: {output_file}")

    return output_file


def check_csv(csv_path: str, timestep: int = None, output_folder: str = "data/energyPlus/inputs") -> str:
    """
    This function checks and processes the DateTime column in the provided CSV file.
    It standardizes the DateTime column to the format 'YYYY-MM-DD HH:MM:SS' and, if needed,
    converts it to MATLAB's datenum format. If a timestep parameter is provided, the function
    will interpolate the data accordingly. The processed CSV file is saved, and the path
    to the file is returned.

    Parameters:
        csv_path (str): The path to the input CSV file.
        timestep (int, optional): The timestep (in minutes) for output data interpolation.
                                  If not specified, no interpolation is performed.
        output_folder (str, optional): The folder path where the processed CSV file will be saved.
                                       Defaults to "data/energyPlus/inputs".

    Returns:
        str: The path to the processed CSV file.
    """
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Check if the DateTime column exists in the DataFrame
    if 'DateTime' not in df.columns:
        raise ValueError("The DateTime column is not found in the CSV file.")
    
    # Check if the first value in the DateTime column is already in MATLAB's datenum format
    first_datetime = df['DateTime'].iloc[0]
    try:
        # MATLAB datenum is a floating-point number, so attempt to convert it to a float.
        # If it can be converted and has no typical date format characteristics, assume it's in datenum format.
        float_value = float(first_datetime)
        if isinstance(float_value, float) and float_value > 0:
            print("The DateTime column is already in MATLAB datenum format, no conversion needed.")
        else:
            raise ValueError
    except ValueError:
        # Try to parse the DateTime column to the standard date-time format 'YYYY-MM-DD HH:MM:SS'
        try:
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            # Format the DateTime column to 'YYYY-MM-DD HH:MM:SS'
            df['DateTime'] = df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise ValueError(f"Failed to parse the DateTime column: {e}")
        
        # Convert the DateTime column to MATLAB's datenum format
        df['DateTime'] = df['DateTime'].apply(lambda x: datestr_to_matlab_datenum(pd.to_datetime(x)))
    
    # If a timestep is specified, perform data interpolation
    if timestep is not None:
        print(f"Interpolating data to {timestep} minutes interval...")
        return convert_csv_with_interpolation(csv_path, timestep, output_folder)
    
    # Extract the file name (without extension) from the original file path
    filename = os.path.splitext(os.path.basename(csv_path))[0]
    
    # Define the output path and ensure the output directory exists
    output_path = os.path.join(output_folder, f"{filename}_checked.csv")
    os.makedirs(output_folder, exist_ok=True)
    
    # Save the processed DataFrame to the specified output path
    df.to_csv(output_path, index=False)
    
 
    
    # Return the path to the processed file
    return output_path


def convert_csv_with_interpolation(csv_path: str, time_step: int, output_folder: str = "data/energyPlus/inputs") -> str:
    """
    This function reads a CSV file provided by the user, interpolates the data based on the specified time step, 
    and saves the processed data to a new CSV file.

    Parameters:
        csv_path (str): The path to the input CSV file.
        time_step (int): The time step (in minutes) for the output data.
        output_folder (str, optional): The folder path where the processed CSV file will be saved.
                                       Defaults to "data/energyPlus/inputs".

    Returns:
        str: The path to the processed CSV file.
    """
    
    # Extract the file name without extension from the original path
    filename = os.path.splitext(os.path.basename(csv_path))[0]
    output_file = f"{output_folder}/{filename}_{time_step}.csv"

    # Check if the output file already exists
    if os.path.isfile(output_file):
        return output_file

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Ensure the DateTime column exists and is in datetime format
    if 'DateTime' not in df.columns:
        raise ValueError("The DateTime column is not found in the CSV file.")
    
    df['DateTime'] = pd.to_datetime(df['DateTime'])

    # Get the start time from the first entry in the DateTime column
    startTime = df['DateTime'].iloc[0]

    # Interpolate the data to the desired time step using a custom interpolation function
    hires_data = interpolate_to_hires(startTime, df, df, interval=time_step * 60)

    # Convert the DateTime column to MATLAB's datenum format
    hires_data["DateTime"] = hires_data["DateTime"].apply(datestr_to_matlab_datenum)

    # Save the interpolated data to a new CSV file
    hires_data.to_csv(output_file, index=False)
    

    return output_file

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.optimize import minimize
from scipy.interpolate import pchip_interpolate
import glob

# Constants
SIGMA = 5.6697e-8
KELVIN = 273.15
SECS_IN_MONTH = 86400 * 365 / 12


def correct_hour_24(time_str):
    """
    Function to correct the '24:00' hour in a datetime string to '00:00' of the next day.

    Parameters:
    time_str (str): The datetime string.

    Returns:
    str: The corrected datetime string.
    """
    if time_str.endswith("24:00"):
        date_part, _ = time_str.split(" ")
        corrected_date = pd.to_datetime(date_part) + pd.DateOffset(days=1)
        return corrected_date.strftime("%Y-%m-%d 00:00")
    else:
        return time_str


def day_light_sum(time, rad):
    """
    Calculate the light sum from the sun [MJ m^{-2} day^{-1}] for each day.
    These values will be constant for each day, and change at midnight.

    Inputs:
        time - timestamps of radiation data.
            These timestamps must be in regular intervals
        rad  - corresponding radiation data (W m^{-2})

    Output:
        lightSum - daily radiation sum, with the same timestamps of time (MJ m^{-2} day^{-1})
    """

    interval = (time[1] - time[0]) * 86400  # interval in time data, in seconds
    mn_before = 0  # the midnight before the current point
    mn_after = (
        np.where(np.diff(np.floor(time)) == 1)[0][0] + 1
    )  # the midnight after the current point

    light_sum = np.zeros(len(time))

    for k in range(len(time)):
        # sum from midnight before until midnight after (not including)
        light_sum[k] = np.sum(rad[mn_before:mn_after])

        if k == mn_after - 1:  # reached new day
            mn_before = mn_after
            new_day_indices = np.where(
                np.diff(np.floor(time[mn_before + 1:])) == 1)[0]

            if len(new_day_indices) > 0:
                mn_after = new_day_indices[0] + mn_before + 2
            else:
                mn_after = len(time)

    # convert to MJ/m2/day
    light_sum = light_sum * interval * 1e-6

    return light_sum


def rh2vaporDens(temp, rh):
    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    Mw = 18.01528e-3  # molar mass of water [kg mol^-{1}]
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]
    # Saturation vapor pressure of air in given temperature [Pa]
    satP = p[0] * np.exp(p[2] * temp / (temp + p[1]))
    pascals = (rh / 100) * satP  # Partial pressure of vapor in air [Pa]
    # convert to density using the ideal gas law
    vaporDens = pascals * Mw / (R * (temp + C2K))
    return vaporDens


def vaporDens2pres(temp, vaporDens):
    p = [610.78, 238.3, 17.2694, -6140.4, 273, 28.916]
    rh = vaporDens / rh2vaporDens(temp, 100)  # relative humidity [0-1]
    # Saturation vapor pressure of air in given temperature [Pa]
    satP = p[0] * np.exp(p[2] * temp / (temp + p[1]))
    vaporPres = satP * rh
    return vaporPres


def co2ppm2dens(temp, ppm):
    """
    Convert CO2 molar concentration [ppm] to density [kg m^{-3}]

    Parameters:
        temp (array_like): given temperatures [°C]
        ppm (array_like): CO2 concentration in air [ppm]

    Returns:
        co2Dens (ndarray): CO2 concentration in air [kg m^{-3}]
    """
    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    M_CO2 = 44.01e-3  # molar mass of CO2 [kg mol^-{1}]
    P = 101325  # pressure (assumed to be 1 atm) [Pa]

    # number of moles n = m / M_CO2 where m is the mass [kg] and M_CO2 is the
    # molar mass [kg mol^{-1}]. So m = p * V * M_CO2 * P / RT where V is 10^-6 * ppm
    co2Dens = P * 10**-6 * ppm * M_CO2 / (R * (temp + C2K))

    return co2Dens


def read_epw_data(epw_path):
    """读取.epw文件并返回对应的pandas DataFrame."""
    column_names = [
        "Year",
        "Month",
        "Day",
        "Hour",
        "Minute",
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
    epw_data = pd.read_csv(epw_path, skiprows=8, header=None)

    assert (
        len(column_names) == epw_data.shape[1]
    ), "Column names length doesn't match data columns number."
    epw_data.columns = column_names

    return epw_data


def preprocess_epw_data(epw_data):
    """
    Preprocess weather data, including deleting and renaming columns, handling time, etc.

    Args:
        epw_data (pandas.DataFrame): The input EPW data.

    Returns:
        pandas.DataFrame: The preprocessed EPW data.
    """
    epw_data["Minute"] = epw_data["Minute"].astype(str).replace("60", "0")
    epw_data["DateTime"] = (
        epw_data["Year"].astype(str)
        + "-"
        + epw_data["Month"].astype(str).str.zfill(2)
        + "-"
        + epw_data["Day"].astype(str).str.zfill(2)
        + " "
        + epw_data["Hour"].astype(str).str.zfill(2)
        + ":"
        + epw_data["Minute"].astype(str).str.zfill(2)
    )
    epw_data = epw_data.drop(["Year", "Month", "Day", "Hour", "Minute"], axis=1)
    columns = ["DateTime"] + [col for col in epw_data.columns if col != "DateTime"]
    epw_data = epw_data.reindex(columns=columns)
    epw_data["DateTime"] = epw_data["DateTime"].apply(correct_hour_24)
    epw_data["DateTime"] = pd.to_datetime(epw_data["DateTime"])
    return epw_data


def compute_additional_data(epw_data, df):
    """
    Compute additional weather parameters such as vapor density, CO2 density, sky temperature, etc.

    Args:
        epw_data (pandas.DataFrame): The preprocessed EPW data.
        df (pandas.DataFrame): The raw EPW data.

    Returns:
        tuple: A tuple containing the computed additional data:
            - vaporDens (numpy.ndarray): Vapor density.
            - co2 (numpy.ndarray): CO2 density.
            - skyT (numpy.ndarray): Sky temperature.
            - soilT (numpy.ndarray): Soil temperature.
            - elevation (float): Elevation.
    """
    # Define soilTsec function
    def soilTsec(sec):
        return (
            s[0] * np.sin(2 * np.pi * sec / SECS_IN_MONTH / per + 2 * np.pi / s[2])
            + s[3]
        )

    # Define least squares cost function
    def cost_function(b):
        return np.sum(
            (b[0] * np.sin(2 * np.pi * x / per + 2 * np.pi / b[2]) + b[3] - y) ** 2
        )

    elevation = df.iloc[0, 0].split(",")[-1]

    rad = epw_data["Global Horizontal Radiation (J/m²)"]
    temp = epw_data["Dry Bulb Temperature (°C)"]
    rh = epw_data["Relative Humidity (%)"]
    radSky = epw_data["Horizontal Infrared Radiation Intensity (J/m²)"]

    vaporDens = rh2vaporDens(temp, rh)
    vapor_pressure = vaporDens2pres(temp, vaporDens)
    co2 = co2ppm2dens(temp, 410)
    skyT = (radSky / SIGMA) ** 0.25 - KELVIN

    # SoilT calculations
    soilT2 = df.iloc[3, 0].split(",")[1:]
    soilT2 = soilT2[21:33]
    y = np.array(soilT2, dtype=float)
    x = np.linspace(0.5, 11.5, len(y))

    yz = y - np.max(y) + (np.max(y) - np.min(y)) / 2
    shifted_yz = np.roll(yz, 1)
    crossings = np.where(yz * shifted_yz <= 0)[0]
    zx = x[crossings]
    per = 2 * np.mean(np.diff(zx))

    initial_guess = [np.max(y) - np.min(y), per, -1, np.mean(y)]
    result = minimize(cost_function, initial_guess, method="Nelder-Mead")
    s = result.x
    s[1] = per

    startTime = epw_data["DateTime"].iloc[0]
    secsInYear = (startTime - datetime(startTime.year, 1, 1, 0, 0, 0)).total_seconds()
    time_diff_seconds = np.arange(0, len(epw_data["DateTime"]) * 3600, 3600)
    soilT = soilTsec(secsInYear + time_diff_seconds)

    return vaporDens, co2, skyT, soilT, elevation


def combine_all_data(epw_data, vaporDens, co2, skyT, soilT, elevation):
    """
    Combine all weather parameters into a new DataFrame.

    Args:
        epw_data (pandas.DataFrame): The preprocessed EPW data.
        vaporDens (numpy.ndarray): Vapor density.
        co2 (numpy.ndarray): CO2 density.
        skyT (numpy.ndarray): Sky temperature.
        soilT (numpy.ndarray): Soil temperature.
        elevation (float): Elevation.

    Returns:
        pandas.DataFrame: A DataFrame containing the combined weather data.
    """
    # Calculate daily light sum
    interval = 3600
    daily_rad_splits = np.array_split(
        epw_data["Global Horizontal Radiation (J/m²)"], len(epw_data) / 24
    )
    daily_rad_sum = [np.sum(day * interval * 1e-6) for day in daily_rad_splits]
    expanded_daily_rad_sum = np.repeat(daily_rad_sum, 24)
    expanded_daily_rad_sum_shifted = np.roll(expanded_daily_rad_sum, -1)
    expanded_daily_rad_sum_shifted[-1] = 0

    # Extract other required data from the original DataFrame

    # Assuming vaporDens2pres is defined
    vapor_pressure = vaporDens2pres(epw_data["Dry Bulb Temperature (°C)"], vaporDens)

    data = pd.DataFrame(
        {
            "DateTime": epw_data["DateTime"],
            "Outdoor global irradiation(W m⁻²)": epw_data[
                "Global Horizontal Radiation (J/m²)"
            ],
            "Outdoor air temperature(°C)": epw_data["Dry Bulb Temperature (°C)"],
            "Outdoor vapor concentration(kg m⁻³)": vaporDens,
            "Outdoor CO2 concentration(kg{CO2} m⁻³{air})": co2,
            "Outdoor wind speed(m s⁻¹)": epw_data["Wind Speed (m/s)"],
            "Sky temperature(°C)": skyT,
            "temperature of external soil layer (°C)": soilT,
            "daily light sum (MJ m^{-2} day^{-1})": expanded_daily_rad_sum_shifted,
            "elevation(m)": elevation,
            "Outdoor vapor pressure(Pa)": vapor_pressure,
        }
    )
    return data


def interpolate_to_hires(startTime, data, length, epw_data, interval=300):
    """
    Interpolate data from 1-hour interval to a specified interval using pchip interpolation.

    Args:
        startTime (pandas.Timestamp): The start time of the data.
        data (pandas.DataFrame): The data to be interpolated.
        length (int): The length of the original EPW data.
        epw_data (pandas.DataFrame): The preprocessed EPW data.
        interval (int, optional): The desired interval in seconds. Defaults to 300 (5 minutes).

    Returns:
        pandas.DataFrame: The interpolated high-resolution data.
    """
    # Calculate time differences
    length = len(epw_data["DateTime"])

    # Original 1-hour interval, representing seconds from start time to end time, every hour.
    time_diff_seconds = np.arange(0, length * 3600, 3600)

    # Use pchip interpolation to interpolate data from 1-hour interval to the specified interval
    new_time_diff_seconds = np.arange(0, length * 3600, interval)
    new_datetimes = [
        startTime + pd.Timedelta(seconds=int(s)) for s in new_time_diff_seconds
    ]

    # Create a new DataFrame to store the interpolated data at the specified interval
    hires_data = pd.DataFrame({"DateTime": new_datetimes})

    for column in data.columns[1:]:
        hires_data[column] = pchip_interpolate(
            time_diff_seconds, data[column].values, new_time_diff_seconds
        )

    return hires_data


def datestr_to_matlab_datenum(date_obj) -> float:
    """
    Convert a datetime or Timestamp object to MATLAB's datenum.

    Args:
        date_obj (datetime.datetime or pandas.Timestamp): The date object to be converted.

    Returns:
        float: The MATLAB datenum corresponding to the input date.
    """
    # If the input is a pandas Timestamp, convert it to a datetime object
    if isinstance(date_obj, pd.Timestamp):
        date_obj = date_obj.to_pydatetime()

    # Calculate days from 0000/1/1 to the given date
    # Adding 366 for the year 0000 being a leap year
    days_to_date = (date_obj - datetime(1, 1, 1)).days + 366

    # Calculate hours in fraction of a day
    hours_fraction = (
        date_obj.hour / 24 + date_obj.minute / 1440 + date_obj.second / 86400
    )  # 86400 = 24*60*60 seconds in a day

    # Calculate MATLAB datenum
    matlab_datenum = days_to_date + hours_fraction + 1

    return matlab_datenum
 

def convert_epw2csv(epw_path, time_step, out_folder="data/energyPlus/inputs"):
    """
    Convert EnergyPlus Weather (EPW) file to a CSV file with additional computed weather parameters.

    Args:
        epw_path (str): Path to the input EPW file.
        time_step (int): Time step in minutes for the output data.
        out_folder (str, optional): Output folder for the converted CSV file. Defaults to "data/energyPlus/inputs".

    Returns:
        str: Path to the output CSV file.
    """
    filename = os.path.splitext(os.path.basename(epw_path))[0]
    output_file = f"{out_folder}/{filename}_{time_step}.csv"
    
    # Check if output file exists
    if os.path.isfile(output_file):
        return output_file
    
    # Create output folder if it doesn't exist
    os.makedirs(out_folder, exist_ok=True)
    print(f"Converting {epw_path} to {output_file} in {time_step} minutes interval")
    
    # Read and preprocess weather data
    epw_data = read_epw_data(epw_path)
    epw_data = preprocess_epw_data(epw_data)
    
    # Read the .epw file again to get the raw data
    df = pd.read_csv(epw_path, delimiter="\t", header=None)
    
    # Compute additional weather parameters
    vaporDens, co2, skyT, soilT, elevation = compute_additional_data(epw_data, df)
    
    # Combine all weather parameters
    data = combine_all_data(epw_data, vaporDens, co2, skyT, soilT, elevation)
    
    # Replace DateTime column in data with MATLAB datenum using datestr_to_matlab_datenum function
    data["DateTime"] = data["DateTime"].apply(datestr_to_matlab_datenum)
    
    # Save as a new weather data CSV file
    data.to_csv(f"{out_folder}/{filename}.csv", index=False)
    
    # Generate high-resolution weather data with a time interval of 5 minutes
    hires_data = interpolate_to_hires(epw_data["DateTime"].iloc[0], data, len(epw_data["DateTime"]), epw_data, interval=time_step * 60)
    
    # Replace DateTime column in hires_data with MATLAB datenum using datestr_to_matlab_datenum function
    hires_data["DateTime"] = hires_data["DateTime"].apply(datestr_to_matlab_datenum)
    
    # Save as a new 5-minute interval external weather data CSV file
    hires_data.to_csv(output_file, index=False)
    
    return output_file
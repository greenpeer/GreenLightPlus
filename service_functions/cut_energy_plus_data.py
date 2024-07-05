import scipy.io as sio
import numpy as np
import pandas as pd


def cut_energy_plus_data_csv(first_day, season_length, csv_path):
    """
    Cut data from EnergyPlus weather CSV file to the required season segment.

    Args:
        first_day (float): Where to start looking at the data (days since start of the year).
                           Example: 1 (Jan 1)
        season_length (float): Length of the input in days (fractions accepted). Example: 1
        csv_path (str): Path of the CSV file containing EnergyPlus data.

    Returns:
        numpy.ndarray: A matrix with the data cut to the specified season.

    Note:
        - The input data should have timestamps in the first column (MATLAB datenum format).
        - The start and end dates of the required season are specified by first_day and season_length.
        - If the season passes over the end of the year, this function will reset the date back to
          the beginning of the year.
    """
    SECONDS_IN_DAY = 24 * 60 * 60

    # Read CSV file
    df = pd.read_csv(csv_path)

    # Assume the first column is timestamps (MATLAB datenum format)
    input_data = df.values
    timestamps = input_data[:, 0]

    # Calculate interval time (assuming all data intervals are equal)
    interval = (timestamps[1] - timestamps[0]) * SECONDS_IN_DAY

    # Adjust start and end times based on first_day and season_length
    year_shift = np.floor(first_day / 365)
    first_day = first_day % 365

    start_point = int(1 + round((first_day - 1) * SECONDS_IN_DAY / interval)) - 1
    end_point = int(start_point + round(season_length * SECONDS_IN_DAY / interval)) + 1

    data_length = len(timestamps)
    new_years = int((end_point - end_point % data_length) / data_length)

    if end_point <= data_length:
        season = input_data[start_point:end_point, :]
    else:
        season = input_data[start_point:, :]
        reset_date = timestamps - timestamps[0] + interval / SECONDS_IN_DAY
        for n in range(new_years - 1):
            date_shift = reset_date + season[-1, 0]
            input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
            season = np.vstack((season, input_date_shift))
        end_point = end_point % data_length
        date_shift = reset_date + season[-1, 0]
        input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
        season = np.vstack((season, input_date_shift[:end_point, :]))

    return season


def cut_energy_plus_data(first_day, season_length, path):
    """
    Cut data from EnergyPlus MAT file to the required season segment.

    Args:
        first_day (float): Where to start looking at the data (days since start of the year).
                           Example: 1 (Jan 1)
        season_length (float): Length of the input in days (fractions accepted). Example: 1
        path (str): Path of a MAT file in the EnergyPlus format, created using saveWeatherMat
                    and has a variable named 'hiresWeather' in the expected format.

    Returns:
        numpy.ndarray: A matrix with the same format of hiresWeather, cut to the specified season.

    Note:
        - The input data should have the format as in hiresWeather.
        - The start and end dates of the required season are specified by first_day and season_length.
        - If the season passes over the end of the year, this function will reset the date back to
          the beginning of the year.
    """
    SECONDS_IN_DAY = 24 * 60 * 60

    # Load hi res seljaar
    mat_contents = sio.loadmat(path)
    input_data = mat_contents["hiresWeather"]

    # Cut out the required season
    interval = (
        input_data[1, 0] - input_data[0, 0]
    ) * SECONDS_IN_DAY  # Assumes all data is equally spaced

    year_shift = np.floor(first_day / 365)  # If first_day is bigger than 365
    first_day = first_day % 365  # In case value is bigger than 365

    # Use only needed dates
    start_point = int(1 + round((first_day - 1) * SECONDS_IN_DAY / interval)) - 1
    end_point = int(start_point + round(season_length * SECONDS_IN_DAY / interval)) + 1

    data_length = len(input_data[:, 0])
    new_years = int((end_point - end_point % data_length) / data_length)

    if end_point <= data_length:
        season = input_data[start_point:end_point, :]
    else:  # Required season passes over end of year
        season = input_data[start_point:, :]
        reset_date = input_data[:, 0] - input_data[0, 0] + interval / SECONDS_IN_DAY
        for n in range(new_years - 1):
            date_shift = reset_date + season[-1, 0]
            input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
            season = np.vstack((season, input_date_shift))
        end_point = end_point % data_length
        date_shift = reset_date + season[-1, 0]
        input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
        season = np.vstack((season, input_date_shift[:end_point, :]))

    return season


def cut_energy_plus_data_csv_extreme(first_day, season_length, csv_path, is_summer=True):
    """
    Cut data from EnergyPlus weather CSV file to the required season segment with extreme weather modifications.

    Args:
        first_day (float): Where to start looking at the data (days since start of the year).
                           Example: 1 (Jan 1)
        season_length (float): Length of the input in days (fractions accepted). Example: 1
        csv_path (str): Path of the CSV file containing EnergyPlus data.
        is_summer (bool, optional): Indicates if the season is summer. Defaults to True.

    Returns:
        numpy.ndarray: A matrix with the data cut to the specified season and modified for extreme weather.

    Note:
        - The input data should have timestamps in the first column (MATLAB datenum format).
        - The start and end dates of the required season are specified by first_day and season_length.
        - If the season passes over the end of the year, this function will reset the date back to
          the beginning of the year.
        - The weather data is modified to be more extreme based on the season (summer or winter).
    """
    # Set random seed
    np.random.seed(42)
    
    SECONDS_IN_DAY = 24 * 60 * 60

    # Read CSV file
    df = pd.read_csv(csv_path)

    # Assume the first column is timestamps (MATLAB datenum format)
    input_data = df.values
    timestamps = input_data[:, 0]

    # Calculate interval time (assuming all data intervals are equal)
    interval = (timestamps[1] - timestamps[0]) * SECONDS_IN_DAY

    # Adjust start and end times based on first_day and season_length
    year_shift = np.floor(first_day / 365)
    first_day = first_day % 365

    start_point = int(1 + round((first_day - 1) * SECONDS_IN_DAY / interval)) - 1
    end_point = int(start_point + round(season_length * SECONDS_IN_DAY / interval)) + 1

    data_length = len(timestamps)
    new_years = int((end_point - end_point % data_length) / data_length)

    if end_point <= data_length:
        season = input_data[start_point:end_point, :]
    else:
        season = input_data[start_point:, :]
        reset_date = timestamps - timestamps[0] + interval / SECONDS_IN_DAY
        for n in range(new_years - 1):
            date_shift = reset_date + season[-1, 0]
            input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
            season = np.vstack((season, input_date_shift))
        end_point = end_point % data_length
        date_shift = reset_date + season[-1, 0]
        input_date_shift = np.column_stack((date_shift, input_data[:, 1:]))
        season = np.vstack((season, input_date_shift[:end_point, :]))

    # Set thresholds and ranges for extreme weather based on season
    if is_summer:
        irradiation_high, irradiation_low = 1000, 200
        temperature_high, temperature_low = 35, 20
        vapor_high, vapor_low = 0.025, 0.01
        co2_high, co2_low = 0.001, 0.0004
        wind_speed_high, wind_speed_low = 15, 2
        sky_temperature_high, sky_temperature_low = 30, 10
        soil_temperature_high, soil_temperature_low = 35, 20
        light_sum_high, light_sum_low = 30, 10
        vapor_pressure_high, vapor_pressure_low = 3000, 1000
    else:
        irradiation_high, irradiation_low = 500, 50
        temperature_high, temperature_low = 10, -10
        vapor_high, vapor_low = 0.005, 0.001
        co2_high, co2_low = 0.0008, 0.0002
        wind_speed_high, wind_speed_low = 25, 0.1
        sky_temperature_high, sky_temperature_low = 5, -20
        soil_temperature_high, soil_temperature_low = 10, -5
        light_sum_high, light_sum_low = 10, 1
        vapor_pressure_high, vapor_pressure_low = 1000, 100

    # Modify weather data to be more extreme
    for i in range(len(season)):
        # Outdoor global irradiation (W m⁻²)
        if season[i, 1] > irradiation_high:
            season[i, 1] = np.random.uniform(irradiation_high, irradiation_high * 1.2)
        elif season[i, 1] < irradiation_low:
            season[i, 1] = np.random.uniform(irradiation_low * 0.8, irradiation_low)

        # Outdoor air temperature (°C)
        if season[i, 2] > temperature_high:
            season[i, 2] = np.random.uniform(temperature_high, temperature_high + 5)
        elif season[i, 2] < temperature_low:
            season[i, 2] = np.random.uniform(temperature_low - 5, temperature_low)

        # Outdoor vapor concentration (kg m⁻³)
        if season[i, 3] > vapor_high:
            season[i, 3] = np.random.uniform(vapor_high, vapor_high * 1.2)
        elif season[i, 3] < vapor_low:
            season[i, 3] = np.random.uniform(vapor_low * 0.8, vapor_low)

        # Outdoor CO2 concentration (kg{CO2} m⁻³{air})
        if season[i, 4] > co2_high:
            season[i, 4] = np.random.uniform(co2_high, co2_high * 1.2)
        elif season[i, 4] < co2_low:
            season[i, 4] = np.random.uniform(co2_low * 0.8, co2_low)

        # Outdoor wind speed (m s⁻¹)
        if season[i, 5] > wind_speed_high:
            season[i, 5] = np.random.uniform(wind_speed_high, wind_speed_high * 1.2)
        elif season[i, 5] < wind_speed_low:
            season[i, 5] = np.random.uniform(wind_speed_low * 0.8, wind_speed_low)

        # Sky temperature (°C)
        if season[i, 6] > sky_temperature_high:
            season[i, 6] = np.random.uniform(sky_temperature_high, sky_temperature_high + 5)
        elif season[i, 6] < sky_temperature_low:
            season[i, 6] = np.random.uniform(sky_temperature_low - 5, sky_temperature_low)

        # Temperature of external soil layer (°C)
        if season[i, 7] > soil_temperature_high:
            season[i, 7] = np.random.uniform(soil_temperature_high, soil_temperature_high + 5)
        elif season[i, 7] < soil_temperature_low:
            season[i, 7] = np.random.uniform(soil_temperature_low - 5, soil_temperature_low)

        # Daily light sum (MJ m^{-2} day^{-1})
        if season[i, 8] > light_sum_high:
            season[i, 8] = np.random.uniform(light_sum_high, light_sum_high * 1.2)
        elif season[i, 8] < light_sum_low:
            season[i, 8] = np.random.uniform(light_sum_low * 0.8, light_sum_low)

        # Outdoor vapor pressure (Pa)
        if season[i, 10] > vapor_pressure_high:
            season[i, 10] = np.random.uniform(vapor_pressure_high, vapor_pressure_high * 1.2)
        elif season[i, 10] < vapor_pressure_low:
            season[i, 10] = np.random.uniform(vapor_pressure_low * 0.8, vapor_pressure_low)

    return season
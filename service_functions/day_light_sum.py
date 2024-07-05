from typing import Union, Tuple, List, Dict
import numpy as np

# GreenLightPlus/service_functions/day_light_sum.py
def day_light_sum(time: Union[List[float], np.ndarray], rad: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Calculate the daily light sum from the sun [MJ m^{-2} day^{-1}].

    This function computes the daily sum of solar radiation. The resulting values
    are constant for each day and change at midnight.

    Args:
        time (array-like): Timestamps of radiation data. Must be in regular intervals.
        rad (array-like): Corresponding radiation data (W m^{-2}).

    Returns:
        np.ndarray: Daily radiation sum, with the same timestamps as input (MJ m^{-2} day^{-1}).
    """
    # Calculate the time interval in seconds
    interval = (time[1] - time[0]) * 86400  # Convert from days to seconds

    # Initialize the index for the midnight before the current point
    midnight_before = 0

    # Find the index of the first midnight after the start
    midnight_after = np.where(np.diff(np.floor(time)) == 1)[0][0] + 1

    # Initialize an array to store the daily light sum for each timestamp
    light_sum = np.zeros(len(time))

    # Iterate through all timestamps
    for k in range(len(time)):
        # Calculate the sum of radiation from midnight before to midnight after
        light_sum[k] = np.sum(rad[midnight_before:midnight_after])

        # Check if we've reached a new day
        if k == midnight_after - 1:
            # Update midnight_before to the current midnight
            midnight_before = midnight_after

            # Find the indices of the next midnights
            new_day_indices = np.where(
                np.diff(np.floor(time[midnight_before + 1:])) == 1)[0]

            # If there are more midnights, update midnight_after
            if len(new_day_indices) > 0:
                midnight_after = new_day_indices[0] + midnight_before + 2
            else:
                # If no more midnights, set to the end of the data
                midnight_after = len(time)

    # Convert the sum from W*s/m^2 to MJ/m^2/day
    light_sum *= interval * 1e-6  # 1e-6 converts from J to MJ

    return light_sum
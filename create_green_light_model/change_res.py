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


import numpy as np
from .set_gl_aux import set_gl_aux
from .set_gl_control import set_gl_control


def interpolate_time(data_matrix, time_step):
    """
    Interpolate data to a new time step.

    Args:
        data_matrix (np.ndarray): Data matrix with time in the first column and y data in the remaining columns.
        time_step (float): New time step to interpolate data to.

    Returns:
        np.ndarray: Data matrix with interpolated y data at the new time step.
    """

    time = data_matrix[:, 0]  # Assume time is in seconds.
    new_time = np.arange(time[0], time[-1], time_step)
    y_data = data_matrix[:, 1:]
    new_y_data = np.column_stack(
        [np.interp(new_time, time, y_data[:, i])
         for i in range(y_data.shape[1])]
    )
    return np.column_stack((new_time[:, np.newaxis], new_y_data))


def process_data(gl, x_matrix, d_matrix):
    """
    Process data using a given gl dictionary.

    Args:
        gl (dict): Dictionary containing the values of the variables used in the calculations.
        x_matrix (np.ndarray): Matrix containing the values of the independent variables.
        d_matrix (np.ndarray): Matrix containing the values of the dependent variables.

    Returns:
        tuple: Two matrices containing the values of the u and a variables.
    """

    x_keys = list(gl["x"].keys())
    d_keys = list(gl["d"].keys())

    num_rows = len(x_matrix)
    a_len = len(gl["a"].keys())
    u_len = len(gl["u"].keys())

    temp_list_a = np.empty((num_rows, a_len + 1))
    temp_list_u = np.empty((num_rows, u_len + 1))

    for count, (x_row, d_row) in enumerate(zip(x_matrix, d_matrix)):
        gl["x"] = dict(zip(x_keys, x_row[1:]))
        gl["d"] = dict(zip(d_keys, d_row[1:]))

        # Set the auxiliary variables
        set_gl_aux(gl)
        # Set the control variables
        set_gl_control(gl)
        # Set the auxiliary variables
        set_gl_aux(gl)

        temp_list_a[count] = np.hstack(([x_row[0]], list(gl["a"].values())))
        temp_list_u[count] = np.hstack(([x_row[0]], list(gl["u"].values())))

    return temp_list_u, temp_list_a


def reorganize_dict(gl, key, new_data):
    """
    Reorganize a dictionary with new data.

    Args:
        gl (dict): Dictionary to reorganize.
        key (str): Key to reorganize within the dictionary.
        new_data (np.ndarray): New data to add to the dictionary.

    Returns:
        dict: The updated dictionary.
    """
    # Retrieve the dictionary at the specified key.
    my_dict = gl[key]

    # Create a new column stack for each key in the dictionary.
    col_stack = [
        np.column_stack(
            (new_data[:, 0], new_data[:, idx + 1])
        )  # Use the first column of new_data and either the (idx+1)th column of new_data or a column of zeros.
        # If new_data has more than (idx+1) columns...
        if new_data.shape[1] > idx + 1
        else np.column_stack(
            (new_data[:, 0], np.zeros(new_data.shape[0]))
        )  # ...use a column of zeros.
        # Loop through the keys in the dictionary.
        for idx in range(len(my_dict))
    ]

    # Update the dictionary with the new column stacks.
    gl[key] = dict(zip(my_dict.keys(), col_stack))
    return gl


def change_res(gl, d, sol, time_step=300):
    """
    Changes the resolution of the GreenLight model solution by interpolating the solution at a different time step.
    Args:
        gl (dict): A dictionary containing the GreenLight model variables.
        d (np.ndarray): An array of the environmental inputs to the model.
        sol (scipy.integrate.ode solution): The solution of the GreenLight model.
        time_step (float): The time step at which to interpolate the solution.

    Returns:
        dict: A dictionary containing the GreenLight model variables interpolated at the new time step.
    """

    # Calculate the interpolation using a vectorized method, where time_step = sol.t
    d_matrix = np.column_stack(
        (sol.t, *[np.interp(sol.t, d[:, 0], d[:, i])
         for i in range(1, d.shape[1])])
    )
    x_matrix = np.column_stack((sol.t, sol.y.T))  # 在ndarray数组的第一列插入t数组

    # Calculate u and a based on x and d
    u_matrix, a_matrix = process_data(gl, x_matrix, d_matrix)

    # Interpolate d_matrix
    d_matrix = interpolate_time(d_matrix, time_step)

    # Interpolate x_matrix
    x_matrix = interpolate_time(x_matrix, time_step)

    # Interpolate u_matrix
    u_matrix = interpolate_time(u_matrix, time_step)

    # Interpolate a_matrix
    a_matrix = interpolate_time(a_matrix, time_step)

    # Reorganize the dictionary
    gl = reorganize_dict(gl, "u", u_matrix)
    gl = reorganize_dict(gl, "a", a_matrix)
    gl = reorganize_dict(gl, "d", d_matrix)
    gl = reorganize_dict(gl, "x", x_matrix)

    return gl

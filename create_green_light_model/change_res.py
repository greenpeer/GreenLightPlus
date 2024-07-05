# File path: GreenLightPlus/create_green_light_model/change_res.py
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

import numpy as np
from .set_gl_aux import set_gl_aux
from .set_gl_control import set_gl_control

class GreenLightChangeRes:
    def __init__(self, gl):
        self.gl = gl


    def _process_data(self, x_matrix, d_matrix):
        """
        Process data using a given gl dictionary.

        Args:
            x_matrix (np.ndarray): Matrix containing the values of the independent variables.
            d_matrix (np.ndarray): Matrix containing the values of the dependent variables.

        Returns:
            tuple: Two matrices containing the values of the u and a variables.
        """
        # Extract keys for x and d variables
        x_keys = list(self.gl["x"].keys())
        d_keys = list(self.gl["d"].keys())

        num_rows = len(x_matrix)
        a_len = len(self.gl["a"].keys())
        u_len = len(self.gl["u"].keys())

        # Initialize temporary lists for a and u variables
        temp_list_a = np.empty((num_rows, a_len + 1))
        temp_list_u = np.empty((num_rows, u_len + 1))

        # Process each row of x and d matrices
        for count, (x_row, d_row) in enumerate(zip(x_matrix, d_matrix)):
            # Update gl dictionary with current x and d values
            self.gl["x"] = dict(zip(x_keys, x_row[1:]))
            self.gl["d"] = dict(zip(d_keys, d_row[1:]))

            # Set the auxiliary variables
            set_gl_aux(self.gl)
            # Set the control variables
            set_gl_control(self.gl)
            # Set the auxiliary variables again
            set_gl_aux(self.gl)

            # Store calculated a and u values
            temp_list_a[count] = np.hstack(([x_row[0]], list(self.gl["a"].values())))
            temp_list_u[count] = np.hstack(([x_row[0]], list(self.gl["u"].values())))

        return temp_list_u, temp_list_a

    def _interpolate_time(self, data_matrix, time_step):
        """
        Interpolate data to a new time step.

        Args:
            data_matrix (np.ndarray): Data matrix with time in the first column and y data in the remaining columns.
            time_step (float): New time step to interpolate data to.

        Returns:
            np.ndarray: Data matrix with interpolated y data at the new time step.
        """
        # Extract time column
        time = data_matrix[:, 0]  # Assume time is in seconds
        # Create new time array with desired time step
        new_time = np.arange(time[0], time[-1], time_step)
        # Extract y data
        y_data = data_matrix[:, 1:]
        # Interpolate y data for each column
        new_y_data = np.column_stack(
            [np.interp(new_time, time, y_data[:, i])
             for i in range(y_data.shape[1])]
        )
        # Combine new time and interpolated y data
        return np.column_stack((new_time[:, np.newaxis], new_y_data))

    def _reorganize_dict(self, key, new_data):
        """
        Reorganize a dictionary with new data.

        Args:
            key (str): Key to reorganize within the dictionary.
            new_data (np.ndarray): New data to add to the dictionary.

        Returns:
            dict: The updated dictionary.
        """
        # Retrieve the dictionary at the specified key
        my_dict = self.gl[key]

        # Create a new column stack for each key in the dictionary
        col_stack = [
            np.column_stack(
                (new_data[:, 0], new_data[:, idx + 1])
            ) if new_data.shape[1] > idx + 1 else np.column_stack(
                (new_data[:, 0], np.zeros(new_data.shape[0]))
            )
            for idx in range(len(my_dict))
        ]

        # Update the dictionary with the new column stacks
        self.gl[key] = dict(zip(my_dict.keys(), col_stack))
        return self.gl

    def change_res(self, d, sol, time_step=300):
        """
        Changes the resolution of the GreenLight model solution by interpolating the solution at a different time step.

        Args:
            d (np.ndarray): An array of the environmental inputs to the model.
            sol (scipy.integrate.ode solution): The solution of the GreenLight model.
            time_step (float): The time step at which to interpolate the solution.

        Returns:
            dict: A dictionary containing the GreenLight model variables interpolated at the new time step.
        """
        # Interpolate d matrix to match solution time points
        d_matrix = np.column_stack(
            (sol.t, *[np.interp(sol.t, d[:, 0], d[:, i])
             for i in range(1, d.shape[1])])
        )
        # Combine solution time and state variables
        x_matrix = np.column_stack((sol.t, sol.y.T))

        # Calculate u and a based on x and d
        u_matrix, a_matrix = self._process_data(x_matrix, d_matrix)

        # Interpolate all matrices to the new time step
        d_matrix = self._interpolate_time(d_matrix, time_step)
        x_matrix = self._interpolate_time(x_matrix, time_step)
        u_matrix = self._interpolate_time(u_matrix, time_step)
        a_matrix = self._interpolate_time(a_matrix, time_step)

        # Reorganize the gl dictionary with the new interpolated data
        self.gl = self._reorganize_dict("u", u_matrix)
        self.gl = self._reorganize_dict("a", a_matrix)
        self.gl = self._reorganize_dict("d", d_matrix)
        self.gl = self._reorganize_dict("x", x_matrix)

        return self.gl
    

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
    # Create GreenLightChangeRes instance
    gl_change_res = GreenLightChangeRes(gl)
    # Change resolution of GreenLight model
    return gl_change_res.change_res(d, sol, time_step)
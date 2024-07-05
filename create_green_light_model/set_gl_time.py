# File path: GreenLightPlus/create_green_light_model/set_gl_time.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

David Katzin, Simon van Mourik, Frank Kempkes, and Eldert J. Van Henten. 2020. “GreenLight - An Open Source Model for Greenhouses with Supplemental Lighting: Evaluation of Heat Requirements under LED and HPS Lamps.” Biosystems Engineering 194: 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010


New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

import numpy as np

def set_gl_time(gl):
    """
    Set time phase for a GreenLight greenhouse model.
    Should be used after the weather inputs for gl have been defined.

    Args:
        gl: A GreenLight model nested dictionary.
        start_time (float): Time when simulation starts (datenum, days since 0/0/0000)
    """

    # Get the start and end time from the weather data
    t_start =  gl["d"]["iGlob"][0, 0]
    t_end =  gl["d"]["iGlob"][-1, 0]
    gl["t"] = np.array([t_start, t_end])
    return gl

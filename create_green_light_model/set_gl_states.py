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


def set_gl_states(gl):

    gl["x"]["co2Air"] = np.array([])

    gl["x"]["co2Top"] = np.array([])

    gl["x"]["tAir"] = np.array([])

    gl["x"]["tTop"] = np.array([])

    gl["x"]["tCan"] = np.array([])

    gl["x"]["tCovIn"] = np.array([])

    gl["x"]["tThScr"] = np.array([])

    gl["x"]["tFlr"] = np.array([])

    gl["x"]["tPipe"] = np.array([])

    gl["x"]["tCovE"] = np.array([])

    gl["x"]["tSo1"] = np.array([])
    gl["x"]["tSo2"] = np.array([])
    gl["x"]["tSo3"] = np.array([])
    gl["x"]["tSo4"] = np.array([])
    gl["x"]["tSo5"] = np.array([])

    gl["x"]["vpAir"] = np.array([])

    gl["x"]["vpTop"] = np.array([])

    gl["x"]["tCan24"] = np.array([])

    gl["x"]["time"] = np.array([])

    gl["x"]["tLamp"] = np.array([])

    gl["x"]["tGroPipe"] = np.array([])

    gl["x"]["tIntLamp"] = np.array([])

    gl["x"]["tBlScr"] = np.array([])

    gl["x"]["cBuf"] = np.array([])

    gl["x"]["cLeaf"] = np.array([])

    gl["x"]["cStem"] = np.array([])

    gl["x"]["cFruit"] = np.array([])

    gl["x"]["tCanSum"] = np.array([])

    return gl

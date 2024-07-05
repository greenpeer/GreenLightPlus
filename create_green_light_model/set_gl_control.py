# File path: GreenLightPlus/create_green_light_model/set_gl_control.py
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

from ..service_functions.funcs import proportionalControl

def set_gl_control(gl):
    a = gl["a"]
    u = gl["u"]
    p = gl["p"]
    x = gl["x"]
    d = gl["d"]

    # 1.Heating from boiler [0 is no heating, 1 is full heating]
    u["boil"] = proportionalControl(x["tAir"], a["heatSetPoint"], p["tHeatBand"], 0, 1)

    # 2.External CO2 supply [0 is no supply, 1 is full supply]
    u["extCo2"] = proportionalControl(
        a["co2InPpm"], a["co2SetPoint"], p["co2Band"], 0, 1
    )

    # 3.shading screen is always open (doesn't exist)
    u["shScr"] = 0

    # 4.permanent shading screen is always open (doesn't exist)
    u["shScrPer"] = 0

    # 5.Thermal screen [0 is open, 1 is closed]
    u["thScr"] = np.minimum(a["thScrCold"], np.minimum(a["thScrHeat"], a["thScrRh"]))

    # 6.Ventilation from the roof [0 is windows fully closed, 1 is fully open]
    u["roof"] = np.minimum(a["ventCold"], np.maximum(a["ventHeat"], a["ventRh"]))

    # 7.side ventilation is always closed (doesn't exist)
    u["side"] = 0

    # 8.Lighting from the top lights [W m^{-2}]
    u["lamp"] = a["lampOn"]

    # 9.Lighting from the interlights [W m^{-2}]
    u["intLamp"] = a["intLampOn"]

    # 10.Heating to grow pipes [0 is no heating, 1 is full heating]
    u["boilGro"] = proportionalControl(
        x["tAir"], a["heatSetPoint"], p["tHeatBand"], 0, 1
    )

    # 11.Blackout screen: 1 if screen is closed, 0 if open
    # Screen is closed at night when lamp is on, the constraints for the
    # lamps in lampOn and intLampOn ensure that screen opens if there is
    # excess heat or humidity
    u["blScr"] = (
        p["useBlScr"] * (1 - d["isDaySmooth"]) * np.maximum(a["lampOn"], a["intLampOn"])
    )
    
     # 更新 gl["u"]
    gl["u"] = u

    return gl

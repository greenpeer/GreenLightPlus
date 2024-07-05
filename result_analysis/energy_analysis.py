# File path: GreenLightPlus/result_analysis/energy_analysis.py
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

from ..service_functions.funcs import *


def energy_analysis(gl, print_val=False):
    # Calculate the energy consumption for each component of the model
    # The calculate_energy_consumption function is imported from another module called "..service_functions.funcs"
    sunIn = calculate_energy_consumption(
        gl,
        "rGlobSunAir",
        "rParSunCan",
        "rNirSunCan",
        "rParSunFlr",
        "rNirSunFlr",
        "rGlobSunCovE",
    )
    heatIn = calculate_energy_consumption(gl, "hBoilPipe", "hBoilGroPipe")
    transp = calculate_energy_consumption(
        gl, "lAirThScr", "lAirBlScr", "lTopCovIn"
    ) - calculate_energy_consumption(gl, "lCanAir")
    soilOut = -calculate_energy_consumption(gl, "hSo5SoOut")
    ventOut = -calculate_energy_consumption(gl, "hAirOut", "hTopOut")
    convOut = -calculate_energy_consumption(gl, "hCovEOut")
    firOut = -calculate_energy_consumption(
        gl,
        "rCovESky",
        "rThScrSky",
        "rBlScrSky",
        "rCanSky",
        "rPipeSky",
        "rFlrSky",
        "rLampSky",
    )
    lampIn = calculate_energy_consumption(gl, "qLampIn", "qIntLampIn")
    lampCool = -calculate_energy_consumption(gl, "hLampCool")

    # Calculate the energy balance of the model
    balance = (
        sunIn
        + heatIn
        + transp
        + soilOut
        + ventOut
        + firOut
        + lampIn
        + convOut
        + lampCool
    )

    # Print a warning message if the absolute value of energy balance is greater than 100 MJ m^{-2}
    if abs(balance) > 100:
        print("Warning: Absolute value of energy balance greater than 100 MJ m^{-2}")

    # Print the energy consumption of each component if print_val is True
    if print_val:
        print(f"sunIn: {sunIn}")
        print(f"heatIn: {heatIn}")
        print(f"transp: {transp}")
        print(f"soilOut: {soilOut}")
        print(f"ventOut: {ventOut}")
        print(f"firOut: {firOut}")
        print(f"lampIn: {lampIn}")
        print(f"convOut: {convOut}")
        print(f"lampCool: {lampCool}")
        print(f"balance: {balance}")

    # Return the energy consumption of each component, and the energy balance
    return (
        sunIn,
        heatIn,
        transp,
        soilOut,
        ventOut,
        firOut,
        lampIn,
        convOut,
        lampCool,
        balance,
    )

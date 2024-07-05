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


def set_dep_params(gl):
    """
    Set the dependent parameters for the GreenLight (2011) model.
    Dependent parameters are parameters that depend on the setting of another parameter.

    Parameters:
        gl: A GreenLight model nested dictionary.

    The function sets the dependent parameters for the GreenLight (2011) model based on the electronic appendices (the
    case of a Dutch greenhouse) of Vanthoor et al. (2011) - A methodology for model-based greenhouse design: Part 1,
    a greenhouse climate model for a broad range of designs and climates, and Vanthoor et al. (2011) - A methodology
    for model-based greenhouse design: Part 2, description and validation of a tomato yield model.

    """

    pi = np.pi
    
    p = gl["p"]

    p["capPipe"] = (
        0.25
        * pi
        * p["lPipe"]
        * (
            (p["phiPipeE"] ** 2 - p["phiPipeI"] ** 2)
            * p["rhoSteel"]
            * p["cPSteel"]
            + p["phiPipeI"] ** 2 * p["rhoWater"] * p["cPWater"]
        )
    )
    p["rhoAir"] = p["rhoAir0"] * np.exp(
        p["g"] * p["mAir"] * p["hElevation"] / (293.15 * p["R"])
    )
    p["capAir"] = p["hAir"] * p["rhoAir"] * p["cPAir"]
    p["capFlr"] = p["hFlr"] * p["rhoFlr"] * p["cPFlr"]
    p["capSo1"] = p["hSo1"] * p["rhoCpSo"]
    p["capSo2"] = p["hSo2"] * p["rhoCpSo"]
    p["capSo3"] = p["hSo3"] * p["rhoCpSo"]
    p["capSo4"] = p["hSo4"] * p["rhoCpSo"]
    p["capSo5"] = p["hSo5"] * p["rhoCpSo"]
    p["capThScr"] = p["hThScr"] * p["rhoThScr"] * p["cPThScr"]
    p["capTop"] = (
        (p["hGh"] - p["hAir"]) * p["rhoAir"] * p["cPAir"]
    )
    p["capBlScr"] = p["hBlScr"] * p["rhoBlScr"] * p["cPBlScr"]
    p["capCo2Air"] = p["hAir"]
    p["capCo2Top"] = p["hGh"] - p["hAir"]
    p["aPipe"] = pi * p["lPipe"] * p["phiPipeE"]
    p["fCanFlr"] = 1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"]
    p["pressure"] = 101325 * (1 - 2.5577e-5 * p["hElevation"]) ** 5.25588
    p["cLeafMax"] = p["laiMax"] / p["sla"]
    p["aGroPipe"] = pi * p["lGroPipe"] * p["phiGroPipeE"]

    p["capGroPipe"] = (
        0.25
        * pi
        * p["lGroPipe"]
        * (
            (p["phiGroPipeE"] ** 2 - p["phiGroPipeI"] ** 2)
            * p["rhoSteel"]
            * p["cPSteel"]
            + p["phiGroPipeI"] ** 2 * p["rhoWater"] * p["cPWater"]
        )
    )

    return gl

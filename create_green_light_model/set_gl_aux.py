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

import copy
import numpy as np

# import jax.numpy as np
from ..service_functions.funcs import *
from ..service_functions.co2_dens2ppm import co2_dens2ppm

pi = np.pi

 
def set_gl_aux(gl, prev_gl=None):
    """
    set_gl_aux Set auxiliary states for the GreenLight greenhouse model

    Based on the electronic appendices of:
      [1] Vanthoor, B., Stanghellini, C., van Henten, E. J. & de Visser, P. H. B.
          A methodology for model-based greenhouse design: Part 1, a greenhouse climate
          model for a broad range of designs and climates. Biosyst. Eng. 110, 363�377 (2011).
      [2] Vanthoor, B., de Visser, P. H. B., Stanghellini, C. & van Henten, E. J.
          A methodology for model-based greenhouse design: Part 2, description and
          validation of a tomato yield model. Biosyst. Eng. 110, 378�395 (2011).
    These are also available as Chapters 8 and 9, respecitvely, of
      [3] Vanthoor, B. A model based greenhouse design method. (Wageningen University, 2011).
    Other sources are:
      [4] De Zwart, H. F. Analyzing energy-saving options in greenhouse cultivation
          using a simulation model. (Landbouwuniversiteit Wageningen, 1996).
    The model is described and evaluated in:
      [5] Katzin, D., van Mourik, S., Kempkes, F., & Van Henten, E. J. (2020).
          GreenLight - An open source model for greenhouses with supplemental
          lighting: Evaluation of heat requirements under LED and HPS lamps.
          Biosystems Engineering, 194, 61�81. https://doi.org/10.1016/j.biosystemseng.2020.03.010
    Additional components are taken from:
      [6] Righini, I., Vanthoor, B., Verheul, M. J., Naseer, M., Maessen, H.,
          Persson, T., & Stanghellini, C. (2020). A greenhouse climate-yield
          model focussing on additional light, heat harvesting and its validation.
          Biosystems Engineering, (194), 1�15. https://doi.org/10.1016/j.biosystemseng.2020.03.009
    The model is further described in:
      [7] Katzin, D. (2021). Energy saving by LED lighting in greenhouses:
          a process-based modelling approach (PhD thesis, Wageningen University).
          https://doi.org/10.18174/544434
    Some control decisions are described in:
      [8] Katzin, D., Marcelis, L. F. M., & van Mourik, S. (2021).
          Energy savings in greenhouses by transition from high-pressure sodium
          to LED lighting. Applied Energy, 281, 116019.
          https://doi.org/10.1016/j.apenergy.2020.116019
    Inputs:
      gl: A GreenLight model nested dictionary.

    """
    a = gl["a"]
    u = gl["u"]
    p = gl["p"]
    x = gl["x"]
    d = gl["d"]

    # keys_to_check = ["tBlScr", "tThScr", "tIntLamp", "tCovIn", "time"]
    # for key in keys_to_check:
    #     if np.isinf(x[key]):
    #         # Replace with previous value if current value is inf
    #         gl["x"][key] = prev_gl["x"][key]
    #         if np.isinf(prev_gl["x"][key]):
    #             print(f"Warning: {key} is inf in both current and previous time step.")
    # # Update x
    # x = gl["x"]

    # # To avoid the error of "overflow encountered ...."
    # if x["tBlScr"] > 100 or x["tCovIn"] > 55:
    #     gl['x'] = prev_gl["x"]
    #     x = gl["x"]

    ## lumped cover layers  - Section 3 [1], Section A[1] [5]
    # shadow screen and permanent shadow screen

    # PAR transmission coefficient of the shadow screen layer [-]
    a["tauShScrPar"] = 1 - u["shScr"] * (1 - p["tauShScrPar"])

    # PAR transmission coefficient of the semi-permanent shadow screen layer [-]
    a["tauShScrPerPar"] = 1 - u["shScrPer"] * (1 - p["tauShScrPerPar"])

    # PAR reflection coefficient of the shadow screen layer [-]
    a["rhoShScrPar"] = u["shScr"] * p["rhoShScrPar"]

    # PAR reflection coefficient of the semi-permanent shadow screen layer [-]
    a["rhoShScrPerPar"] = u["shScrPer"] * p["rhoShScrPerPar"]

    # PAR transmission coefficient of the shadow screen and semi permanent shadow screen layer [-]
    # Equation 16 [1]
    a["tauShScrShScrPerPar"] = tau12(
        a["tauShScrPar"],
        a["tauShScrPerPar"],
        a["rhoShScrPar"],
        a["rhoShScrPar"],
        a["rhoShScrPerPar"],
        a["rhoShScrPerPar"],
    )

    # PAR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the top [-]
    # Equation 17 [1]
    a["rhoShScrShScrPerParUp"] = rhoUp(
        a["tauShScrPar"],
        a["tauShScrPerPar"],
        a["rhoShScrPar"],
        a["rhoShScrPar"],
        a["rhoShScrPerPar"],
        a["rhoShScrPerPar"],
    )

    # PAR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the bottom [-]
    # Equation 17 [1]
    a["rhoShScrShScrPerParDn"] = rhoDn(
        a["tauShScrPar"],
        a["tauShScrPerPar"],
        a["rhoShScrPar"],
        a["rhoShScrPar"],
        a["rhoShScrPerPar"],
        a["rhoShScrPerPar"],
    )

    # NIR transmission coefficient of the shadow screen layer [-]
    a["tauShScrNir"] = 1 - u["shScr"] * (1 - p["tauShScrNir"])

    # NIR transmission coefficient of the semi-permanent shadow screen layer [-]
    a["tauShScrPerNir"] = 1 - u["shScrPer"] * (1 - p["tauShScrPerNir"])

    # NIR reflection coefficient of the shadow screen layer [-]
    a["rhoShScrNir"] = u["shScr"] * p["rhoShScrNir"]

    # NIR reflection coefficient of the semi-permanent shadow screen layer [-]
    a["rhoShScrPerNir"] = u["shScrPer"] * p["rhoShScrPerNir"]

    # NIR transmission coefficient of the shadow screen and semi permanent shadow screen layer [-]
    a["tauShScrShScrPerNir"] = tau12(
        a["tauShScrNir"],
        a["tauShScrPerNir"],
        a["rhoShScrNir"],
        a["rhoShScrNir"],
        a["rhoShScrPerNir"],
        a["rhoShScrPerNir"],
    )

    # NIR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the top [-]
    a["rhoShScrShScrPerNirUp"] = rhoUp(
        a["tauShScrNir"],
        a["tauShScrPerNir"],
        a["rhoShScrNir"],
        a["rhoShScrNir"],
        a["rhoShScrPerNir"],
        a["rhoShScrPerNir"],
    )

    # NIR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the bottom [-]
    a["rhoShScrShScrPerNirDn"] = rhoDn(
        a["tauShScrNir"],
        a["tauShScrPerNir"],
        a["rhoShScrNir"],
        a["rhoShScrNir"],
        a["rhoShScrPerNir"],
        a["rhoShScrPerNir"],
    )

    # FIR  transmission coefficient of the shadow screen layer [-]
    a["tauShScrFir"] = 1 - u["shScr"] * (1 - p["tauShScrFir"])

    # FIR transmission coefficient of the semi-permanent shadow screen layer [-]
    a["tauShScrPerFir"] = 1 - u["shScrPer"] * (1 - p["tauShScrPerFir"])

    # FIR reflection coefficient of the shadow screen layer [-]
    a["rhoShScrFir"] = u["shScr"] * p["rhoShScrFir"]

    # FIR reflection coefficient of the semi-permanent shadow screen layer [-]
    a["rhoShScrPerFir"] = u["shScrPer"] * p["rhoShScrPerFir"]

    # FIR transmission coefficient of the shadow screen and semi permanent shadow screen layer [-]
    a["tauShScrShScrPerFir"] = tau12(
        a["tauShScrFir"],
        a["tauShScrPerFir"],
        a["rhoShScrFir"],
        a["rhoShScrFir"],
        a["rhoShScrPerFir"],
        a["rhoShScrPerFir"],
    )

    # FIR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the top [-]
    a["rhoShScrShScrPerFirUp"] = rhoUp(
        a["tauShScrFir"],
        a["tauShScrPerFir"],
        a["rhoShScrFir"],
        a["rhoShScrFir"],
        a["rhoShScrPerFir"],
        a["rhoShScrPerFir"],
    )

    # FIR reflection coefficient of the shadow screen and semi permanent shadow screen layer towards the bottom [-]
    a["rhoShScrShScrPerFirDn"] = rhoDn(
        a["tauShScrFir"],
        a["tauShScrPerFir"],
        a["rhoShScrFir"],
        a["rhoShScrFir"],
        a["rhoShScrPerFir"],
        a["rhoShScrPerFir"],
    )

    # thermal screen and roof
    # PAR

    # PAR transmission coefficient of the thermal screen [-]
    a["tauThScrPar"] = 1 - u["thScr"] * (1 - p["tauThScrPar"])

    # PAR reflection coefficient of the thermal screen [-]
    a["rhoThScrPar"] = u["thScr"] * p["rhoThScrPar"]

    # PAR transmission coefficient of the thermal screen and roof [-]
    a["tauCovThScrPar"] = tau12(
        p["tauRfPar"],
        a["tauThScrPar"],
        p["rhoRfPar"],
        p["rhoRfPar"],
        a["rhoThScrPar"],
        a["rhoThScrPar"],
    )

    # PAR reflection coefficient of the thermal screen and roof towards the top [-]
    a["rhoCovThScrParUp"] = rhoUp(
        p["tauRfPar"],
        a["tauThScrPar"],
        p["rhoRfPar"],
        p["rhoRfPar"],
        a["rhoThScrPar"],
        a["rhoThScrPar"],
    )

    # PAR reflection coefficient of the thermal screen and roof towards the bottom [-]
    a["rhoCovThScrParDn"] = rhoDn(
        p["tauRfPar"],
        a["tauThScrPar"],
        p["rhoRfPar"],
        p["rhoRfPar"],
        a["rhoThScrPar"],
        a["rhoThScrPar"],
    )

    # NIR
    # NIR transmission coefficient of the thermal screen [-]
    a["tauThScrNir"] = 1 - u["thScr"] * (1 - p["tauThScrNir"])

    # NIR reflection coefficient of the thermal screen [-]
    a["rhoThScrNir"] = u["thScr"] * p["rhoThScrNir"]

    # NIR transmission coefficient of the thermal screen and roof [-]
    a["tauCovThScrNir"] = tau12(
        p["tauRfNir"],
        a["tauThScrNir"],
        p["rhoRfNir"],
        p["rhoRfNir"],
        a["rhoThScrNir"],
        a["rhoThScrNir"],
    )

    # NIR reflection coefficient of the thermal screen and roof towards the top [-]
    a["rhoCovThScrNirUp"] = rhoUp(
        p["tauRfNir"],
        a["tauThScrNir"],
        p["rhoRfNir"],
        p["rhoRfNir"],
        a["rhoThScrNir"],
        a["rhoThScrNir"],
    )

    # NIR reflection coefficient of the thermal screen and roof towards the top [-]
    a["rhoCovThScrNirDn"] = rhoDn(
        p["tauRfNir"],
        a["tauThScrNir"],
        p["rhoRfNir"],
        p["rhoRfNir"],
        a["rhoThScrNir"],
        a["rhoThScrNir"],
    )

    # all 4 layers of the Vanthoor model
    # Vanthoor PAR transmission coefficient of the cover [-]
    a["tauCovParOld"] = tau12(
        a["tauShScrShScrPerPar"],
        a["tauCovThScrPar"],
        a["rhoShScrShScrPerParUp"],
        a["rhoShScrShScrPerParDn"],
        a["rhoCovThScrParUp"],
        a["rhoCovThScrParDn"],
    )

    # Vanthoor PAR reflection coefficient of the cover towards the top [-]
    a["rhoCovParOldUp"] = rhoUp(
        a["tauShScrShScrPerPar"],
        a["tauCovThScrPar"],
        a["rhoShScrShScrPerParUp"],
        a["rhoShScrShScrPerParDn"],
        a["rhoCovThScrParUp"],
        a["rhoCovThScrParDn"],
    )

    # Vanthoor PAR reflection coefficient of the cover towards the bottom [-]
    a["rhoCovParOldDn"] = rhoDn(
        a["tauShScrShScrPerPar"],
        a["tauCovThScrPar"],
        a["rhoShScrShScrPerParUp"],
        a["rhoShScrShScrPerParDn"],
        a["rhoCovThScrParUp"],
        a["rhoCovThScrParDn"],
    )

    # Vanthoor NIR transmission coefficient of the cover [-]
    a["tauCovNirOld"] = tau12(
        a["tauShScrShScrPerNir"],
        a["tauCovThScrNir"],
        a["rhoShScrShScrPerNirUp"],
        a["rhoShScrShScrPerNirDn"],
        a["rhoCovThScrNirUp"],
        a["rhoCovThScrNirDn"],
    )

    # Vanthoor NIR reflection coefficient of the cover towards the top [-]
    a["rhoCovNirOldUp"] = rhoUp(
        a["tauShScrShScrPerNir"],
        a["tauCovThScrNir"],
        a["rhoShScrShScrPerNirUp"],
        a["rhoShScrShScrPerNirDn"],
        a["rhoCovThScrNirUp"],
        a["rhoCovThScrNirDn"],
    )

    # Vanthoor NIR reflection coefficient of the cover towards the bottom [-]
    a["rhoCovNirOldDn"] = rhoDn(
        a["tauShScrShScrPerNir"],
        a["tauCovThScrNir"],
        a["rhoShScrShScrPerNirUp"],
        a["rhoShScrShScrPerNirDn"],
        a["rhoCovThScrNirUp"],
        a["rhoCovThScrNirDn"],
    )

    # Vanthoor cover with blackout screen
    # PAR transmission coefficient of the blackout screen [-]
    a["tauBlScrPar"] = 1 - u["blScr"] * (1 - p["tauBlScrPar"])

    # PAR reflection coefficient of the blackout screen [-]
    a["rhoBlScrPar"] = u["blScr"] * p["rhoBlScrPar"]

    # PAR transmission coefficient of the old cover and blackout screen [-]
    # Equation A9 [5]
    a["tauCovBlScrPar"] = tau12(
        a["tauCovParOld"],
        a["tauBlScrPar"],
        a["rhoCovParOldUp"],
        a["rhoCovParOldDn"],
        a["rhoBlScrPar"],
        a["rhoBlScrPar"],
    )

    # PAR up reflection coefficient of the old cover and blackout screen [-]
    # Equation A10 [5]
    a["rhoCovBlScrParUp"] = rhoUp(
        a["tauCovParOld"],
        a["tauBlScrPar"],
        a["rhoCovParOldUp"],
        a["rhoCovParOldDn"],
        a["rhoBlScrPar"],
        a["rhoBlScrPar"],
    )

    # PAR down reflection coefficient of the old cover and blackout screen [-]
    # Equation A11 [5]
    a["rhoCovBlScrParDn"] = rhoDn(
        a["tauCovParOld"],
        a["tauBlScrPar"],
        a["rhoCovParOldUp"],
        a["rhoCovParOldDn"],
        a["rhoBlScrPar"],
        a["rhoBlScrPar"],
    )

    # NIR transmission coefficient of the blackout screen [-]
    a["tauBlScrNir"] = 1 - u["blScr"] * (1 - p["tauBlScrNir"])

    # NIR reflection coefficient of the blackout screen [-]
    a["rhoBlScrNir"] = u["blScr"] * p["rhoBlScrNir"]

    # NIR transmission coefficient of the old cover and blackout screen [-]
    a["tauCovBlScrNir"] = tau12(
        a["tauCovNirOld"],
        a["tauBlScrNir"],
        a["rhoCovNirOldUp"],
        a["rhoCovNirOldDn"],
        a["rhoBlScrNir"],
        a["rhoBlScrNir"],
    )

    # NIR up reflection coefficient of the old cover and blackout screen [-]
    a["rhoCovBlScrNirUp"] = rhoUp(
        a["tauCovNirOld"],
        a["tauBlScrNir"],
        a["rhoCovNirOldUp"],
        a["rhoCovNirOldDn"],
        a["rhoBlScrNir"],
        a["rhoBlScrNir"],
    )

    # NIR down reflection coefficient of the old cover and blackout screen [-]
    a["rhoCovBlScrNirDn"] = rhoDn(
        a["tauCovNirOld"],
        a["tauBlScrNir"],
        a["rhoCovNirOldUp"],
        a["rhoCovNirOldDn"],
        a["rhoBlScrNir"],
        a["rhoBlScrNir"],
    )

    # all layers
    # PAR transmission coefficient of the cover [-]
    # Equation A12 [5]
    a["tauCovPar"] = tau12(
        a["tauCovBlScrPar"],
        p["tauLampPar"],
        a["rhoCovBlScrParUp"],
        a["rhoCovBlScrParDn"],
        p["rhoLampPar"],
        p["rhoLampPar"],
    )

    # PAR reflection coefficient of the cover [-]
    # Equation A13 [5]
    a["rhoCovPar"] = rhoUp(
        a["tauCovBlScrPar"],
        p["tauLampPar"],
        a["rhoCovBlScrParUp"],
        a["rhoCovBlScrParDn"],
        p["rhoLampPar"],
        p["rhoLampPar"],
    )

    # NIR transmission coefficient of the cover [-]
    a["tauCovNir"] = tau12(
        a["tauCovBlScrNir"],
        p["tauLampNir"],
        a["rhoCovBlScrNirUp"],
        a["rhoCovBlScrNirDn"],
        p["rhoLampNir"],
        p["rhoLampNir"],
    )

    # NIR reflection coefficient of the cover [-]
    a["rhoCovNir"] = rhoUp(
        a["tauCovBlScrNir"],
        p["tauLampNir"],
        a["rhoCovBlScrNirUp"],
        a["rhoCovBlScrNirDn"],
        p["rhoLampNir"],
        p["rhoLampNir"],
    )

    # FIR transmission coefficient of the cover, excluding screens and lamps [-]
    a["tauCovFir"] = tau12(
        a["tauShScrShScrPerFir"],
        p["tauRfFir"],
        a["rhoShScrShScrPerFirUp"],
        a["rhoShScrShScrPerFirDn"],
        p["rhoRfFir"],
        p["rhoRfFir"],
    )

    # FIR reflection coefficient of the cover, excluding screens and lamps [-]
    a["rhoCovFir"] = rhoUp(
        a["tauShScrShScrPerFir"],
        p["tauRfFir"],
        a["rhoShScrShScrPerFirUp"],
        a["rhoShScrShScrPerFirDn"],
        p["rhoRfFir"],
        p["rhoRfFir"],
    )

    # PAR absorption coefficient of the cover [-]
    a["aCovPar"] = 1 - a["tauCovPar"] - a["rhoCovPar"]

    # NIR absorption coefficient of the cover [-]
    a["aCovNir"] = 1 - a["tauCovNir"] - a["rhoCovNir"]

    # FIR absorption coefficient of the cover [-]
    a["aCovFir"] = 1 - a["tauCovFir"] - a["rhoCovFir"]

    # FIR emission coefficient of the cover [-]
    # See comment before equation 18 [1]
    a["epsCovFir"] = a["aCovFir"]

    # Heat capacity of the lumped cover [J K^{-1} m^{-2}]
    # Equation 18 [1]
    a["capCov"] = cosd(p["psi"]) * (
        u["shScrPer"] * p["hShScrPer"] * p["rhoShScrPer"] * p["cPShScrPer"]
        + p["hRf"] * p["rhoRf"] * p["cPRf"]
    )

    ## Capacities - Section 4 [1]

    # Leaf area index [m^2{leaf} m^{-2}]
    # Equation 5 [2]
    a["lai"] = p["sla"] * x["cLeaf"]

    # Heat capacity of canopy [J K^{-1} m^{-2}]
    # Equation 19 [1]
    a["capCan"] = p["capLeaf"] * a["lai"]

    # Heat capacity of external and internal cover [J K^{-1} m^{-2}]
    # Equation 20 [1]
    a["capCovE"] = 0.1 * a["capCov"]
    a["capCovIn"] = 0.1 * a["capCov"]

    # Vapor capacity of main compartment [kg m J^{-1}]
    # Equation 24 [1]
    a["capVpAir"] = p["mWater"] * p["hAir"] / (p["R"] * (x["tAir"] + 273.15))

    # Vapor capacity of top compartment [kg m J^{-1}]
    a["capVpTop"] = (
        p["mWater"] * (p["hGh"] - p["hAir"]) / (p["R"] * (x["tTop"] + 273.15))
    )

    ## Global, PAR, and NIR heat fluxes - Section 5.1 [1]

    # Lamp electrical input [W m^{-2}]
    # Equation A16 [5]

    a["qLampIn"] = p["thetaLampMax"] * u["lamp"]

    # Interlight electrical input [W m^{-2}]
    # Equation A26 [5]
    a["qIntLampIn"] = p["thetaIntLampMax"] * u["intLamp"]

    # PAR above the canopy from the sun [W m^{-2}]
    # Equation 27 [1], Equation A14 [5]
    a["rParGhSun"] = (
        (1 - p["etaGlobAir"]) * a["tauCovPar"] * p["etaGlobPar"] * d["iGlob"]
    )

    # PAR above the canopy from the lamps [W m^{-2}]
    # Equation A15 [5]
    a["rParGhLamp"] = p["etaLampPar"] * a["qLampIn"]

    # PAR outside the canopy from the interlights [W m^{-2}]
    # Equation 7.7, 7.14 [7]
    a["rParGhIntLamp"] = p["etaIntLampPar"] * a["qIntLampIn"]

    # Global radiation above the canopy from the sun [W m^{-2}]
    # (PAR+NIR, where UV is counted together with NIR)
    # Equation 7.24 [7]
    a["rCanSun"] = (
        (1 - p["etaGlobAir"])
        * d["iGlob"]
        * (p["etaGlobPar"] * a["tauCovPar"] + p["etaGlobNir"] * a["tauCovNir"])
    )
    # perhaps tauHatCovNir should be used here?

    # Global radiation above the canopy from the lamps [W m^{-2}]
    # (PAR+NIR, where UV is counted together with NIR)
    # Equation 7.25 [7]
    a["rCanLamp"] = (p["etaLampPar"] + p["etaLampNir"]) * a["qLampIn"]

    # Global radiation outside the canopy from the interlight lamps [W m^{-2}]
    # (PAR+NIR, where UV is counted together with NIR)
    # Equation 7.26 [7]
    a["rCanIntLamp"] = (p["etaIntLampPar"] + p["etaIntLampNir"]) * gl["a"]["qIntLampIn"]

    # Global radiation above and outside the canopy [W m^{-2}]
    # (PAR+NIR, where UV is counted together with NIR)
    # Equation 7.23 [7]
    a["rCan"] = a["rCanSun"] + a["rCanLamp"] + a["rCanIntLamp"]

    # PAR from the sun directly absorbed by the canopy [W m^{-2}]
    # Equation 26 [1]
    a["rParSunCanDown"] = (
        a["rParGhSun"] * (1 - p["rhoCanPar"]) * (1 - np.exp(-p["k1Par"] * a["lai"]))
    )

    # PAR from the lamps directly absorbed by the canopy [W m^{-2}]
    # Equation A17 [5]
    a["rParLampCanDown"] = (
        a["rParGhLamp"] * (1 - p["rhoCanPar"]) * (1 - np.exp(-p["k1Par"] * a["lai"]))
    )

    # Fraction of PAR from the interlights reaching the canopy [-]
    # Equation 7.13 [7]
    a["fIntLampCanPar"] = (
        1
        - p["fIntLampDown"] * np.exp(-p["k1IntPar"] * p["vIntLampPos"] * a["lai"])
        + (p["fIntLampDown"] - 1)
        * np.exp(-p["k1IntPar"] * (1 - p["vIntLampPos"]) * a["lai"])
    )
    # Fraction going up and absorbed is (1-gl['p']['fIntLampDown'])*(1-np.exp(-gl['p']['k1IntPar']*(1-gl['p']['vIntLampPos'])*gl['a']['lai']))
    # Fraction going down and absorbed isgl['p']['fIntLampDown']*(1-np.exp(-gl['p']['k1IntPar']*gl['p']['vIntLampPos']*gl['a']['lai']))
    # This is their sum
    # e['g']., ifgl['p']['vIntLampPos']==1, the lamp is above the canopy
    # fraction going up and abosrbed is 0
    # fraction going down and absroebd isgl['p']['fIntLampDown']*(1-np.exp(-gl['p']['k1IntPar']*gl['a']['lai']))

    # Fraction of NIR from the interlights reaching the canopy [-]
    # Analogous to Equation 7.13 [7]
    a["fIntLampCanNir"] = (
        1
        - p["fIntLampDown"] * np.exp(-p["kIntNir"] * p["vIntLampPos"] * a["lai"])
        + (p["fIntLampDown"] - 1)
        * np.exp(-p["kIntNir"] * (1 - p["vIntLampPos"]) * a["lai"])
    )

    # PAR from the interlights directly absorbed by the canopy [W m^{-2}]
    # Equation 7.16 [7]
    a["rParIntLampCanDown"] = (
        a["rParGhIntLamp"] * a["fIntLampCanPar"] * (1 - p["rhoCanPar"])
    )

    # PAR from the sun absorbed by the canopy after reflection from the floor [W m^{-2}]
    # Equation 28 [1]
    a["rParSunFlrCanUp"] = mulNoBracks(
        a["rParGhSun"],
        np.exp(-p["k1Par"] * a["lai"])
        * p["rhoFlrPar"]
        * (1 - p["rhoCanPar"])
        * (1 - np.exp(-p["k2Par"] * a["lai"])),
    )

    # PAR from the lamps absorbed by the canopy after reflection from the floor [W m^{-2}]
    # Equation A18 [5]
    a["rParLampFlrCanUp"] = (
        a["rParGhLamp"]
        * np.exp(-p["k1Par"] * a["lai"])
        * p["rhoFlrPar"]
        * (1 - p["rhoCanPar"])
        * (1 - np.exp(-p["k2Par"] * a["lai"]))
    )

    # PAR from the interlights absorbed by the canopy after reflection from the floor [W m^{-2}]
    # Equation 7.18 [7]
    a["rParIntLampFlrCanUp"] = (
        a["rParGhIntLamp"]
        * p["fIntLampDown"]
        * np.exp(-p["k1IntPar"] * p["vIntLampPos"] * a["lai"])
        * p["rhoFlrPar"]
        * (1 - p["rhoCanPar"])
        * (1 - np.exp(-p["k2IntPar"] * a["lai"]))
    )
    # ifgl['p']['vIntLampPos']==1, the lamp is above the canopy, light loses
    # np.exp(-k*LAI) on its way to the floor.
    # ifgl['p']['vIntLampPos']==0, the lamp is below the canopy, no light is
    # lost on the way to the floor

    # Total PAR from the sun absorbed by the canopy [W m^{-2}]
    # Equation 25 [1]
    a["rParSunCan"] = a["rParSunCanDown"] + a["rParSunFlrCanUp"]

    # Total PAR from the lamps absorbed by the canopy [W m^{-2}]
    # Equation A19 [5]
    a["rParLampCan"] = a["rParLampCanDown"] + a["rParLampFlrCanUp"]

    # Total PAR from the interlights absorbed by the canopy [W m^{-2}]
    # Equation A19 [5], Equation 7.19 [7]
    a["rParIntLampCan"] = a["rParIntLampCanDown"] + a["rParIntLampFlrCanUp"]

    # Virtual NIR transmission for the cover-canopy-floor lumped model [-]
    # Equation 29 [1]
    a["tauHatCovNir"] = 1 - a["rhoCovNir"]
    a["tauHatFlrNir"] = 1 - p["rhoFlrNir"]

    # NIR transmission coefficient of the canopy [-]
    # Equation 30 [1]
    a["tauHatCanNir"] = np.exp(-p["kNir"] * a["lai"])

    # NIR reflection coefficient of the canopy [-]
    # Equation 31 [1]
    a["rhoHatCanNir"] = p["rhoCanNir"] * (1 - a["tauHatCanNir"])

    # NIR transmission coefficient of the cover and canopy [-]
    a["tauCovCanNir"] = tau12(
        a["tauHatCovNir"],
        a["tauHatCanNir"],
        a["rhoCovNir"],
        a["rhoCovNir"],
        a["rhoHatCanNir"],
        a["rhoHatCanNir"],
    )

    # NIR reflection coefficient of the cover and canopy towards the top [-]
    a["rhoCovCanNirUp"] = rhoUp(
        a["tauHatCovNir"],
        a["tauHatCanNir"],
        a["rhoCovNir"],
        a["rhoCovNir"],
        a["rhoHatCanNir"],
        a["rhoHatCanNir"],
    )

    # NIR reflection coefficient of the cover and canopy towards the bottom [-]
    a["rhoCovCanNirDn"] = rhoDn(
        a["tauHatCovNir"],
        a["tauHatCanNir"],
        a["rhoCovNir"],
        a["rhoCovNir"],
        a["rhoHatCanNir"],
        a["rhoHatCanNir"],
    )

    # NIR transmission coefficient of the cover, canopy and floor [-]
    a["tauCovCanFlrNir"] = tau12(
        a["tauCovCanNir"],
        a["tauHatFlrNir"],
        a["rhoCovCanNirUp"],
        a["rhoCovCanNirDn"],
        p["rhoFlrNir"],
        p["rhoFlrNir"],
    )

    # NIR reflection coefficient of the cover, canopy and floor [-]
    a["rhoCovCanFlrNir"] = rhoUp(
        a["tauCovCanNir"],
        a["tauHatFlrNir"],
        a["rhoCovCanNirUp"],
        a["rhoCovCanNirDn"],
        p["rhoFlrNir"],
        p["rhoFlrNir"],
    )

    # The calculated absorption coefficient equals m['a']['aCanNir'] [-]
    # pg. 23 [1]
    a["aCanNir"] = 1 - a["tauCovCanFlrNir"] - a["rhoCovCanFlrNir"]

    # The calculated transmission coefficient equals m['a']['aFlrNir'] [-]
    # pg. 23 [1]
    a["aFlrNir"] = a["tauCovCanFlrNir"]

    # NIR from the sun absorbed by the canopy [W m^{-2}]
    # Equation 32 [1]
    a["rNirSunCan"] = (
        (1 - p["etaGlobAir"]) * a["aCanNir"] * p["etaGlobNir"] * d["iGlob"]
    )

    # NIR from the lamps absorbed by the canopy [W m^{-2}]
    # Equation A20 [5]
    a["rNirLampCan"] = (
        p["etaLampNir"]
        * a["qLampIn"]
        * (1 - p["rhoCanNir"])
        * (1 - np.exp(-p["kNir"] * a["lai"]))
    )

    # NIR from the interlights absorbed by the canopy [W m^{-2}]
    # Equation 7.20 [7]
    a["rNirIntLampCan"] = (
        p["etaIntLampNir"]
        * a["qIntLampIn"]
        * a["fIntLampCanNir"]
        * (1 - p["rhoCanNir"])
    )

    # NIR from the sun absorbed by the floor [W m^{-2}]
    # Equation 33 [1]
    a["rNirSunFlr"] = (
        (1 - p["etaGlobAir"]) * a["aFlrNir"] * p["etaGlobNir"] * d["iGlob"]
    )

    # NIR from the lamps absorbed by the floor [W m^{-2}]
    # Equation A22 [5]
    a["rNirLampFlr"] = (
        (1 - p["rhoFlrNir"])
        * np.exp(-p["kNir"] * a["lai"])
        * p["etaLampNir"]
        * a["qLampIn"]
    )

    # NIR from the interlights absorbed by the floor [W m^{-2}]
    # Equation 7.21 [7]
    a["rNirIntLampFlr"] = (
        p["fIntLampDown"]
        * (1 - p["rhoFlrNir"])
        * np.exp(-p["kIntNir"] * a["lai"] * p["vIntLampPos"])
        * p["etaIntLampNir"]
        * a["qIntLampIn"]
    )
    # ifgl['p']['vIntLampPos']==1, the lamp is above the canopy, light loses
    # np.exp(-k*LAI) on its way to the floor.
    # ifgl['p']['vIntLampPos']==0, the lamp is below the canopy, no light is
    # lost on the way to the floor

    # PAR from the sun absorbed by the floor [W m^{-2}]
    # Equation 34 [1]
    a["rParSunFlr"] = (
        (1 - p["rhoFlrPar"]) * np.exp(-p["k1Par"] * a["lai"]) * a["rParGhSun"]
    )

    # PAR from the lamps absorbed by the floor [W m^{-2}]
    # Equation A21 [5]
    a["rParLampFlr"] = (
        (1 - p["rhoFlrPar"]) * np.exp(-p["k1Par"] * a["lai"]) * a["rParGhLamp"]
    )

    # PAR from the interlights absorbed by the floor [W m^{-2}]
    # Equation 7.17 [7]
    a["rParIntLampFlr"] = (
        a["rParGhIntLamp"]
        * p["fIntLampDown"]
        * (1 - p["rhoFlrPar"])
        * np.exp(-p["k1IntPar"] * a["lai"] * p["vIntLampPos"])
    )

    # PAR and NIR from the lamps absorbed by the greenhouse air [W m^{-2}]
    # Equation A23 [5]
    a["rLampAir"] = (
        (p["etaLampPar"] + p["etaLampNir"]) * a["qLampIn"]
        - a["rParLampCan"]
        - a["rNirLampCan"]
        - a["rParLampFlr"]
        - a["rNirLampFlr"]
    )

    # PAR and NIR from the interlights absorbed by the greenhouse air [W m^{-2}]
    # Equation 7.22 [7]
    a["rIntLampAir"] = (
        (p["etaIntLampPar"] + p["etaIntLampNir"]) * a["qIntLampIn"]
        - a["rParIntLampCan"]
        - a["rNirIntLampCan"]
        - a["rParIntLampFlr"]
        - a["rNirIntLampFlr"]
    )

    # Global radiation from the sun absorbed by the greenhouse air [W m^{-2}]
    # Equation 35 [1]
    a["rGlobSunAir"] = (
        p["etaGlobAir"]
        * d["iGlob"]
        * (
            a["tauCovPar"] * p["etaGlobPar"]
            + (a["aCanNir"] + a["aFlrNir"]) * p["etaGlobNir"]
        )
    )

    # Global radiation from the sun absorbed by the cover [W m^{-2}]
    # Equation 36 [1]
    a["rGlobSunCovE"] = (
        a["aCovPar"] * p["etaGlobPar"] + a["aCovNir"] * p["etaGlobNir"]
    ) * d["iGlob"]

    ## FIR heat fluxes - Section 5.2 [1]

    # FIR transmission coefficient of the thermal screen
    # Equation 38 [1]
    a["tauThScrFirU"] = 1 - u["thScr"] * (1 - p["tauThScrFir"])

    # FIR transmission coefficient of the blackout screen
    a["tauBlScrFirU"] = 1 - u["blScr"] * (1 - p["tauBlScrFir"])

    # Surface of canopy per floor area [-]
    # Table 3 [1]
    a["aCan"] = 1 - np.exp(-p["kFir"] * a["lai"])

    # FIR between greenhouse objects [W m^{-2}]
    # Table 7.4 [7]. Based on Table 3 [1] and Table A1 [5]

    # FIR between canopy and cover [W m^{-2}]
    a["rCanCovIn"] = fir(
        a["aCan"],
        p["epsCan"],
        a["epsCovFir"],
        p["tauLampFir"] * a["tauThScrFirU"] * a["tauBlScrFirU"],
        x["tCan"],
        x["tCovIn"],
    )

    # FIR between canopy and sky [W m^{-2}]
    a["rCanSky"] = fir(
        a["aCan"],
        p["epsCan"],
        p["epsSky"],
        p["tauLampFir"] * a["tauCovFir"] * a["tauThScrFirU"] * a["tauBlScrFirU"],
        x["tCan"],
        d["tSky"],
    )

    # FIR between canopy and thermal screen [W m^{-2}]
    a["rCanThScr"] = fir(
        a["aCan"],
        p["epsCan"],
        p["epsThScrFir"],
        p["tauLampFir"] * u["thScr"] * a["tauBlScrFirU"],
        x["tCan"],
        x["tThScr"],
    )

    # FIR between canopy and floor [W m^{-2}]
    a["rCanFlr"] = fir(
        a["aCan"],
        p["epsCan"],
        p["epsFlr"],
        p["fCanFlr"],
        x["tCan"],
        x["tFlr"],
    )

    # FIR between pipes and cover [W m^{-2}]
    a["rPipeCovIn"] = fir(
        p["aPipe"],
        p["epsPipe"],
        a["epsCovFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * 0.49
        * np.exp(-p["kFir"] * a["lai"]),
        x["tPipe"],
        x["tCovIn"],
    )

    # FIR between pipes and sky [W m^{-2}]
    a["rPipeSky"] = fir(
        p["aPipe"],
        p["epsPipe"],
        p["epsSky"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * a["tauCovFir"]
        * a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * 0.49
        * np.exp(-p["kFir"] * a["lai"]),
        x["tPipe"],
        d["tSky"],
    )

    # FIR between pipes and thermal screen [W m^{-2}]
    a["rPipeThScr"] = fir(
        p["aPipe"],
        p["epsPipe"],
        p["epsThScrFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * u["thScr"]
        * a["tauBlScrFirU"]
        * 0.49
        * np.exp(-p["kFir"] * a["lai"]),
        x["tPipe"],
        x["tThScr"],
    )

    # FIR between pipes and floor [W m^{-2}]
    a["rPipeFlr"] = fir(
        p["aPipe"],
        p["epsPipe"],
        p["epsFlr"],
        0.49,
        x["tPipe"],
        x["tFlr"],
    )

    # FIR between pipes and canopy [W m^{-2}]
    a["rPipeCan"] = fir(
        p["aPipe"],
        p["epsPipe"],
        p["epsCan"],
        0.49 * (1 - np.exp(-p["kFir"] * a["lai"])),
        x["tPipe"],
        x["tCan"],
    )

    # FIR between floor and cover [W m^{-2}]
    a["rFlrCovIn"] = fir(
        1,
        p["epsFlr"],
        a["epsCovFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"])
        * np.exp(-p["kFir"] * a["lai"]),
        x["tFlr"],
        x["tCovIn"],
    )

    # FIR between floor and sky [W m^{-2}]
    a["rFlrSky"] = fir(
        1,
        p["epsFlr"],
        p["epsSky"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * a["tauCovFir"]
        * a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"])
        * np.exp(-p["kFir"] * a["lai"]),
        x["tFlr"],
        d["tSky"],
    )

    # FIR between floor and thermal screen [W m^{-2}]
    a["rFlrThScr"] = fir(
        1,
        p["epsFlr"],
        p["epsThScrFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * u["thScr"]
        * a["tauBlScrFirU"]
        * (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"])
        * np.exp(-p["kFir"] * a["lai"]),
        x["tFlr"],
        x["tThScr"],
    )

    # FIR between thermal screen and cover [W m^{-2}]
    a["rThScrCovIn"] = fir(
        1,
        p["epsThScrFir"],
        a["epsCovFir"],
        u["thScr"],
        x["tThScr"],
        x["tCovIn"],
    )

    # FIR between thermal screen and sky [W m^{-2}]
    a["rThScrSky"] = fir(
        1,
        p["epsThScrFir"],
        p["epsSky"],
        a["tauCovFir"] * u["thScr"],
        x["tThScr"],
        d["tSky"],
    )

    # FIR between cover and sky [W m^{-2}]
    a["rCovESky"] = fir(1, a["aCovFir"], p["epsSky"], 1, x["tCovE"], d["tSky"])

    # FIR between lamps and floor [W m^{-2}]
    a["rFirLampFlr"] = fir(
        p["aLamp"],
        p["epsLampBottom"],
        p["epsFlr"],
        p["tauIntLampFir"]
        * (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"])
        * np.exp(-p["kFir"] * a["lai"]),
        x["tLamp"],
        x["tFlr"],
    )

    # FIR between lamps and pipe [W m^{-2}]
    a["rLampPipe"] = fir(
        p["aLamp"],
        p["epsLampBottom"],
        p["epsPipe"],
        p["tauIntLampFir"]
        * 0.49
        * pi
        * p["lPipe"]
        * p["phiPipeE"]
        * np.exp(-p["kFir"] * a["lai"]),
        x["tLamp"],
        x["tPipe"],
    )

    # FIR between lamps and canopy [W m^{-2}]
    a["rFirLampCan"] = fir(
        p["aLamp"],
        p["epsLampBottom"],
        p["epsCan"],
        a["aCan"],
        x["tLamp"],
        x["tCan"],
    )

    # FIR between lamps and thermal screen [W m^{-2}]
    a["rLampThScr"] = fir(
        p["aLamp"],
        p["epsLampTop"],
        p["epsThScrFir"],
        u["thScr"] * a["tauBlScrFirU"],
        x["tLamp"],
        x["tThScr"],
    )

    # FIR between lamps and cover [W m^{-2}]
    a["rLampCovIn"] = fir(
        p["aLamp"],
        p["epsLampTop"],
        a["epsCovFir"],
        a["tauThScrFirU"] * a["tauBlScrFirU"],
        x["tLamp"],
        x["tCovIn"],
    )

    # FIR between lamps and sky [W m^{-2}]
    a["rLampSky"] = fir(
        p["aLamp"],
        p["epsLampTop"],
        p["epsSky"],
        a["tauCovFir"] * a["tauThScrFirU"] * a["tauBlScrFirU"],
        x["tLamp"],
        d["tSky"],
    )

    # FIR between grow pipes and canopy [W m^{-2}]
    a["rGroPipeCan"] = fir(
        p["aGroPipe"],
        p["epsGroPipe"],
        p["epsCan"],
        1,
        x["tGroPipe"],
        x["tCan"],
    )

    # FIR between blackout screen and floor [W m^{-2}]
    a["rFlrBlScr"] = fir(
        1,
        p["epsFlr"],
        p["epsBlScrFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * u["blScr"]
        * (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"])
        * np.exp(-p["kFir"] * a["lai"]),
        x["tFlr"],
        x["tBlScr"],
    )

    # FIR between blackout screen and pipe [W m^{-2}]
    a["rPipeBlScr"] = fir(
        p["aPipe"],
        p["epsPipe"],
        p["epsBlScrFir"],
        p["tauIntLampFir"]
        * p["tauLampFir"]
        * u["blScr"]
        * 0.49
        * np.exp(-p["kFir"] * a["lai"]),
        x["tPipe"],
        x["tBlScr"],
    )

    # FIR between blackout screen and canopy [W m^{-2}]
    a["rCanBlScr"] = fir(
        a["aCan"],
        p["epsCan"],
        p["epsBlScrFir"],
        p["tauLampFir"] * u["blScr"],
        x["tCan"],
        x["tBlScr"],
    )

    # FIR between blackout screen and thermal screen [W m^{-2}]
    a["rBlScrThScr"] = fir(
        u["blScr"],
        p["epsBlScrFir"],
        p["epsThScrFir"],
        u["thScr"],
        x["tBlScr"],
        x["tThScr"],
    )

    # FIR between blackout screen and cover [W m^{-2}]
    a["rBlScrCovIn"] = fir(
        u["blScr"],
        p["epsBlScrFir"],
        a["epsCovFir"],
        a["tauThScrFirU"],
        x["tBlScr"],
        x["tCovIn"],
    )

    # FIR between blackout screen and sky [W m^{-2}]
    a["rBlScrSky"] = fir(
        u["blScr"],
        p["epsBlScrFir"],
        p["epsSky"],
        a["tauCovFir"] * a["tauThScrFirU"],
        x["tBlScr"],
        d["tSky"],
    )

    # FIR between blackout screen and lamps [W m^{-2}]
    a["rLampBlScr"] = fir(
        p["aLamp"],
        p["epsLampTop"],
        p["epsBlScrFir"],
        u["blScr"],
        x["tLamp"],
        x["tBlScr"],
    )

    # Fraction of radiation going up from the interlight to the canopy [-]
    # Equation 7.29 [7]
    a["fIntLampCanUp"] = 1 - np.exp(-p["kIntFir"] * (1 - p["vIntLampPos"]) * a["lai"])

    # Fraction of radiation going down from the interlight to the canopy [-]
    # Equation 7.30 [7]
    a["fIntLampCanDown"] = 1 - np.exp(-p["kIntFir"] * p["vIntLampPos"] * a["lai"])

    # FIR between interlights and floor [W m^{-2}]
    a["rFirIntLampFlr"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsFlr"],
        (1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"]) * (1 - a["fIntLampCanDown"]),
        x["tIntLamp"],
        x["tFlr"],
    )

    # FIR between interlights and pipe [W m^{-2}]
    a["rIntLampPipe"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsPipe"],
        0.49 * pi * p["lPipe"] * p["phiPipeE"] * (1 - a["fIntLampCanDown"]),
        x["tIntLamp"],
        x["tPipe"],
    )

    # FIR between interlights and canopy [W m^{-2}]
    a["rFirIntLampCan"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsCan"],
        a["fIntLampCanDown"] + a["fIntLampCanUp"],
        x["tIntLamp"],
        x["tCan"],
    )

    # FIR between interlights and toplights [W m^{-2}]
    a["rIntLampLamp"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsLampBottom"],
        (1 - a["fIntLampCanUp"]) * p["aLamp"],
        x["tIntLamp"],
        x["tLamp"],
    )

    # FIR between interlights and blackout screen [W m^{-2}]
    a["rIntLampBlScr"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsBlScrFir"],
        u["blScr"] * p["tauLampFir"] * (1 - a["fIntLampCanUp"]),
        x["tIntLamp"],
        x["tBlScr"],
    )
    # ifgl['p']['vIntLampPos']==0, the lamp is above the canopy, no light is
    # lost on its way up
    # ifgl['p']['vIntLampPos']==1, the lamp is below the canopy, the light
    # loses np.exp(-k*LAI) on its way up

    # FIR between interlights and thermal screen [W m^{-2}]
    a["rIntLampThScr"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsThScrFir"],
        u["thScr"] * a["tauBlScrFirU"] * p["tauLampFir"] * (1 - a["fIntLampCanUp"]),
        x["tIntLamp"],
        x["tThScr"],
    )

    # FIR between interlights and cover [W m^{-2}]
    a["rIntLampCovIn"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        a["epsCovFir"],
        a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * p["tauLampFir"]
        * (1 - a["fIntLampCanUp"]),
        x["tIntLamp"],
        x["tCovIn"],
    )

    # FIR between interlights and sky [W m^{-2}]
    a["rIntLampSky"] = fir(
        p["aIntLamp"],
        p["epsIntLamp"],
        p["epsSky"],
        a["tauCovFir"]
        * a["tauThScrFirU"]
        * a["tauBlScrFirU"]
        * p["tauLampFir"]
        * (1 - a["fIntLampCanUp"]),
        x["tIntLamp"],
        d["tSky"],
    )



    ## Natural ventilation - Section 9.7 [1]

    # Aperture of the roof [m^{2}]
    # Equation 67 [1]
    a["aRoofU"] = u["roof"] * p["aRoof"]
    a["aRoofUMax"] = p["aRoof"]
    a["aRoofMin"] = 0

    # Aperture of the sidewall [m^{2}]
    # Equation 68 [1]
    # (this is 0 in the Dutch greenhouse)
    a["aSideU"] = u["side"] * p["aSide"]

    # Ratio between roof vent area and total ventilation area [-]
    # (not very clear in the reference [1], but always 1 if m['a']['aSideU'] == 0)

    a["etaRoof"] = 1
    a["etaRoofNoSide"] = 1

    # Ratio between side vent area and total ventilation area [-]
    # (not very clear in the reference [1], but always 0 if m['a']['aSideU'] == 0)
    a["etaSide"] = 0

    # Discharge coefficient [-]
    # Equation 73 [1]
    a["cD"] = p["cDgh"] * (1 - p["etaShScrCd"] * u["shScr"])

    # Discharge coefficient [-]
    # Equation 74 [-]
    a["cW"] = p["cWgh"] * (1 - p["etaShScrCw"] * u["shScr"])

    # Natural ventilation rate due to roof ventilation [m^{3} m^{-2} s^{-1}]
    # Equation 64 [1]
    a["fVentRoof2"] = (
        u["roof"]
        * p["aRoof"]
        * a["cD"]
        / (2 * p["aFlr"])
        * np.sqrt(
            abs(
                p["g"]
                * p["hVent"]
                * (x["tAir"] - d["tOut"])
                / (2 * (0.5 * x["tAir"] + 0.5 * d["tOut"] + 273.15))
                + a["cW"] * d["wind"] ** 2
            )
        )
    )
    a["fVentRoof2Max"] = (
        p["aRoof"]
        * a["cD"]
        / (2 * p["aFlr"])
        * np.sqrt(
            abs(
                p["g"]
                * p["hVent"]
                * (x["tAir"] - d["tOut"])
                / (2 * (0.5 * x["tAir"] + 0.5 * d["tOut"] + 273.15))
                + a["cW"] * d["wind"] ** 2
            )
        )
    )
    a["fVentRoof2Min"] = 0

    # Ventilation rate through roof and side vents [m^{3} m^{-2} s^{-1}]
    # Equation 65 [1]
    a["fVentRoofSide2"] = (
        a["cD"]
        / p["aFlr"]
        * np.sqrt(
            (
                a["aRoofU"]
                * a["aSideU"]
                / np.sqrt(np.maximum(a["aRoofU"] ** 2 + a["aSideU"] ** 2, 0.01))
            )
            ** 2
            * (
                2
                * p["g"]
                * p["hSideRoof"]
                * (x["tAir"] - d["tOut"])
                / (0.5 * x["tAir"] + 0.5 * d["tOut"] + 273.15)
            )
            + ((a["aRoofU"] + a["aSideU"]) / 2) ** 2 * a["cW"] * d["wind"] ** 2
        )
    )

    # Ventilation rate through sidewall only [m^{3} m^{-2} s^{-1}]
    # Equation 66 [1]
    a["fVentSide2"] = (
        a["cD"] * a["aSideU"] * d["wind"] / (2 * p["aFlr"]) * np.sqrt(a["cW"])
    )

    # Leakage ventilation [m^{3} m^{-2} s^{-1}]
    # Equation 70 [1]
    a["fLeakage"] = ifElse(
        d["wind"] < p["minWind"],
        p["minWind"] * p["cLeakage"],
        p["cLeakage"] * d["wind"],
    )

    # Total ventilation through the roof [m^{3} m^{-2} s^{-1}]
    # Equation 71 [1], Equation A42 [5]

    a["fVentRoof"] = ifElse(
        a["etaRoof"] >= p["etaRoofThr"],
        p["etaInsScr"] * a["fVentRoof2"] + p["cLeakTop"] * a["fLeakage"],
        p["etaInsScr"]
        * (
            np.maximum(u["thScr"], u["blScr"]) * a["fVentRoof2"]
            + (1 - np.maximum(u["thScr"], u["blScr"]))
            * a["fVentRoofSide2"]
            * a["etaRoof"]
        )
        + p["cLeakTop"] * a["fLeakage"],
    )

    # Total ventilation through side vents [m^{3} m^{-2} s^{-1}]
    # Equation 72 [1], Equation A43 [5]
    a["fVentSide"] = ifElse(
        a["etaRoof"] >= p["etaRoofThr"],
        p["etaInsScr"] * a["fVentSide2"] + (1 - p["cLeakTop"]) * a["fLeakage"],
        p["etaInsScr"]
        * (
            np.maximum(u["thScr"], u["blScr"]) * a["fVentSide2"]
            + (1 - np.maximum(u["thScr"], u["blScr"]))
            * a["fVentRoofSide2"]
            * a["etaSide"]
        )
        + (1 - p["cLeakTop"]) * a["fLeakage"],
    )

    ## Control rules

    # Hours since midnight [h]
    # result = hours_since_midnight(timestamp)
    # gl['a']['timeOfDay'] = hours_since_midnight(gl['x']['time'])

    # gl['a']['timeOfDay'] = 24*(gl['x']['time']-np.floor(gl['x']['time']))

    # # try:112366.612714
    # if x["time"] == np.inf:
    #     # print(f"时间出错！{gl['x']['time']}")
    #     x["time"] = prev_gl["x"]["time"]
    #     # print(f"时间纠正！{gl['x']['time']}")

    a["timeOfDay"] = 24 * (x["time"] - np.floor(x["time"]))
    # print(f"gl['x']['time'] = {gl['x']['time']}")
    # except RuntimeWarning as e:
    #     print('时间出错！')
    #     print(e)

    # 24*(x(19)-(floor(x(19))));

    # Day of year [d]
    a["dayOfYear"] = np.mod(x["time"], 365.2425)

    # gl['a']['dayOfYear'] = day_of_year(gl['x']['time'])

    # Control of the lamp according to the time of day [0/1]
    # if gl['p']['lampsOn'] <gl['p']['lampsOff'], lamps are on fromgl['p']['lampsOn'] togl['p']['lampsOff'] each day
    # if gl['p']['lampsOn'] >gl['p']['lampsOff'], lamps are on fromgl['p']['lampsOn'] untilgl['p']['lampsOff'] the next day
    # if gl['p']['lampsOn'] ==gl['p']['lampsOff'], lamps are always off
    # for continuous light, setgl['p']['lampsOn'] = -1,gl['p']['lampsOff'] = 25

    cond1 = np.logical_and(
        p["lampsOn"] <= p["lampsOff"],
        np.logical_and(
            p["lampsOn"] < a["timeOfDay"],
            a["timeOfDay"] < p["lampsOff"],
        ),
    )

    cond2 = np.logical_not(p["lampsOn"] <= p["lampsOff"])
    cond3 = np.logical_or(
        p["lampsOn"] < a["timeOfDay"],
        a["timeOfDay"] < p["lampsOff"],
    )

    a["lampTimeOfDay"] = (cond1 + cond2 * cond3) * 1

    # Control of the lamp according to the day of year [0/1]
    # ifgl['p']['dayLampStart'] <gl['p']['dayLampStop'], lamps are on fromgl['p']['dayLampStart'] togl['p']['dayLampStop']
    # ifgl['p']['dayLampStart'] >gl['p']['dayLampStop'], lamps are on fromgl['p']['lampsOn'] untilgl['p']['lampsOff'] the next year
    # ifgl['p']['dayLampStart'] ==gl['p']['dayLampStop'], lamps are always off
    # for no influence of day of year, setgl['p']['dayLampStart'] = -1,gl['p']['dayLampStop'] > 366

    # gl['a']['lampDayOfYear'] = ((gl['p']['dayLampStart']<=gl['p']['dayLampStop'])* (gl['p']['dayLampStart'] < gl['a']['dayOfYear'] & gl['a']['dayOfYear'] <gl['p']['dayLampStop']) +  (1-(gl['p']['dayLampStart']<=gl['p']['dayLampStop']))*(gl['p']['dayLampStart']<gl['a']['dayOfYear'] | gl['a']['dayOfYear']<gl['p']['dayLampStop']))*1 # multiply by 1 to convert from logical to double

    cond1 = np.logical_and(
        p["dayLampStart"] <= p["dayLampStop"],
        np.logical_and(
            p["dayLampStart"] < a["dayOfYear"],
            a["dayOfYear"] < p["dayLampStop"],
        ),
    )

    cond2 = np.logical_not(p["dayLampStart"] <= p["dayLampStop"])
    cond3 = np.logical_or(
        p["dayLampStart"] < a["dayOfYear"],
        a["dayOfYear"] < p["dayLampStop"],
    )

    a["lampDayOfYear"] = (cond1 + cond2 * cond3) * 1

    # Control for the lamps disregarding temperature and humidity constraints
    # Chapter 4 Section 2.3['2'], Chapter 5 Section 2.4 [7]
    # Section 2.3['2'] [8]
    # This variable is used to decide if the greenhouse is in the light period
    # ("day inside"), needed to set the climate setpoints.
    # However, the lamps may be switched off if it is too hot or too humid
    # in the greenhouse. In this case, the greenhouse is still considered
    # to be in the light period
    a["lampNoCons"] = (
        1
        * (d["iGlob"] < p["lampsOffSun"])
        * (d["dayRadSum"] < p["lampRadSumLimit"])
        * a["lampTimeOfDay"]
        * a["lampDayOfYear"]
    )  # and the day of year is within the lighting season

    ## Smoothing of control of the lamps
    # To allow smooth transition between day and night setpoints

    # Linear version of lamp switching on:
    # 1 at lampOn, 0 one hour before lampOn, with linear transition
    # Note: this current function doesn't do a linear interpolation if
    # lampOn == 0
    a["linearLampSwitchOn"] = np.maximum(0, min(1, a["timeOfDay"] - p["lampsOn"] + 1))

    # Linear version of lamp switching on:
    # 1 at lampOff, 0 one hour after lampOff, with linear transition
    # Note: this current function doesn't do a linear interpolation if
    # lampOff == 24
    a["linearLampSwitchOff"] = np.maximum(0, min(1, p["lampsOff"] - a["timeOfDay"] + 1))

    # Combination of linear transitions above
    # ifgl['p']['lampsOn'] <gl['p']['lampsOff'], take the minimum of the above
    # ifgl['p']['lampsOn'] >gl['p']['lampsOn'], take the maximum
    # ifgl['p']['lampsOn'] ==gl['p']['lampsOff'], set at 0
    a["linearLampBothSwitches"] = (p["lampsOn"] != p["lampsOff"]) * (
        (p["lampsOn"] < p["lampsOff"])
        * min(a["linearLampSwitchOn"], a["linearLampSwitchOff"])
        + (1 - (p["lampsOn"] < p["lampsOff"]))
        * np.maximum(a["linearLampSwitchOn"], a["linearLampSwitchOff"])
    )

    # Smooth (linear) approximation of the lamp control
    # To allow smooth transition between light period and dark period setpoints
    # 1 when lamps are on, 0 when lamps are off, with a linear
    # interpolation in between
    # Does not take into account the lamp switching off due to
    # instantaenous sun radiation, excess heat or humidity
    a["smoothLamp"] = (
        a["linearLampBothSwitches"]
        * (d["dayRadSum"] < p["lampRadSumLimit"])
        * a["lampDayOfYear"]
    )  # lamps off if day of year is not within the lighting season

    # Indicates whether daytime climate settings should be used, i['e']., if
    # the sun is out or the lamps are on
    # 1 if day, 0 if night. If lamps are on it is considered day

    a["isDayInside"] = np.maximum(a["smoothLamp"], d["isDay"])

    # Decision on whether mechanical cooling and dehumidification is allowed to work
    # (0 - not allowed, 1 - allowed)
    # By default there is no mechanical cooling and dehumidification
    a["mechAllowed"] = 0

    # Decision on whether heating from buffer is allowed to run
    # (0 - not allowed, 1 - allowed)
    # By default there is no heating from the buffer
    a["hotBufAllowed"] = 0
    # Only runs if the hot buffer is not empty

    # Heating set point [°C]
    # Chapter 5, Section 2.4, point 6 [7]
    # Chapter 4, Section 2.3['2'], point 3 and Section 2.3['3'] [7]
    # Section 2.3['2'], point 3 and Section 2.3['3'] [8]
    a["heatSetPoint"] = (
        a["isDayInside"] * p["tSpDay"]
        + (1 - a["isDayInside"]) * p["tSpNight"]
        + p["heatCorrection"] * a["lampNoCons"]
    )  # correction for LEDs when lamps are on

    # Ventilation setpoint due to excess heating set point [°C]
    # Chapter 5, Section 2.4, point 8 [7]
    # Chapter 4, Section 2.3['2'], point 4 [7]
    # Section 2.3['2'], point 4 [8]
    a["heatMax"] = a["heatSetPoint"] + p["heatDeadZone"]

    # CO2 set point [ppm]
    # Chapter 5, Section 2.4, point 5 [7]
    # Chapter 4, Section 2.3['2'], point 2 [7]
    # Section 2.3['2'], point 2 [8]
    a["co2SetPoint"] = a["isDayInside"] * p["co2SpDay"]

    # CO2 concentration in main compartment [ppm]
    a["co2InPpm"] = co2_dens2ppm(x["tAir"], 1e-6 * x["co2Air"])

    # Ventilation due to excess heat [0-1, 0 means vents are closed]
    a["ventHeat"] = proportionalControl(
        x["tAir"], a["heatMax"], p["ventHeatPband"], 0, 1
    )
    

    # Relative humidity [#]
    if satVp(x["tAir"]) == 0:
        a["rhIn"] = 100
    else:
        a["rhIn"] = 100 * x["vpAir"] / satVp(x["tAir"])
        

    # Ventilation due to excess humidity [0-1, 0 means vents are closed]
    # Chapter 5, Section 2.4, point 7 [7]
    # Chapter 4, Section 2.3['2'], point 4 [7]
    # Section 2.3['2'], point 4 [8]
    a["ventRh"] = proportionalControl(
        a["rhIn"],
        p["rhMax"] + a["mechAllowed"] * p["mechDehumidPband"],
        p["ventRhPband"],
        0,
        1,
    )
    # the setpoint of when to start ventilating depends on the mechanical dehumidification:
    # if it is on (a['mechAllowed'] == 1), start ventilating only when
    # mechanical dehumidification is at full capacity.
    # If it is off (a['mechAllowed'] == 0)
    # start at the normal setpoint

    # Ventilation closure due to too cold temperatures
    # [0-1, 0 means vents are closed because it's too cold inside to ventilate,
    # better to raise the RH by heating]
    # Chapter 5, Section 2.4, point 7 [7]
    # Chapter 4, Section 2.3['2'], point 4 [7]
    # Section 2.3['2'], point 4 [8]
    a["ventCold"] = proportionalControl(
        x["tAir"],
        a["heatSetPoint"] - p["tVentOff"],
        p["ventColdPband"],
        1,
        0,
    )

    # Setpoint for closing the thermal screen [°C]
    # Chapter 5, Section 2.4, point 4 [7]
    # Chapter 4, Section 2.3['2'], point 5 [7]
    # Section 2.3['2'], point 5 [8]
    a["thScrSp"] = d["isDay"] * p["thScrSpDay"] + (1 - d["isDay"]) * p["thScrSpNight"]

    # Closure of the thermal screen based on outdoor temperature [0-1, 0 is fully open]
    # Chapter 5, Section 2.4, point 4 [7]
    # Chapter 4, Section 2.3['2'], point 5 [7]
    # Section 2.3['2'], point 5 [8]
    a["thScrCold"] = proportionalControl(d["tOut"], a["thScrSp"], p["thScrPband"], 0, 1)

    # gl['a']['thScrCold'] = np.exp(((-2/(p["thScrPband"]))*4.6052)*(d["tOut"]-(a["thScrSp"])-((p["thScrPband"])/2)))
    # Opening of thermal screen closure due to too high temperatures
    # Chapter 5, Section 2.4, point 4 [7]
    # Chapter 4, Section 2.3['2'], point 5 [7]
    # Section 2.3['2'], point 5 [8]
    a["thScrHeat"] = proportionalControl(
        x["tAir"],
        a["heatSetPoint"] + p["thScrDeadZone"],
        -p["thScrPband"],
        1,
        0,
    )

    # Opening of thermal screen due to high humidity [0-1, 0 is fully open]
    # Chapter 5, Section 2.4, point 4 [7]
    # Chapter 4, Section 2.3['2'], point 5 [7]
    # Section 2.3['2'], point 5 [8]

    a["thScrRh"] = np.maximum(
        proportionalControl(
            a["rhIn"],
            p["rhMax"] + p["thScrRh"],
            p["thScrRhPband"],
            1,
            0,
        ),
        1 - a["ventCold"],
    )
    # if 1-a['ventCold'] == 0 (it's too cold inside to ventilate)
    # don't force to open the screen (even if RH says it should be 0)
    # Better to reduce RH by increasing temperature

    # Control for the top lights:
    # 1 if lamps are on, 0 if lamps are off

    a["lampOn"] = (
        a["lampNoCons"]
        * proportionalControl(x["tAir"], a["heatMax"] + p["lampExtraHeat"], -0.5, 0, 1)
        * (
            d["isDaySmooth"]
            + (1 - d["isDaySmooth"])
            * np.maximum(
                proportionalControl(
                    a["rhIn"],
                    p["rhMax"] + p["blScrExtraRh"],
                    -0.5,
                    0,
                    1,
                ),
                1 - a["ventCold"],
            )
        )
    )  # Unless ventCold == 0
    # print(gl['a']['lampOn'])
    # # 计算指数函数的参数的对数

    # # if np.isnan(x["tAir"]):
    # #     x["tAir"]= 0
    # # if np.isnan(a["heatMax"]):
    # #     a["heatMax"]= 0

    # if ventCold is 0 it's too cold inside to ventilate,
    # better to raise the RH by heating.
    # So don't open the blackout screen and
    # don't stop illuminating in this case.

    # Control for the interlights:
    # 1 if interlights are on, 0 if interlights are off
    a["intLampOn"] = (
        a["lampNoCons"]
        * proportionalControl(x["tAir"], a["heatMax"] + p["lampExtraHeat"], -0.5, 0, 1)
        * (
            d["isDaySmooth"]
            + (1 - d["isDaySmooth"])
            * np.maximum(
                proportionalControl(
                    a["rhIn"],
                    p["rhMax"] + p["blScrExtraRh"],
                    -0.5,
                    0,
                    1,
                ),
                1 - a["ventCold"],
            )
        )
    )
    # if ventCold is 0 it's too cold inside to ventilate,
    # better to raise the RH by heating.
    # So don't open the blackout screen and
    # don't stop illuminating in this case.

    ## Convection and conduction - Section 5.3 [1] 

    # density of air as it depends on pressure and temperature, see
    # https://en['wikipedia']['org']/wiki/Density_of_air
    a["rhoTop"] = p["mAir"] * p["pressure"] / ((x["tTop"] + 273.15) * p["R"])
    a["rhoAir"] = p["mAir"] * p["pressure"] / ((x["tAir"] + 273.15) * p["R"])

    # note a mistake in [1] - says rhoAirMean is the mean density "of the
    # greenhouse and the outdoor air". See [4], where rhoMean is "the mean
    # density of air beneath and above the screen".
    a["rhoAirMean"] = 0.5 * (a["rhoTop"] + a["rhoAir"])

    # Air flux through the thermal screen [m s^{-1}]
    # Equation 40 [1], Equation A36 [5]
    # There is a mistake in [1], see equation 5.68, pg. 91, [4]
    # tOut, rhoOut, should be tTop, rhoTop
    # There is also a mistake in [4], whenever sqrt is taken, abs should be included
    a["fThScr"] = u["thScr"] * p["kThScr"] * (abs((x["tAir"] - x["tTop"])) ** 0.66) + (
        (1 - u["thScr"]) / a["rhoAirMean"]
    ) * np.sqrt(
        0.5
        * a["rhoAirMean"]
        * (1 - u["thScr"])
        * p["g"]
        * abs(a["rhoAir"] - a["rhoTop"])
    )

    # Air flux through the blackout screen [m s^{-1}]
    # Equation A37 [5]
    a["fBlScr"] = u["blScr"] * p["kBlScr"] * (abs((x["tAir"] - x["tTop"])) ** 0.66) + (
        (1 - u["blScr"]) / a["rhoAirMean"]
    ) * np.sqrt(
        0.5
        * a["rhoAirMean"]
        * (1 - u["blScr"])
        * p["g"]
        * abs(a["rhoAir"] - a["rhoTop"])
    )

    # Air flux through the screens [m s^{-1}]
    # Equation A38 [5]
    a["fScr"] = np.minimum(a["fThScr"], a["fBlScr"])

    ## Convective and conductive heat fluxes [W m^{-2}]
    # Table 4 [1]

    # Forced ventilation (doesn't exist in current gh)
    a["fVentForced"] = 0

    # Between canopy and air in main compartment [W m^{-2}]
    a["hCanAir"] = sensible(2 * p["alfaLeafAir"] * a["lai"], x["tCan"], x["tAir"])

    # Between air in main compartment and floor [W m^{-2}]
    a["hAirFlr"] = sensible(
        ifElse(
            x["tFlr"] > x["tAir"],
            1.7 * nthroot(abs(x["tFlr"] - x["tAir"]), 3),
            1.3 * nthroot(abs(x["tAir"] - x["tFlr"]), 4),
        ),
        x["tAir"],
        x["tFlr"],
    )

    # Between air in main compartment and thermal screen [W m^{-2}]
    a["hAirThScr"] = sensible(
        1.7 * u["thScr"] * nthroot(abs(x["tAir"] - x["tThScr"]), 3),
        x["tAir"],
        x["tThScr"],
    )

    # Between air in main compartment and blackout screen [W m^{-2}]
    # Equations A28, A32 [5]

    a["hAirBlScr"] = sensible(
        1.7 * u["blScr"] * nthroot(abs(x["tAir"] - x["tBlScr"]), 3),
        x["tAir"],
        x["tBlScr"],
    )

    # Between air in main compartment and outside air [W m^{-2}]
    a["hAirOut"] = sensible(
        p["rhoAir"] * p["cPAir"] * (a["fVentSide"] + a["fVentForced"]),
        x["tAir"],
        d["tOut"],
    )

    # Between air in main and top compartment [W m^{-2}]
    a["hAirTop"] = sensible(
        p["rhoAir"] * p["cPAir"] * a["fScr"],
        x["tAir"],
        x["tTop"],
    )
 
    # Between thermal screen and top compartment [W m^{-2}]
    a["hThScrTop"] = sensible(
        1.7 * u["thScr"] * nthroot(abs(x["tThScr"] - x["tTop"]), 3),
        x["tThScr"],
        x["tTop"],
    )

    # Between blackout screen and top compartment [W m^{-2}]
    a["hBlScrTop"] = sensible(
        1.7 * u["blScr"] * nthroot(abs(x["tBlScr"] - x["tTop"]), 3),
        x["tBlScr"],
        x["tTop"],
    )

    # Between top compartment and cover [W m^{-2}]
    a["hTopCovIn"] = sensible(
        p["cHecIn"] * nthroot(abs(x["tTop"] - x["tCovIn"]), 3) * p["aCov"] / p["aFlr"],
        x["tTop"],
        x["tCovIn"],
    )

    # Between top compartment and outside air [W m^{-2}]
    a["hTopOut"] = sensible(
        p["rhoAir"] * p["cPAir"] * a["fVentRoof"],
        x["tTop"],
        d["tOut"],
    )

    # Between cover and outside air [W m^{-2}]
    a["hCovEOut"] = sensible(
        p["aCov"]
        / p["aFlr"]
        * (p["cHecOut1"] + p["cHecOut2"] * d["wind"] ** p["cHecOut3"]),
        x["tCovE"],
        d["tOut"],
    )

    # Between pipes and air in main compartment [W m^{-2}]
    a["hPipeAir"] = sensible(
        1.99 * pi * p["phiPipeE"] * p["lPipe"] * (abs(x["tPipe"] - x["tAir"])) ** 0.32,
        x["tPipe"],
        x["tAir"],
    )

    # Between floor and soil layer 1 [W m^{-2}]
    a["hFlrSo1"] = sensible(
        2 / (p["hFlr"] / p["lambdaFlr"] + p["hSo1"] / p["lambdaSo"]),
        x["tFlr"],
        x["tSo1"],
    )

    # Between soil layers 1 and 2 [W m^{-2}]
    a["hSo1So2"] = sensible(
        2 * p["lambdaSo"] / (p["hSo1"] + p["hSo2"]),
        x["tSo1"],
        x["tSo2"],
    )

    # Between soil layers 2 and 3 [W m^{-2}]
    a["hSo2So3"] = sensible(
        2 * p["lambdaSo"] / (p["hSo2"] + p["hSo3"]),
        x["tSo2"],
        x["tSo3"],
    )

    # Between soil layers 3 and 4 [W m^{-2}]
    a["hSo3So4"] = sensible(
        2 * p["lambdaSo"] / (p["hSo3"] + p["hSo4"]),
        x["tSo3"],
        x["tSo4"],
    )

    # Between soil layers 4 and 5 [W m^{-2}]
    a["hSo4So5"] = sensible(
        2 * p["lambdaSo"] / (p["hSo4"] + p["hSo5"]),
        x["tSo4"],
        x["tSo5"],
    )

    # Between soil layer 5 and the external soil temperature [W m^{-2}]
    # See Equations 4 and 77 [1]
    a["hSo5SoOut"] = sensible(
        2 * p["lambdaSo"] / (p["hSo5"] + p["hSoOut"]),
        x["tSo5"],
        d["tSoOut"],
    )

    # Conductive heat flux through the lumped cover [W K^{-1} m^{-2}]
    # See comment after Equation 18 [1]
    a["hCovInCovE"] = sensible(
        1
        / (
            p["hRf"] / p["lambdaRf"]
            + u["shScrPer"] * p["hShScrPer"] / p["lambdaShScrPer"]
        ),
        x["tCovIn"],
        x["tCovE"],
    )

    # Between lamps and air in main compartment [W m^{-2}]
    # Equation A29 [5]
    a["hLampAir"] = sensible(p["cHecLampAir"], x["tLamp"], x["tAir"])

    # Between grow pipes and air in main compartment [W m^{-2}]
    # Equations A31, A33 [5]
    a["hGroPipeAir"] = sensible(
        1.99
        * pi
        * p["phiGroPipeE"]
        * p["lGroPipe"]
        * (abs(x["tGroPipe"] - x["tAir"])) ** 0.32,
        x["tGroPipe"],
        x["tAir"],
    )

    # Between interlights and air in main compartment [W m^{-2}]
    # Equation A30 [5]
    a["hIntLampAir"] = sensible(p["cHecIntLampAir"], x["tIntLamp"], x["tAir"])

    ## Canopy transpiration - Section 8 [1]

    # Smooth switch between day and night [-]
    # Equation 50 [1]

    a["sRs"] = 1 / (1 + np.exp(p["sRs"] * (a["rCan"] - p["rCanSp"])))

    # Parameter for co2 influence on stomatal resistance [ppm{CO2}^{-2}]
    # Equation 51 [1]
    a["cEvap3"] = p["cEvap3Night"] * (1 - a["sRs"]) + p["cEvap3Day"] * a["sRs"]

    # Parameter for vapor pressure influence on stomatal resistance [Pa^{-2}]
    a["cEvap4"] = p["cEvap4Night"] * (1 - a["sRs"]) + p["cEvap4Day"] * a["sRs"]

    # Radiation influence on stomatal resistance [-]
    # Equation 49 [1]
    a["rfRCan"] = (a["rCan"] + p["cEvap1"]) / (a["rCan"] + p["cEvap2"])

    # CO2 influence on stomatal resistance [-]
    # Equation 49 [1]
    a["rfCo2"] = np.minimum(
        1.5,
        1 + a["cEvap3"] * (p["etaMgPpm"] * x["co2Air"] - 200) ** 2,
    )
    # perhpas replacegl['p']['etaMgPpm']*gl['x']['co2Air'] with a['co2InPpm']

    # Vapor pressure influence on stomatal resistance [-]
    # Equation 49 [1]
    a["rfVp"] = np.minimum(5.8, 1 + a["cEvap4"] * (satVp(x["tCan"]) - x["vpAir"]) ** 2)

    # Stomatal resistance [s m^{-1}]
    # Equation 48 [1]
    a["rS"] = p["rSMin"] * a["rfRCan"] * a["rfCo2"] * a["rfVp"]

    # Vapor transfer coefficient of canopy transpiration [kg m^{-2} Pa^{-1} s^{-1}]
    # Equation 47 [1]
    a["vecCanAir"] = (
        2
        * p["rhoAir"]
        * p["cPAir"]
        * a["lai"]
        / (p["L"] * p["gamma"] * (p["rB"] + a["rS"]))
    )

    # Canopy transpiration [kg m^{-2} s^{-1}]
    # Equation 46 [1]
    a["mvCanAir"] = (satVp(x["tCan"]) - x["vpAir"]) * a["vecCanAir"]

    ## Vapor fluxes  - Section 6 [1]

    # Vapor fluxes currently not included in the model - set at 0
    a["mvPadAir"] = 0
    a["mvFogAir"] = 0
    a["mvBlowAir"] = 0
    a["mvAirOutPad"] = 0

    # Condensation from main compartment on thermal screen [kg m^{-2} s^{-1}]
    # Table 4 [1], Equation 42 [1]
    a["mvAirThScr"] = cond(
        1.7 * u["thScr"] * nthroot(abs(x["tAir"] - x["tThScr"]), 3),
        x["vpAir"],
        satVp(x["tThScr"]),
    )

    # Condensation from main compartment on blackout screen [kg m^{-2} s^{-1}]
    # Equatio A39 [5], Equation 7.39 [7]
    a["mvAirBlScr"] = cond(
        1.7 * u["blScr"] * nthroot(abs(x["tAir"] - x["tBlScr"]), 3),
        x["vpAir"],
        satVp(x["tBlScr"]),
    )

    # Condensation from top compartment to cover [kg m^{-2} s^{-1}]
    # Table 4 [1]
    a["mvTopCovIn"] = cond(
        p["cHecIn"] * nthroot(abs(x["tTop"] - x["tCovIn"]), 3) * p["aCov"] / p["aFlr"],
        x["vpTop"],
        satVp(x["tCovIn"]),
    )

    # Vapor flux from main to top compartment [kg m^{-2} s^{-1}]
    a["mvAirTop"] = airMv(
        a["fScr"],
        x["vpAir"],
        x["vpTop"],
        x["tAir"],
        x["tTop"],
    )

    # Vapor flux from top compartment to outside [kg  m^{-2} s^{-1}]
    a["mvTopOut"] = airMv(
        a["fVentRoof"],
        x["vpTop"],
        d["vpOut"],
        x["tTop"],
        d["tOut"],
    )

    # Vapor flux from main compartment to outside [kg m^{-2} s^{-1}]
    a["mvAirOut"] = airMv(
        a["fVentSide"] + a["fVentForced"],
        x["vpAir"],
        d["vpOut"],
        x["tAir"],
        d["tOut"],
    )

    ## Latent heat fluxes - Section 5.4 [1]
    # Equation 41 [1]

    # Latent heat flux by transpiration [W m^{-2}]
    a["lCanAir"] = p["L"] * a["mvCanAir"]

    # Latent heat flux by condensation on thermal screen [W m^{-2}]
    a["lAirThScr"] = p["L"] * a["mvAirThScr"]

    # Latent heat flux by condensation on blackout screen [W m^{-2}]
    a["lAirBlScr"] = p["L"] * a["mvAirBlScr"]

    # Latent heat flux by condensation on cover [W m^{-2}]
    a["lTopCovIn"] = p["L"] * a["mvTopCovIn"]

    ## Canopy photosynthesis - Section 4.1 [2]

    # PAR absorbed by the canopy [umol{photons} m^{-2} s^{-1}]
    # Equation 17 [2]
    a["parCan"] = (
        p["zetaLampPar"] * a["rParLampCan"]
        + p["parJtoUmolSun"] * a["rParSunCan"]
        + p["zetaIntLampPar"] * a["rParIntLampCan"]
    )

    # Maximum rate of electron transport rate at 25C [umol{e-} m^{-2} s^{-1}]
    # Equation 16 [2]
    a["j25CanMax"] = a["lai"] * p["j25LeafMax"]

    # CO2 compensation point [ppm]
    # Equation 23 [2]

    a["gamma"] = divNoBracks(p["j25LeafMax"], (a["j25CanMax"]) * 1) * p["cGamma"] * x[
        "tCan"
    ] + 20 * p["cGamma"] * (1 - divNoBracks(p["j25LeafMax"], (a["j25CanMax"]) * 1))

    # CO2 concentration in the stomata [ppm]
    # Equation 21 [2]
    a["co2Stom"] = p["etaCo2AirStom"] * a["co2InPpm"]

    # Potential rate of electron transport [umol{e-} m^{-2} s^{-1}]
    # Equation 15 [2]
    # Note that R in [2] is 8.314 and R in [1] is 8314
    a["jPot"] = (
        a["j25CanMax"]
        * np.exp(
            p["eJ"]
            * (x["tCan"] + 273.15 - p["t25k"])
            / (1e-3 * p["R"] * (x["tCan"] + 273.15) * p["t25k"])
        )
        * (1 + np.exp((p["S"] * p["t25k"] - p["H"]) / (1e-3 * p["R"] * p["t25k"])))
        / (
            1
            + np.exp(
                (p["S"] * (x["tCan"] + 273.15) - p["H"])
                / (1e-3 * p["R"] * (x["tCan"] + 273.15))
            )
        )
    )

    # Electron transport rate [umol{e-} m^{-2} s^{-1}]
    # Equation 14 [2]
    a["j"] = (1 / (2 * p["theta"])) * (
        a["jPot"]
        + p["alpha"] * a["parCan"]
        - np.sqrt(
            (a["jPot"] + p["alpha"] * a["parCan"]) ** 2
            - 4 * p["theta"] * a["jPot"] * p["alpha"] * a["parCan"]
        )
    )

    # Photosynthesis rate at canopy level [umol{co2} m^{-2} s^{-1}]
    # Equation 12 [2]
    a["p"] = (
        a["j"] * (a["co2Stom"] - a["gamma"]) / (4 * (a["co2Stom"] + 2 * a["gamma"]))
    )

    # Photrespiration [umol{co2} m^{-2} s^{-1}]
    # Equation 13 [2]
    a["r"] = a["p"] * a["gamma"] / a["co2Stom"]

    # Inhibition due to full carbohydrates buffer [-]
    # Equation 11, Equation B[1], Table 5 [2]
    a["hAirBuf"] = 1 / (1 + np.exp(5e-4 * (x["cBuf"] - p["cBufMax"])))

    # Net photosynthesis [mg{CH2O} m^{-2} s^{-1}]
    # Equation 10 [2]
    a["mcAirBuf"] = p["mCh2o"] * a["hAirBuf"] * (a["p"] - a["r"])

    ## Carbohydrate buffer
    # Temperature effect on structural carbon flow to organs
    # Equation 28 [2]
    a["gTCan24"] = 0.047 * x["tCan24"] + 0.06

    # Inhibition of carbohydrate flow to the organs
    # Equation B['3'] [2]
    a["hTCan24"] = (
        1
        / (1 + np.exp(-1.1587 * (x["tCan24"] - p["tCan24Min"])))
        * 1
        / (1 + np.exp(1.3904 * (x["tCan24"] - p["tCan24Max"])))
    )

    # Inhibition of carbohydrate flow to the fruit
    # Equation B['3'] [2]
    a["hTCan"] = (
        1
        / (1 + np.exp(-0.869 * (x["tCan"] - p["tCanMin"])))
        * 1
        / (1 + np.exp(0.5793 * (x["tCan"] - p["tCanMax"])))
    )

    # Inhibition due to development stage
    # Equation B['6'] [2]
    a["hTCanSum"] = 0.5 * (
        x["tCanSum"] / p["tEndSum"] + np.sqrt((x["tCanSum"] / p["tEndSum"]) ** 2 + 1e-4)
    ) - 0.5 * (
        (x["tCanSum"] - p["tEndSum"]) / p["tEndSum"]
        + np.sqrt(((x["tCanSum"] - p["tEndSum"]) / p["tEndSum"]) ** 2 + 1e-4)
    )

    # Inhibition due to insufficient carbohydrates in the buffer [-]
    # Equation 26 [2]
    a["hBufOrg"] = 1 / (1 + np.exp(-5e-3 * (x["cBuf"] - p["cBufMin"])))

    # Carboyhdrate flow from buffer to leaves [mg{CH2O} m^{2} s^{-1}]
    # Equation 25 [2]
    a["mcBufLeaf"] = a["hBufOrg"] * a["hTCan24"] * a["gTCan24"] * p["rgLeaf"]

    # Carboyhdrate flow from buffer to stem [mg{CH2O} m^{2} s^{-1}]
    # Equation 25 [2]
    a["mcBufStem"] = a["hBufOrg"] * a["hTCan24"] * a["gTCan24"] * p["rgStem"]

    # Carboyhdrate flow from buffer to fruit [mg{CH2O} m^{2} s^{-1}]
    # Equation 24 [2]
    a["mcBufFruit"] = (
        a["hBufOrg"]
        * a["hTCan"]
        * a["hTCan24"]
        * a["hTCanSum"]
        * a["gTCan24"]
        * p["rgFruit"]
    )

    ## Growth and maintenance respiration - Section 4.4 [2]

    # Growth respiration [mg{CH2O} m^{-2] s^{-1}]
    # Equations 43-44 [2]
    a["mcBufAir"] = (
        p["cLeafG"] * a["mcBufLeaf"]
        + p["cStemG"] * a["mcBufStem"]
        + p["cFruitG"] * a["mcBufFruit"]
    )

    # Leaf maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
    # Equation 45 [2]
    a["mcLeafAir"] = (
        (1 - np.exp(-p["cRgr"] * p["rgr"]))
        * p["q10m"] ** (0.1 * (x["tCan24"] - 25))
        * x["cLeaf"]
        * p["cLeafM"]
    )

    # Stem maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
    # Equation 45 [2]
    a["mcStemAir"] = (
        (1 - np.exp(-p["cRgr"] * p["rgr"]))
        * p["q10m"] ** (0.1 * (x["tCan24"] - 25))
        * x["cStem"]
        * p["cStemM"]
    )

    # Fruit maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
    # Equation 45 [2]
    a["mcFruitAir"] = (
        (1 - np.exp(-p["cRgr"] * p["rgr"]))
        * p["q10m"] ** (0.1 * (x["tCan24"] - 25))
        * x["cFruit"]
        * p["cFruitM"]
    )

    # Total maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
    # Equation 45 [2]
    a["mcOrgAir"] = a["mcLeafAir"] + a["mcStemAir"] + a["mcFruitAir"]

    ## Leaf pruning and fruit harvest
    # A new smoothing function has been applied here to avoid stiffness
    # Leaf pruning [mg{CH2O} m^{-2] s^{-1}]
    # Equation B['5'] [2]
    a["mcLeafHar"] = smoothHar(x["cLeaf"], p["cLeafMax"], 1e4, 5e4)

    # Fruit harvest [mg{CH2O} m^{-2} s^{-1}]
    # Equation A45 [5], Equation 7.45 [7]
    a["mcFruitHar"] = smoothHar(x["cFruit"], p["cFruitMax"], 1e4, 5e4)

    ## CO2 Fluxes - Section 7 [1]

    # Net crop assimilation [mg{CO2} m^{-2} s^{-1}]
    # It is assumed that for every mol of CH2O in net assimilation, a mol
    # of CO2 is taken from the air, thus the conversion uses molar masses
    a["mcAirCan"] = (p["mCo2"] / p["mCh2o"]) * (
        a["mcAirBuf"] - a["mcBufAir"] - a["mcOrgAir"]
    )

    # Other CO2 flows [mg{CO2} m^{-2} s^{-1}]
    # Equation 45 [1]

    # From main to top compartment
    a["mcAirTop"] = airMc(a["fScr"], x["co2Air"], x["co2Top"])

    # From top compartment outside
    a["mcTopOut"] = airMc(a["fVentRoof"], x["co2Top"], d["co2Out"])

    # From main compartment outside
    a["mcAirOut"] = airMc(
        a["fVentSide"] + a["fVentForced"],
        x["co2Air"],
        d["co2Out"],
    )

    ## Heat from boiler - Section 9.2 [1]

    # Heat from boiler to pipe rails [W m^{-2}]
    # Equation 55 [1]
    a["hBoilPipe"] = u["boil"] * p["pBoil"] / p["aFlr"]

    # Heat from boiler to grow pipes [W m^{-2}]
    a["hBoilGroPipe"] = u["boilGro"] * p["pBoilGro"] / p["aFlr"]

    ## External CO2 source - Section 9.9 [1]

    # CO2 injection [mg m^{-2} s^{-1}]
    # Equation 76 [1]
    a["mcExtAir"] = u["extCo2"] * p["phiExtCo2"] / p["aFlr"]

    ## Objects not currently included in the model
    a["mcBlowAir"] = 0
    a["mcPadAir"] = 0
    a["hPadAir"] = 0
    a["hPasAir"] = 0
    a["hBlowAir"] = 0
    a["hAirPadOut"] = 0
    a["hAirOutPad"] = 0
    a["lAirFog"] = 0
    a["hIndPipe"] = 0
    a["hGeoPipe"] = 0

    ## Lamp cooling
    # Equation A34 [5], Equation 7.34 [7]
    a["hLampCool"] = p["etaLampCool"] * a["qLampIn"]

    ## Heat harvesting, mechanical cooling and dehumidification
    # By default there is no mechanical cooling or heat harvesting
    # see addHeatHarvesting['m'] for mechanical cooling and heat harvesting
    a["hecMechAir"] = 0
    a["hAirMech"] = 0
    a["mvAirMech"] = 0
    a["lAirMech"] = 0
    a["hBufHotPipe"] = 0

    # return gl

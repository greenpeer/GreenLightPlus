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



def set_gl_params(gl):
    """
    Set parameters for a GreenLight model based on the electronic appendices of Vanthoor (2011).
        Args:
    - gl: A GreenLight model nested dictionary.

    References:
    - Vanthoor, B., Stanghellini, C., van Henten, E. J. & de Visser, P. H. B.
    A methodology for model-based greenhouse design: Part 1, a greenhouse climate
    model for a broad range of designs and climates. Biosyst. Eng. 110, 363–377 (2011).
    - Vanthoor, B., de Visser, P. H. B., Stanghellini, C. & van Henten, E. J.
    A methodology for model-based greenhouse design: Part 2, description and
    validation of a tomato yield model. Biosyst. Eng. 110, 378-395 (2011).
    - Vanthoor, B. A model based greenhouse design method. (Wageningen University, 2011).
    - Vanthoor, B., van Henten, E.J., Stanghellini, C., and de Visser, P.H.B. (2011).
    A methodology for model-based greenhouse design: Part 3, sensitivity
    analysis of a combined greenhouse climate-crop yield model.
    Biosyst. Eng. 110, 396-412.
    - Vermeulen, P.C.M. (2016). Kwantitatieve informatie voor de glastuinbouw
    2016-2017 (Bleiswijk), page V56-V58 Vine tomato
    - Dueck, T., Elings, A., Kempkes, F., Knies, P., Garcia, N., Heij, G.,
    Janse, J., Kaarsemaker, R., Korsten, P., Maaswinkel, R., et al. (2004).
    Energie in kengetallen : op zoek naar een nieuwe balans.
    - Dueck, T., De Gelder, A., Janse, J., Kempkes, F., Baar, P.H., and
    Valstar, W. (2014). Het nieuwe belichten onder diffuus glas (Wageningen).
    - Katzin, D., van Mourik, S., Kempkes, F., & Van Henten, E. J. (2020).
    GreenLight - An open source model for greenhouses with supplemental
    lighting: Evaluation of heat requirements under LED and HPS lamps.
    Biosystems Engineering, 194, 61–81. https://doi.org/10.1016/j.biosystemseng.2020.03.010
    - Katzin, D. (2021). Energy saving by LED lighting in greenhouses:
    a process-based modelling approach (PhD thesis, Wageningen University).
    https://doi.org/10.18174/544434
    - Katzin, D., Marcelis, L. F. M., & van Mourik, S. (2021).
    Energy savings in greenhouses by transition from high-pressure sodium
    to LED lighting. Applied Energy, 281, 116019.
    https://doi.org/10.1016/j.apenergy.2020.116019

    """

    pi = np.pi

    p = gl["p"]
    
    p["alfaLeafAir"] = 5  # Convective heat exchange coefficient from the canopy leaf to the greenhouse air, W m^{-2} K^{-1}, nominal value: 5 [1]
    p["L"] = 2.45e6  # Latent heat of evaporation, J kg^{-1}{water}, nominal value: 2.45e6 [1]
    p["sigma"] = 5.67e-8  # Stefan-Boltzmann constant, W m^{-2} K^{-4}, nominal value: 5.67e-8 [1]
    p["epsCan"] = 1  # FIR emission coefficient of canopy, -, nominal value: 1 [1]
    p["epsSky"] = 1  # FIR emission coefficient of the sky, -, nominal value: 1 [1]
    p["etaGlobNir"] = 0.5  # Ratio of NIR in global radiation, -, nominal value: 0.5 [1]
    p["etaGlobPar"] = 0.5  # Ratio of PAR in global radiation, -, nominal value: 0.5 [1]
    
    p["etaMgPpm"] = 0.554  # CO2 conversion factor from mg m^{-3} to ppm, ppm mg^{-1} m^{3}, nominal value: 0.554 [1]
    p["etaRoofThr"] = 0.9  # Ratio between roof vent area and total vent area where no chimney effects is assumed, -, nominal value: 0.9 [1]
    p["rhoAir0"] = 1.2  # Density of air at sea level, kg m^{-3}, nominal value: 1.2 [1]
    p["rhoCanPar"] = 0.07  # PAR reflection coefficient, -, nominal value: 0.07 [1]
    p["rhoCanNir"] = 0.35  # NIR reflection coefficient of the top of the canopy, -, nominal value: 0.35 [1]
    p["rhoSteel"] = 7850  # Density of steel, kg m^{-3}, nominal value: 7850 [1]
    p["rhoWater"] = 1e3  # Density of water, kg m^{-3}, nominal value: 1e3 [1]
    p["gamma"] = 65.8  # Psychrometric constant, Pa K^{-1}, nominal value: 65.8 [1]
    p["omega"] = 1.99e-7  # Yearly frequency to calculate soil temperature, s^{-1}, nominal value: 1.99e-7 [1]
    p["capLeaf"] = 1.2e3  # Heat capacity of canopy leaves, J K^{-1} m^{-2}{leaf}, nominal value: 1.2e3 [1]
    p["cEvap1"] = 4.3  # Coefficient for radiation effect on stomatal resistance, W m^{-2}, nominal value: 4.3 [1]
    p["cEvap2"] = 0.54  # Coefficient for radiation effect on stomatal resistance, W m^{-2}, nominal value: 0.54 [1]
    
    
    p["cEvap3Day"] = 6.1e-7  # Coefficient for co2 effect on stomatal resistance (day), ppm^{-2}, nominal value: 6.1e-7 [1]
    p["cEvap3Night"] = 1.1e-11  # Coefficient for co2 effect on stomatal resistance (night), ppm^{-2}, nominal value: 1.1e-11 [1]
    p["cEvap4Day"] = 4.3e-6  # Coefficient for vapor pressure effect on stomatal resistance (day), Pa^{-2}, nominal value: 4.3e-6 [1]
    p["cEvap4Night"] = 5.2e-6  # Coefficient for vapor pressure effect on stomatal resistance (night), Pa^{-2}, nominal value: 5.2e-6 [1]
    p["cPAir"] = 1e3  # Specific heat capacity of air, J K^{-1} kg^{-1}, nominal value: 1e3 [1]
    p["cPSteel"] = 0.64e3  # Specific heat capacity of steel, J K^{-1} kg^{-1}, nominal value: 0.64e3 [1]
    p["cPWater"] = 4.18e3  # Specific heat capacity of water, J K^{-1} kg^{-1}, nominal value: 4.18e3 [1]
    p["g"] = 9.81  # Acceleration of gravity, m s^{-2}, nominal value: 9.81 [1]
    p["hSo1"] = 0.04  # Thickness of soil layer 1, m, nominal value: 0.04 [1]
    p["hSo2"] = 0.08  # Thickness of soil layer 2, m, nominal value: 0.08 [1]
    p["hSo3"] = 0.16  # Thickness of soil layer 3, m, nominal value: 0.16 [1]
    p["hSo4"] = 0.32  # Thickness of soil layer 4, m, nominal value: 0.32 [1]
    p["hSo5"] = 0.64  # Thickness of soil layer 5, m, nominal value: 0.64 [1]
    p["k1Par"] = 0.7  # PAR extinction coefficient of the canopy, -, nominal value: 0.7 [1]
    p["k2Par"] = 0.7  # PAR extinction coefficient of the canopy for light reflected from the floor, -, nominal value: 0.7 [1]
    p["kNir"] = 0.27  # NIR extinction coefficient of the canopy, -, nominal value: 0.27 [1]
    p["kFir"] = 0.94  # FIR extinction coefficient of the canopy, -, nominal value: 0.94 [1]
    p["mAir"] = 28.96  # Molar mass of air, kg kmol^{-1}, nominal value: 28.96 [1]
    p["hSoOut"] = 1.28  # Thickness of the external soil layer, m, nominal value: 1.28 (assumed)
    
    p["mWater"] = 18  # Molar mass of water, kg kmol^{-1}, nominal value: 18 [1]
    p["R"] = 8314  # Molar gas constant, J kmol^{-1} K^{-1}, nominal value: 8314 [1]
    p["rCanSp"] = 5  # Radiation value above the canopy when night becomes day, W m^{-2}, nominal value: 5 [1]
    p["rB"] = 275  # Boundary layer resistance of the canopy for transpiration, s m^{-1}, nominal value: 275 [1]
    p["rSMin"] = 82  # Minimum canopy resistance for transpiration, s m^{-1}, nominal value: 82 [1]
    p["sRs"] = -1  # Slope of smoothed stomatal resistance model, m W^{-2}, nominal value: -1 [1]
    
    
    # Location specific parameters - The Netherlands
    
    # Construction properties
    p["etaGlobAir"] = 0.1  # Ratio of global radiation absorbed by the greenhouse construction, -, nominal value: 0.1 [1]
    p["psi"] = 25  # Mean greenhouse cover slope, �, nominal value: 25 [1]
    p["aFlr"] = 1.4e4  # Floor area of greenhouse, m^{2}, nominal value: 1.4e4 [1]
    p["aCov"] = 1.8e4  # Surface of the cover including side walls, m^{2}, nominal value: 1.8e4 [1]
    p["hAir"] = 3.8  # Height of the main compartment, m, nominal value: 3.8 [1]
    p["hGh"] = 4.2  # Mean height of the greenhouse, m, nominal value: 4.2 [1]
    p["cHecIn"] = 1.86  # Convective heat exchange between cover and outdoor air, W m^{-2} K^{-1}, nominal value: 1.86 [1]
    p["cHecOut1"] = 2.8  # Convective heat exchange parameter between cover and outdoor air, W m^{-2}{cover} K^{-1}, nominal value: 2.8 [1]
    p["cHecOut2"] = 1.2  # Convective heat exchange parameter between cover and outdoor air, J m^{-3} K^{-1}, nominal value: 1.2 [1]
    p["cHecOut3"] = 1  # Convective heat exchange parameter between cover and outdoor air, -, nominal value: 1 [1]
    p["hElevation"] = 0  # Altitude of greenhouse, m above sea level, nominal value: 0 [1]
    
    # Ventilation properties 
    p["aRoof"] = 1.4e3  # Maximum roof ventilation area, -, nominal value: 0.1*aFlr [1]
    p["hVent"] = 0.68  # Vertical dimension of single ventilation opening, m, nominal value: 0.68 [1]
    p["etaInsScr"] = 1  # Porosity of the insect screen, -, nominal value: 1 [1]
    p["aSide"] = 0  # Side ventilation area, -, nominal value: 0 [1]
    p["cDgh"] = 0.75  # Ventilation discharge coefficient, -, nominal value: 0.75 [1]
    p["cLeakage"] = 1e-4  # Greenhouse leakage coefficient, -, nominal value: 1e-4 [1]
    p["cWgh"] = 0.09  # Ventilation global wind pressure coefficient, -, nominal value: 0.09 [1]
    p["hSideRoof"] = 0  # Vertical distance between mid points of side wall and roof ventilation opening, m, nominal value: 0 (no side ventilation)
    
    #  Roof 
    p["epsRfFir"] = 0.85  # FIR emission coefficient of the roof, -, nominal value: 0.85 [1]
    p["rhoRf"] = 2.6e3  # Density of the roof layer, kg m^{-3}, nominal value: 2.6e3 [1]
    p["rhoRfNir"] = 0.13  # NIR reflection coefficient of the roof, -, nominal value: 0.13 [1]
    p["rhoRfPar"] = 0.13  # PAR reflection coefficient of the roof, -, nominal value: 0.13 [1]
    p["rhoRfFir"] = 0.15  # FIR reflection coefficient of the roof, -, nominal value: 0.15 [1]
    p["tauRfNir"] = 0.85  # NIR transmission coefficient of the roof, -, nominal value: 0.85 [1]
    p["tauRfPar"] = 0.85  # PAR transmission coefficient of the roof, -, nominal value: 0.85 [1]
    p["tauRfFir"] = 0  # FIR transmission coefficient of the roof, -, nominal value: 0 [1]
    p["lambdaRf"] = 1.05  # Thermal heat conductivity of the roof, W m^{-1} K^{-1}, nominal value: 1.05 [1]
    p["cPRf"] = 0.84e3  # Specific heat capacity of roof layer, J K^{-1} kg^{-1}, nominal value: 0.84e3 [1]
    p["hRf"] = 4e-3  # Thickness of roof layer, m, nominal value: 4e-3 [1]
    
    
    # Whitewash
    p["epsShScrPerFir"] = 0  # FIR emission coefficient of the whitewash - 0 (no whitewash)
    p["rhoShScrPer"] = 0  # Density of the whitewash - 0 (no whitewash)
    p["rhoShScrPerNir"] = 0  # NIR reflection coefficient of whitewash - 0 (no whitewash)
    p["rhoShScrPerPar"] = 0  # PAR reflection coefficient of whitewash - 0 (no whitewash)
    p["rhoShScrPerFir"] = 0  # FIR reflection coefficient of whitewash - 0 (no whitewash)
    p["tauShScrPerNir"] = 1  # NIR transmission coefficient of whitewash - 1 (no whitewash)
    p["tauShScrPerPar"] = 1  # PAR transmission coefficient of whitewash - 1 (no whitewash)
    p["tauShScrPerFir"] = 1  # FIR transmission coefficient of whitewash - 1 (no whitewash)
    p["lambdaShScrPer"] = 1e20  # Thermal heat conductivity of the whitewash - Inf (no whitewash)
    p["cPShScrPer"] = 0  # Specific heat capacity of the whitewash - 0 (no whitewash)
    p["hShScrPer"] = 0  # Thickness of the whitewash - 0 (no whitewash)
    
    # Shadow screen 
    p["rhoShScrNir"] = 0  # NIR reflection coefficient of shadow screen - 0 (no shadow screen)
    p["rhoShScrPar"] = 0  # PAR reflection coefficient of shadow screen - 0 (no shadow screen)
    p["rhoShScrFir"] = 0  # FIR reflection coefficient of shadow screen - 0 (no shadow screen)
    p["tauShScrNir"] = 1  # NIR transmission coefficient of shadow screen - 1 (no shadow screen)
    p["tauShScrPar"] = 1  # PAR transmission coefficient of shadow screen - 1 (no shadow screen)
    p["tauShScrFir"] = 1  # FIR transmission coefficient of shadow screen - 1 (no shadow screen)
    p["etaShScrCd"] = 0  # Effect of shadow screen on discharge coefficient - 0 (no shadow screen)
    p["etaShScrCw"] = 0  # Effect of shadow screen on wind pressure coefficient - 0 (no shadow screen)
    p["kShScr"] = 0  # Shadow screen flux coefficient - 0 (no shadow screen)
    
    # Thermal screen 
    p["epsThScrFir"] = 0.67  # FIR emissions coefficient of the thermal screen - 0.67 [1]
    p["rhoThScr"] = 0.2e3  # Density of thermal screen - 0.2e3 [1]
    p["rhoThScrNir"] = 0.35  # NIR reflection coefficient of thermal screen - 0.35 [1]
    p["rhoThScrPar"] = 0.35  # PAR reflection coefficient of thermal screen - 0.35 [1]
    p["rhoThScrFir"] = 0.18  # FIR reflection coefficient of thermal screen - 0.18 [1]
    p["tauThScrNir"] = 0.6  # NIR transmission coefficient of thermal screen - 0.6 [1]
    p["tauThScrPar"] = 0.6  # PAR transmission coefficient of thermal screen - 0.6 [1]
    p["tauThScrFir"] = 0.15  # FIR transmission coefficient of thermal screen - 0.15 [1]
    p["cPThScr"] = 1.8e3  # Specific heat capacity of thermal screen - 1.8e3 [1]
    p["hThScr"] = 0.35e-3  # Thickness of thermal screen - 0.35e-3 [1]
    p["kThScr"] = 0.05e-3  # Thermal screen flux coefficient - 0.05e-3 [1]
    
    
    # Blackout screen
    # Assumed to be the same as the thermal screen, except 1% transmissivity, and a higher FIR transmission
    p["epsBlScrFir"] = 0.67  # FIR emissions coefficient of the blackout screen
    p["rhoBlScr"] = 0.2e3  # Density of blackout screen
    p["rhoBlScrNir"] = 0.35  # NIR reflection coefficient of blackout screen
    p["rhoBlScrPar"] = 0.35  # PAR reflection coefficient of blackout screen
    p["tauBlScrNir"] = 0.01  # NIR transmission coefficient of blackout screen
    p["tauBlScrPar"] = 0.01  # PAR transmission coefficient of blackout screen
    p["tauBlScrFir"] = 0.7  # FIR transmission coefficient of blackout screen
    p["cPBlScr"] = 1.8e3  # Specific heat capacity of blackout screen
    p["hBlScr"] = 0.35e-3  # Thickness of blackout screen
    p["kBlScr"] = 0.05e-3  # Blackout screen flux coefficient
    
    # Floor
    p["epsFlr"] = 1  # FIR emission coefficient of the floor
    p["rhoFlr"] = 2300  # Density of the floor
    p["rhoFlrNir"] = 0.5  # NIR reflection coefficient of the floor
    p["rhoFlrPar"] = 0.65  # PAR reflection coefficient of the floor
    p["lambdaFlr"] = 1.7  # Thermal heat conductivity of the floor
    p["cPFlr"] = 0.88e3  # Specific heat capacity of the floor
    p["hFlr"] = 0.02  # Thickness of floor

    # Soil
    p["rhoCpSo"] = 1.73e6  # Volumetric heat capacity of the soil
    p["lambdaSo"] = 0.85  # Thermal heat conductivity of the soil layers

    # Heating system
    p["epsPipe"] = 0.88  # FIR emission coefficient of the heating pipes
    p["phiPipeE"] = 51e-3  # External diameter of pipes
    p["phiPipeI"] = 47e-3  # Internal diameter of pipes
    p["lPipe"] = 1.875  # Length of heating pipes per greenhouse floor area
    p["pBoil"] = 130 * p["aFlr"]  # Capacity of the heating system
    
    #  Active climate control
    p["phiExtCo2"] = 7.2e4
    
    
    #  Other parameters that depend on previously defined parameters
    
    # Heat capacity of heating pipes [J K^{-1} m^{-2}]
    p["capPipe"] = (
        0.25
        * pi
        * p["lPipe"]
        * (
            (p["phiPipeE"] ** 2 - p["phiPipeI"] ** 2) * p["rhoSteel"] * p["cPSteel"]
            + p["phiPipeI"] ** 2 * p["rhoWater"] * p["cPWater"]
        )
    )
    
    # Density of the air [kg m^{-3}]
    p["rhoAir"] = p["rhoAir0"] * np.exp(
        p["g"] * p["mAir"] * p["hElevation"] / (293.15 * p["R"])
    )
    
    # Heat capacity of greenhouse objects [J K^{-1} m^{-2}]
    p["capAir"] = p["hAir"] * p["rhoAir"] * p["cPAir"]
    p["capFlr"] = p["hFlr"] * p["rhoFlr"] * p["cPFlr"]
    p["capSo1"] = p["hSo1"] * p["rhoCpSo"]
    p["capSo2"] = p["hSo2"] * p["rhoCpSo"]
    p["capSo3"] = p["hSo3"] * p["rhoCpSo"]
    p["capSo4"] = p["hSo4"] * p["rhoCpSo"]
    p["capSo5"] = p["hSo5"] * p["rhoCpSo"]
    p["capThScr"] = p["hThScr"] * p["rhoThScr"] * p["cPThScr"]
    p["capTop"] = (p["hGh"] - p["hAir"]) * p["rhoAir"] * p["cPAir"]
    p["capBlScr"] = p["hBlScr"] * p["rhoBlScr"] * p["cPBlScr"]
    p["capCo2Air"] = p["hAir"]
    p["capCo2Top"] = p["hGh"] - p["hAir"]
    p["aPipe"] = pi * p["lPipe"] * p["phiPipeE"]
    p["fCanFlr"] = 1 - 0.49 * pi * p["lPipe"] * p["phiPipeE"]
    p["pressure"] = 101325 * (1 - 2.5577e-5 * p["hElevation"]) ** 5.25588
    p["globJtoUmol"] = 2.3
    p["j25LeafMax"] = 210
    p["cGamma"] = 1.7
    p["etaCo2AirStom"] = 0.67
    p["eJ"] = 37e3
    p["t25k"] = 298.15
    p["S"] = 710
    p["H"] = 22e4
    p["theta"] = 0.7
    p["alpha"] = 0.385
    p["mCh2o"] = 30e-3
    p["mCo2"] = 44e-3
    p["parJtoUmolSun"] = 4.6
    p["laiMax"] = 3
    p["sla"] = 2.66e-5
    p["rgr"] = 3e-6
    p["cLeafMax"] = p["laiMax"] / p["sla"]
    p["cFruitMax"] = 300e3
    p["cFruitG"] = 0.27
    p["cLeafG"] = 0.28
    p["cStemG"] = 0.3
    p["cRgr"] = 2.85e6
    p["q10m"] = 2
    p["cFruitM"] = 1.16e-7
    p["cLeafM"] = 3.47e-7
    p["cStemM"] = 1.47e-7
    p["rgFruit"] = 0.328
    p["rgLeaf"] = 0.095
    p["rgStem"] = 0.074
    p["cBufMax"] = 20e3
    p["cBufMin"] = 1e3
    p["tCan24Max"] = 24.5
    p["tCan24Min"] = 15
    p["tCanMax"] = 34
    p["tCanMin"] = 10
    p["tEndSum"] = 1035
    p["rhMax"] = 90
    p["dayThresh"] = 20
    p["tSpDay"] = 19.5
    p["tSpNight"] = 16.5
    p["tHeatBand"] = -1
    p["tVentOff"] = 1
    p["tScreenOn"] = 2
    p["thScrSpDay"] = 5
    p["thScrSpNight"] = 10
    p["thScrPband"] = -1
    p["co2SpDay"] = 800
    p["co2Band"] = -100
    p["heatDeadZone"] = 5
    p["ventHeatPband"] = 4
    p["ventColdPband"] = -1
    p["ventRhPband"] = 5
    p["thScrRh"] = -2
    p["thScrRhPband"] = 2
    p["thScrDeadZone"] = 4
    p["lampsOn"] = 0
    p["lampsOff"] = 0
    p["dayLampStart"] = -1
    p["dayLampStop"] = 400
    p["lampsOffSun"] = 400
    p["lampRadSumLimit"] = 10
    p["lampExtraHeat"] = 2
    p["blScrExtraRh"] = 100
    p["useBlScr"] = 0
    p["mechCoolPband"] = 1
    p["mechDehumidPband"] = 2
    p["heatBufPband"] = -1
    p["mechCoolDeadZone"] = 2
    p["epsGroPipe"] = 0
    p["lGroPipe"] = 1.655
    p["phiGroPipeE"] = 35e-3
    p["phiGroPipeI"] = (35e-3) - (1.2e-3)
    p["aGroPipe"] = pi * p["lGroPipe"] * p["phiGroPipeE"]
    p["pBoilGro"] = 0
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
    p["thetaLampMax"] = 0
    p["heatCorrection"] = 0
    p["etaLampPar"] = 0
    p["etaLampNir"] = 0
    p["tauLampPar"] = 1
    p["rhoLampPar"] = 0
    p["tauLampNir"] = 1
    p["rhoLampNir"] = 0
    p["tauLampFir"] = 1
    p["aLamp"] = 0
    p["epsLampTop"] = 0
    p["epsLampBottom"] = 0
    p["capLamp"] = 350
    p["cHecLampAir"] = 0
    p["etaLampCool"] = 0
    p["zetaLampPar"] = 0
    p["vIntLampPos"] = 0.5
    p["fIntLampDown"] = 0.5
    p["capIntLamp"] = 10
    p["etaIntLampPar"] = 0
    p["etaIntLampNir"] = 0
    p["aIntLamp"] = 0
    p["epsIntLamp"] = 0
    p["thetaIntLampMax"] = 0
    p["zetaIntLampPar"] = 0
    p["cHecIntLampAir"] = 0
    p["tauIntLampFir"] = 1
    p["k1IntPar"] = 1.4
    p["k2IntPar"] = 1.4
    p["kIntNir"] = 0.54
    p["kIntFir"] = 1.88
    p["cLeakTop"] = 0.5
    p["minWind"] = 0.25

    return gl

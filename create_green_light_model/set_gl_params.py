# File path: GreenLightPlus/create_green_light_model/set_gl_params.py
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
class GreenLightParams:
    """
    The GreenLightParams class is a comprehensive parameter setter for a greenhouse model. 
    It configures a wide range of parameters including physical constants, thermodynamic properties, radiation factors,
    material characteristics, greenhouse structural elements, plant canopy attributes, climate control settings, 
    and various system-specific parameters for heating, lighting, ventilation, and crop growth.

    """
    
    def __init__(self, gl):
        self.gl = gl
        self.p = gl["p"]

    def set_physical_constants(self):
        """Set physical constants in the model."""
        self.p["sigma"] = 5.67e-8  # Stefan-Boltzmann constant [W m^{-2} K^{-4}]
        self.p["g"]        = 9.81     # Acceleration of gravity [m s^{-2}]
        self.p["R"]        = 8314     # Molar gas constant [J kmol^{-1} K^{-1}]

    def set_thermodynamic_params(self):
        """Set thermodynamic parameters in the model."""
        self.p["L"]        = 2.45e6   # Latent heat of evaporation [J kg^{-1}{water}]
        self.p["gamma"]    = 65.8     # Psychrometric constant [Pa K^{-1}]
        self.p["cPAir"]    = 1e3      # Specific heat capacity of air [J K^{-1} kg^{-1}]
        self.p["cPSteel"]  = 0.64e3   # Specific heat capacity of steel [J K^{-1} kg^{-1}]
        self.p["cPWater"]  = 4.18e3   # Specific heat capacity of water [J K^{-1} kg^{-1}]

    def set_radiation_params(self):
        """Set radiation-related parameters in the model."""
        self.p["etaGlobNir"] = 0.5    # Ratio of NIR in global radiation [-]
        self.p["etaGlobPar"] = 0.5    # Ratio of PAR in global radiation [-]
        self.p["epsCan"]     = 1      # FIR emission coefficient of canopy [-]
        self.p["epsSky"]     = 1      # FIR emission coefficient of the sky [-]
        self.p["rhoCanPar"]  = 0.07   # PAR reflection coefficient [-]
        self.p["rhoCanNir"]  = 0.35   # NIR reflection coefficient of the top of the canopy [-]
        self.p["k1Par"]      = 0.7    # PAR extinction coefficient of the canopy [-]
        self.p["k2Par"]      = 0.7    # PAR extinction coefficient of the canopy for light reflected from the floor [-]
        self.p["kNir"]       = 0.27   # NIR extinction coefficient of the canopy [-]
        self.p["kFir"]       = 0.94   # FIR extinction coefficient of the canopy [-]

    def set_material_properties(self):
        """Set material properties in the model."""
        self.p["rhoAir0"]    = 1.2    # Density of air at sea level [kg m^{-3}]
        self.p["rhoSteel"]   = 7850   # Density of steel [kg m^{-3}]
        self.p["rhoWater"]   = 1e3    # Density of water [kg m^{-3}]
        self.p["mAir"]       = 28.96  # Molar mass of air [kg kmol^{-1}]
        self.p["mWater"]     = 18     # Molar mass of water [kg kmol^{-1}]


    def set_canopy_params(self):
        """Set canopy-related parameters in the model."""
        self.p["alfaLeafAir"] = 5      # Convective heat exchange coefficient from the canopy leaf to the greenhouse air [W m^{-2} K^{-1}]
        self.p["capLeaf"]     = 1.2e3  # Heat capacity of canopy leaves [J K^{-1} m^{-2}{leaf}]
        self.p["rB"]          = 275    # Boundary layer resistance of the canopy for transpiration [s m^{-1}]
        self.p["rSMin"]       = 82     # Minimum canopy resistance for transpiration [s m^{-1}]

    def set_stomatal_resistance_params(self):
        """Set stomatal resistance parameters in the model."""
        self.p["cEvap1"]        = 4.3      # Coefficient for radiation effect on stomatal resistance [W m^{-2}]
        self.p["cEvap2"]        = 0.54     # Coefficient for radiation effect on stomatal resistance [W m^{-2}]
        self.p["cEvap3Day"]     = 6.1e-7   # Coefficient for CO2 effect on stomatal resistance (day) [ppm^{-2}]
        self.p["cEvap3Night"]   = 1.1e-11  # Coefficient for CO2 effect on stomatal resistance (night) [ppm^{-2}]
        self.p["cEvap4Day"]     = 4.3e-6   # Coefficient for vapor pressure effect on stomatal resistance (day) [Pa^{-2}]
        self.p["cEvap4Night"]   = 5.2e-6   # Coefficient for vapor pressure effect on stomatal resistance (night) [Pa^{-2}]
        self.p["sRs"]           = -1       # Slope of smoothed stomatal resistance model [m W^{-2}]

    def set_soil_params(self):
        """Set soil parameters in the model."""
        self.p["hSo1"]      = 0.04      # Thickness of soil layer 1 [m]
        self.p["hSo2"]      = 0.08      # Thickness of soil layer 2 [m]
        self.p["hSo3"]      = 0.16      # Thickness of soil layer 3 [m]
        self.p["hSo4"]      = 0.32      # Thickness of soil layer 4 [m]
        self.p["hSo5"]      = 0.64      # Thickness of soil layer 5 [m]
        self.p["hSoOut"]    = 1.28      # Thickness of the external soil layer [m]
        self.p["omega"]     = 1.99e-7   # Yearly frequency to calculate soil temperature [s^{-1}]
 
    def set_construction_properties(self):
        """Set construction properties of the greenhouse."""
        self.p["etaGlobAir"]   = 0.1    # Ratio of global radiation absorbed by the greenhouse construction [-]
        self.p["psi"]          = 25     # Mean greenhouse cover slope [degrees]
        self.p["aFlr"]         = 1.4e4  # Floor area of greenhouse [m^2]
        self.p["aCov"]         = 1.8e4  # Surface of the cover including side walls [m^2]
        self.p["hAir"]         = 3.8    # Height of the main compartment [m]
        self.p["hGh"]          = 4.2    # Mean height of the greenhouse [m]
        self.p["cHecIn"]       = 1.86   # Convective heat exchange between cover and outdoor air [W m^{-2} K^{-1}]
        self.p["cHecOut1"]     = 2.8    # Convective heat exchange parameter between cover and outdoor air [W m^{-2}{cover} K^{-1}]
        self.p["cHecOut2"]     = 1.2    # Convective heat exchange parameter between cover and outdoor air [J m^{-3} K^{-1}]
        self.p["cHecOut3"]     = 1      # Convective heat exchange parameter between cover and outdoor air [-]
        self.p["hElevation"]   = 0      # Altitude of greenhouse [m above sea level]

    def set_ventilation_properties(self):
        """Set ventilation properties of the greenhouse."""
        self.p["aRoof"]        = 1.4e3  # Maximum roof ventilation area [-]
        self.p["hVent"]        = 0.68   # Vertical dimension of single ventilation opening [m]
        self.p["etaInsScr"]    = 1      # Porosity of the insect screen [-]
        self.p["aSide"]        = 0      # Side ventilation area [-]
        self.p["cDgh"]         = 0.75   # Ventilation discharge coefficient [-]
        self.p["cLeakage"]     = 1e-4   # Greenhouse leakage coefficient [-]
        self.p["cWgh"]         = 0.09   # Ventilation global wind pressure coefficient [-]
        self.p["hSideRoof"]    = 0      # Vertical distance between mid points of side wall and roof ventilation opening [m]

    def set_roof_properties(self):
        """Set roof properties of the greenhouse."""
        self.p["epsRfFir"]  = 0.85    # FIR emission coefficient of the roof [-]
        self.p["rhoRf"]     = 2.6e3   # Density of the roof layer [kg m^{-3}]
        self.p["rhoRfNir"]  = 0.13    # NIR reflection coefficient of the roof [-]
        self.p["rhoRfPar"]  = 0.13    # PAR reflection coefficient of the roof [-]
        self.p["rhoRfFir"]  = 0.15    # FIR reflection coefficient of the roof [-]
        self.p["tauRfNir"]  = 0.85    # NIR transmission coefficient of the roof [-]
        self.p["tauRfPar"]  = 0.85    # PAR transmission coefficient of the roof [-]
        self.p["tauRfFir"]  = 0       # FIR transmission coefficient of the roof [-]
        self.p["lambdaRf"]  = 1.05    # Thermal heat conductivity of the roof [W m^{-1} K^{-1}]
        self.p["cPRf"]      = 0.84e3  # Specific heat capacity of roof layer [J K^{-1} kg^{-1}]
        self.p["hRf"]       = 4e-3    # Thickness of roof layer [m]

    def set_whitewash_properties(self):
        """Set whitewash properties of the greenhouse."""
        self.p["epsShScrPerFir"]  = 0       # FIR emission coefficient of the whitewash [-]
        self.p["rhoShScrPer"]     = 0       # Density of the whitewash [-]
        self.p["rhoShScrPerNir"]  = 0       # NIR reflection coefficient of whitewash [-]
        self.p["rhoShScrPerPar"]  = 0       # PAR reflection coefficient of whitewash [-]
        self.p["rhoShScrPerFir"]  = 0       # FIR reflection coefficient of whitewash [-]
        self.p["tauShScrPerNir"]  = 1       # NIR transmission coefficient of whitewash [-]
        self.p["tauShScrPerPar"]  = 1       # PAR transmission coefficient of whitewash [-]
        self.p["tauShScrPerFir"]  = 1       # FIR transmission coefficient of whitewash [-]
        self.p["lambdaShScrPer"]  = float('inf')  # Thermal heat conductivity of the whitewash [W m^{-1} K^{-1}]
        self.p["cPShScrPer"]      = 0       # Specific heat capacity of the whitewash [J K^{-1} kg^{-1}]
        self.p["hShScrPer"]       = 0       #3 Thickness of the whitewash [m]

    def set_shadow_screen_properties(self):
        """Set shadow screen properties of the greenhouse."""
        self.p["rhoShScrNir"]  = 0       # NIR reflection coefficient of shadow screen [-]
        self.p["rhoShScrPar"]  = 0       # PAR reflection coefficient of shadow screen [-]
        self.p["rhoShScrFir"]  = 0       # FIR reflection coefficient of shadow screen [-]
        self.p["tauShScrNir"]  = 1       # NIR transmission coefficient of shadow screen [-]
        self.p["tauShScrPar"]  = 1       # PAR transmission coefficient of shadow screen [-]
        self.p["tauShScrFir"]  = 1       # FIR transmission coefficient of shadow screen [-]
        self.p["etaShScrCd"]   = 0       # Effect of shadow screen on discharge coefficient [-]
        self.p["etaShScrCw"]   = 0       # Effect of shadow screen on wind pressure coefficient [-]
        self.p["kShScr"]       = 0       # Shadow screen flux coefficient [m^{3} m^{-2} K^{-2/3} s^{-1}]

    def set_thermal_screen_properties(self):
        """Set thermal screen properties of the greenhouse."""
        self.p["epsThScrFir"]  = 0.67    # FIR emissions coefficient of the thermal screen [-]
        self.p["rhoThScr"]     = 0.2e3   # Density of thermal screen [kg m^{-3}]
        self.p["rhoThScrNir"]  = 0.35    # NIR reflection coefficient of thermal screen [-]
        self.p["rhoThScrPar"]  = 0.35    # PAR reflection coefficient of thermal screen [-]
        self.p["rhoThScrFir"]  = 0.18    # FIR reflection coefficient of thermal screen [-]
        self.p["tauThScrNir"]  = 0.6     # NIR transmission coefficient of thermal screen [-]
        self.p["tauThScrPar"]  = 0.6     # PAR transmission coefficient of thermal screen [-]
        self.p["tauThScrFir"]  = 0.15    # FIR transmission coefficient of thermal screen [-]
        self.p["cPThScr"]      = 1.8e3   # Specific heat capacity of thermal screen [J kg^{-1} K^{-1}]
        self.p["hThScr"]       = 0.35e-3 # Thickness of thermal screen [m]
        self.p["kThScr"]       = 0.05e-3 # Thermal screen flux coefficient [m^{3} m^{-2} K^{-2/3} s^{-1}]

    def set_blackout_screen_properties(self):
        """Set blackout screen properties of the greenhouse."""
        self.p["epsBlScrFir"]  = 0.67    # FIR emissions coefficient of the blackout screen [-]
        self.p["rhoBlScr"]     = 0.2e3   # Density of blackout screen [kg m^{-3}]
        self.p["rhoBlScrNir"]  = 0.35    # NIR reflection coefficient of blackout screen [-]
        self.p["rhoBlScrPar"]  = 0.35    # PAR reflection coefficient of blackout screen [-]
        self.p["tauBlScrNir"]  = 0.01    # NIR transmission coefficient of blackout screen [-]
        self.p["tauBlScrPar"]  = 0.01    # PAR transmission coefficient of blackout screen [-]
        self.p["tauBlScrFir"]  = 0.7     # FIR transmission coefficient of blackout screen [-]
        self.p["cPBlScr"]      = 1.8e3   # Specific heat capacity of blackout screen [J kg^{-1} K^{-1}]
        self.p["hBlScr"]       = 0.35e-3 # Thickness of blackout screen [m]
        self.p["kBlScr"]       = 0.05e-3 # Blackout screen flux coefficient [m^{3} m^{-2} K^{-2/3} s^{-1}]
        
    def set_floor_properties(self):
        """Set floor properties of the greenhouse."""
        self.p["epsFlr"]     = 1       # FIR emission coefficient of the floor [-]
        self.p["rhoFlr"]     = 2300    # Density of the floor [kg m^{-3}]
        self.p["rhoFlrNir"]  = 0.5     # NIR reflection coefficient of the floor [-]
        self.p["rhoFlrPar"]  = 0.65    # PAR reflection coefficient of the floor [-]
        self.p["lambdaFlr"]  = 1.7     # Thermal heat conductivity of the floor [W m^{-1} K^{-1}]
        self.p["cPFlr"]      = 0.88e3  # Specific heat capacity of the floor [J kg^{-1} K^{-1}]
        self.p["hFlr"]       = 0.02    # Thickness of floor [m]

    def set_soil_properties(self):
        """Set soil properties of the greenhouse."""
        self.p["rhoCpSo"]    = 1.73e6  # Volumetric heat capacity of the soil [J m^{-3} K^{-1}]
        self.p["lambdaSo"]   = 0.85    # Thermal heat conductivity of the soil layers [W m^{-1} K^{-1}]

    def set_heating_system_properties(self):
        """Set heating system properties of the greenhouse."""
        self.p["epsPipe"]    = 0.88    # FIR emission coefficient of the heating pipes [-]
        self.p["phiPipeE"]   = 51e-3   # External diameter of pipes [m]
        self.p["phiPipeI"]   = 47e-3   # Internal diameter of pipes [m]
        self.p["lPipe"]      = 1.875   # Length of heating pipes per gh floor area [m m^{-2}]
        self.p["pBoil"]      = 130 *self.p["aFlr"]  # Capacity of the heating system [W]

    def set_active_climate_control_properties(self):
        """Set active climate control properties of the greenhouse."""
        self.p["phiExtCo2"]  = 7.2e4   # Capacity of external CO2 source [mg s^{-1}]

        
    def set_heating_pipe_params(self):
        """Set heating pipe related parameters."""
        self.p["capPipe"] = 0.25 * np.pi *self.p["lPipe"] * (
            (self.gl["p"]["phiPipeE"]**2 -self.p["phiPipeI"]**2) *self.p["rhoSteel"] *self.p["cPSteel"] +
            self.p["phiPipeI"]**2 *self.p["rhoWater"] *self.p["cPWater"]
        )  # Heat capacity of heating pipes [J K^{-1} m^{-2}], Equation 21 [1]
        self.p["aPipe"] = np.pi *self.p["lPipe"] *self.p["phiPipeE"]
        # Surface of pipes for floor area [-], Table 3 [1]

    def set_air_density_params(self):
        """Set air density related parameters."""
        self.p["rhoAir"] =self.p["rhoAir0"] * np.exp(
            self.p["g"] *self.p["mAir"] *self.p["hElevation"] / (293.15 *self.p["R"])
        )  # Density of the air [kg m^{-3}], Equation 23 [1]
        self.p["pressure"] = 101325 * (1 - 2.5577e-5 *self.p["hElevation"])**5.25588
        # Absolute air pressure at given elevation [Pa], See https://www.engineeringtoolbox.com/air-altitude-pressure-d_462.html

    def set_heat_capacity_params(self):
        """Set heat capacity related parameters."""
        self.p["capAir"]     =self.p["hAir"] *self.p["rhoAir"] *self.p["cPAir"]              # Heat capacity of air in main compartment [J K^{-1} m^{-2}], Equation 22 [1]
        self.p["capFlr"]     =self.p["hFlr"] *self.p["rhoFlr"] *self.p["cPFlr"]              # Heat capacity of the floor [J K^{-1} m^{-2}]
        self.p["capSo1"]     =self.p["hSo1"] *self.p["rhoCpSo"]                              # Heat capacity of soil layer 1 [J K^{-1} m^{-2}]
        self.p["capSo2"]     =self.p["hSo2"] *self.p["rhoCpSo"]                              # Heat capacity of soil layer 2 [J K^{-1} m^{-2}]
        self.p["capSo3"]     =self.p["hSo3"] *self.p["rhoCpSo"]                              # Heat capacity of soil layer 3 [J K^{-1} m^{-2}]
        self.p["capSo4"]     =self.p["hSo4"] *self.p["rhoCpSo"]                              # Heat capacity of soil layer 4 [J K^{-1} m^{-2}]
        self.p["capSo5"]     =self.p["hSo5"] *self.p["rhoCpSo"]                              # Heat capacity of soil layer 5 [J K^{-1} m^{-2}]
        self.p["capThScr"]   =self.p["hThScr"] *self.p["rhoThScr"] *self.p["cPThScr"]        # Heat capacity of thermal screen [J K^{-1} m^{-2}]
        self.p["capTop"]     = (self.gl["p"]["hGh"] -self.p["hAir"]) *self.p["rhoAir"] *self.p["cPAir"]  # Heat capacity of air in top compartments [J K^{-1} m^{-2}]
        self.p["capBlScr"]   =self.p["hBlScr"] *self.p["rhoBlScr"] *self.p["cPBlScr"]        # Heat capacity of blackout screen [J K^{-1} m^{-2}]

    def set_co2_capacity_params(self):
        """Set CO2 capacity related parameters."""
        self.p["capCo2Air"]  =self.p["hAir"]                                # Capacity for CO2 in air [m]
        self.p["capCo2Top"]  =self.p["hGh"] -self.p["hAir"]                 # Capacity for CO2 in top [m]

    def set_view_factor_params(self):
        """Set view factor related parameters."""
        self.p["fCanFlr"] = 1 - 0.49 * np.pi *self.p["lPipe"] *self.p["phiPipeE"]
        # View factor from canopy to floor, Table 3 [1]

    def set_canopy_photosynthesis_and_growth_params(self):
        """Set canopy photosynthesis and growth related parameters in the model."""
        self.p["globJtoUmol"]      = 2.3       # Conversion factor from global radiation to PAR [umol{photons} J^{-1}]
        self.p["j25LeafMax"]       = 210       # Maximal rate of electron transport at 25°C of the leaf [umol{e-} m^{-2}{leaf} s^{-1}]
        self.p["cGamma"]           = 1.7       # Effect of canopy temperature on CO2 compensation point [umol{co2} mol^{-1}{air} K^{-1}]
        self.p["etaCo2AirStom"]    = 0.67      # Conversion from greenhouse air CO2 concentration and stomatal CO2 concentration [umol{co2} mol^{-1}{air}]
        self.p["eJ"]               = 37e3      # Activation energy for Jpot calculation [J mol^{-1}]
        self.p["t25k"]             = 298.15    # Reference temperature for Jpot calculation [K]
        self.p["S"]                = 710       # Entropy term for Jpot calculation [J mol^{-1} K^{-1}]
        self.p["H"]                = 22e4      # Deactivation energy for Jpot calculation [J mol^{-1}]
        self.p["theta"]            = 0.7       # Degree of curvature of the electron transport rate [-]
        self.p["alpha"]            = 0.385     # Conversion factor from photons to electrons including efficiency term [umol{e-} umol^{-1}{photons}]
        self.p["mCh2o"]            = 30e-3     # Molar mass of CH2O [mg umol^{-1}]
        self.p["mCo2"]             = 44e-3     # Molar mass of CO2 [mg umol^{-1}]
        self.p["parJtoUmolSun"]    = 4.6       # Conversion factor of sun's PAR from J to [umol{photons} J^{-1}]
        self.p["laiMax"]           = 3         # Leaf area index [m^{2}{leaf} m^{-2}{floor}]
        self.p["sla"]              = 2.66e-5   # Specific leaf area [m^{2}{leaf} mg^{-1}{leaf}]
        self.p["rgr"]              = 3e-6      # Relative growth rate [kg{dw grown} kg^{-1}{existing dw} s^{-1}]
        self.p["cLeafMax"]         =self.p["laiMax"] /self.p["sla"]  # Maximum leaf size [mg{leaf} m^{-2}]
        self.p["cFruitMax"]        = 300e3     # Maximum fruit size [mg{fruit} m^{-2}]
        self.p["cFruitG"]          = 0.27      # Fruit growth respiration coefficient [-]
        self.p["cLeafG"]           = 0.28      # Leaf growth respiration coefficient [-]
        self.p["cStemG"]           = 0.3       # Stem growth respiration coefficient [-]
        self.p["cRgr"]             = 2.85e6    # Regression coefficient in maintenance respiration function [s^{-1}]
        self.p["q10m"]             = 2         # Q10 value of temperature effect on maintenance respiration [-]
        self.p["cFruitM"]          = 1.16e-7   # Fruit maintenance respiration coefficient [mg mg^{-1} s^{-1}]
        self.p["cLeafM"]           = 3.47e-7   # Leaf maintenance respiration coefficient [mg mg^{-1} s^{-1}]
        self.p["cStemM"]           = 1.47e-7   # Stem maintenance respiration coefficient [mg mg^{-1} s^{-1}]
        self.p["rgFruit"]          = 0.328     # Potential fruit growth coefficient [mg m^{-2} s^{-1}]
        self.p["rgLeaf"]           = 0.095     # Potential leaf growth coefficient [mg m^{-2} s^{-1}]
        self.p["rgStem"]           = 0.074     # Potential stem growth coefficient [mg m^{-2} s^{-1}]
        
    def set_carbohydrates_buffer_params(self):
        """Set carbohydrates buffer related parameters."""
        self.p["cBufMax"]    = 20e3     # Maximum capacity of carbohydrate buffer [mg m^{-2}]
        self.p["cBufMin"]    = 1e3      # Minimum capacity of carbohydrate buffer [mg m^{-2}]
        self.p["tCan24Max"]  = 24.5     # Inhibition of carbohydrate flow because of high temperatures [°C]
        self.p["tCan24Min"]  = 15       # Inhibition of carbohydrate flow because of low temperatures [°C]
        self.p["tCanMax"]    = 34       # Inhibition of carbohydrate flow because of high instantaneous temperatures [°C]
        self.p["tCanMin"]    = 10       # Inhibition of carbohydrate flow because of low instantaneous temperatures [°C]

    def set_crop_development_params(self):
        """Set crop development related parameters."""
        self.p["tEndSum"]    = 1035     # Temperature sum where crop is fully generative [°C day]

    def set_control_params(self):
        """Set control related parameters."""
        self.p["rhMax"]               = 90     # Upper bound on relative humidity [%]
        self.p["dayThresh"]           = 20     # Threshold to consider switch from night to day [W m^{-2}]
        self.p["tSpDay"]              = 19.5   # Heat is on below this point in day [°C]
        self.p["tSpNight"]            = 16.5   # Heat is on below this point in night [°C]
        self.p["tHeatBand"]           = -1     # P-band for heating [°C]
        self.p["tVentOff"]            = 1      # Distance from heating setpoint where ventilation stops (even if humidity is too high) [°C]
        self.p["tScreenOn"]           = 2      # Distance from screen setpoint where screen is on (even if humidity is too high) [°C]
        self.p["thScrSpDay"]          = 5      # Screen is closed at day when outdoor is below this temperature [°C]
        self.p["thScrSpNight"]        = 10     # Screen is closed at night when outdoor is below this temperature [°C]
        self.p["thScrPband"]          = -1     # P-band for thermal screen [°C]
        self.p["co2SpDay"]            = 800    # CO2 is supplied if CO2 is below this point during day [ppm]
        self.p["co2Band"]             = -100   # P-band for CO2 supply [ppm]
        self.p["heatDeadZone"]        = 5      # Zone between heating setpoint and ventilation setpoint [°C]
        self.p["ventHeatPband"]       = 4      # P-band for ventilation due to excess heat [°C]
        self.p["ventColdPband"]       = -1     # P-band for ventilation due to low indoor temperature [°C]
        self.p["ventRhPband"]         = 5      # P-band for ventilation due to relative humidity [%]
        self.p["thScrRh"]             = -2     # Relative humidity where thermal screen is forced to open, with respect to rhMax [%]
        self.p["thScrRhPband"]        = 2      # P-band for thermal screen opening due to excess relative humidity [%]
        self.p["thScrDeadZone"]       = 4      # Zone between heating setpoint and point where screen opens
        self.p["lampsOn"]             = 0      # Time of day to switch on lamps [hours since midnight]
        self.p["lampsOff"]            = 0      # Time of day to switch off lamps [hours since midnight]
        self.p["dayLampStart"]        = -1     # Day of year when lamps start [day of year]
        self.p["dayLampStop"]         = 400    # Day of year when lamps stop [day of year]
        self.p["lampsOffSun"]         = 400    # Lamps are switched off if global radiation is above this value [W m^{-2}]
        self.p["lampRadSumLimit"]     = 10     # Predicted daily radiation sum from the sun where lamps are not used that day [MJ m^{-2} day^{-1}]
        self.p["lampExtraHeat"]       = 2      # Control for lamps due to too much heat - switched off if indoor temperature is above setpoint + heatDeadZone + lampExtraHeat [°C]
        self.p["blScrExtraRh"]        = 100    # Control for blackout screen due to humidity - screens open if relative humidity exceeds rhMax + blScrExtraRh [%]
        self.p["useBlScr"]            = 0      # Determines whether a blackout screen is used (1 if used, 0 otherwise) [-]
        self.p["mechCoolPband"]       = 1      # P-band for mechanical cooling [°C]
        self.p["mechDehumidPband"]    = 2      # P-band for mechanical dehumidification [%]
        self.p["heatBufPband"]        = -1     # P-band for heating from the buffer [°C]
        self.p["mechCoolDeadZone"]    = 2      # Zone between heating setpoint and mechanical cooling setpoint [°C]

    def set_grow_pipe_params(self):
        """Set grow pipe related parameters."""
        self.p["epsGroPipe"]   = 0      # Emissivity of grow pipes [-]
        self.p["lGroPipe"]     = 1.655  # Length of grow pipes per gh floor area [m m^{-2}]
        self.p["phiGroPipeE"]  = 35e-3  # External diameter of grow pipes [m]
        self.p["phiGroPipeI"]  = 35e-3 - 1.2e-3  # Internal diameter of grow pipes [m]
        self.p["aGroPipe"]     = np.pi *self.p["lGroPipe"] *self.p["phiGroPipeE"]  # Surface area of pipes for floor area [m^{2}{pipe} m^{-2}{floor}]
        self.p["pBoilGro"]     = 0      # Capacity of the grow pipe heating system [W]
        self.p["capGroPipe"]   = 0.25 * np.pi *self.p["lGroPipe"] * (
            (self.gl["p"]["phiGroPipeE"]**2 -self.p["phiGroPipeI"]**2) *self.p["rhoSteel"] *self.p["cPSteel"] +
            self.p["phiGroPipeI"]**2 *self.p["rhoWater"] *self.p["cPWater"]
        )  # Heat capacity of grow pipes [J K^{-1} m^{-2}]

    def set_lamp_params(self):
        """Set lamp related parameters."""
        self.p["thetaLampMax"]    = 0     # Maximum intensity of lamps [W m^{-2}]
        self.p["heatCorrection"]  = 0     # Correction for temperature setpoint when lamps are on [°C]
        self.p["etaLampPar"]      = 0     # Fraction of lamp input converted to PAR [-]
        self.p["etaLampNir"]      = 0     # Fraction of lamp input converted to NIR [-]
        self.p["tauLampPar"]      = 1     # Transmissivity of lamp layer to PAR [-]
        self.p["rhoLampPar"]      = 0     # Reflectivity of lamp layer to PAR [-]
        self.p["tauLampNir"]      = 1     # Transmissivity of lamp layer to NIR [-]
        self.p["rhoLampNir"]      = 0     # Reflectivity of lamp layer to NIR [-]
        self.p["tauLampFir"]      = 1     # Transmissivity of lamp layer to FIR [-]
        self.p["aLamp"]           = 0     # Lamp area [m^{2}{lamp} m^{-2}{floor}]
        self.p["epsLampTop"]      = 0     # Emissivity of top side of lamp [-]
        self.p["epsLampBottom"]   = 0     # Emissivity of bottom side of lamp [-]
        self.p["capLamp"]         = 350   # Heat capacity of lamp [J K^{-1} m^{-2}]
        self.p["cHecLampAir"]     = 0     # Heat exchange coefficient of lamp [W m^{-2} K^{-1}]
        self.p["etaLampCool"]     = 0     # Fraction of lamp input removed by cooling [-]
        self.p["zetaLampPar"]     = 0     # J to umol conversion of PAR output of lamp [J{PAR} umol{PAR}^{-1}]

    def set_interlight_params(self):
        """Set interlight related parameters."""
        self.p["vIntLampPos"] = 0.5     # Vertical position of the interlights within the canopy [0-1, 0 is above canopy and 1 is below] [-]
        self.p["fIntLampDown"] = 0.5    # Fraction of interlight light output (PAR and NIR) that goes downwards [-]
        self.p["capIntLamp"] = 10       # Heat capacity of lamp [J K^{-1} m^{-2}]
        self.p["etaIntLampPar"] = 0     # Fraction of lamp input converted to PAR [-]
        self.p["etaIntLampNir"] = 0     # Fraction of lamp input converted to NIR [-]
        self.p["aIntLamp"] = 0          # Interlight lamp area [m^{2}{lamp} m^{-2}{floor}]
        self.p["epsIntLamp"] = 0        # Emissivity of interlight [-]
        self.p["thetaIntLampMax"] = 0   # Maximum intensity of lamps [W m^{-2}]
        self.p["zetaIntLampPar"] = 0    # Conversion from Joules to umol photons within the PAR output of the interlight [J{PAR} umol{PAR}^{-1}]
        self.p["cHecIntLampAir"] = 0    # Heat exchange coefficient of interlights [W m^{-2} K^{-1}]
        self.p["tauIntLampFir"] = 1     # Transmissivity of FIR through the interlights [-]
        self.p["k1IntPar"] = 1.4        # PAR extinction coefficient of the canopy for light coming from the interlights [-]
        self.p["k2IntPar"] = 1.4        # PAR extinction coefficient of the canopy for light coming from the interlights through the floor [-]
        self.p["kIntNir"] = 0.54        # NIR extinction coefficient of the canopy for light coming from the interlights [-]
        self.p["kIntFir"] = 1.88        # FIR extinction coefficient of the canopy for light coming from the interlights [-]

    def set_other_params(self):
        """Set other miscellaneous parameters in the model."""
        self.p["etaMgPpm"] = 0.554      # CO2 conversion factor from mg m^{-3} to ppm [ppm mg^{-1} m^{3}]
        self.p["etaRoofThr"] = 0.9      # Ratio between roof vent area and total vent area where no chimney effects is assumed [-]
        self.p["rCanSp"] = 5            # Radiation value above the canopy when night becomes day [W m^{-2}]
        self.p["cLeakTop"] = 0.5        # Fraction of leakage ventilation going from the top [-]
        self.p["minWind"] = 0.25        # Wind speed where the effect of wind on leakage begins [m s^{-1}]
        
    def set_gl_params(self):
        """Initialize all parameters in the model."""
        self.set_physical_constants()        # Set physical constants, e.g., Stefan-Boltzmann constant, gravity acceleration
        self.set_thermodynamic_params()      # Set thermodynamic parameters, e.g., latent heat of evaporation, specific heat capacities
        self.set_radiation_params()          # Set radiation-related parameters, e.g., ratio of NIR and PAR in global radiation
        self.set_material_properties()       # Set material properties, e.g., air density, steel density
        self.set_canopy_params()             # Set canopy-related parameters, e.g., convective heat exchange coefficient from leaf to air
        self.set_stomatal_resistance_params()# Set stomatal resistance parameters, e.g., coefficients for radiation effect
        self.set_soil_params()               # Set soil parameters, e.g., thickness of different soil layers
        self.set_construction_properties()   # Set greenhouse construction properties, e.g., floor area, cover surface area
        self.set_ventilation_properties()    # Set ventilation properties, e.g., maximum roof ventilation area, vertical dimension of vent opening
        self.set_roof_properties()           # Set roof properties, e.g., FIR emission coefficient, density of roof layer
        self.set_whitewash_properties()      # Set whitewash properties, e.g., FIR emission coefficient, density
        self.set_shadow_screen_properties()  # Set shadow screen properties, e.g., NIR and PAR reflection coefficients
        self.set_thermal_screen_properties() # Set thermal screen properties, e.g., FIR emission coefficient, density
        self.set_blackout_screen_properties()# Set blackout screen properties, e.g., FIR emission coefficient, density
        self.set_floor_properties()          # Set floor properties, e.g., FIR emission coefficient, density
        self.set_soil_properties()           # Set soil properties, e.g., volumetric heat capacity, thermal conductivity
        self.set_heating_system_properties() # Set heating system properties, e.g., FIR emission coefficient of heating pipes
        self.set_active_climate_control_properties() # Set active climate control properties, e.g., capacity of external CO2 source
        self.set_heating_pipe_params()       # Set heating pipe related parameters, e.g., heat capacity of pipes
        self.set_air_density_params()        # Set air density related parameters, e.g., air density at given elevation
        self.set_heat_capacity_params()      # Set heat capacity related parameters, e.g., heat capacity of air in main compartment
        self.set_co2_capacity_params()       # Set CO2 capacity related parameters, e.g., CO2 capacity in main and top compartments
        self.set_view_factor_params()        # Set view factor related parameters, e.g., view factor from canopy to floor
        self.set_canopy_photosynthesis_and_growth_params() # Set canopy photosynthesis and growth related parameters, e.g., max electron transport rate
        self.set_carbohydrates_buffer_params() # Set carbohydrates buffer related parameters, e.g., maximum buffer capacity
        self.set_crop_development_params()   # Set crop development related parameters, e.g., temperature sum for fully generative crop
        self.set_control_params()            # Set control related parameters, e.g., relative humidity upper bound, day/night temperature setpoints
        self.set_grow_pipe_params()          # Set grow pipe related parameters, e.g., emissivity of grow pipes
        self.set_lamp_params()               # Set lamp related parameters, e.g., maximum intensity of lamps
        self.set_interlight_params()         # Set interlight related parameters, e.g., vertical position of interlights within canopy
        self.set_other_params()              # Set other miscellaneous parameters, e.g., CO2 conversion factor
        return self.gl                       # Return the gl dictionary containing all set parameters


def set_gl_params(gl):
    gl_params = GreenLightParams(gl)
    return gl_params.set_gl_params()
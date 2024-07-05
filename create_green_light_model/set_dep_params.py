# File path: GreenLightPlus/create_green_light_model/set_dep_params.py
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

class DependentParameters:
    def __init__(self, gl):
        self.gl = gl

    def set_heating_pipe_capacity(self):
        """Set heat capacity of heating pipes [J K^{-1} m^{-2}] (Equation 21 [1])"""
        self.gl["p"]["capPipe"] = 0.25 * np.pi * self.gl["p"]["lPipe"] * (
            (self.gl["p"]["phiPipeE"]**2 - self.gl["p"]["phiPipeI"]**2) * self.gl["p"]["rhoSteel"] * self.gl["p"]["cPSteel"] +
            self.gl["p"]["phiPipeI"]**2 * self.gl["p"]["rhoWater"] * self.gl["p"]["cPWater"]
        )

    def set_air_density(self):
        """Set density of the air [kg m^{-3}] (Equation 23 [1])"""
        self.gl["p"]["rhoAir"] = self.gl["p"]["rhoAir0"] * np.exp(self.gl["p"]["g"] * self.gl["p"]["mAir"] * self.gl["p"]["hElevation"] / (293.15 * self.gl["p"]["R"]))

    def set_heat_capacities(self):
        """Set heat capacity of greenhouse objects [J K^{-1} m^{-2}] (Equation 22 [1])"""
        self.gl["p"]["capAir"] = self.gl["p"]["hAir"] * self.gl["p"]["rhoAir"] * self.gl["p"]["cPAir"]  # air in main compartment
        self.gl["p"]["capFlr"] = self.gl["p"]["hFlr"] * self.gl["p"]["rhoFlr"] * self.gl["p"]["cPFlr"]  # floor
        self.gl["p"]["capSo1"] = self.gl["p"]["hSo1"] * self.gl["p"]["rhoCpSo"]  # soil layer 1
        self.gl["p"]["capSo2"] = self.gl["p"]["hSo2"] * self.gl["p"]["rhoCpSo"]  # soil layer 2
        self.gl["p"]["capSo3"] = self.gl["p"]["hSo3"] * self.gl["p"]["rhoCpSo"]  # soil layer 3
        self.gl["p"]["capSo4"] = self.gl["p"]["hSo4"] * self.gl["p"]["rhoCpSo"]  # soil layer 4
        self.gl["p"]["capSo5"] = self.gl["p"]["hSo5"] * self.gl["p"]["rhoCpSo"]  # soil layer 5
        self.gl["p"]["capThScr"] = self.gl["p"]["hThScr"] * self.gl["p"]["rhoThScr"] * self.gl["p"]["cPThScr"]  # thermal screen
        self.gl["p"]["capTop"] = (self.gl["p"]["hGh"] - self.gl["p"]["hAir"]) * self.gl["p"]["rhoAir"] * self.gl["p"]["cPAir"]  # air in top compartments
        self.gl["p"]["capBlScr"] = self.gl["p"]["hBlScr"] * self.gl["p"]["rhoBlScr"] * self.gl["p"]["cPBlScr"]  # blackout screen

    def set_co2_capacities(self):
        """Set capacity for CO2 [m]"""
        self.gl["p"]["capCo2Air"] = self.gl["p"]["hAir"]
        self.gl["p"]["capCo2Top"] = self.gl["p"]["hGh"] - self.gl["p"]["hAir"]

    def set_pipe_surface_area(self):
        """Set surface of pipes for floor area [-] (Table 3 [1])"""
        self.gl["p"]["aPipe"] = np.pi * self.gl["p"]["lPipe"] * self.gl["p"]["phiPipeE"]

    def set_canopy_floor_view_factor(self):
        """Set view factor from canopy to floor (Table 3 [1])"""
        self.gl["p"]["fCanFlr"] = 1 - 0.49 * np.pi * self.gl["p"]["lPipe"] * self.gl["p"]["phiPipeE"]

    def set_air_pressure(self):
        """Set absolute air pressure at given elevation [Pa]"""
        self.gl["p"]["pressure"] = 101325 * (1 - 2.5577e-5 * self.gl["p"]["hElevation"])**5.25588
        
    def set_maximum_leaf_size(self):
        """Set maximum leaf size [mg{leaf} m^{-2}]"""
        self.gl["p"]["cLeafMax"] = self.gl["p"]["laiMax"] / self.gl["p"]["sla"]

    def set_grow_pipe_surface_area(self):
        """Set surface area of grow pipes for floor area [m^{2}{pipe} m^{-2}{floor}]"""
        self.gl["p"]["aGroPipe"] = np.pi * self.gl["p"]["lGroPipe"] * self.gl["p"]["phiGroPipeE"]

    def set_grow_pipe_capacity(self):
        """Set heat capacity of grow pipes [J K^{-1} m^{-2}] (Equation 21 [1])"""
        self.gl["p"]["capGroPipe"] = 0.25 * np.pi * self.gl["p"]["lGroPipe"] * (
            (self.gl["p"]["phiGroPipeE"]**2 - self.gl["p"]["phiGroPipeI"]**2) * self.gl["p"]["rhoSteel"] * self.gl["p"]["cPSteel"] +
            self.gl["p"]["phiGroPipeI"]**2 * self.gl["p"]["rhoWater"] * self.gl["p"]["cPWater"]
        )

    def set_dep_params(self):
        """Set all dependent parameters"""
        self.set_heating_pipe_capacity()
        self.set_air_density()
        self.set_heat_capacities()
        self.set_co2_capacities()
        self.set_pipe_surface_area()
        self.set_canopy_floor_view_factor()
        self.set_air_pressure()
        self.set_maximum_leaf_size()
        self.set_grow_pipe_surface_area()
        self.set_grow_pipe_capacity()
        
        return self.gl


def set_dep_params(gl):
    """Set any model-dependent parameters."""
    dependent_params = DependentParameters(gl)
    return dependent_params.set_dep_params()



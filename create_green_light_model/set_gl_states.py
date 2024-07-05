# File path: GreenLightPlus/create_green_light_model/set_gl_states.py
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

import numpy as np  # Import NumPy for numerical operations

class GreenLightModelStates:
    """
    A class to set and manage states for the GreenLight greenhouse model.

    This class initializes and sets various environmental and crop-related states
    used in the GreenLight model simulations.

    Attributes:
        gl (dict): A dictionary containing the GreenLight model structure and data.
    """

    def __init__(self, gl):
        """
        Initialize the GreenLightModelStates instance.

        Args:
            gl (dict): A dictionary representing the GreenLight model structure.
        """
        self.gl = gl  # Store the GreenLight model dictionary

    def set_environmental_states(self):
        """
        Set the environmental states of the greenhouse model.

        This method initializes various environmental parameters such as CO2 concentrations,
        temperatures, vapor pressures, and other related states.

        Returns:
            None
        """
        # CO2 concentration in main compartment [mg m^{-3}]
        self.gl["x"]["co2Air"] = np.array([])

        # CO2 concentration in top compartment [mg m^{-3}]
        self.gl["x"]["co2Top"] = np.array([])

        # Air temperature in main compartment [°C]
        self.gl["x"]["tAir"] = np.array([])

        # Air temperature in top compartment [°C]
        self.gl["x"]["tTop"] = np.array([])

        # Canopy temperature [°C]
        self.gl["x"]["tCan"] = np.array([])

        # Indoor cover temperature [°C]
        self.gl["x"]["tCovIn"] = np.array([])

        # Thermal screen temperature [°C]
        self.gl["x"]["tThScr"] = np.array([])

        # Floor temperature [°C]
        self.gl["x"]["tFlr"] = np.array([])

        # Pipe temperature [°C]
        self.gl["x"]["tPipe"] = np.array([])

        # Outdoor cover temperature [°C]
        self.gl["x"]["tCovE"] = np.array([])

        # Soil layers temperature [°C]
        self.gl["x"]["tSo1"] = np.array([])
        self.gl["x"]["tSo2"] = np.array([])
        self.gl["x"]["tSo3"] = np.array([])
        self.gl["x"]["tSo4"] = np.array([])
        self.gl["x"]["tSo5"] = np.array([])

        # Vapor pressure in main compartment [Pa]
        self.gl["x"]["vpAir"] = np.array([])

        # Vapor pressure in top compartment [Pa]
        self.gl["x"]["vpTop"] = np.array([])

        # Average canopy temperature in last 24 hours [°C]
        self.gl["x"]["tCan24"] = np.array([])

        # Time since beginning simulation [s]
        self.gl["x"]["time"] = np.array([])

        # Lamp temperature [°C]
        self.gl["x"]["tLamp"] = np.array([])

        # Growpipes temperature [°C]
        self.gl["x"]["tGroPipe"] = np.array([])

        # Interlights temperature [°C]
        self.gl["x"]["tIntLamp"] = np.array([])

        # Blackout screen temperature [°C]
        self.gl["x"]["tBlScr"] = np.array([])

    def set_crop_states(self):
        """
        Set the crop model states of the greenhouse model.

        This method initializes various crop-related parameters such as carbohydrate
        levels in different parts of the plant and crop development stage.

        Returns:
            None
        """
        # Carbohydrates in buffer [mg{CH2O} m^{-2}]
        self.gl["x"]["cBuf"] = np.array([])

        # Carbohydrates in leaves [mg{CH2O} m^{-2}]
        self.gl["x"]["cLeaf"] = np.array([])

        # Carbohydrates in stem [mg{CH2O} m^{-2}]
        self.gl["x"]["cStem"] = np.array([])

        # Carbohydrates in fruit [mg{CH2O} m^{-2}]
        self.gl["x"]["cFruit"] = np.array([])

        # Crop development stage [°C day]
        self.gl["x"]["tCanSum"] = np.array([])

    def set_gl_states(self):
        """
        Set states for the GreenLight greenhouse model.

        This method calls both set_environmental_states and set_crop_states
        to initialize all necessary states for the GreenLight model.

        See setGlOdes for equations and references.

        Returns:
            dict: The updated GreenLight model dictionary with initialized states.
        """
        self.set_environmental_states()  # Set environmental states
        self.set_crop_states()  # Set crop states
        return self.gl  # Return the updated GreenLight model dictionary

def set_gl_states(gl):
    """
    A wrapper function to set states for a GreenLight model instance.

    This function creates an instance of GreenLightModelStates and uses it
    to initialize and set all necessary states for the GreenLight model.

    Args:
        gl (dict): A dictionary representing the GreenLight model structure.

    Returns:
        dict: The updated GreenLight model dictionary with initialized states.
    """
    gl_states = GreenLightModelStates(gl)  # Create a GreenLightModelStates instance
    return gl_states.set_gl_states()  # Set states and return updated model
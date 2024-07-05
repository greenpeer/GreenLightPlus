# File path: GreenLightPlus/create_green_light_model/set_params4ha_world_comparison.py
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

def set_params4ha_world_comparison(gl):
    """
    Set parameters for GreenLight model of a modern 4 ha greenhouse with settings used to compare greenhouses around the world.
    Used to generate the data in:
    Katzin, D., Marcelis, L. F. M., & van Mourik, S. (2021). 
    Energy savings in greenhouses by transition from high-pressure sodium 
    to LED lighting. Applied Energy, 281, 116019. 
    https://doi.org/10.1016/j.apenergy.2020.116019

    References:
        [1] Vanthoor, B., Stanghellini, C., van Henten, E. J., & de Visser, P. H. B. (2011). 
            A methodology for model-based greenhouse design: Part 1, a greenhouse 
            climate model for a broad range of designs and climates. 
            Biosystems Engineering, 110(4), 363-377. https://doi.org/10.1016/j.biosystemseng.2011.06.001
            (In particular, settings for Dutch greenhouse in electronic appendix)
        [2] Raaphorst, M., Benninga, J., & Eveleens, B. A. (2019). 
            Quantitative information on Dutch greenhouse horticulture 2019. Bleiswijk.
        [3] De Zwart, H. F. (1996). Analyzing energy-saving options in greenhouse 
            cultivation using a simulation model. Landbouwuniversiteit Wageningen.

    Parameters:
        gl (dict): A nested dictionary representing the GreenLight model.

    The function sets the parameters for a GreenLight model instance of a modern 4 ha greenhouse with settings used to compare
    greenhouses around the world, as described in the references above. The function modifies the input dictionary
    in place and returns the modified dictionary.
    """
    
    gl["p"]["psi"] = 22                      # Mean greenhouse cover slope [°]
    gl["p"]["aFlr"] = 4e4                    # Floor area of greenhouse [m^2]
    gl["p"]["aCov"] = 4.84e4                 # Surface of the cover including side walls [m^2]
    gl["p"]["hAir"] = 6.3                    # Height of the main compartment [m]
                                             # The ridge height is 6.5, screen is 20 cm below it
    gl["p"]["hGh"] = 6.905                   # Average height of greenhouse [m]
                                             # Each triangle in the greenhouse roof has width 4m, angle 22°, so
                                             # height of 0.81m. The ridge is 6.5 m high
    gl["p"]["aRoof"] = 0.1169 * 4e4          # Maximum roof ventilation area [-]
                                             # A greenhouse roof segment is composed of 6 panels of glass
                                             # measuring 1.67m x 2.16m. This segment totals (1.67x3)x(2.16x2) =
                                             # 5x4.32 = 21.6 m^2. This segment lies above a floor segment of
                                             # 5x4 = 20 m^2. 
                                             # In this segment, one panel has a window sized 1.67m x 1.4m. 
                                             # This makes the relative roof area 1.4x1.67/20 = 0.1169
    gl["p"]["hVent"] = 1.3                   # Vertical dimension of single ventilation opening [m]
                                             # A length of a roof segment is 1.4m, and the maximum opening angle
                                             # is 60°
    gl["p"]["cDgh"] = 0.75                   # Ventilation discharge coefficient [-] [1]
    gl["p"]["lPipe"] = 1.25                  # Length of heating pipes per gh floor area [m m^-2]
                                             # In an 8m trellis there are 5 paths of 1.6m with two lines of
                                             # pipes. In a greenhouse segment of 1.6m x 200m, there is a length
                                             # of 200m x 2 of pipes. 2/1.6 = 1.25
    gl["p"]["phiExtCo2"] = 7.2e4 * 4e4 / 1.4e4  # Capacity of external CO2 source [mg s^-1]
                                             # This is 185 kg/ha/hour, based on [1] and adjusted to 4 ha
    gl["p"]["co2SpDay"] = 1000               # CO2 is supplied if CO2 is below this point during day [ppm] [2]
    gl["p"]["tSpNight"] = 18.5               # Heat is on below this point in night [°C]
    gl["p"]["tSpDay"] = 19.5                 # Heat is on below this point in day [°C]
                                             # [2] says 17.5 night, 18.5 day, the values here are used to get
                                             # approximately that value in practice
    gl["p"]["rhMax"] = 87                    # Upper bound on relative humidity [%] [2]
    gl["p"]["ventHeatPband"] = 4             # P-band for ventilation due to excess heat [°C]
    gl["p"]["ventRhPband"] = 50              # P-band for ventilation due to relative humidity [%] [3]
    gl["p"]["thScrRhPband"] = 10             # P-band for thermal screen opening due to excess relative humidity [%]
    gl["p"]["lampsOn"] = 0                   # Time of day (in morning) to switch on lamps [hours since midnight]
    gl["p"]["lampsOff"] = 18                 # Time of day (in evening) to switch off lamps [hours since midnight]
    gl["p"]["lampsOffSun"] = 400             # Lamps are switched off if global radiation is above this value [W m^-2]
    gl["p"]["lampRadSumLimit"] = 10          # Predicted daily radiation sum from the sun where lamps are not used that day [MJ m^-2 day^-1]
    gl["p"]["pBoil"] = 300 * gl["p"]["aFlr"] # Capacity of the heating system [W]

    return gl
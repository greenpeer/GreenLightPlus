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

def set_params4ha_world_comparison(gl):
    """
    Set parameters for GreenLight model of a modern 4 ha greenhouse with settings used to compare greenhouses around the world.
    Used to generate the data in Katzin et al. (2021) - Energy savings in greenhouses by transition from high-pressure sodium to LED lighting.

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
        gl (DynamicModel): A DynamicModel object representing the GreenLight model.

    The function sets the parameters for a GreenLight model instance of a modern 4 ha greenhouse with settings used to compare
    greenhouses around the world, as described in the references above. The function modifies the input `DynamicModel`
    object in place and does not return anything.
    """
    
    gl["p"]["psi"] = 22
    gl["p"]["aFlr"] = 4e4
    gl["p"]["aCov"] = 4.84e4
    gl["p"]["hAir"] = 6.3
    gl["p"]["hGh"] = 6.905
    gl["p"]["aRoof"] = 0.1169 * 4e4
    gl["p"]["hVent"] = 1.3
    gl["p"]["cDgh"] = 0.75
    gl["p"]["lPipe"] = 1.25
    gl["p"]["phiExtCo2"] = 7.2e4 * 4e4 / 1.4e4
    gl["p"]["co2SpDay"] = 1000
    gl["p"]["tSpNight"] = 18.5
    gl["p"]["tSpDay"] = 19.5
    gl["p"]["rhMax"] = 87
    gl["p"]["ventHeatPband"] = 4
    gl["p"]["ventRhPband"] = 50
    gl["p"]["thScrRhPband"] = 10
    gl["p"]["lampsOn"] = 0
    gl["p"]["lampsOff"] = 18
    gl["p"]["lampsOffSun"] = 400
    gl["p"]["lampRadSumLimit"] = 10
    gl["p"]["pBoil"] = 300 * gl["p"]["aFlr"]

    return gl



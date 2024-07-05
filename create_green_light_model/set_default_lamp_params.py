# File path: GreenLightPlus/create_green_light_model/set_default_lamp_params.py
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

def set_default_lamp_params(gl, lamp_type):
    """
    Set default settings for the lamp type in the GreenLight model.

    Inputs:
    gl: A GreenLight model nested dictionary.
    lamp_type: The lamp type to be used, either 'hps' or 'led' (other types will be ignored)

    Based on the following research papers:
    [1] Nelson, J. A., & Bugbee, B. (2014). Economic Analysis of Greenhouse 
        Lighting: Light Emitting Diodes vs. High Intensity Discharge Fixtures. 
        PLoS ONE, 9(6), e99010. https://doi.org/10.1371/journal.pone.0099010
    [2] Nelson, J. A., & Bugbee, B. (2015). Analysis of Environmental Effects 
        on Leaf Temperature under Sunlight, High Pressure Sodium and Light 
        Emitting Diodes. PLOS ONE, 10(10), e0138930. 
        https://doi.org/10.1371/journal.pone.0138930
    [3] De Zwart, H. F., Baeza, E., Van Breugel, B., Mohammadkhani, V., & 
        Janssen, H. (2017). De uitstralingmonitor.
    [4] Katzin, D., van Mourik, S., Kempkes, F., & 
        van Henten, E. J. (2020). GreenLight - An open source model for 
        greenhouses with supplemental lighting: Evaluation of heat requirements 
        under LED and HPS lamps. Biosystems Engineering, 194, 61-81. 
        https://doi.org/10.1016/j.biosystemseng.2020.03.010
    [5] Kusuma, P., Pattison, P. M., & Bugbee, B. (2020). From physics to 
        fixtures to food: current and potential LED efficacy. 
        Horticulture Research, 7(56). https://doi.org/10.1038/s41438-020-0283-7
    """

    if lamp_type.lower() == "hps":
        gl["p"]["thetaLampMax"] = 200 / 1.8    # Maximum intensity of lamps [W m^{-2}], Set to achieve a PPFD of 200 umol (PAR) m^{-2} s^{-1}
        gl["p"]["heatCorrection"] = 0          # Correction for temperature setpoint when lamps are on [°C]
        gl["p"]["etaLampPar"] = 1.8 / 4.9      # Fraction of lamp input converted to PAR [-], Set to give a PPE of 1.8 umol (PAR) J^{-1} [1, including comments online]
        gl["p"]["etaLampNir"] = 0.22           # Fraction of lamp input converted to NIR [-] [2]
        gl["p"]["tauLampPar"] = 0.98           # Transmissivity of lamp layer to PAR [-] [3]
        gl["p"]["rhoLampPar"] = 0              # Reflectivity of lamp layer to PAR [-] [3, pg. 26]
        gl["p"]["tauLampNir"] = 0.98           # Transmissivity of lamp layer to NIR [-] [3]
        gl["p"]["rhoLampNir"] = 0              # Reflectivity of lamp layer to NIR [-]
        gl["p"]["tauLampFir"] = 0.98           # Transmissivity of lamp layer to FIR [-]
        gl["p"]["aLamp"] = 0.02                # Lamp area [m^{2}{lamp} m^{-2}{floor}] [3, pg. 35]
        gl["p"]["epsLampTop"] = 0.1            # Emissivity of top side of lamp [-] [4]
        gl["p"]["epsLampBottom"] = 0.9         # Emissivity of bottom side of lamp [-] [4]
        gl["p"]["capLamp"] = 100               # Heat capacity of lamp [J K^{-1} m^{-2}] [4]
        gl["p"]["cHecLampAir"] = 0.09          # Heat exchange coefficient of lamp [W m^{-2} K^{-1}] [4]
        gl["p"]["etaLampCool"] = 0             # Fraction of lamp input removed by cooling [-] (No cooling)
        gl["p"]["zetaLampPar"] = 4.9           # J to umol conversion of PAR output of lamp [umol{PAR} J^{-1}] [2]
        gl["p"]["lampsOn"] = 0                 # Time of day when lamps go on [hour]
        gl["p"]["lampsOff"] = 18               # Time of day when lamps go off [hour]
    elif lamp_type.lower() == "led":
        gl["p"]["thetaLampMax"] = 200 / 3      # Maximum intensity of lamps [W m^{-2}], Set to achieve a PPFD of 200 umol (PAR) m^{-2} s^{-1}
        gl["p"]["heatCorrection"] = 0          # Correction for temperature setpoint when lamps are on [°C]
        gl["p"]["etaLampPar"] = 3 / 5.41       # Fraction of lamp input converted to PAR [-], Set to give a PPE of 3 umol (PAR) J^{-1} [5]
        gl["p"]["etaLampNir"] = 0.02           # Fraction of lamp input converted to NIR [-] [2]
        gl["p"]["tauLampPar"] = 0.98           # Transmissivity of lamp layer to PAR [-] [3]
        gl["p"]["rhoLampPar"] = 0              # Reflectivity of lamp layer to PAR [-] [3, pg. 26]
        gl["p"]["tauLampNir"] = 0.98           # Transmissivity of lamp layer to NIR [-] [3]
        gl["p"]["rhoLampNir"] = 0              # Reflectivity of lamp layer to NIR [-]
        gl["p"]["tauLampFir"] = 0.98           # Transmissivity of lamp layer to FIR [-]
        gl["p"]["aLamp"] = 0.02                # Lamp area [m^{2}{lamp} m^{-2}{floor}] [3, pg. 35]
        gl["p"]["epsLampTop"] = 0.88           # Emissivity of top side of lamp [-] [4]
        gl["p"]["epsLampBottom"] = 0.88        # Emissivity of bottom side of lamp [-] [4]
        gl["p"]["capLamp"] = 10                # Heat capacity of lamp [J K^{-1} m^{-2}] [4]
        gl["p"]["cHecLampAir"] = 2.3           # Heat exchange coefficient of lamp [W m^{-2} K^{-1}] [4]
        gl["p"]["etaLampCool"] = 0             # Fraction of lamp input removed by cooling [-]
        gl["p"]["zetaLampPar"] = 5.41          # J to umol conversion of PAR output of lamp [umol{PAR} J^{-1}], assuming 6% blue (450 nm) and 94% red (660 nm) [5]
        gl["p"]["lampsOn"] = 0                 # Time of day when lamps go on [hour]
        gl["p"]["lampsOff"] = 18               # Time of day when lamps go off [hour]

    return gl
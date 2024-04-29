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



def set_default_lamp_params(gl, lamp_type):
    """
    Set default settings for the lamp type in the GreenLight model.

    Inputs:
    gl: A GreenLight model nested dictionary.
    lampType: the lamp type to be used, either 'hps' or 'led' (other types will be ignored)
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
        gl["p"]["thetaLampMax"] = 200 / 1.8
        gl["p"]["heatCorrection"] = 0
        gl["p"]["etaLampPar"] = 1.8 / 4.9
        gl["p"]["etaLampNir"] = 0.22
        gl["p"]["tauLampPar"] = 0.98
        gl["p"]["rhoLampPar"] = 0
        gl["p"]["tauLampNir"] = 0.98
        gl["p"]["rhoLampNir"] = 0
        gl["p"]["tauLampFir"] = 0.98
        gl["p"]["aLamp"] = 0.02
        gl["p"]["epsLampTop"] = 0.1
        gl["p"]["epsLampBottom"] = 0.9
        gl["p"]["capLamp"] = 100
        gl["p"]["cHecLampAir"] = 0.09
        gl["p"]["etaLampCool"] = 0
        gl["p"]["zetaLampPar"] = 4.9
        gl["p"]["lampsOn"] = 0
        gl["p"]["lampsOff"] = 18
    elif lamp_type.lower() == "led":
        gl["p"]["thetaLampMax"] = 200 / 3
        gl["p"]["heatCorrection"] = 0
        gl["p"]["etaLampPar"] = 3 / 5.41
        gl["p"]["etaLampNir"] = 0.02
        gl["p"]["tauLampPar"] = 0.98
        gl["p"]["rhoLampPar"] = 0
        gl["p"]["tauLampNir"] = 0.98
        gl["p"]["rhoLampNir"] = 0
        gl["p"]["tauLampFir"] = 0.98
        gl["p"]["aLamp"] = 0.02
        gl["p"]["epsLampTop"] = 0.88
        gl["p"]["epsLampBottom"] = 0.88
        gl["p"]["capLamp"] = 10
        gl["p"]["cHecLampAir"] = 2.3
        gl["p"]["etaLampCool"] = 0
        gl["p"]["zetaLampPar"] = 5.41
        gl["p"]["lampsOn"] = 0
        gl["p"]["lampsOff"] = 18

    return gl

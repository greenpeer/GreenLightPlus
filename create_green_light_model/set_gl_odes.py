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


from ..service_functions.funcs import ifElse


def set_gl_odes(gl):
    a = gl["a"]
    p = gl["p"]
    x = gl["x"]
    d = gl["d"]

    dx = {}  # initialize the dictionary of ODEs

    # The following equations must be in the right order, because they depend on each other to be calculated

    # 1.Carbon concentration of greenhouse air [mg m^{-3} s^{-1}]
    # Equation 12 [1]
    dx["co2Air"] = (
        1
        / p["capCo2Air"]
        * (
            a["mcBlowAir"]
            + a["mcExtAir"]
            + a["mcPadAir"]
            - a["mcAirCan"]
            - a["mcAirTop"]
            - a["mcAirOut"]
        )
    )

    # 2. Carbon concentration of top compartment [mg m^{-3} s^{-1}]
    # Equation 13 [1]
    dx["co2Top"] = 1 / p["capCo2Top"] * (a["mcAirTop"] - a["mcTopOut"])

    # 3.Greenhouse air temperature [°C s^{-1}]
    # Equation 2 [1], Equation A1 [5], Equation 7.1 [6]
    dx["tAir"] = (
        1
        / p["capAir"]
        * (
            a["hCanAir"]
            + a["hPadAir"]
            - a["hAirMech"]
            + a["hPipeAir"]
            + a["hPasAir"]
            + a["hBlowAir"]
            + a["rGlobSunAir"]
            - a["hAirFlr"]
            - a["hAirThScr"]
            - a["hAirOut"]
            - a["hAirTop"]
            - a["hAirOutPad"]
            - a["lAirFog"]
            - a["hAirBlScr"]
            + a["hLampAir"]
            + a["rLampAir"]
            + a["hGroPipeAir"]
            + a["hIntLampAir"]
            + a["rIntLampAir"]
        )
    )

    # 4.Air above screen temperature [°C s^{-1}]
    # Equation 6 [1]
    dx["tTop"] = (
        1
        / p["capTop"]
        * (
            a["hThScrTop"]
            + a["hAirTop"]
            - a["hTopCovIn"]
            - a["hTopOut"]
            + a["hBlScrTop"]
        )
    )

    # 5.Canopy temperature [°C s^{-1}]
    # Equation 1 [1], Equation A1 [5], Equation 7.1 [6]
    dx["tCan"] = (1 / a["capCan"]) * (
        a["rParSunCan"]
        + a["rNirSunCan"]
        + a["rPipeCan"]
        - a["hCanAir"]
        - a["lCanAir"]
        - a["rCanCovIn"]
        - a["rCanFlr"]
        - a["rCanSky"]
        - a["rCanThScr"]
        - a["rCanBlScr"]
        + a["rParLampCan"]
        + a["rNirLampCan"]
        + a["rFirLampCan"]
        + a["rGroPipeCan"]
        + a["rParIntLampCan"]
        + a["rNirIntLampCan"]
        + a["rFirIntLampCan"]
    )

    # 6.Internal cover temperature [°C s^{-1}]
    # Equation 7 [1], Equation A1 [5], Equation 7.1 [6]
    dx["tCovIn"] = (1 / a["capCovIn"]) * (
        a["hTopCovIn"]
        + a["lTopCovIn"]
        + a["rCanCovIn"]
        + a["rFlrCovIn"]
        + a["rPipeCovIn"]
        + a["rThScrCovIn"]
        - a["hCovInCovE"]
        + a["rLampCovIn"]
        + a["rBlScrCovIn"]
        + a["rIntLampCovIn"]
    )

    # 7.Thermal screen temperature [°C s^{-1}]
    # Equation 5 [1], Equation A1 [5], Equation 7.1 [6]
    dx["tThScr"] = (1 / p["capThScr"]) * (
        a["hAirThScr"]
        + a["lAirThScr"]
        + a["rCanThScr"]
        + a["rFlrThScr"]
        + a["rPipeThScr"]
        - a["hThScrTop"]
        - a["rThScrCovIn"]
        - a["rThScrSky"]
        + a["rBlScrThScr"]
        + a["rLampThScr"]
        + a["rIntLampThScr"]
    )

    # 8.Greenhouse floor temperature [°C s^{-1}]
    # Equation 3 [1], Equation A1 [5], Equation 7.1 [6]
    dx["tFlr"] = (
        1
        / p["capFlr"]
        * (
            a["hAirFlr"]
            + a["rParSunFlr"]
            + a["rNirSunFlr"]
            + a["rCanFlr"]
            + a["rPipeFlr"]
            - a["hFlrSo1"]
            - a["rFlrCovIn"]
            - a["rFlrSky"]
            - a["rFlrThScr"]
            + a["rParLampFlr"]
            + a["rNirLampFlr"]
            + a["rFirLampFlr"]
            - a["rFlrBlScr"]
            + a["rParIntLampFlr"]
            + a["rNirIntLampFlr"]
            + a["rFirIntLampFlr"]
        )
    )

    # 9.Pipe temperature [°C s^{-1}]
    if "tPipe" in d:
        # Pipe temperature is given as an input.  In this case gl['x']['tPipe']
        # should be equal to gl['d']['tPipe'], unless gl['d']['tPipe'] == 0, then it should
        # be calculated by using the ODE
        a["tPipeOn"] = d["tPipe"] - x["tPipe"]
        a["tPipeOff"] = (
            1
            / p["capPipe"]
            * (
                a["hBoilPipe"]
                + a["hIndPipe"]
                + a["hGeoPipe"]
                - a["rPipeSky"]
                - a["rPipeCovIn"]
                - a["rPipeCan"]
                - a["rPipeFlr"]
                - a["rPipeThScr"]
                - a["hPipeAir"]
                + a["rLampPipe"]
                - a["rPipeBlScr"]
                + a["hBufHotPipe"]
                + a["rIntLampPipe"]
            )
        )

        # when gl['d']['tPipe'] == 0 (or just about to), use the ODE for tPipe, otherwise mimic gl['d']['tPipe']
        dx["tPipe"] = ifElse(
            (d["tPipe"] == 0) | (d["pipeSwitchOff"] > 0),
            a["tPipeOff"],
            a["tPipeOn"],
        )

    else:
        # Equation 9 [1], Equation A1 [5], Equation 7.1 [6]
        dx["tPipe"] = (
            1
            / p["capPipe"]
            * (
                a["hBoilPipe"]
                + a["hIndPipe"]
                + a["hGeoPipe"]
                - a["rPipeSky"]
                - a["rPipeCovIn"]
                - a["rPipeCan"]
                - a["rPipeFlr"]
                - a["rPipeThScr"]
                - a["hPipeAir"]
                + a["rLampPipe"]
                - a["rPipeBlScr"]
                + a["hBufHotPipe"]
                + a["rIntLampPipe"]
            )
        )

    # 10.External cover temperature [°C s^{-1}]
    # Equation 8 [1]
    dx["tCovE"] = (1 / a["capCovE"]) * (
        a["rGlobSunCovE"] + a["hCovInCovE"] - a["hCovEOut"] - a["rCovESky"]
    )

    # Soil temperatures
    # Equation 4 [1]

    # 11.Soil layer 1 temperature [°C s^{-1}]
    dx["tSo1"] = 1 / p["capSo1"] * (a["hFlrSo1"] - a["hSo1So2"])

    # 12.Soil layer 2 temperature [°C s^{-1}]
    dx["tSo2"] = 1 / p["capSo2"] * (a["hSo1So2"] - a["hSo2So3"])

    # 13.Soil layer 3 temperature [°C s^{-1}]
    dx["tSo3"] = 1 / p["capSo3"] * (a["hSo2So3"] - a["hSo3So4"])

    # 14.Soil layer 4 temperature [°C s^{-1}]
    dx["tSo4"] = 1 / p["capSo4"] * (a["hSo3So4"] - a["hSo4So5"])

    # 15.Soil layer 5 temperature [°C s^{-1}]
    dx["tSo5"] = 1 / p["capSo5"] * (a["hSo4So5"] - a["hSo5SoOut"])

    # 16.Vapor pressure of greenhouse air [Pa s^{-1}] = [kg m^{-1} s^{-3}]
    # Equation 10 [1], Equation A40 [5], Equation 7.40, 7.50 [6]
    dx["vpAir"] = (1 / a["capVpAir"]) * (
        a["mvCanAir"]
        + a["mvPadAir"]
        + a["mvFogAir"]
        + a["mvBlowAir"]
        - a["mvAirThScr"]
        - a["mvAirTop"]
        - a["mvAirOut"]
        - a["mvAirOutPad"]
        - a["mvAirMech"]
        - a["mvAirBlScr"]
    )

    # 17.Vapor pressure of air in top compartment [Pa s^{-1}] = [kg m^{-1} s^{-3}]
    # Equation 11 [1]
    dx["vpTop"] = (1 / a["capVpTop"]) * (
        a["mvAirTop"] - a["mvTopCovIn"] - a["mvTopOut"]
    )

    # 18.Average canopy temperature in last 24 hours
    # Equation 9 [2]
    dx["tCan24"] = 1 / 86400 * (x["tCan"] - x["tCan24"])

    # 19.Date and time [datenum, days since 0-0-0000]
    dx["time"] = 1 / 86400

    # 20.Lamp temperature [°C s^{-1}]
    # Equation A1 [5], Equation 7.1 [6]
    dx["tLamp"] = (
        1
        / p["capLamp"]
        * (
            a["qLampIn"]
            - a["hLampAir"]
            - a["rLampSky"]
            - a["rLampCovIn"]
            - a["rLampThScr"]
            - a["rLampPipe"]
            - a["rLampAir"]
            - a["rLampBlScr"]
            - a["rParLampFlr"]
            - a["rNirLampFlr"]
            - a["rFirLampFlr"]
            - a["rParLampCan"]
            - a["rNirLampCan"]
            - a["rFirLampCan"]
            - a["hLampCool"]
            + a["rIntLampLamp"]
        )
    )

    # 21.Grow pipes temperature [°C s^{-1}]
    if "tGroPipe" in d:
        # Growpipe temperature is given as an input.  In this case gl['x']['tGroPipe']
        # should be equal to gl['d']['tGroPipe'], unless gl['d']['tGroPipe'] == 0, then it should
        # be calculated by using the ODE
        a["tGroPipeOn"] = d["tGroPipe"] - x["tGroPipe"]
        a["tGroPipeOff"] = (
            1
            / p["capGroPipe"]
            * (a["hBoilGroPipe"] - a["rGroPipeCan"] - a["hGroPipeAir"])
        )

        # when gl['d']['tGroPipe'] == 0 (or just about to), use the ODE for tGroPipe, otherwise mimic gl['d']['tPipe']
        dx["tGroPipe"] = ifElse(
            (d["tGroPipe"] == 0) | (d["groPipeSwitchOff"] > 0),
            a["tGroPipeOff"],
            a["tGroPipeOn"],
        )

    else:
        # Equation A1 [5], Equation 7.1 [6]
        dx["tGroPipe"] = (
            1
            / p["capGroPipe"]
            * (a["hBoilGroPipe"] - a["rGroPipeCan"] - a["hGroPipeAir"])
        )

    # 22.Interlight temperature [°C s^{-1}]
    # Equation 7.1 [6]
    dx["tIntLamp"] = (
        1
        / p["capIntLamp"]
        * (
            a["qIntLampIn"]
            - a["hIntLampAir"]
            - a["rIntLampSky"]
            - a["rIntLampCovIn"]
            - a["rIntLampThScr"]
            - a["rIntLampPipe"]
            - a["rIntLampAir"]
            - a["rIntLampBlScr"]
            - a["rParIntLampFlr"]
            - a["rNirIntLampFlr"]
            - a["rFirIntLampFlr"]
            - a["rParIntLampCan"]
            - a["rNirIntLampCan"]
            - a["rFirIntLampCan"]
            - a["rIntLampLamp"]
        )
    )

    # 23.Blackout screen temperature [°C s^{-1}]
    # Equation A1 [5], Equation 7.1 [6]
    dx["tBlScr"] = (1 / p["capBlScr"]) * (
        a["hAirBlScr"]
        + a["lAirBlScr"]
        + a["rCanBlScr"]
        + a["rFlrBlScr"]
        + a["rPipeBlScr"]
        - a["hBlScrTop"]
        - a["rBlScrCovIn"]
        - a["rBlScrSky"]
        - a["rBlScrThScr"]
        + a["rLampBlScr"]
        + a["rIntLampBlScr"]
    )

    # 24.Carbohydrates in buffer [mg{CH2O} m^{-2} s^{-1}]
    # Equation 1 [2]
    dx["cBuf"] = (
        a["mcAirBuf"]
        - a["mcBufFruit"]
        - a["mcBufLeaf"]
        - a["mcBufStem"]
        - a["mcBufAir"]
    )

    # 25.Carbohydrates in leaves [mg{CH2O} m^{-2} s^{-1}]
    # Equation 4 [2]
    dx["cLeaf"] = a["mcBufLeaf"] - a["mcLeafAir"] - a["mcLeafHar"]

    # 26.Carbohydrates in stem [mg{CH2O} m^{-2} s^{-1}]
    # Equation 6 [2]
    dx["cStem"] = a["mcBufStem"] - a["mcStemAir"]

    # 27.Carbohydrates in fruit [mg{CH2O} m^{-2} s^{-1}]
    # Equation 2 [2], Equation A44 [5]
    dx["cFruit"] = a["mcBufFruit"] - a["mcFruitAir"] - a["mcFruitHar"]

    # 28.Crop development stage [°C day s^{-1}]
    # Equation 8 [2]
    dx["tCanSum"] = 1 / 86400 * x["tCan"]

    return list(dx.values())  # return list of values

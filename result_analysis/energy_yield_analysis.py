# File path: GreenLightPlus/result_analysis/energy_yield_analysis.py
"""
Copyright Statement:

This Python version of the code is based on the open-source Matlab code released by David Katzin at Wageningen University and is subject to his original copyright.

Original Matlab code author: David Katzin
Original author's email: david.katzin@wur.nl, david.katzin1@gmail.com

New Python code author: Daidai Qiu
Author's email: qiu.daidai@outlook.com, daidai.qiu@wur.nl

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


from ..service_functions.funcs import *


def energy_yield_analysis(gl, print_val=False):
    """
    Input:
    gl -    a GreenLight model dict, after simulating
    Outputs:
    lampIn -        Energy consumption of the lamps [MJ m^{-2}]
    boilIn -        Energy consumption of the boiler [MJ m^{-2}]
    hhIn -          Energy consumption of the heat harvesting system [MJ m^{-2}]
    parSun -        PAR light from the sun reaching above the canopy [mol m^{-2}]
    parLamps -      PAR light from the lamps reaching outside the canopy [mol m^{-2}]
    yield -         Fresh weight tomato yield [kg m^{-2}]
    efficiency -    Energy input needed per tomato yield [MJ kg^{-1}]

    """
    # If the model did not have heat harvesting, set these values as 0
    if "mech" not in gl["u"]:
        gl["u"]["mech"] = 0
    if "heatPump" not in gl["u"]:
        gl["u"]["heatPump"] = 0
    if "pMech" not in gl["p"]:
        gl["p"]["pMech"] = 0
    if "etaMech" not in gl["p"]:
        gl["p"]["etaMech"] = 0.25
    if "pHeatPump" not in gl["p"]:
        gl["p"]["pHeatPump"] = 0

    # Dry matter content, see Chapter 5 Section 2.3.3 [1]
    dmc = 0.06

    # Energy consumption of the lamps [MJ m^{-2}]
    lampIn = calculate_energy_consumption(gl, "qLampIn", "qIntLampIn")

    # # Energy consumption of the boiler [MJ m^{-2}]
    boilIn = calculate_energy_consumption(gl, "hBoilPipe", "hBoilGroPipe")

    # Energy consumption of the heat harvesting system [MJ m^{-2}]
    # See Equation 5.1 [1]
    hhIn = (
        trapz_arrays(
            gl["p"]["pHeatPump"] * gl["u"]["heatPump"]
            + gl["p"]["etaMech"] * gl["p"]["pMech"] * gl["u"]["mech"],
            gl["u"]["heatPump"],
        )
        / 1e6
    )

    # PAR light from the sun reaching above the canopy [mol m^{-2}]
    parSun = (
        trapz_arrays(
            gl["p"]["parJtoUmolSun"] * gl["a"]["rParGhSun"], gl["a"]["rParGhSun"]
        )
        / 1e6
    )

    # PAR light from the lamps reaching outside the canopy [mol m^{-2}]
    parLamps = (
        trapz_arrays(
            gl["p"]["zetaLampPar"] * gl["a"]["rParGhLamp"]
            + gl["p"]["zetaIntLampPar"] * gl["a"]["rParGhIntLamp"],
            gl["a"]["rParGhIntLamp"],
        )
        / 1e6
    )

    # Fresh weight tomato yield [kg m^{-2}]
    yield_fw = calculate_energy_consumption(gl, "mcFruitHar") / dmc

    # Energy input needed per tomato yield [MJ kg^{-1}]
    efficiency = (lampIn + boilIn + hhIn) / yield_fw

    if print_val:
        print(f"lampIn: {lampIn}")
        print(f"boilIn: {boilIn}")
        print(f"hhIn: {hhIn}")
        print(f"parSun: {parSun}")
        print(f"parLamps: {parLamps}")
        print(f"yield_fw: {yield_fw}")
        print(f"efficiency: {efficiency}")

    return lampIn, boilIn, hhIn, parSun, parLamps, yield_fw, efficiency

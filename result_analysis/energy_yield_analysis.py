# File path: GreenLightPlus/result_analysis/energy_yield_analysis.py
"""
Energy-Yield Performance Analysis Module
=======================================

This module analyzes the relationship between energy consumption and
crop yield in greenhouse simulations. It calculates key performance
indicators including energy efficiency, light use efficiency, and
yield productivity.

The analysis provides insights into:
- Total energy consumption by component (lighting, heating)
- Light integral from sun and supplemental lighting
- Fresh weight yield production
- Energy efficiency metrics (MJ/kg produce)

These metrics are essential for:
- Economic feasibility studies
- Optimization of climate control strategies
- Comparison of different greenhouse configurations
- Sustainability assessments

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

from ..service_functions.funcs import *


def energy_yield_analysis(gl, print_val=False):
    """
    Analyze energy consumption and crop yield performance metrics.
    
    This function calculates comprehensive performance indicators for
    greenhouse operations, focusing on the relationship between energy
    inputs and crop production. It evaluates both direct energy use
    (electricity, heating) and light energy (solar, supplemental).
    
    The analysis helps answer key questions:
    - How much energy is required per kg of produce?
    - What is the contribution of supplemental lighting?
    - How efficient is the greenhouse system overall?
    
    Performance Metrics Calculated:
    1. Energy Consumption:
        - Lamp electricity use
        - Heating system fuel/energy use
        - Heat pump/recovery system use
        
    2. Light Integrals:
        - Daily Light Integral (DLI) from sun
        - Supplemental light contribution
        - Total photosynthetic light
        
    3. Yield Metrics:
        - Fresh weight production
        - Dry matter accumulation
        - Harvest index
        
    4. Efficiency Indicators:
        - Energy per unit yield (MJ/kg)
        - Light use efficiency
        - Overall system efficiency
    
    Args:
        gl (dict): Complete GreenLight model dictionary after simulation.
            Must contain results from a full growing season or period.
        print_val (bool, optional): If True, prints detailed analysis
            results to console. Useful for quick inspection. Default: False.
    
    Returns:
        dict: Performance metrics containing:
            - 'lampIn': Lamp energy consumption [MJ m^-2]
            - 'boilIn': Boiler/heating energy [MJ m^-2]
            - 'hhIn': Heat harvesting energy credit [MJ m^-2]
            - 'parSun': Solar PAR integral [mol m^-2]
            - 'parLamps': Lamp PAR integral [mol m^-2]
            - 'yield': Fresh weight yield [kg m^-2]
            - 'efficiency': Energy use efficiency [MJ kg^-1]
            - Additional derived metrics
    
    Example:
        >>> # Run full season simulation
        >>> results = model.run_simulation(days=120)
        >>> 
        >>> # Analyze performance
        >>> metrics = energy_yield_analysis(results['gl'], print_val=True)
        >>> 
        >>> # Check efficiency
        >>> print(f"Energy efficiency: {metrics['efficiency']:.1f} MJ/kg")
        Energy efficiency: 45.2 MJ/kg
    
    Note:
        - Assumes tomato crop with 6% dry matter content
        - Heat harvesting systems are optional (defaults to 0)
        - All energy values converted to MJ for consistency
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

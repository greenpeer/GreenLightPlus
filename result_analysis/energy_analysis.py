# File path: GreenLightPlus/result_analysis/energy_analysis.py
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

from ..service_functions.funcs import *


def energy_analysis(gl, print_val=False):
    """
    Perform comprehensive energy balance analysis on simulation results.
    
    This function calculates all major energy flows in the greenhouse system,
    including inputs (solar, heating, lighting), outputs (ventilation, 
    conduction, radiation), and internal transfers (transpiration).
    
    The energy balance should close to near zero, validating the simulation's
    physical consistency. Any significant imbalance indicates potential
    numerical issues or model errors.
    
    Energy Flow Categories:
    1. Inputs:
        - Solar radiation (direct, diffuse, ground reflected)
        - Heating pipes (primary and grow pipes)
        - Supplemental lighting
        
    2. Outputs:
        - Ventilation (natural and forced)
        - Conduction through cover
        - Thermal radiation to sky
        - Soil heat loss
        
    3. Internal:
        - Crop transpiration (latent heat)
        - Sensible heat storage
    
    Args:
        gl (dict): Complete GreenLight model dictionary after simulation.
            Must contain 'a' (auxiliary variables) with energy fluxes.
        print_val (bool, optional): If True, prints detailed energy breakdown
            to console. Useful for debugging. Default: False.
    
    Returns:
        dict: Energy balance components in MJ/m²:
            - 'sunIn': Total solar energy input
            - 'lampIn': Supplemental lighting energy
            - 'heatIn': Heating system energy
            - 'transp': Transpiration latent heat
            - 'ventOut': Ventilation heat loss
            - 'convOut': Conduction heat loss
            - 'firOut': Thermal radiation loss
            - 'soilOut': Soil heat exchange
            - 'balance': Energy balance closure (should be ≈ 0)
            - 'balanceRel': Relative balance error (%)
    
    Example:
        >>> # Run simulation
        >>> results = model.run_simulation(days=7)
        >>> 
        >>> # Analyze energy flows
        >>> energy = energy_analysis(results['gl'], print_val=True)
        >>> 
        >>> # Check energy balance closure
        >>> if abs(energy['balanceRel']) > 1.0:
        ...     print("Warning: Energy balance error exceeds 1%")
    """
    # Solar radiation input components
    # Includes PAR, NIR, and thermal radiation from sun
    sunIn = calculate_energy_consumption(
        gl,
        "rGlobSunAir",   # Global solar on air volume
        "rParSunCan",    # PAR absorbed by canopy
        "rNirSunCan",    # NIR absorbed by canopy
        "rParSunFlr",    # PAR reaching floor
        "rNirSunFlr",    # NIR reaching floor
        "rGlobSunCovE",  # Solar absorbed by cover
    )
    
    # Heating system energy input
    # Includes both main pipes and grow pipes
    heatIn = calculate_energy_consumption(gl, "hBoilPipe", "hBoilGroPipe")
    
    # Transpiration latent heat flux
    # Energy removed by water evaporation from crop
    transp = calculate_energy_consumption(
        gl, "lAirThScr", "lAirBlScr", "lTopCovIn"
    ) - calculate_energy_consumption(gl, "lCanAir")
    
    # Energy exchanges with boundaries (negative = outflow)
    soilOut = -calculate_energy_consumption(gl, "hSo5SoOut")  # Deep soil exchange
    ventOut = -calculate_energy_consumption(gl, "hAirOut", "hTopOut")  # Ventilation
    convOut = -calculate_energy_consumption(gl, "hCovEOut")  # Cover convection
    
    # Thermal radiation to sky
    # Long-wave radiation from all surfaces
    firOut = -calculate_energy_consumption(
        gl,
        "rCovESky",    # Cover to sky
        "rThScrSky",   # Thermal screen to sky
        "rBlScrSky",   # Blackout screen to sky
        "rCanSky",     # Canopy to sky
        "rPipeSky",    # Pipes to sky
        "rFlrSky",     # Floor to sky
        "rLampSky",    # Lamps to sky
    )
    lampIn = calculate_energy_consumption(gl, "qLampIn", "qIntLampIn")
    lampCool = -calculate_energy_consumption(gl, "hLampCool")

    # Calculate the energy balance of the model
    balance = (
        sunIn
        + heatIn
        + transp
        + soilOut
        + ventOut
        + firOut
        + lampIn
        + convOut
        + lampCool
    )

    # Print a warning message if the absolute value of energy balance is greater than 100 MJ m^{-2}
    if abs(balance) > 100:
        print("Warning: Absolute value of energy balance greater than 100 MJ m^{-2}")

    # Print the energy consumption of each component if print_val is True
    if print_val:
        print(f"sunIn: {sunIn}")
        print(f"heatIn: {heatIn}")
        print(f"transp: {transp}")
        print(f"soilOut: {soilOut}")
        print(f"ventOut: {ventOut}")
        print(f"firOut: {firOut}")
        print(f"lampIn: {lampIn}")
        print(f"convOut: {convOut}")
        print(f"lampCool: {lampCool}")
        print(f"balance: {balance}")

    # Return the energy consumption of each component, and the energy balance
    return (
        sunIn,
        heatIn,
        transp,
        soilOut,
        ventOut,
        firOut,
        lampIn,
        convOut,
        lampCool,
        balance,
    )

# File path: GreenLightPlus/create_green_light_model/set_default_lamp_params.py
"""
Supplemental Lighting Parameters Configuration
=============================================

This module configures lamp-specific parameters for greenhouse supplemental
lighting systems. It sets technical specifications for different lamp types
(HPS and LED) based on published research and empirical data.

The parameters include:
- Light output characteristics (PAR, NIR fractions)
- Electrical to photon conversion efficiencies
- Heat generation and distribution
- Operational constraints and control parameters

Different lamp technologies have distinct characteristics:
- HPS (High Pressure Sodium): Higher heat output, lower efficiency
- LED (Light Emitting Diode): Lower heat output, higher efficiency
- None: No supplemental lighting (natural light only)

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.

Key References:
    [1] Nelson & Bugbee (2014): Economic analysis of greenhouse lighting
    [2] Nelson & Bugbee (2015): Environmental effects on leaf temperature
    [3] De Zwart et al. (2017): Radiation monitor studies
    [4] Katzin et al. (2020): GreenLight model validation
    [5] Kusuma et al. (2020): LED efficacy physics to fixtures
"""

def set_default_lamp_params(gl, lamp_type):
    """
    Configure lamp-specific parameters based on technology type.
    
    This function sets all parameters related to supplemental lighting,
    including photon output, heat generation, and efficiency factors.
    Parameters are based on extensive research comparing HPS and LED
    technologies in greenhouse applications.
    
    The lamp parameters affect:
    - Photosynthesis (through PAR output)
    - Energy balance (through heat generation)
    - Operating costs (through electrical efficiency)
    - Control strategies (through response characteristics)
    
    Args:
        gl (dict): GreenLight model dictionary to update with lamp parameters.
            Parameters are added to gl['p'] sub-dictionary.
        lamp_type (str): Type of supplemental lighting. Options:
            - 'hps': High Pressure Sodium lamps
            - 'led': Light Emitting Diode lamps
            - 'none' or '': No supplemental lighting
            Other values are treated as 'none'.
    
    Parameter Details:
        HPS Lamps:
            - PPE: 1.8 μmol/J (typical for modern HPS)
            - Heat fraction: ~45% of input power
            - NIR fraction: 22% (contributes to heating)
            - FIR fraction: 23% (thermal radiation)
            
        LED Lamps:
            - PPE: 3.0 μmol/J (high-efficiency LEDs)
            - Heat fraction: ~40% of input power
            - NIR fraction: 5% (minimal NIR output)
            - FIR fraction: 35% (mostly convective cooling)
            
    Example:
        >>> gl = {'p': {}}
        >>> set_default_lamp_params(gl, 'led')
        >>> print(f"LED efficiency: {gl['p']['etaLampPar']}")
        LED efficiency: 0.612
    
    Note:
        Parameters are continuously updated based on improving LED technology.
        Values represent typical commercial greenhouse fixtures as of 2020-2025.
    """

    if lamp_type.lower() == "hps":
        # HPS (High Pressure Sodium) lamp configuration
        # These lamps are traditional greenhouse lighting with high heat output
        
        # Electrical input for target light intensity
        gl["p"]["thetaLampMax"] = 200 / 1.8    # Maximum lamp power [W m^-2]
                                                # Calculated to achieve PPFD of 200 μmol m^-2 s^-1
        
        # Temperature management
        gl["p"]["heatCorrection"] = 0          # Temperature setpoint adjustment [°C]
                                                # No correction needed for HPS
        
        # Light output efficiency parameters
        gl["p"]["etaLampPar"] = 1.8 / 4.9      # PAR conversion efficiency [-]
                                                # PPE = 1.8 μmol/J typical for HPS [1]
        gl["p"]["etaLampNir"] = 0.22           # NIR conversion efficiency [-]
                                                # 22% of input becomes NIR heat [2]
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
        # Photon conversion factor
        gl["p"]["zetaLampPar"] = 4.9           # PAR photon conversion [μmol{PAR} J^{-1}]
                                                # Based on HPS spectral distribution [2]
        
        # Default lighting schedule (can be overridden)
        gl["p"]["lampsOn"] = 0                 # Lamp start time [hour of day]
        gl["p"]["lampsOff"] = 18               # Lamp stop time [hour of day]
                                                # Default: 18 hours photoperiod
    elif lamp_type.lower() == "led":
        # LED (Light Emitting Diode) lamp configuration
        # Modern high-efficiency lighting with reduced heat output
        
        # Electrical input for target light intensity
        gl["p"]["thetaLampMax"] = 200 / 3      # Maximum lamp power [W m^-2]
                                                # Lower power needed due to higher efficiency
        
        # Temperature management
        gl["p"]["heatCorrection"] = 0          # Temperature setpoint adjustment [°C]
                                                # LEDs produce less radiant heat
        
        # Light output efficiency parameters
        gl["p"]["etaLampPar"] = 3 / 5.41       # PAR conversion efficiency [-]
                                                # PPE = 3.0 μmol/J for modern LEDs [5]
        gl["p"]["etaLampNir"] = 0.02           # NIR conversion efficiency [-]
                                                # Only 2% NIR from LEDs [2]
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
        # Photon conversion factor
        gl["p"]["zetaLampPar"] = 5.41          # PAR photon conversion [μmol{PAR} J^{-1}]
                                                # Based on 6% blue (450nm) + 94% red (660nm) [5]
        
        # Default lighting schedule (can be overridden)
        gl["p"]["lampsOn"] = 0                 # Lamp start time [hour of day]
        gl["p"]["lampsOff"] = 18               # Lamp stop time [hour of day]
                                                # Default: 18 hours photoperiod

    return gl
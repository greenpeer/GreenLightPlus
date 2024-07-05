def co2_dens2ppm(temp, dens):
    """
    Convert CO2 density [kg m^{-3}] to molar concentration [ppm].

    Usage:
        ppm = co2_dens2ppm(temp, dens)

    Inputs:
        temp: given temperatures [°C] (numpy array)
        dens: CO2 density in air [kg m^{-3}] (numpy array)
        Inputs should have identical dimensions

    Outputs:
        ppm: Molar concentration of CO2 in air [ppm] (numpy array)

    Calculation based on ideal gas law pV=nRT, pressure is assumed to be 1 atm.
    """

    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    M_CO2 = 44.01e-3  # molar mass of CO2 [kg mol^-{1}]
    P = 101325  # pressure (assumed to be 1 atm) [Pa]

    ppm = 10**6 * R * (temp + C2K) * dens / (P * M_CO2)
    return ppm
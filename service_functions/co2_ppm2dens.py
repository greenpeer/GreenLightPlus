def co2_ppm2dens(temp, ppm):
    """
    Convert CO2 molar concentration [ppm] to density [kg m^{-3}]
    
    Parameters:
        temp (array_like): given temperatures [°C]
        ppm (array_like): CO2 concentration in air [ppm]
    
    Returns:
        co2Dens (ndarray): CO2 concentration in air [kg m^{-3}]
    """
    R = 8.3144598  # molar gas constant [J mol^{-1} K^{-1}]
    C2K = 273.15  # conversion from Celsius to Kelvin [K]
    M_CO2 = 44.01e-3  # molar mass of CO2 [kg mol^-{1}]
    P = 101325  # pressure (assumed to be 1 atm) [Pa]

    # number of moles n = m / M_CO2 where m is the mass [kg] and M_CO2 is the
    # molar mass [kg mol^{-1}]. So m = p * V * M_CO2 * P / RT where V is 10^-6 * ppm
    co2Dens = P * 10**-6 * ppm * M_CO2 / (R * (temp + C2K))

    return co2Dens

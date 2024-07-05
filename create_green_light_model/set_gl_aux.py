import copy
import numpy as np
from ..service_functions.funcs import *
from ..service_functions.co2_dens2ppm import co2_dens2ppm

class GreenLightAuxiliaryStates:
    def __init__(self, gl):
        self.gl = gl
        self.a = gl["a"]
        self.u = gl["u"]
        self.p = gl["p"]
        self.x = gl["x"]
        self.d = gl["d"]

    def set_lumped_cover_layers(self):
        """
        Set the properties of the lumped cover layers, including shadow screen and semi-permanent shadow screen
        transmission and reflection coefficients.
        Reference: Section 3 [1], Section A[1] [5]
        """
        # Set PAR transmission and reflection coefficients
        self._set_par_coefficients()
        # Set NIR transmission and reflection coefficients
        self._set_nir_coefficients()
        # Set FIR transmission and reflection coefficients
        self._set_fir_coefficients()
        # Set thermal screen and roof coefficients
        self._set_thermal_screen_and_roof_coefficients()
        # Set Vanthoor model coefficients
        self._set_vanthoor_coefficients()
        # Set all layers transmission and reflection coefficients
        self._set_all_layers_coefficients()
        # Set cover heat capacity
        self._set_cover_heat_capacity()

    def _set_par_coefficients(self):
        """
        Set the PAR (Photosynthetically Active Radiation) transmission and reflection coefficients
        for shadow screen and semi-permanent shadow screen.
        """
        # PAR transmission coefficient of the shadow screen layer [-]
        self.a["tauShScrPar"] = 1 - self.u["shScr"] * (1 - self.p["tauShScrPar"])

        # PAR transmission coefficient of the semi-permanent shadow screen layer [-]
        self.a["tauShScrPerPar"] = 1 - self.u["shScrPer"] * (1 - self.p["tauShScrPerPar"])

        # PAR reflection coefficient of the shadow screen layer [-]
        self.a["rhoShScrPar"] = self.u["shScr"] * self.p["rhoShScrPar"]

        # PAR reflection coefficient of the semi-permanent shadow screen layer [-]
        self.a["rhoShScrPerPar"] = self.u["shScrPer"] * self.p["rhoShScrPerPar"]

        # PAR transmission coefficient of the shadow screen and semi-permanent shadow screen layer [-]
        self.a["tauShScrShScrPerPar"] = tau12(
            self.a["tauShScrPar"],
            self.a["tauShScrPerPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPerPar"],
            self.a["rhoShScrPerPar"],
        )

        # PAR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the top [-]
        self.a["rhoShScrShScrPerParUp"] = rhoUp(
            self.a["tauShScrPar"],
            self.a["tauShScrPerPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPerPar"],
            self.a["rhoShScrPerPar"],
        )

        # PAR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the bottom [-]
        self.a["rhoShScrShScrPerParDn"] = rhoDn(
            self.a["tauShScrPar"],
            self.a["tauShScrPerPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPar"],
            self.a["rhoShScrPerPar"],
            self.a["rhoShScrPerPar"],
        )

    def _set_nir_coefficients(self):
        """
        Set the NIR (Near-Infrared) transmission and reflection coefficients for shadow screen
        and semi-permanent shadow screen.
        """
        # NIR transmission coefficient of the shadow screen layer [-]
        self.a["tauShScrNir"] = 1 - self.u["shScr"] * (1 - self.p["tauShScrNir"])

        # NIR transmission coefficient of the semi-permanent shadow screen layer [-]
        self.a["tauShScrPerNir"] = 1 - self.u["shScrPer"] * (1 - self.p["tauShScrPerNir"])

        # NIR reflection coefficient of the shadow screen layer [-]
        self.a["rhoShScrNir"] = self.u["shScr"] * self.p["rhoShScrNir"]

        # NIR reflection coefficient of the semi-permanent shadow screen layer [-]
        self.a["rhoShScrPerNir"] = self.u["shScrPer"] * self.p["rhoShScrPerNir"]

        # NIR transmission coefficient of the shadow screen and semi-permanent shadow screen layer [-]
        self.a["tauShScrShScrPerNir"] = tau12(
            self.a["tauShScrNir"],
            self.a["tauShScrPerNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrPerNir"],
            self.a["rhoShScrPerNir"],
        )

        # NIR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the top [-]
        self.a["rhoShScrShScrPerNirUp"] = rhoUp(
            self.a["tauShScrNir"],
            self.a["tauShScrPerNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrPerNir"],
            self.a["rhoShScrPerNir"],
        )

        # NIR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the bottom [-]
        self.a["rhoShScrShScrPerNirDn"] = rhoDn(
            self.a["tauShScrNir"],
            self.a["tauShScrPerNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrNir"],
            self.a["rhoShScrPerNir"],
            self.a["rhoShScrPerNir"],
        )

    def _set_fir_coefficients(self):
        """
        Set the FIR (Far-Infrared) transmission and reflection coefficients for shadow screen
        and semi-permanent shadow screen.
        """
        # FIR transmission coefficient of the shadow screen layer [-]
        self.a["tauShScrFir"] = 1 - self.u["shScr"] * (1 - self.p["tauShScrFir"])

        # FIR transmission coefficient of the semi-permanent shadow screen layer [-]
        self.a["tauShScrPerFir"] = 1 - self.u["shScrPer"] * (1 - self.p["tauShScrPerFir"])

        # FIR reflection coefficient of the shadow screen layer [-]
        self.a["rhoShScrFir"] = self.u["shScr"] * self.p["rhoShScrFir"]

        # FIR reflection coefficient of the semi-permanent shadow screen layer [-]
        self.a["rhoShScrPerFir"] = self.u["shScrPer"] * self.p["rhoShScrPerFir"]

        # FIR transmission coefficient of the shadow screen and semi-permanent shadow screen layer [-]
        self.a["tauShScrShScrPerFir"] = tau12(
            self.a["tauShScrFir"],
            self.a["tauShScrPerFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrPerFir"],
            self.a["rhoShScrPerFir"],
        )

        # FIR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the top [-]
        self.a["rhoShScrShScrPerFirUp"] = rhoUp(
            self.a["tauShScrFir"],
            self.a["tauShScrPerFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrPerFir"],
            self.a["rhoShScrPerFir"],
        )

        # FIR reflection coefficient of the shadow screen and semi-permanent shadow screen layer towards the bottom [-]
        self.a["rhoShScrShScrPerFirDn"] = rhoDn(
            self.a["tauShScrFir"],
            self.a["tauShScrPerFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrFir"],
            self.a["rhoShScrPerFir"],
            self.a["rhoShScrPerFir"],
        )

    def _set_thermal_screen_and_roof_coefficients(self):
        """
        Set the thermal screen and roof transmission and reflection coefficients.
        """
        # PAR transmission coefficient of the thermal screen [-]
        self.a["tauThScrPar"] = 1 - self.u["thScr"] * (1 - self.p["tauThScrPar"])

        # PAR reflection coefficient of the thermal screen [-]
        self.a["rhoThScrPar"] = self.u["thScr"] * self.p["rhoThScrPar"]

        # PAR transmission coefficient of the thermal screen and roof [-]
        self.a["tauCovThScrPar"] = tau12(
            self.p["tauRfPar"],
            self.a["tauThScrPar"],
            self.p["rhoRfPar"],
            self.p["rhoRfPar"],
            self.a["rhoThScrPar"],
            self.a["rhoThScrPar"],
        )

        # PAR reflection coefficient of the thermal screen and roof towards the top [-]
        self.a["rhoCovThScrParUp"] = rhoUp(
            self.p["tauRfPar"],
            self.a["tauThScrPar"],
            self.p["rhoRfPar"],
            self.p["rhoRfPar"],
            self.a["rhoThScrPar"],
            self.a["rhoThScrPar"],
        )

        # PAR reflection coefficient of the thermal screen and roof towards the bottom [-]
        self.a["rhoCovThScrParDn"] = rhoDn(
            self.p["tauRfPar"],
            self.a["tauThScrPar"],
            self.p["rhoRfPar"],
            self.p["rhoRfPar"],
            self.a["rhoThScrPar"],
            self.a["rhoThScrPar"],
        )

        # NIR transmission coefficient of the thermal screen [-]
        self.a["tauThScrNir"] = 1 - self.u["thScr"] * (1 - self.p["tauThScrNir"])

        # NIR reflection coefficient of the thermal screen [-]
        self.a["rhoThScrNir"] = self.u["thScr"] * self.p["rhoThScrNir"]

        # NIR transmission coefficient of the thermal screen and roof [-]
        self.a["tauCovThScrNir"] = tau12(
            self.p["tauRfNir"],
            self.a["tauThScrNir"],
            self.p["rhoRfNir"],
            self.p["rhoRfNir"],
            self.a["rhoThScrNir"],
            self.a["rhoThScrNir"],
        )

        # NIR reflection coefficient of the thermal screen and roof towards the top [-]
        self.a["rhoCovThScrNirUp"] = rhoUp(
            self.p["tauRfNir"],
            self.a["tauThScrNir"],
            self.p["rhoRfNir"],
            self.p["rhoRfNir"],
            self.a["rhoThScrNir"],
            self.a["rhoThScrNir"],
        )

        # NIR reflection coefficient of the thermal screen and roof towards the bottom [-]
        self.a["rhoCovThScrNirDn"] = rhoDn(
            self.p["tauRfNir"],
            self.a["tauThScrNir"],
            self.p["rhoRfNir"],
            self.p["rhoRfNir"],
            self.a["rhoThScrNir"],
            self.a["rhoThScrNir"],
        )

    def _set_vanthoor_coefficients(self):
        """
        Set the Vanthoor model transmission and reflection coefficients for the cover.
        """
        # Vanthoor PAR transmission coefficient of the cover [-]
        self.a["tauCovParOld"] = tau12(
            self.a["tauShScrShScrPerPar"],
            self.a["tauCovThScrPar"],
            self.a["rhoShScrShScrPerParUp"],
            self.a["rhoShScrShScrPerParDn"],
            self.a["rhoCovThScrParUp"],
            self.a["rhoCovThScrParDn"],
        )

        # Vanthoor PAR reflection coefficient of the cover towards the top [-]
        self.a["rhoCovParOldUp"] = rhoUp(
            self.a["tauShScrShScrPerPar"],
            self.a["tauCovThScrPar"],
            self.a["rhoShScrShScrPerParUp"],
            self.a["rhoShScrShScrPerParDn"],
            self.a["rhoCovThScrParUp"],
            self.a["rhoCovThScrParDn"],
        )

        # Vanthoor PAR reflection coefficient of the cover towards the bottom [-]
        self.a["rhoCovParOldDn"] = rhoDn(
            self.a["tauShScrShScrPerPar"],
            self.a["tauCovThScrPar"],
            self.a["rhoShScrShScrPerParUp"],
            self.a["rhoShScrShScrPerParDn"],
            self.a["rhoCovThScrParUp"],
            self.a["rhoCovThScrParDn"],
        )

        # Vanthoor NIR transmission coefficient of the cover [-]
        self.a["tauCovNirOld"] = tau12(
            self.a["tauShScrShScrPerNir"],
            self.a["tauCovThScrNir"],
            self.a["rhoShScrShScrPerNirUp"],
            self.a["rhoShScrShScrPerNirDn"],
            self.a["rhoCovThScrNirUp"],
            self.a["rhoCovThScrNirDn"],
        )

        # Vanthoor NIR reflection coefficient of the cover towards the top [-]
        self.a["rhoCovNirOldUp"] = rhoUp(
            self.a["tauShScrShScrPerNir"],
            self.a["tauCovThScrNir"],
            self.a["rhoShScrShScrPerNirUp"],
            self.a["rhoShScrShScrPerNirDn"],
            self.a["rhoCovThScrNirUp"],
            self.a["rhoCovThScrNirDn"],
        )

        # Vanthoor NIR reflection coefficient of the cover towards the bottom [-]
        self.a["rhoCovNirOldDn"] = rhoDn(
            self.a["tauShScrShScrPerNir"],
            self.a["tauCovThScrNir"],
            self.a["rhoShScrShScrPerNirUp"],
            self.a["rhoShScrShScrPerNirDn"],
            self.a["rhoCovThScrNirUp"],
            self.a["rhoCovThScrNirDn"],
        )

    def _set_all_layers_coefficients(self):
        """
        Set the transmission and reflection coefficients for all layers including blackout screen and lamp.
        """
        # PAR transmission coefficient of the blackout screen [-]
        self.a["tauBlScrPar"] = 1 - self.u["blScr"] * (1 - self.p["tauBlScrPar"])

        # PAR reflection coefficient of the blackout screen [-]
        self.a["rhoBlScrPar"] = self.u["blScr"] * self.p["rhoBlScrPar"]

        # PAR transmission coefficient of the old cover and blackout screen [-]
        self.a["tauCovBlScrPar"] = tau12(
            self.a["tauCovParOld"],
            self.a["tauBlScrPar"],
            self.a["rhoCovParOldUp"],
            self.a["rhoCovParOldDn"],
            self.a["rhoBlScrPar"],
            self.a["rhoBlScrPar"],
        )

        # PAR reflection coefficient of the old cover and blackout screen towards the top [-]
        self.a["rhoCovBlScrParUp"] = rhoUp(
            self.a["tauCovParOld"],
            self.a["tauBlScrPar"],
            self.a["rhoCovParOldUp"],
            self.a["rhoCovParOldDn"],
            self.a["rhoBlScrPar"],
            self.a["rhoBlScrPar"],
        )

        # PAR reflection coefficient of the old cover and blackout screen towards the bottom [-]
        self.a["rhoCovBlScrParDn"] = rhoDn(
            self.a["tauCovParOld"],
            self.a["tauBlScrPar"],
            self.a["rhoCovParOldUp"],
            self.a["rhoCovParOldDn"],
            self.a["rhoBlScrPar"],
            self.a["rhoBlScrPar"],
        )

        # NIR transmission coefficient of the blackout screen [-]
        self.a["tauBlScrNir"] = 1 - self.u["blScr"] * (1 - self.p["tauBlScrNir"])

        # NIR reflection coefficient of the blackout screen [-]
        self.a["rhoBlScrNir"] = self.u["blScr"] * self.p["rhoBlScrNir"]

        # NIR transmission coefficient of the old cover and blackout screen [-]
        self.a["tauCovBlScrNir"] = tau12(
            self.a["tauCovNirOld"],
            self.a["tauBlScrNir"],
            self.a["rhoCovNirOldUp"],
            self.a["rhoCovNirOldDn"],
            self.a["rhoBlScrNir"],
            self.a["rhoBlScrNir"],
        )

        # NIR reflection coefficient of the old cover and blackout screen towards the top [-]
        self.a["rhoCovBlScrNirUp"] = rhoUp(
            self.a["tauCovNirOld"],
            self.a["tauBlScrNir"],
            self.a["rhoCovNirOldUp"],
            self.a["rhoCovNirOldDn"],
            self.a["rhoBlScrNir"],
            self.a["rhoBlScrNir"],
        )

        # NIR reflection coefficient of the old cover and blackout screen towards the bottom [-]
        self.a["rhoCovBlScrNirDn"] = rhoDn(
            self.a["tauCovNirOld"],
            self.a["tauBlScrNir"],
            self.a["rhoCovNirOldUp"],
            self.a["rhoCovNirOldDn"],
            self.a["rhoBlScrNir"],
            self.a["rhoBlScrNir"],
        )

        # All layers PAR transmission coefficient of the cover [-]
        self.a["tauCovPar"] = tau12(
            self.a["tauCovBlScrPar"],
            self.p["tauLampPar"],
            self.a["rhoCovBlScrParUp"],
            self.a["rhoCovBlScrParDn"],
            self.p["rhoLampPar"],
            self.p["rhoLampPar"],
        )

        # All layers PAR reflection coefficient of the cover [-]
        self.a["rhoCovPar"] = rhoUp(
            self.a["tauCovBlScrPar"],
            self.p["tauLampPar"],
            self.a["rhoCovBlScrParUp"],
            self.a["rhoCovBlScrParDn"],
            self.p["rhoLampPar"],
            self.p["rhoLampPar"],
        )

        # All layers NIR transmission coefficient of the cover [-]
        self.a["tauCovNir"] = tau12(
            self.a["tauCovBlScrNir"],
            self.p["tauLampNir"],
            self.a["rhoCovBlScrNirUp"],
            self.a["rhoCovBlScrNirDn"],
            self.p["rhoLampNir"],
            self.p["rhoLampNir"],
        )

        # All layers NIR reflection coefficient of the cover [-]
        self.a["rhoCovNir"] = rhoUp(
            self.a["tauCovBlScrNir"],
            self.p["tauLampNir"],
            self.a["rhoCovBlScrNirUp"],
            self.a["rhoCovBlScrNirDn"],
            self.p["rhoLampNir"],
            self.p["rhoLampNir"],
        )

        # All layers FIR transmission coefficient of the cover, excluding screens and lamps [-]
        self.a["tauCovFir"] = tau12(
            self.a["tauShScrShScrPerFir"],
            self.p["tauRfFir"],
            self.a["rhoShScrShScrPerFirUp"],
            self.a["rhoShScrShScrPerFirDn"],
            self.p["rhoRfFir"],
            self.p["rhoRfFir"],
        )

        # All layers FIR reflection coefficient of the cover, excluding screens and lamps [-]
        self.a["rhoCovFir"] = rhoUp(
            self.a["tauShScrShScrPerFir"],
            self.p["tauRfFir"],
            self.a["rhoShScrShScrPerFirUp"],
            self.a["rhoShScrShScrPerFirDn"],
            self.p["rhoRfFir"],
            self.p["rhoRfFir"],
        )

        # PAR absorption coefficient of the cover [-]
        self.a["aCovPar"] = 1 - self.a["tauCovPar"] - self.a["rhoCovPar"]

        # NIR absorption coefficient of the cover [-]
        self.a["aCovNir"] = 1 - self.a["tauCovNir"] - self.a["rhoCovNir"]

        # FIR absorption coefficient of the cover [-]
        self.a["aCovFir"] = 1 - self.a["tauCovFir"] - self.a["rhoCovFir"]

        # FIR emission coefficient of the cover [-]
        self.a["epsCovFir"] = self.a["aCovFir"]

    def _set_cover_heat_capacity(self):
        """
        Set the heat capacity of the lumped cover [J K^{-1} m^{-2}].
        Equation 18 [1]
        """
        self.a["capCov"] = cosd(self.p["psi"]) * (
            self.u["shScrPer"] * self.p["hShScrPer"] * self.p["rhoShScrPer"] * self.p["cPShScrPer"]
            + self.p["hRf"] * self.p["rhoRf"] * self.p["cPRf"]
        )
                   
    def set_capacities(self):
        """
        Set the capacities for different components including canopy, cover, and vapor.
        Reference: Section 4 [1]
        """
        # Leaf area index [m^2{leaf} m^{-2}]
        # Equation 5 [2]
        self.a["lai"] = self.p["sla"] * self.x["cLeaf"]

        # Heat capacity of canopy [J K^{-1} m^{-2}]
        # Equation 19 [1]
        self.a["capCan"] = self.p["capLeaf"] * self.a["lai"]

        # Heat capacity of external and internal cover [J K^{-1} m^{-2}]
        # Equation 20 [1]
        self.a["capCovE"] = 0.1 * self.a["capCov"]
        self.a["capCovIn"] = 0.1 * self.a["capCov"]

        # Vapor capacity of main compartment [kg m J^{-1}]
        # Equation 24 [1]
        self.a["capVpAir"] = self.p["mWater"] * self.p["hAir"] / (self.p["R"] * (self.x["tAir"] + 273.15))

        # Vapor capacity of top compartment [kg m J^{-1}]
        self.a["capVpTop"] = self.p["mWater"] * (self.p["hGh"] - self.p["hAir"]) / (self.p["R"] * (self.x["tTop"] + 273.15))
    
    def set_heat_fluxes(self):
        """
        Set global, PAR, and NIR heat fluxes.
        Reference: Section 5.1 [1]
        """
        # Lamp electrical input [W m^{-2}]
        # Equation A16 [5]
        self.a["qLampIn"] = self.p["thetaLampMax"] * self.u["lamp"]

        # Interlight electrical input [W m^{-2}]
        # Equation A26 [5]
        self.a["qIntLampIn"] = self.p["thetaIntLampMax"] * self.u["intLamp"]

        # PAR above the canopy from the sun [W m^{-2}]
        # Equation 27 [1], Equation A14 [5]
        self.a["rParGhSun"] = (
            (1 - self.p["etaGlobAir"]) * self.a["tauCovPar"] * self.p["etaGlobPar"] * self.d["iGlob"]
        )

        # PAR above the canopy from the lamps [W m^{-2}]
        # Equation A15 [5]
        self.a["rParGhLamp"] = self.p["etaLampPar"] * self.a["qLampIn"]

        # PAR outside the canopy from the interlights [W m^{-2}]
        # Equation 7.7, 7.14 [7]
        self.a["rParGhIntLamp"] = self.p["etaIntLampPar"] * self.a["qIntLampIn"]

        # Global radiation above the canopy from the sun [W m^{-2}]
        # (PAR+NIR, where UV is counted together with NIR)
        # Equation 7.24 [7]
        self.a["rCanSun"] = (
            (1 - self.p["etaGlobAir"])
            * self.d["iGlob"]
            * (self.p["etaGlobPar"] * self.a["tauCovPar"] + self.p["etaGlobNir"] * self.a["tauCovNir"])
        )

        # Global radiation above the canopy from the lamps [W m^{-2}]
        # (PAR+NIR, where UV is counted together with NIR)
        # Equation 7.25 [7]
        self.a["rCanLamp"] = (self.p["etaLampPar"] + self.p["etaLampNir"]) * self.a["qLampIn"]

        # Global radiation outside the canopy from the interlight lamps [W m^{-2}]
        # (PAR+NIR, where UV is counted together with NIR)
        # Equation 7.26 [7]
        self.a["rCanIntLamp"] = (self.p["etaIntLampPar"] + self.p["etaIntLampNir"]) * self.gl["a"]["qIntLampIn"]

        # Global radiation above and outside the canopy [W m^{-2}]
        # (PAR+NIR, where UV is counted together with NIR)
        # Equation 7.23 [7]
        self.a["rCan"] = self.a["rCanSun"] + self.a["rCanLamp"] + self.a["rCanIntLamp"]

        # PAR from the sun directly absorbed by the canopy [W m^{-2}]
        # Equation 26 [1]
        self.a["rParSunCanDown"] = (
            self.a["rParGhSun"] * (1 - self.p["rhoCanPar"]) * (1 - np.exp(-self.p["k1Par"] * self.a["lai"]))
        )

        # PAR from the lamps directly absorbed by the canopy [W m^{-2}]
        # Equation A17 [5]
        self.a["rParLampCanDown"] = (
            self.a["rParGhLamp"] * (1 - self.p["rhoCanPar"]) * (1 - np.exp(-self.p["k1Par"] * self.a["lai"]))
        )

        # Fraction of PAR from the interlights reaching the canopy [-]
        # Equation 7.13 [7]
        self.a["fIntLampCanPar"] = (
            1
            - self.p["fIntLampDown"] * np.exp(-self.p["k1IntPar"] * self.p["vIntLampPos"] * self.a["lai"])
            + (self.p["fIntLampDown"] - 1)
            * np.exp(-self.p["k1IntPar"] * (1 - self.p["vIntLampPos"]) * self.a["lai"])
        )

        # Fraction of NIR from the interlights reaching the canopy [-]
        # Analogous to Equation 7.13 [7]
        self.a["fIntLampCanNir"] = (
            1
            - self.p["fIntLampDown"] * np.exp(-self.p["kIntNir"] * self.p["vIntLampPos"] * self.a["lai"])
            + (self.p["fIntLampDown"] - 1)
            * np.exp(-self.p["kIntNir"] * (1 - self.p["vIntLampPos"]) * self.a["lai"])
        )

        # PAR from the interlights directly absorbed by the canopy [W m^{-2}]
        # Equation 7.16 [7]
        self.a["rParIntLampCanDown"] = (
            self.a["rParGhIntLamp"] * self.a["fIntLampCanPar"] * (1 - self.p["rhoCanPar"])
        )

        # PAR from the sun absorbed by the canopy after reflection from the floor [W m^{-2}]
        # Equation 28 [1]
        self.a["rParSunFlrCanUp"] = mulNoBracks(
            self.a["rParGhSun"],
            np.exp(-self.p["k1Par"] * self.a["lai"])
            * self.p["rhoFlrPar"]
            * (1 - self.p["rhoCanPar"])
            * (1 - np.exp(-self.p["k2Par"] * self.a["lai"])),
        )

        # PAR from the lamps absorbed by the canopy after reflection from the floor [W m^{-2}]
        # Equation A18 [5]
        self.a["rParLampFlrCanUp"] = (
            self.a["rParGhLamp"]
            * np.exp(-self.p["k1Par"] * self.a["lai"])
            * self.p["rhoFlrPar"]
            * (1 - self.p["rhoCanPar"])
            * (1 - np.exp(-self.p["k2Par"] * self.a["lai"]))
        )

        # PAR from the interlights absorbed by the canopy after reflection from the floor [W m^{-2}]
        # Equation 7.18 [7]
        self.a["rParIntLampFlrCanUp"] = (
            self.a["rParGhIntLamp"]
            * self.p["fIntLampDown"]
            * np.exp(-self.p["k1IntPar"] * self.p["vIntLampPos"] * self.a["lai"])
            * self.p["rhoFlrPar"]
            * (1 - self.p["rhoCanPar"])
            * (1 - np.exp(-self.p["k2IntPar"] * self.a["lai"]))
        )

        # Total PAR from the sun absorbed by the canopy [W m^{-2}]
        # Equation 25 [1]
        self.a["rParSunCan"] = self.a["rParSunCanDown"] + self.a["rParSunFlrCanUp"]

        # Total PAR from the lamps absorbed by the canopy [W m^{-2}]
        # Equation A19 [5]
        self.a["rParLampCan"] = self.a["rParLampCanDown"] + self.a["rParLampFlrCanUp"]

        # Total PAR from the interlights absorbed by the canopy [W m^{-2}]
        # Equation A19 [5], Equation 7.19 [7]
        self.a["rParIntLampCan"] = self.a["rParIntLampCanDown"] + self.a["rParIntLampFlrCanUp"]

        # Virtual NIR transmission for the cover-canopy-floor lumped model [-]
        # Equation 29 [1]
        self.a["tauHatCovNir"] = 1 - self.a["rhoCovNir"]
        self.a["tauHatFlrNir"] = 1 - self.p["rhoFlrNir"]

        # NIR transmission coefficient of the canopy [-]
        # Equation 30 [1]
        self.a["tauHatCanNir"] = np.exp(-self.p["kNir"] * self.a["lai"])

        # NIR reflection coefficient of the canopy [-]
        # Equation 31 [1]
        self.a["rhoHatCanNir"] = self.p["rhoCanNir"] * (1 - self.a["tauHatCanNir"])

        # NIR transmission coefficient of the cover and canopy [-]
        self.a["tauCovCanNir"] = tau12(
            self.a["tauHatCovNir"],
            self.a["tauHatCanNir"],
            self.a["rhoCovNir"],
            self.a["rhoCovNir"],
            self.a["rhoHatCanNir"],
            self.a["rhoHatCanNir"],
        )

        # NIR reflection coefficient of the cover and canopy towards the top [-]
        self.a["rhoCovCanNirUp"] = rhoUp(
            self.a["tauHatCovNir"],
            self.a["tauHatCanNir"],
            self.a["rhoCovNir"],
            self.a["rhoCovNir"],
            self.a["rhoHatCanNir"],
            self.a["rhoHatCanNir"],
        )

        # NIR reflection coefficient of the cover and canopy towards the bottom [-]
        self.a["rhoCovCanNirDn"] = rhoDn(
            self.a["tauHatCovNir"],
            self.a["tauHatCanNir"],
            self.a["rhoCovNir"],
            self.a["rhoCovNir"],
            self.a["rhoHatCanNir"],
            self.a["rhoHatCanNir"],
        )

        # NIR transmission coefficient of the cover, canopy and floor [-]
        self.a["tauCovCanFlrNir"] = tau12(
            self.a["tauCovCanNir"],
            self.a["tauHatFlrNir"],
            self.a["rhoCovCanNirUp"],
            self.a["rhoCovCanNirDn"],
            self.p["rhoFlrNir"],
            self.p["rhoFlrNir"],
        )

        # NIR reflection coefficient of the cover, canopy and floor [-]
        self.a["rhoCovCanFlrNir"] = rhoUp(
            self.a["tauCovCanNir"],
            self.a["tauHatFlrNir"],
            self.a["rhoCovCanNirUp"],
            self.a["rhoCovCanNirDn"],
            self.p["rhoFlrNir"],
            self.p["rhoFlrNir"],
        )

        # The calculated absorption coefficient equals m['a']['aCanNir'] [-]
        # pg. 23 [1]
        self.a["aCanNir"] = 1 - self.a["tauCovCanFlrNir"] - self.a["rhoCovCanFlrNir"]

        # The calculated transmission coefficient equals m['a']['aFlrNir'] [-]
        # pg. 23 [1]
        self.a["aFlrNir"] = self.a["tauCovCanFlrNir"]

        # NIR from the sun absorbed by the canopy [W m^{-2}]
        # Equation 32 [1]
        self.a["rNirSunCan"] = (
            (1 - self.p["etaGlobAir"]) * self.a["aCanNir"] * self.p["etaGlobNir"] * self.d["iGlob"]
        )

        # NIR from the lamps absorbed by the canopy [W m^{-2}]
        # Equation A20 [5]
        self.a["rNirLampCan"] = (
            self.p["etaLampNir"]
            * self.a["qLampIn"]
            * (1 - self.p["rhoCanNir"])
            * (1 - np.exp(-self.p["kNir"] * self.a["lai"]))
        )

        # NIR from the interlights absorbed by the canopy [W m^{-2}]
        # Equation 7.20 [7]
        self.a["rNirIntLampCan"] = (
            self.p["etaIntLampNir"]
            * self.a["qIntLampIn"]
            * self.a["fIntLampCanNir"]
            * (1 - self.p["rhoCanNir"])
        )

        # NIR from the sun absorbed by the floor [W m^{-2}]
        # Equation 33 [1]
        self.a["rNirSunFlr"] = (
            (1 - self.p["etaGlobAir"]) * self.a["aFlrNir"] * self.p["etaGlobNir"] * self.d["iGlob"]
        )

        # NIR from the lamps absorbed by the floor [W m^{-2}]
        # Equation A22 [5]
        self.a["rNirLampFlr"] = (
            (1 - self.p["rhoFlrNir"])
            * np.exp(-self.p["kNir"] * self.a["lai"])
            * self.p["etaLampNir"]
            * self.a["qLampIn"]
        )

        # NIR from the interlights absorbed by the floor [W m^{-2}]
        # Equation 7.21 [7]
        self.a["rNirIntLampFlr"] = (
            self.p["fIntLampDown"]
            * (1 - self.p["rhoFlrNir"])
            * np.exp(-self.p["kIntNir"] * self.a["lai"] * self.p["vIntLampPos"])
            * self.p["etaIntLampNir"]
            * self.a["qIntLampIn"]
        )

        # PAR from the sun absorbed by the floor [W m^{-2}]
        # Equation 34 [1]
        self.a["rParSunFlr"] = (
            (1 - self.p["rhoFlrPar"]) * np.exp(-self.p["k1Par"] * self.a["lai"]) * self.a["rParGhSun"]
        )

        # PAR from the lamps absorbed by the floor [W m^{-2}]
        # Equation A21 [5]
        self.a["rParLampFlr"] = (
            (1 - self.p["rhoFlrPar"]) * np.exp(-self.p["k1Par"] * self.a["lai"]) * self.a["rParGhLamp"]
        )

        # PAR from the interlights absorbed by the floor [W m^{-2}]
        # Equation 7.17 [7]
        self.a["rParIntLampFlr"] = (
            self.a["rParGhIntLamp"]
            * self.p["fIntLampDown"]
            * (1 - self.p["rhoFlrPar"])
            * np.exp(-self.p["k1IntPar"] * self.a["lai"] * self.p["vIntLampPos"])
        )

        # PAR and NIR from the lamps absorbed by the greenhouse air [W m^{-2}]
        # Equation A23 [5]
        self.a["rLampAir"] = (
            (self.p["etaLampPar"] + self.p["etaLampNir"]) * self.a["qLampIn"]
            - self.a["rParLampCan"]
            - self.a["rNirLampCan"]
            - self.a["rParLampFlr"]
            - self.a["rNirLampFlr"]
        )

        # PAR and NIR from the interlights absorbed by the greenhouse air [W m^{-2}]
        # Equation 7.22 [7]
        self.a["rIntLampAir"] = (
            (self.p["etaIntLampPar"] + self.p["etaIntLampNir"]) * self.a["qIntLampIn"]
            - self.a["rParIntLampCan"]
            - self.a["rNirIntLampCan"]
            - self.a["rParIntLampFlr"]
            - self.a["rNirIntLampFlr"]
        )

        # Global radiation from the sun absorbed by the greenhouse air [W m^{-2}]
        # Equation 35 [1]
        self.a["rGlobSunAir"] = (
            self.p["etaGlobAir"]
            * self.d["iGlob"]
            * (
                self.a["tauCovPar"] * self.p["etaGlobPar"]
                + (self.a["aCanNir"] + self.a["aFlrNir"]) * self.p["etaGlobNir"]
            )
        )

        # Global radiation from the sun absorbed by the cover [W m^{-2}]
        # Equation 36 [1]
        self.a["rGlobSunCovE"] = (
            self.a["aCovPar"] * self.p["etaGlobPar"] + self.a["aCovNir"] * self.p["etaGlobNir"]
        ) * self.d["iGlob"]

    def set_fir_heat_fluxes(self):
        """
        Set FIR heat fluxes.
        Reference: Section 5.2 [1]
        """
        # FIR transmission coefficient of the thermal screen
        # Equation 38 [1]
        self.a["tauThScrFirU"] = 1 - self.u["thScr"] * (1 - self.p["tauThScrFir"])

        # FIR transmission coefficient of the blackout screen
        self.a["tauBlScrFirU"] = 1 - self.u["blScr"] * (1 - self.p["tauBlScrFir"])

        # Surface of canopy per floor area [-]
        # Table 3 [1]
        self.a["aCan"] = 1 - np.exp(-self.p["kFir"] * self.a["lai"])

        # FIR between canopy and cover [W m^{-2}]
        self.a["rCanCovIn"] = fir(
            self.a["aCan"],
            self.p["epsCan"],
            self.a["epsCovFir"],
            self.p["tauLampFir"] * self.a["tauThScrFirU"] * self.a["tauBlScrFirU"],
            self.x["tCan"],
            self.x["tCovIn"],
        )

        # FIR between canopy and sky [W m^{-2}]
        self.a["rCanSky"] = fir(
            self.a["aCan"],
            self.p["epsCan"],
            self.p["epsSky"],
            self.p["tauLampFir"] * self.a["tauCovFir"] * self.a["tauThScrFirU"] * self.a["tauBlScrFirU"],
            self.x["tCan"],
            self.d["tSky"],
        )

        # FIR between canopy and thermal screen [W m^{-2}]
        self.a["rCanThScr"] = fir(
            self.a["aCan"],
            self.p["epsCan"],
            self.p["epsThScrFir"],
            self.p["tauLampFir"] * self.u["thScr"] * self.a["tauBlScrFirU"],
            self.x["tCan"],
            self.x["tThScr"],
        )

        # FIR between canopy and floor [W m^{-2}]
        self.a["rCanFlr"] = fir(
            self.a["aCan"],
            self.p["epsCan"],
            self.p["epsFlr"],
            self.p["fCanFlr"],
            self.x["tCan"],
            self.x["tFlr"],
        )

        # FIR between pipes and cover [W m^{-2}]
        self.a["rPipeCovIn"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.a["epsCovFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * 0.49
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tPipe"],
            self.x["tCovIn"],
        )

        # FIR between pipes and sky [W m^{-2}]
        self.a["rPipeSky"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.p["epsSky"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.a["tauCovFir"]
            * self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * 0.49
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tPipe"],
            self.d["tSky"],
        )

        # FIR between pipes and thermal screen [W m^{-2}]
        self.a["rPipeThScr"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.p["epsThScrFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.u["thScr"]
            * self.a["tauBlScrFirU"]
            * 0.49
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tPipe"],
            self.x["tThScr"],
        )

        # FIR between pipes and floor [W m^{-2}]
        self.a["rPipeFlr"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.p["epsFlr"],
            0.49,
            self.x["tPipe"],
            self.x["tFlr"],
        )

        # FIR between pipes and canopy [W m^{-2}]
        self.a["rPipeCan"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.p["epsCan"],
            0.49 * (1 - np.exp(-self.p["kFir"] * self.a["lai"])),
            self.x["tPipe"],
            self.x["tCan"],
        )

        # FIR between floor and cover [W m^{-2}]
        self.a["rFlrCovIn"] = fir(
            1,
            self.p["epsFlr"],
            self.a["epsCovFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"])
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tFlr"],
            self.x["tCovIn"],
        )

        # FIR between floor and sky [W m^{-2}]
        self.a["rFlrSky"] = fir(
            1,
            self.p["epsFlr"],
            self.p["epsSky"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.a["tauCovFir"]
            * self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"])
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tFlr"],
            self.d["tSky"],
        )

        # FIR between floor and thermal screen [W m^{-2}]
        self.a["rFlrThScr"] = fir(
            1,
            self.p["epsFlr"],
            self.p["epsThScrFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.u["thScr"]
            * self.a["tauBlScrFirU"]
            * (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"])
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tFlr"],
            self.x["tThScr"],
        )

        # FIR between thermal screen and cover [W m^{-2}]
        self.a["rThScrCovIn"] = fir(
            1,
            self.p["epsThScrFir"],
            self.a["epsCovFir"],
            self.u["thScr"],
            self.x["tThScr"],
            self.x["tCovIn"],
        )

        # FIR between thermal screen and sky [W m^{-2}]
        self.a["rThScrSky"] = fir(
            1,
            self.p["epsThScrFir"],
            self.p["epsSky"],
            self.a["tauCovFir"] * self.u["thScr"],
            self.x["tThScr"],
            self.d["tSky"],
        )

        # FIR between cover and sky [W m^{-2}]
        self.a["rCovESky"] = fir(1, self.a["aCovFir"], self.p["epsSky"], 1, self.x["tCovE"], self.d["tSky"])

        # FIR between lamps and floor [W m^{-2}]
        self.a["rFirLampFlr"] = fir(
            self.p["aLamp"],
            self.p["epsLampBottom"],
            self.p["epsFlr"],
            self.p["tauIntLampFir"]
            * (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"])
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tLamp"],
            self.x["tFlr"],
        )

        # FIR between lamps and pipe [W m^{-2}]
        self.a["rLampPipe"] = fir(
            self.p["aLamp"],
            self.p["epsLampBottom"],
            self.p["epsPipe"],
            self.p["tauIntLampFir"]
            * 0.49
            * np.pi
            * self.p["lPipe"]
            * self.p["phiPipeE"]
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tLamp"],
            self.x["tPipe"],
        )

        # FIR between lamps and canopy [W m^{-2}]
        self.a["rFirLampCan"] = fir(
            self.p["aLamp"],
            self.p["epsLampBottom"],
            self.p["epsCan"],
            self.a["aCan"],
            self.x["tLamp"],
            self.x["tCan"],
        )

        # FIR between lamps and thermal screen [W m^{-2}]
        self.a["rLampThScr"] = fir(
            self.p["aLamp"],
            self.p["epsLampTop"],
            self.p["epsThScrFir"],
            self.u["thScr"] * self.a["tauBlScrFirU"],
            self.x["tLamp"],
            self.x["tThScr"],
        )

        # FIR between lamps and cover [W m^{-2}]
        self.a["rLampCovIn"] = fir(
            self.p["aLamp"],
            self.p["epsLampTop"],
            self.a["epsCovFir"],
            self.a["tauThScrFirU"] * self.a["tauBlScrFirU"],
            self.x["tLamp"],
            self.x["tCovIn"],
        )

        # FIR between lamps and sky [W m^{-2}]
        self.a["rLampSky"] = fir(
            self.p["aLamp"],
            self.p["epsLampTop"],
            self.p["epsSky"],
            self.a["tauCovFir"] * self.a["tauThScrFirU"] * self.a["tauBlScrFirU"],
            self.x["tLamp"],
            self.d["tSky"],
        )

        # FIR between grow pipes and canopy [W m^{-2}]
        self.a["rGroPipeCan"] = fir(
            self.p["aGroPipe"],
            self.p["epsGroPipe"],
            self.p["epsCan"],
            1,
            self.x["tGroPipe"],
            self.x["tCan"],
        )

        # FIR between blackout screen and floor [W m^{-2}]
        self.a["rFlrBlScr"] = fir(
            1,
            self.p["epsFlr"],
            self.p["epsBlScrFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.u["blScr"]
            * (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"])
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tFlr"],
            self.x["tBlScr"],
        )

        # FIR between blackout screen and pipe [W m^{-2}]
        self.a["rPipeBlScr"] = fir(
            self.p["aPipe"],
            self.p["epsPipe"],
            self.p["epsBlScrFir"],
            self.p["tauIntLampFir"]
            * self.p["tauLampFir"]
            * self.u["blScr"]
            * 0.49
            * np.exp(-self.p["kFir"] * self.a["lai"]),
            self.x["tPipe"],
            self.x["tBlScr"],
        )

        # FIR between blackout screen and canopy [W m^{-2}]
        self.a["rCanBlScr"] = fir(
            self.a["aCan"],
            self.p["epsCan"],
            self.p["epsBlScrFir"],
            self.p["tauLampFir"] * self.u["blScr"],
            self.x["tCan"],
            self.x["tBlScr"],
        )

        # FIR between blackout screen and thermal screen [W m^{-2}]
        self.a["rBlScrThScr"] = fir(
            self.u["blScr"],
            self.p["epsBlScrFir"],
            self.p["epsThScrFir"],
            self.u["thScr"],
            self.x["tBlScr"],
            self.x["tThScr"],
        )

        # FIR between blackout screen and cover [W m^{-2}]
        self.a["rBlScrCovIn"] = fir(
            self.u["blScr"],
            self.p["epsBlScrFir"],
            self.a["epsCovFir"],
            self.a["tauThScrFirU"],
            self.x["tBlScr"],
            self.x["tCovIn"],
        )

        # FIR between blackout screen and sky [W m^{-2}]
        self.a["rBlScrSky"] = fir(
            self.u["blScr"],
            self.p["epsBlScrFir"],
            self.p["epsSky"],
            self.a["tauCovFir"] * self.a["tauThScrFirU"],
            self.x["tBlScr"],
            self.d["tSky"],
        )

        # FIR between blackout screen and lamps [W m^{-2}]
        self.a["rLampBlScr"] = fir(
            self.p["aLamp"],
            self.p["epsLampTop"],
            self.p["epsBlScrFir"],
            self.u["blScr"],
            self.x["tLamp"],
            self.x["tBlScr"],
        )

        # Fraction of radiation going up from the interlight to the canopy [-]
        # Equation 7.29 [7]
        self.a["fIntLampCanUp"] = 1 - np.exp(-self.p["kIntFir"] * (1 - self.p["vIntLampPos"]) * self.a["lai"])

        # Fraction of radiation going down from the interlight to the canopy [-]
        # Equation 7.30 [7]
        self.a["fIntLampCanDown"] = 1 - np.exp(-self.p["kIntFir"] * self.p["vIntLampPos"] * self.a["lai"])

        # FIR between interlights and floor [W m^{-2}]
        self.a["rFirIntLampFlr"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsFlr"],
            (1 - 0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"]) * (1 - self.a["fIntLampCanDown"]),
            self.x["tIntLamp"],
            self.x["tFlr"],
        )

        # FIR between interlights and pipe [W m^{-2}]
        self.a["rIntLampPipe"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsPipe"],
            0.49 * np.pi * self.p["lPipe"] * self.p["phiPipeE"] * (1 - self.a["fIntLampCanDown"]),
            self.x["tIntLamp"],
            self.x["tPipe"],
        )

        # FIR between interlights and canopy [W m^{-2}]
        self.a["rFirIntLampCan"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsCan"],
            self.a["fIntLampCanDown"] + self.a["fIntLampCanUp"],
            self.x["tIntLamp"],
            self.x["tCan"],
        )

        # FIR between interlights and toplights [W m^{-2}]
        self.a["rIntLampLamp"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsLampBottom"],
            (1 - self.a["fIntLampCanUp"]) * self.p["aLamp"],
            self.x["tIntLamp"],
            self.x["tLamp"],
        )

        # FIR between interlights and blackout screen [W m^{-2}]
        self.a["rIntLampBlScr"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsBlScrFir"],
            self.u["blScr"] * self.p["tauLampFir"] * (1 - self.a["fIntLampCanUp"]),
            self.x["tIntLamp"],
            self.x["tBlScr"],
        )

        # FIR between interlights and thermal screen [W m^{-2}]
        self.a["rIntLampThScr"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsThScrFir"],
            self.u["thScr"] * self.a["tauBlScrFirU"] * self.p["tauLampFir"] * (1 - self.a["fIntLampCanUp"]),
            self.x["tIntLamp"],
            self.x["tThScr"],
        )

        # FIR between interlights and cover [W m^{-2}]
        self.a["rIntLampCovIn"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.a["epsCovFir"],
            self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * self.p["tauLampFir"]
            * (1 - self.a["fIntLampCanUp"]),
            self.x["tIntLamp"],
            self.x["tCovIn"],
        )

        # FIR between interlights and sky [W m^{-2}]
        self.a["rIntLampSky"] = fir(
            self.p["aIntLamp"],
            self.p["epsIntLamp"],
            self.p["epsSky"],
            self.a["tauCovFir"]
            * self.a["tauThScrFirU"]
            * self.a["tauBlScrFirU"]
            * self.p["tauLampFir"]
            * (1 - self.a["fIntLampCanUp"]),
            self.x["tIntLamp"],
            self.d["tSky"],
        )

        """
        Set natural ventilation parameters.
        Reference: Section 9.7 [1]
        """
        # Aperture of the roof [m^{2}]
        # Equation 67 [1]
        self.a["aRoofU"] = self.u["roof"] * self.p["aRoof"]
        self.a["aRoofUMax"] = self.p["aRoof"]
        self.a["aRoofMin"] = 0

        # Aperture of the sidewall [m^{2}]
        # Equation 68 [1]
        # (this is 0 in the Dutch greenhouse)
        self.a["aSideU"] = self.u["side"] * self.p["aSide"]

        # Ratio between roof vent area and total ventilation area [-]
        # (not very clear in the reference [1], but always 1 if self.a["aSideU"] == 0)
        self.a["etaRoof"] = 1
        self.a["etaRoofNoSide"] = 1

        # Ratio between side vent area and total ventilation area [-]
        # (not very clear in the reference [1], but always 0 if self.a["aSideU"] == 0)
        self.a["etaSide"] = 0

        # Discharge coefficient [-]
        # Equation 73 [1]
        self.a["cD"] = self.p["cDgh"] * (1 - self.p["etaShScrCd"] * self.u["shScr"])

        # Discharge coefficient [-]
        # Equation 74 [1]
        self.a["cW"] = self.p["cWgh"] * (1 - self.p["etaShScrCw"] * self.u["shScr"])

        # Natural ventilation rate due to roof ventilation [m^{3} m^{-2} s^{-1}]
        # Equation 64 [1]
        self.a["fVentRoof2"] = (
            self.u["roof"]
            * self.p["aRoof"]
            * self.a["cD"]
            / (2 * self.p["aFlr"])
            * np.sqrt(
                abs(
                    self.p["g"]
                    * self.p["hVent"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (2 * (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15))
                    + self.a["cW"] * self.d["wind"] ** 2
                )
            )
        )
        self.a["fVentRoof2Max"] = (
            self.p["aRoof"]
            * self.a["cD"]
            / (2 * self.p["aFlr"])
            * np.sqrt(
                abs(
                    self.p["g"]
                    * self.p["hVent"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (2 * (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15))
                    + self.a["cW"] * self.d["wind"] ** 2
                )
            )
        )
        self.a["fVentRoof2Min"] = 0

        # Ventilation rate through roof and side vents [m^{3} m^{-2} s^{-1}]
        # Equation 65 [1]
        self.a["fVentRoofSide2"] = (
            self.a["cD"]
            / self.p["aFlr"]
            * np.sqrt(
                (
                    self.a["aRoofU"]
                    * self.a["aSideU"]
                    / np.sqrt(np.maximum(self.a["aRoofU"] ** 2 + self.a["aSideU"] ** 2, 0.01))
                )
                ** 2
                * (
                    2
                    * self.p["g"]
                    * self.p["hSideRoof"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15)
                )
                + ((self.a["aRoofU"] + self.a["aSideU"]) / 2) ** 2 * self.a["cW"] * self.d["wind"] ** 2
            )
        )

        # Ventilation rate through sidewall only [m^{3} m^{-2} s^{-1}]
        # Equation 66 [1]
        self.a["fVentSide2"] = (
            self.a["cD"] * self.a["aSideU"] * self.d["wind"] / (2 * self.p["aFlr"]) * np.sqrt(self.a["cW"])
        )

        # Leakage ventilation [m^{3} m^{-2} s^{-1}]
        # Equation 70 [1]
        self.a["fLeakage"] = ifElse(
            self.d["wind"] < self.p["minWind"],
            self.p["minWind"] * self.p["cLeakage"],
            self.p["cLeakage"] * self.d["wind"],
        )

        # Total ventilation through the roof [m^{3} m^{-2} s^{-1}]
        # Equation 71 [1], Equation A42 [5]
        self.a["fVentRoof"] = ifElse(
            self.a["etaRoof"] >= self.p["etaRoofThr"],
            self.p["etaInsScr"] * self.a["fVentRoof2"] + self.p["cLeakTop"] * self.a["fLeakage"],
            self.p["etaInsScr"]
            * (
                np.maximum(self.u["thScr"], self.u["blScr"]) * self.a["fVentRoof2"]
                + (1 - np.maximum(self.u["thScr"], self.u["blScr"]))
                * self.a["fVentRoofSide2"]
                * self.a["etaRoof"]
            )
            + self.p["cLeakTop"] * self.a["fLeakage"],
        )

        # Total ventilation through side vents [m^{3} m^{-2} s^{-1}]
        # Equation 72 [1], Equation A43 [5]
        self.a["fVentSide"] = ifElse(
            self.a["etaRoof"] >= self.p["etaRoofThr"],
            self.p["etaInsScr"] * self.a["fVentSide2"] + (1 - self.p["cLeakTop"]) * self.a["fLeakage"],
            self.p["etaInsScr"]
            * (
                np.maximum(self.u["thScr"], self.u["blScr"]) * self.a["fVentSide2"]
                + (1 - np.maximum(self.u["thScr"], self.u["blScr"]))
                * self.a["fVentRoofSide2"]
                * self.a["etaSide"]
            )
            + (1 - self.p["cLeakTop"]) * self.a["fLeakage"],
        )
  
    def set_natural_ventilation(self):
        """
        Set natural ventilation parameters.
        Reference: Section 9.7 [1]
        """
        # Aperture of the roof [m^{2}]
        # Equation 67 [1]
        self.a["aRoofU"] = self.u["roof"] * self.p["aRoof"]
        self.a["aRoofUMax"] = self.p["aRoof"]
        self.a["aRoofMin"] = 0

        # Aperture of the sidewall [m^{2}]
        # Equation 68 [1]
        # (this is 0 in the Dutch greenhouse)
        self.a["aSideU"] = self.u["side"] * self.p["aSide"]

        # Ratio between roof vent area and total ventilation area [-]
        # (not very clear in the reference [1], but always 1 if self.a["aSideU"] == 0)
        self.a["etaRoof"] = 1
        self.a["etaRoofNoSide"] = 1

        # Ratio between side vent area and total ventilation area [-]
        # (not very clear in the reference [1], but always 0 if self.a["aSideU"] == 0)
        self.a["etaSide"] = 0

        # Discharge coefficient [-]
        # Equation 73 [1]
        self.a["cD"] = self.p["cDgh"] * (1 - self.p["etaShScrCd"] * self.u["shScr"])

        # Discharge coefficient [-]
        # Equation 74 [1]
        self.a["cW"] = self.p["cWgh"] * (1 - self.p["etaShScrCw"] * self.u["shScr"])

        # Natural ventilation rate due to roof ventilation [m^{3} m^{-2} s^{-1}]
        # Equation 64 [1]
        self.a["fVentRoof2"] = (
            self.u["roof"]
            * self.p["aRoof"]
            * self.a["cD"]
            / (2 * self.p["aFlr"])
            * np.sqrt(
                abs(
                    self.p["g"]
                    * self.p["hVent"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (2 * (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15))
                    + self.a["cW"] * self.d["wind"] ** 2
                )
            )
        )
        self.a["fVentRoof2Max"] = (
            self.p["aRoof"]
            * self.a["cD"]
            / (2 * self.p["aFlr"])
            * np.sqrt(
                abs(
                    self.p["g"]
                    * self.p["hVent"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (2 * (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15))
                    + self.a["cW"] * self.d["wind"] ** 2
                )
            )
        )
        self.a["fVentRoof2Min"] = 0

        # Ventilation rate through roof and side vents [m^{3} m^{-2} s^{-1}]
        # Equation 65 [1]
        self.a["fVentRoofSide2"] = (
            self.a["cD"]
            / self.p["aFlr"]
            * np.sqrt(
                (
                    self.a["aRoofU"]
                    * self.a["aSideU"]
                    / np.sqrt(np.maximum(self.a["aRoofU"] ** 2 + self.a["aSideU"] ** 2, 0.01))
                )
                ** 2
                * (
                    2
                    * self.p["g"]
                    * self.p["hSideRoof"]
                    * (self.x["tAir"] - self.d["tOut"])
                    / (0.5 * self.x["tAir"] + 0.5 * self.d["tOut"] + 273.15)
                )
                + ((self.a["aRoofU"] + self.a["aSideU"]) / 2) ** 2 * self.a["cW"] * self.d["wind"] ** 2
            )
        )

        # Ventilation rate through sidewall only [m^{3} m^{-2} s^{-1}]
        # Equation 66 [1]
        self.a["fVentSide2"] = (
            self.a["cD"] * self.a["aSideU"] * self.d["wind"] / (2 * self.p["aFlr"]) * np.sqrt(self.a["cW"])
        )

        # Leakage ventilation [m^{3} m^{-2} s^{-1}]
        # Equation 70 [1]
        self.a["fLeakage"] = ifElse(
            self.d["wind"] < self.p["minWind"],
            self.p["minWind"] * self.p["cLeakage"],
            self.p["cLeakage"] * self.d["wind"],
        )

        # Total ventilation through the roof [m^{3} m^{-2} s^{-1}]
        # Equation 71 [1], Equation A42 [5]
        self.a["fVentRoof"] = ifElse(
            self.a["etaRoof"] >= self.p["etaRoofThr"],
            self.p["etaInsScr"] * self.a["fVentRoof2"] + self.p["cLeakTop"] * self.a["fLeakage"],
            self.p["etaInsScr"]
            * (
                np.maximum(self.u["thScr"], self.u["blScr"]) * self.a["fVentRoof2"]
                + (1 - np.maximum(self.u["thScr"], self.u["blScr"]))
                * self.a["fVentRoofSide2"]
                * self.a["etaRoof"]
            )
            + self.p["cLeakTop"] * self.a["fLeakage"],
        )

        # Total ventilation through side vents [m^{3} m^{-2} s^{-1}]
        # Equation 72 [1], Equation A43 [5]
        self.a["fVentSide"] = ifElse(
            self.a["etaRoof"] >= self.p["etaRoofThr"],
            self.p["etaInsScr"] * self.a["fVentSide2"] + (1 - self.p["cLeakTop"]) * self.a["fLeakage"],
            self.p["etaInsScr"]
            * (
                np.maximum(self.u["thScr"], self.u["blScr"]) * self.a["fVentSide2"]
                + (1 - np.maximum(self.u["thScr"], self.u["blScr"]))
                * self.a["fVentRoofSide2"]
                * self.a["etaSide"]
            )
            + (1 - self.p["cLeakTop"]) * self.a["fLeakage"],
        )
    
    def set_control_rules(self):
        """
        Set control rules for the greenhouse system.
        """

        # Hours since midnight [h]
        # Calculated based on the current time in the system
        self.a["timeOfDay"] = 24 * (self.x["time"] - np.floor(self.x["time"]))

        # Day of year [d]
        # Calculated based on the current time in the system
        self.a["dayOfYear"] = np.mod(self.x["time"], 365.2425)

        # Control of the lamp according to the time of day [0/1]
        # Determines if the lamps should be on based on the time of day
        cond1 = np.logical_and(
            self.p["lampsOn"] <= self.p["lampsOff"],
            np.logical_and(
                self.p["lampsOn"] < self.a["timeOfDay"],
                self.a["timeOfDay"] < self.p["lampsOff"],
            ),
        )

        cond2 = np.logical_not(self.p["lampsOn"] <= self.p["lampsOff"])
        cond3 = np.logical_or(
            self.p["lampsOn"] < self.a["timeOfDay"],
            self.a["timeOfDay"] < self.p["lampsOff"],
        )

        self.a["lampTimeOfDay"] = (cond1 + cond2 * cond3) * 1

        # Control of the lamp according to the day of year [0/1]
        # Determines if the lamps should be on based on the day of the year
        cond1 = np.logical_and(
            self.p["dayLampStart"] <= self.p["dayLampStop"],
            np.logical_and(
                self.p["dayLampStart"] < self.a["dayOfYear"],
                self.a["dayOfYear"] < self.p["dayLampStop"],
            ),
        )

        cond2 = np.logical_not(self.p["dayLampStart"] <= self.p["dayLampStop"])
        cond3 = np.logical_or(
            self.p["dayLampStart"] < self.a["dayOfYear"],
            self.a["dayOfYear"] < self.p["dayLampStop"],
        )

        self.a["lampDayOfYear"] = (cond1 + cond2 * cond3) * 1

        # Control for the lamps disregarding temperature and humidity constraints
        # Determines if the lamps should be on based on global radiation and daily radiation sum
        self.a["lampNoCons"] = (
            1
            * (self.d["iGlob"] < self.p["lampsOffSun"])
            * (self.d["dayRadSum"] < self.p["lampRadSumLimit"])
            * self.a["lampTimeOfDay"]
            * self.a["lampDayOfYear"]
        )

        ## Smoothing of control of the lamps
        # Linear version of lamp switching on
        self.a["linearLampSwitchOn"] = np.maximum(0, np.minimum(1, self.a["timeOfDay"] - self.p["lampsOn"] + 1))

        # Linear version of lamp switching off
        self.a["linearLampSwitchOff"] = np.maximum(0, np.minimum(1, self.p["lampsOff"] - self.a["timeOfDay"] + 1))

        # Combination of linear transitions above
        self.a["linearLampBothSwitches"] = (self.p["lampsOn"] != self.p["lampsOff"]) * (
            (self.p["lampsOn"] < self.p["lampsOff"])
            * np.minimum(self.a["linearLampSwitchOn"], self.a["linearLampSwitchOff"])
            + (1 - (self.p["lampsOn"] < self.p["lampsOff"]))
            * np.maximum(self.a["linearLampSwitchOn"], self.a["linearLampSwitchOff"])
        )

        # Smooth (linear) approximation of the lamp control
        # Allows smooth transition between light period and dark period setpoints
        self.a["smoothLamp"] = (
            self.a["linearLampBothSwitches"]
            * (self.d["dayRadSum"] < self.p["lampRadSumLimit"])
            * self.a["lampDayOfYear"]
        )

        # Indicates whether daytime climate settings should be used
        # 1 if day, 0 if night. If lamps are on it is considered day
        self.a["isDayInside"] = np.maximum(self.a["smoothLamp"], self.d["isDay"])

        # Decision on whether mechanical cooling and dehumidification is allowed to work
        # (0 - not allowed, 1 - allowed)
        self.a["mechAllowed"] = 0

        # Decision on whether heating from buffer is allowed to run
        # (0 - not allowed, 1 - allowed)
        self.a["hotBufAllowed"] = 0

        # Heating set point [°C]
        self.a["heatSetPoint"] = (
            self.a["isDayInside"] * self.p["tSpDay"]
            + (1 - self.a["isDayInside"]) * self.p["tSpNight"]
            + self.p["heatCorrection"] * self.a["lampNoCons"]
        )

        # Ventilation setpoint due to excess heating set point [°C]
        self.a["heatMax"] = self.a["heatSetPoint"] + self.p["heatDeadZone"]

        # CO2 set point [ppm]
        self.a["co2SetPoint"] = self.a["isDayInside"] * self.p["co2SpDay"]

        # CO2 concentration in main compartment [ppm]
        self.a["co2InPpm"] = co2_dens2ppm(self.x["tAir"], 1e-6 * self.x["co2Air"])

        # Ventilation due to excess heat [0-1, 0 means vents are closed]
        self.a["ventHeat"] = proportionalControl(
            self.x["tAir"], self.a["heatMax"], self.p["ventHeatPband"], 0, 1
        )

        # Relative humidity [#]
        if satVp(self.x["tAir"]) == 0:
            self.a["rhIn"] = 100
        else:
            self.a["rhIn"] = 100 * self.x["vpAir"] / satVp(self.x["tAir"])

        # Ventilation due to excess humidity [0-1, 0 means vents are closed]
        self.a["ventRh"] = proportionalControl(
            self.a["rhIn"],
            self.p["rhMax"] + self.a["mechAllowed"] * self.p["mechDehumidPband"],
            self.p["ventRhPband"],
            0,
            1,
        )

        # Ventilation closure due to too cold temperatures [0-1, 0 means vents are closed]
        self.a["ventCold"] = proportionalControl(
            self.x["tAir"],
            self.a["heatSetPoint"] - self.p["tVentOff"],
            self.p["ventColdPband"],
            1,
            0,
        )

        # Setpoint for closing the thermal screen [°C]
        self.a["thScrSp"] = self.d["isDay"] * self.p["thScrSpDay"] + (1 - self.d["isDay"]) * self.p["thScrSpNight"]

        # Closure of the thermal screen based on outdoor temperature [0-1, 0 is fully open]
        self.a["thScrCold"] = proportionalControl(self.d["tOut"], self.a["thScrSp"], self.p["thScrPband"], 0, 1)

        # Opening of thermal screen closure due to too high temperatures
        self.a["thScrHeat"] = proportionalControl(
            self.x["tAir"],
            self.a["heatSetPoint"] + self.p["thScrDeadZone"],
            -self.p["thScrPband"],
            1,
            0,
        )

        # Opening of thermal screen due to high humidity [0-1, 0 is fully open]
        self.a["thScrRh"] = np.maximum(
            proportionalControl(
                self.a["rhIn"],
                self.p["rhMax"] + self.p["thScrRh"],
                self.p["thScrRhPband"],
                1,
                0,
            ),
            1 - self.a["ventCold"],
        )

        # Control for the top lights [0/1]
        self.a["lampOn"] = (
            self.a["lampNoCons"]
            * proportionalControl(self.x["tAir"], self.a["heatMax"] + self.p["lampExtraHeat"], -0.5, 0, 1)
            * (
                self.d["isDaySmooth"]
                + (1 - self.d["isDaySmooth"])
                * np.maximum(
                    proportionalControl(
                        self.a["rhIn"],
                        self.p["rhMax"] + self.p["blScrExtraRh"],
                        -0.5,
                        0,
                        1,
                    ),
                    1 - self.a["ventCold"],
                )
            )
        )

        # Control for the interlights [0/1]
        self.a["intLampOn"] = (
            self.a["lampNoCons"]
            * proportionalControl(self.x["tAir"], self.a["heatMax"] + self.p["lampExtraHeat"], -0.5, 0, 1)
            * (
                self.d["isDaySmooth"]
                + (1 - self.d["isDaySmooth"])
                * np.maximum(
                    proportionalControl(
                        self.a["rhIn"],
                        self.p["rhMax"] + self.p["blScrExtraRh"],
                        -0.5,
                        0,
                        1,
                    ),
                    1 - self.a["ventCold"],
                )
            )
        )

    def set_convection_conduction(self):
        """
        Set convection and conduction parameters for the greenhouse system.
        """

        ## Convection and conduction - Section 5.3 [1] 

        # Density of air as it depends on pressure and temperature
        # Calculated based on the ideal gas law
        self.a["rhoTop"] = self.p["mAir"] * self.p["pressure"] / ((self.x["tTop"] + 273.15) * self.p["R"])
        self.a["rhoAir"] = self.p["mAir"] * self.p["pressure"] / ((self.x["tAir"] + 273.15) * self.p["R"])

        # Mean density of air beneath and above the screen
        # Note: a mistake in [1] where it says rhoAirMean is the mean density "of the greenhouse and the outdoor air".
        self.a["rhoAirMean"] = 0.5 * (self.a["rhoTop"] + self.a["rhoAir"])

        # Air flux through the thermal screen [m s^{-1}]
        # Equation 40 [1], Equation A36 [5]
        # Correcting mistakes in [1] and [4] regarding the usage of tTop and rhoTop
        self.a["fThScr"] = self.u["thScr"] * self.p["kThScr"] * (abs((self.x["tAir"] - self.x["tTop"])) ** 0.66) + (
            (1 - self.u["thScr"]) / self.a["rhoAirMean"]
        ) * np.sqrt(
            0.5
            * self.a["rhoAirMean"]
            * (1 - self.u["thScr"])
            * self.p["g"]
            * abs(self.a["rhoAir"] - self.a["rhoTop"])
        )

        # Air flux through the blackout screen [m s^{-1}]
        # Equation A37 [5]
        self.a["fBlScr"] = self.u["blScr"] * self.p["kBlScr"] * (abs((self.x["tAir"] - self.x["tTop"])) ** 0.66) + (
            (1 - self.u["blScr"]) / self.a["rhoAirMean"]
        ) * np.sqrt(
            0.5
            * self.a["rhoAirMean"]
            * (1 - self.u["blScr"])
            * self.p["g"]
            * abs(self.a["rhoAir"] - self.a["rhoTop"])
        )

        # Air flux through the screens [m s^{-1}]
        # Equation A38 [5]
        self.a["fScr"] = np.minimum(self.a["fThScr"], self.a["fBlScr"])

    def set_convective_conductive_heat_fluxes(self):
        """
        Set convective and conductive heat flux parameters for the greenhouse system.
        """

        ## Convective and conductive heat fluxes [W m^{-2}]
        # Table 4 [1]

        # Forced ventilation (doesn't exist in current greenhouse)
        self.a["fVentForced"] = 0

        # Heat flux between canopy and air in main compartment [W m^{-2}]
        self.a["hCanAir"] = sensible(2 * self.p["alfaLeafAir"] * self.a["lai"], self.x["tCan"], self.x["tAir"])

        # Heat flux between air in main compartment and floor [W m^{-2}]
        self.a["hAirFlr"] = sensible(
            ifElse(
                self.x["tFlr"] > self.x["tAir"],
                1.7 * nthroot(abs(self.x["tFlr"] - self.x["tAir"]), 3),
                1.3 * nthroot(abs(self.x["tAir"] - self.x["tFlr"]), 4),
            ),
            self.x["tAir"],
            self.x["tFlr"],
        )

        # Heat flux between air in main compartment and thermal screen [W m^{-2}]
        self.a["hAirThScr"] = sensible(
            1.7 * self.u["thScr"] * nthroot(abs(self.x["tAir"] - self.x["tThScr"]), 3),
            self.x["tAir"],
            self.x["tThScr"],
        )

        # Heat flux between air in main compartment and blackout screen [W m^{-2}]
        self.a["hAirBlScr"] = sensible(
            1.7 * self.u["blScr"] * nthroot(abs(self.x["tAir"] - self.x["tBlScr"]), 3),
            self.x["tAir"],
            self.x["tBlScr"],
        )

        # Heat flux between air in main compartment and outside air [W m^{-2}]
        self.a["hAirOut"] = sensible(
            self.p["rhoAir"] * self.p["cPAir"] * (self.a["fVentSide"] + self.a["fVentForced"]),
            self.x["tAir"],
            self.d["tOut"],
        )

        # Heat flux between air in main and top compartment [W m^{-2}]
        self.a["hAirTop"] = sensible(
            self.p["rhoAir"] * self.p["cPAir"] * self.a["fScr"],
            self.x["tAir"],
            self.x["tTop"],
        )

        # Heat flux between thermal screen and top compartment [W m^{-2}]
        self.a["hThScrTop"] = sensible(
            1.7 * self.u["thScr"] * nthroot(abs(self.x["tThScr"] - self.x["tTop"]), 3),
            self.x["tThScr"],
            self.x["tTop"],
        )

        # Heat flux between blackout screen and top compartment [W m^{-2}]
        self.a["hBlScrTop"] = sensible(
            1.7 * self.u["blScr"] * nthroot(abs(self.x["tBlScr"] - self.x["tTop"]), 3),
            self.x["tBlScr"],
            self.x["tTop"],
        )

        # Heat flux between top compartment and cover [W m^{-2}]
        self.a["hTopCovIn"] = sensible(
            self.p["cHecIn"] * nthroot(abs(self.x["tTop"] - self.x["tCovIn"]), 3) * self.p["aCov"] / self.p["aFlr"],
            self.x["tTop"],
            self.x["tCovIn"],
        )

        # Heat flux between top compartment and outside air [W m^{-2}]
        self.a["hTopOut"] = sensible(
            self.p["rhoAir"] * self.p["cPAir"] * self.a["fVentRoof"],
            self.x["tTop"],
            self.d["tOut"],
        )

        # Heat flux between cover and outside air [W m^{-2}]
        self.a["hCovEOut"] = sensible(
            self.p["aCov"]
            / self.p["aFlr"]
            * (self.p["cHecOut1"] + self.p["cHecOut2"] * self.d["wind"] ** self.p["cHecOut3"]),
            self.x["tCovE"],
            self.d["tOut"],
        )

        # Heat flux between pipes and air in main compartment [W m^{-2}]
        self.a["hPipeAir"] = sensible(
            1.99 * np.pi * self.p["phiPipeE"] * self.p["lPipe"] * (abs(self.x["tPipe"] - self.x["tAir"])) ** 0.32,
            self.x["tPipe"],
            self.x["tAir"],
        )

        # Heat flux between floor and soil layer 1 [W m^{-2}]
        self.a["hFlrSo1"] = sensible(
            2 / (self.p["hFlr"] / self.p["lambdaFlr"] + self.p["hSo1"] / self.p["lambdaSo"]),
            self.x["tFlr"],
            self.x["tSo1"],
        )

        # Heat flux between soil layers 1 and 2 [W m^{-2}]
        self.a["hSo1So2"] = sensible(
            2 * self.p["lambdaSo"] / (self.p["hSo1"] + self.p["hSo2"]),
            self.x["tSo1"],
            self.x["tSo2"],
        )

        # Heat flux between soil layers 2 and 3 [W m^{-2}]
        self.a["hSo2So3"] = sensible(
            2 * self.p["lambdaSo"] / (self.p["hSo2"] + self.p["hSo3"]),
            self.x["tSo2"],
            self.x["tSo3"],
        )

        # Heat flux between soil layers 3 and 4 [W m^{-2}]
        self.a["hSo3So4"] = sensible(
            2 * self.p["lambdaSo"] / (self.p["hSo3"] + self.p["hSo4"]),
            self.x["tSo3"],
            self.x["tSo4"],
        )

        # Heat flux between soil layers 4 and 5 [W m^{-2}]
        self.a["hSo4So5"] = sensible(
            2 * self.p["lambdaSo"] / (self.p["hSo4"] + self.p["hSo5"]),
            self.x["tSo4"],
            self.x["tSo5"],
        )

        # Heat flux between soil layer 5 and the external soil temperature [W m^{-2}]
        # See Equations 4 and 77 [1]
        self.a["hSo5SoOut"] = sensible(
            2 * self.p["lambdaSo"] / (self.p["hSo5"] + self.p["hSoOut"]),
            self.x["tSo5"],
            self.d["tSoOut"],
        )

        # Conductive heat flux through the lumped cover [W K^{-1} m^{-2}]
        # See comment after Equation 18 [1]
        self.a["hCovInCovE"] = sensible(
            1
            / (
                self.p["hRf"] / self.p["lambdaRf"]
                + self.u["shScrPer"] * self.p["hShScrPer"] / self.p["lambdaShScrPer"]
            ),
            self.x["tCovIn"],
            self.x["tCovE"],
        )

        # Heat flux between lamps and air in main compartment [W m^{-2}]
        self.a["hLampAir"] = sensible(self.p["cHecLampAir"], self.x["tLamp"], self.x["tAir"])

        # Heat flux between grow pipes and air in main compartment [W m^{-2}]
        self.a["hGroPipeAir"] = sensible(
            1.99
            * np.pi
            * self.p["phiGroPipeE"]
            * self.p["lGroPipe"]
            * (abs(self.x["tGroPipe"] - self.x["tAir"])) ** 0.32,
            self.x["tGroPipe"],
            self.x["tAir"],
        )

        # Heat flux between interlights and air in main compartment [W m^{-2}]
        self.a["hIntLampAir"] = sensible(self.p["cHecIntLampAir"], self.x["tIntLamp"], self.x["tAir"])

    def set_canopy_transpiration(self):
        """
        Set canopy transpiration parameters for the greenhouse system.
        """

        ## Canopy transpiration - Section 8 [1]

        # Smooth switch between day and night [-]
        # Equation 50 [1]
        self.a["sRs"] = 1 / (1 + np.exp(self.p["sRs"] * (self.a["rCan"] - self.p["rCanSp"])))

        # Parameter for CO2 influence on stomatal resistance [ppm{CO2}^{-2}]
        # Equation 51 [1]
        self.a["cEvap3"] = self.p["cEvap3Night"] * (1 - self.a["sRs"]) + self.p["cEvap3Day"] * self.a["sRs"]

        # Parameter for vapor pressure influence on stomatal resistance [Pa^{-2}]
        self.a["cEvap4"] = self.p["cEvap4Night"] * (1 - self.a["sRs"]) + self.p["cEvap4Day"] * self.a["sRs"]

        # Radiation influence on stomatal resistance [-]
        # Equation 49 [1]
        self.a["rfRCan"] = (self.a["rCan"] + self.p["cEvap1"]) / (self.a["rCan"] + self.p["cEvap2"])

        # CO2 influence on stomatal resistance [-]
        # Equation 49 [1]
        self.a["rfCo2"] = np.minimum(
            1.5,
            1 + self.a["cEvap3"] * (self.p["etaMgPpm"] * self.x["co2Air"] - 200) ** 2,
        )
        # perhaps replace p["etaMgPpm"] * x["co2Air"] with a["co2InPpm"]

        # Vapor pressure influence on stomatal resistance [-]
        # Equation 49 [1]
        self.a["rfVp"] = np.minimum(5.8, 1 + self.a["cEvap4"] * (satVp(self.x["tCan"]) - self.x["vpAir"]) ** 2)

        # Stomatal resistance [s m^{-1}]
        # Equation 48 [1]
        self.a["rS"] = self.p["rSMin"] * self.a["rfRCan"] * self.a["rfCo2"] * self.a["rfVp"]

        # Vapor transfer coefficient of canopy transpiration [kg m^{-2} Pa^{-1} s^{-1}]
        # Equation 47 [1]
        self.a["vecCanAir"] = (
            2
            * self.p["rhoAir"]
            * self.p["cPAir"]
            * self.a["lai"]
            / (self.p["L"] * self.p["gamma"] * (self.p["rB"] + self.a["rS"]))
        )

        # Canopy transpiration [kg m^{-2} s^{-1}]
        # Equation 46 [1]
        self.a["mvCanAir"] = (satVp(self.x["tCan"]) - self.x["vpAir"]) * self.a["vecCanAir"]

    def set_vapor_fluxes(self):
        """
        Set vapor fluxes parameters for the greenhouse system.
        """

        ## Vapor fluxes - Section 6 [1]

        # Vapor fluxes currently not included in the model - set at 0
        self.a["mvPadAir"] = 0
        self.a["mvFogAir"] = 0
        self.a["mvBlowAir"] = 0
        self.a["mvAirOutPad"] = 0

        # Condensation from main compartment on thermal screen [kg m^{-2} s^{-1}]
        # Table 4 [1], Equation 42 [1]
        self.a["mvAirThScr"] = cond(
            1.7 * self.u["thScr"] * nthroot(abs(self.x["tAir"] - self.x["tThScr"]), 3),
            self.x["vpAir"],
            satVp(self.x["tThScr"]),
        )

        # Condensation from main compartment on blackout screen [kg m^{-2} s^{-1}]
        # Equation A39 [5], Equation 7.39 [7]
        self.a["mvAirBlScr"] = cond(
            1.7 * self.u["blScr"] * nthroot(abs(self.x["tAir"] - self.x["tBlScr"]), 3),
            self.x["vpAir"],
            satVp(self.x["tBlScr"]),
        )

        # Condensation from top compartment to cover [kg m^{-2} s^{-1}]
        # Table 4 [1]
        self.a["mvTopCovIn"] = cond(
            self.p["cHecIn"] * nthroot(abs(self.x["tTop"] - self.x["tCovIn"]), 3) * self.p["aCov"] / self.p["aFlr"],
            self.x["vpTop"],
            satVp(self.x["tCovIn"]),
        )

        # Vapor flux from main to top compartment [kg m^{-2} s^{-1}]
        self.a["mvAirTop"] = airMv(
            self.a["fScr"],
            self.x["vpAir"],
            self.x["vpTop"],
            self.x["tAir"],
            self.x["tTop"],
        )

        # Vapor flux from top compartment to outside [kg m^{-2} s^{-1}]
        self.a["mvTopOut"] = airMv(
            self.a["fVentRoof"],
            self.x["vpTop"],
            self.d["vpOut"],
            self.x["tTop"],
            self.d["tOut"],
        )

        # Vapor flux from main compartment to outside [kg m^{-2} s^{-1}]
        self.a["mvAirOut"] = airMv(
            self.a["fVentSide"] + self.a["fVentForced"],
            self.x["vpAir"],
            self.d["vpOut"],
            self.x["tAir"],
            self.d["tOut"],
        )

    def set_latent_heat_fluxes(self):
        """
        Set latent heat fluxes parameters for the greenhouse system.
        """

        ## Latent heat fluxes - Section 5.4 [1]

        # Latent heat flux by transpiration [W m^{-2}]
        self.a["lCanAir"] = self.p["L"] * self.a["mvCanAir"]

        # Latent heat flux by condensation on thermal screen [W m^{-2}]
        self.a["lAirThScr"] = self.p["L"] * self.a["mvAirThScr"]

        # Latent heat flux by condensation on blackout screen [W m^{-2}]
        self.a["lAirBlScr"] = self.p["L"] * self.a["mvAirBlScr"]

        # Latent heat flux by condensation on cover [W m^{-2}]
        self.a["lTopCovIn"] = self.p["L"] * self.a["mvTopCovIn"]
 
    def set_canopy_photosynthesis(self):
        """
        Set canopy photosynthesis parameters for the greenhouse system.
        """

        ## Canopy photosynthesis - Section 4.1 [2]

        # PAR absorbed by the canopy [umol{photons} m^{-2} s^{-1}]
        self.a["parCan"] = (
            self.p["zetaLampPar"] * self.a["rParLampCan"]
            + self.p["parJtoUmolSun"] * self.a["rParSunCan"]
            + self.p["zetaIntLampPar"] * self.a["rParIntLampCan"]
        )

        # Maximum rate of electron transport rate at 25C [umol{e-} m^{-2} s^{-1}]
        self.a["j25CanMax"] = self.a["lai"] * self.p["j25LeafMax"]

        # CO2 compensation point [ppm]
        self.a["gamma"]= divNoBracks(self.p["j25LeafMax"], (self.a["j25CanMax"]) * 1) * self.p["cGamma"] * self.x[
            "tCan"
        ] + 20 * self.p["cGamma"] * (1 - divNoBracks(self.p["j25LeafMax"], (self.a["j25CanMax"]) * 1))


        # CO2 concentration in the stomata [ppm]
        self.a["co2Stom"] = self.p["etaCo2AirStom"] * self.a["co2InPpm"]

        # Potential rate of electron transport [umol{e-} m^{-2} s^{-1}]
        self.a["jPot"] = (
            self.a["j25CanMax"]
            * np.exp(
                self.p["eJ"]
                * (self.x["tCan"] + 273.15 - self.p["t25k"])
                / (1e-3 * self.p["R"] * (self.x["tCan"] + 273.15) * self.p["t25k"])
            )
            * (1 + np.exp((self.p["S"] * self.p["t25k"] - self.p["H"]) / (1e-3 * self.p["R"] * self.p["t25k"])))
            / (
                1
                + np.exp(
                    (self.p["S"] * (self.x["tCan"] + 273.15) - self.p["H"])
                    / (1e-3 * self.p["R"] * (self.x["tCan"] + 273.15))
                )
            )
        )

        # Electron transport rate [umol{e-} m^{-2} s^{-1}]
        self.a["j"] = (1 / (2 * self.p["theta"])) * (
            self.a["jPot"]
            + self.p["alpha"] * self.a["parCan"]
            - np.sqrt(
                (self.a["jPot"] + self.p["alpha"] * self.a["parCan"]) ** 2
                - 4 * self.p["theta"] * self.a["jPot"] * self.p["alpha"] * self.a["parCan"]
            )
        )

        # Photosynthesis rate at canopy level [umol{co2} m^{-2} s^{-1}]
        self.a["p"] = (
            self.a["j"] * (self.a["co2Stom"] - self.a["gamma"]) / (4 * (self.a["co2Stom"] + 2 * self.a["gamma"]))
        )

        # Photorespiration [umol{co2} m^{-2} s^{-1}]
        self.a["r"] = self.a["p"] * self.a["gamma"] / self.a["co2Stom"]

        # Inhibition due to full carbohydrates buffer [-]
        self.a["hAirBuf"] = 1 / (1 + np.exp(5e-4 * (self.x["cBuf"] - self.p["cBufMax"])))

        # Net photosynthesis [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcAirBuf"] = self.p["mCh2o"] * self.a["hAirBuf"] * (self.a["p"] - self.a["r"])
        
    def set_carbohydrate_buffer(self):
        """
        Set carbohydrate buffer parameters for the greenhouse system.
        """

        ## Carbohydrate buffer

        # Temperature effect on structural carbon flow to organs
        self.a["gTCan24"] = 0.047 * self.x["tCan24"] + 0.06

        # Inhibition of carbohydrate flow to the organs
        self.a["hTCan24"] = (
            1 / (1 + np.exp(-1.1587 * (self.x["tCan24"] - self.p["tCan24Min"])))
            * 1 / (1 + np.exp(1.3904 * (self.x["tCan24"] - self.p["tCan24Max"])))
        )

        # Inhibition of carbohydrate flow to the fruit
        self.a["hTCan"] = (
            1 / (1 + np.exp(-0.869 * (self.x["tCan"] - self.p["tCanMin"])))
            * 1 / (1 + np.exp(0.5793 * (self.x["tCan"] - self.p["tCanMax"])))
        )

        # Inhibition due to development stage
        self.a["hTCanSum"] = 0.5 * (
            self.x["tCanSum"] / self.p["tEndSum"] + np.sqrt((self.x["tCanSum"] / self.p["tEndSum"]) ** 2 + 1e-4)
        ) - 0.5 * (
            (self.x["tCanSum"] - self.p["tEndSum"]) / self.p["tEndSum"]
            + np.sqrt(((self.x["tCanSum"] - self.p["tEndSum"]) / self.p["tEndSum"]) ** 2 + 1e-4)
        )

        # Inhibition due to insufficient carbohydrates in the buffer [-]
        self.a["hBufOrg"] = 1 / (1 + np.exp(-5e-3 * (self.x["cBuf"] - self.p["cBufMin"])))

        # Carbohydrate flow from buffer to leaves [mg{CH2O} m^{2} s^{-1}]
        self.a["mcBufLeaf"] = self.a["hBufOrg"] * self.a["hTCan24"] * self.a["gTCan24"] * self.p["rgLeaf"]

        # Carbohydrate flow from buffer to stem [mg{CH2O} m^{2} s^{-1}]
        self.a["mcBufStem"] = self.a["hBufOrg"] * self.a["hTCan24"] * self.a["gTCan24"] * self.p["rgStem"]

        # Carbohydrate flow from buffer to fruit [mg{CH2O} m^{2} s^{-1}]
        self.a["mcBufFruit"] = (
            self.a["hBufOrg"]
            * self.a["hTCan"]
            * self.a["hTCan24"]
            * self.a["hTCanSum"]
            * self.a["gTCan24"]
            * self.p["rgFruit"]
        )

    def set_growth_and_maintenance_respiration(self):
        """
        Set growth and maintenance respiration parameters for the greenhouse system.
        """

        ## Growth and maintenance respiration - Section 4.4 [2]

        # Growth respiration [mg{CH2O} m^{-2] s^{-1}]
        self.a["mcBufAir"] = (
            self.p["cLeafG"] * self.a["mcBufLeaf"]
            + self.p["cStemG"] * self.a["mcBufStem"]
            + self.p["cFruitG"] * self.a["mcBufFruit"]
        )

        # Leaf maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcLeafAir"] = (
            (1 - np.exp(-self.p["cRgr"] * self.p["rgr"]))
            * self.p["q10m"] ** (0.1 * (self.x["tCan24"] - 25))
            * self.x["cLeaf"]
            * self.p["cLeafM"]
        )

        # Stem maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcStemAir"] = (
            (1 - np.exp(-self.p["cRgr"] * self.p["rgr"]))
            * self.p["q10m"] ** (0.1 * (self.x["tCan24"] - 25))
            * self.x["cStem"]
            * self.p["cStemM"]
        )

        # Fruit maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcFruitAir"] = (
            (1 - np.exp(-self.p["cRgr"] * self.p["rgr"]))
            * self.p["q10m"] ** (0.1 * (self.x["tCan24"] - 25))
            * self.x["cFruit"]
            * self.p["cFruitM"]
        )

        # Total maintenance respiration [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcOrgAir"] = self.a["mcLeafAir"] + self.a["mcStemAir"] + self.a["mcFruitAir"]
        
    def set_leaf_pruning_and_fruit_harvest(self):
        """
        Set leaf pruning and fruit harvest parameters for the greenhouse system.
        """

        ## Leaf pruning and fruit harvest

        # Leaf pruning [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcLeafHar"] = smoothHar(self.x["cLeaf"], self.p["cLeafMax"], 1e4, 5e4)

        # Fruit harvest [mg{CH2O} m^{-2} s^{-1}]
        self.a["mcFruitHar"] = smoothHar(self.x["cFruit"], self.p["cFruitMax"], 1e4, 5e4)
        
    def set_co2_fluxes(self):
        """
        Set CO2 fluxes parameters for the greenhouse system.
        """

        ## CO2 Fluxes - Section 7 [1]

        # Net crop assimilation [mg{CO2} m^{-2} s^{-1}]
        self.a["mcAirCan"] = (self.p["mCo2"] / self.p["mCh2o"]) * (
            self.a["mcAirBuf"] - self.a["mcBufAir"] - self.a["mcOrgAir"]
        )

        # Other CO2 flows [mg{CO2} m^{-2} s^{-1}]

        # From main to top compartment
        self.a["mcAirTop"] = airMc(self.a["fScr"], self.x["co2Air"], self.x["co2Top"])

        # From top compartment outside
        self.a["mcTopOut"] = airMc(self.a["fVentRoof"], self.x["co2Top"], self.d["co2Out"])

        # From main compartment outside
        self.a["mcAirOut"] = airMc(
            self.a["fVentSide"] + self.a["fVentForced"],
            self.x["co2Air"],
            self.d["co2Out"],
        )

    def set_heat_from_boiler(self):
        """
        Set parameters for heat from the boiler to different components in the greenhouse.
        """

        ## Heat from boiler - Section 9.2 [1]

        # Heat from boiler to pipe rails [W m^{-2}]
        self.a["hBoilPipe"] = self.u["boil"] * self.p["pBoil"] / self.p["aFlr"]

        # Heat from boiler to grow pipes [W m^{-2}]
        self.a["hBoilGroPipe"] = self.u["boilGro"] * self.p["pBoilGro"] / self.p["aFlr"]
    
    def set_external_co2_source(self):
        """
        Set parameters for external CO2 sources in the greenhouse.
        """

        ## External CO2 source - Section 9.9 [1]

        # CO2 injection [mg m^{-2} s^{-1}]
        self.a["mcExtAir"] = self.u["extCo2"] * self.p["phiExtCo2"] / self.p["aFlr"]

        ## Objects not currently included in the model
        self.a["mcBlowAir"] = 0
        self.a["mcPadAir"] = 0
        self.a["hPadAir"] = 0
        self.a["hPasAir"] = 0
        self.a["hBlowAir"] = 0
        self.a["hAirPadOut"] = 0
        self.a["hAirOutPad"] = 0
        self.a["lAirFog"] = 0
        self.a["hIndPipe"] = 0
        self.a["hGeoPipe"] = 0

    def set_lamp_cooling(self):
        """
        Set parameters for lamp cooling in the greenhouse.
        """

        ## Lamp cooling
        self.a["hLampCool"] = self.p["etaLampCool"] * self.a["qLampIn"]

    def set_heat_harvesting_and_mechanical_cooling(self):
        """
        Set parameters for heat harvesting, mechanical cooling, and dehumidification in the greenhouse.
        """

        ## Heat harvesting, mechanical cooling, and dehumidification
        # By default, there is no mechanical cooling or heat harvesting
        self.a["hecMechAir"] = 0
        self.a["hAirMech"] = 0
        self.a["mvAirMech"] = 0
        self.a["lAirMech"] = 0
        self.a["hBufHotPipe"] = 0

    # Set all auxiliary states
    def set_gl_aux(self):
        self.set_lumped_cover_layers()                     # Set parameters for cover layers
        self.set_capacities()                              # Set various capacity parameters
        self.set_heat_fluxes()                             # Set heat flux parameters
        self.set_fir_heat_fluxes()                         # Set far-infrared heat flux parameters
        self.set_natural_ventilation()                     # Set natural ventilation parameters
        self.set_control_rules()                           # Set control rules
        self.set_convection_conduction()                   # Set convection and conduction parameters
        self.set_convective_conductive_heat_fluxes()       # Set convective and conductive heat flux parameters
        self.set_canopy_transpiration()                    # Set canopy transpiration parameters
        self.set_vapor_fluxes()                            # Set vapor flux parameters
        self.set_latent_heat_fluxes()                      # Set latent heat flux parameters
        self.set_canopy_photosynthesis()                   # Set canopy photosynthesis parameters
        self.set_carbohydrate_buffer()                     # Set carbohydrate buffer parameters
        self.set_growth_and_maintenance_respiration()      # Set growth and maintenance respiration parameters
        self.set_leaf_pruning_and_fruit_harvest()          # Set leaf pruning and fruit harvest parameters
        self.set_co2_fluxes()                              # Set CO2 flux parameters
        self.set_heat_from_boiler()                        # Set boiler heat parameters
        self.set_external_co2_source()                     # Set external CO2 source parameters
        self.set_lamp_cooling()                            # Set lamp cooling parameters
        self.set_heat_harvesting_and_mechanical_cooling()  # Set heat harvesting and mechanical cooling parameters
        return self.gl                                     # Return the updated gl dictionary                    # Return the gl dictionary containing all set parameters


def set_gl_aux(gl):
    gl_aux = GreenLightAuxiliaryStates(gl)
    return gl_aux.set_gl_aux()
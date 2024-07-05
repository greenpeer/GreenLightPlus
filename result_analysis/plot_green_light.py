# File path: GreenLightPlus/result_analysis/plot_green_light.py
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


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from ..service_functions.funcs import *
from ..service_functions.vp2dens import vp2dens
from ..service_functions.rh2vapor_dens import rh2vapor_dens
from ..service_functions.co2_dens2ppm import co2_dens2ppm


def plot_green_light(gl):
    # Convert the time series to datetime objects
    t_label = "2023-01-01 01:00:00"
    start_time = datetime.strptime(t_label, "%Y-%m-%d %H:%M:%S")
    x_datetime = [
        start_time + timedelta(seconds=300 * i) for i in range(len(gl["x"]["tAir"]))
    ]

    end_time = x_datetime[-1]

    # Set up the figure and subplots
    fig = plt.figure(figsize=(20, 8), dpi=300)
    n_rows = 3
    n_cols = 4

    # Suplot 1
    ax1 = fig.add_subplot(n_rows, n_cols, 1)
    ax1.plot(x_datetime, gl["x"]["tAir"][:, 1], label="Indoor")
    ax1.plot(x_datetime, gl["d"]["tOut"][:, 1], label="Outdoor")
    ax1.set_ylabel("Temperature (°C)")
    ax1.legend()

    # Suplot 2
    ax2 = fig.add_subplot(n_rows, n_cols, 2)
    ax2.plot(x_datetime, gl["x"]["vpAir"][:, 1], label="Indoor")
    ax2.plot(x_datetime, gl["d"]["vpOut"][:, 1], label="Outdoor")
    ax2.set_ylabel("Vapor pressure (Pa)")
    ax2.legend()

    # Suplot 3
    ax3 = fig.add_subplot(n_rows, n_cols, 3)
    ax3.plot(x_datetime, gl["a"]["rhIn"][:, 1], label="Indoor")
    ax3.plot(
        x_datetime,
        100
        * vp2dens(gl["d"]["tOut"][:, 1], gl["d"]["vpOut"][:, 1])
        / rh2vapor_dens(gl["d"]["tOut"][:, 1], 100),
        label="Outdoor",
    )
    ax3.set_ylabel("Relative humidity (%)")
    ax3.legend()

    # Suplot 4
    ax4 = fig.add_subplot(n_rows, n_cols, 4)
    ax4.plot(x_datetime, gl["x"]["co2Air"][:, 1], label="Indoor")
    ax4.plot(x_datetime, gl["d"]["co2Out"][:, 1], label="Outdoor")
    ax4.set_ylabel("CO2 concentration (mg m^{-3})")
    ax4.legend()

    # Suplot 5
    ax5 = fig.add_subplot(n_rows, n_cols, 5)
    ax5.plot(x_datetime, gl["a"]["co2InPpm"][:, 1], label="Indoor")
    ax5.plot(
        x_datetime,
        co2_dens2ppm(gl["d"]["tOut"][:, 1], 1e-6 * gl["d"]["co2Out"][:, 1]),
        label="Outdoor",
    )
    ax5.set_ylabel("CO2 concentration (ppm)")
    ax5.legend()

    # Suplot 6
    ax6 = fig.add_subplot(n_rows, n_cols, 6)
    ax6.plot(x_datetime, gl["d"]["iGlob"][:, 1], label="Outdoor global solar radiation")
    ax6.plot(
        x_datetime,
        gl["a"]["rParGhSun"][:, 1] + gl["a"]["rParGhLamp"][:, 1],
        label="PAR above the canopy (sun+lamp)",
    )
    ax6.plot(x_datetime, gl["a"]["qLampIn"][:, 1], label="Lamp electric input")
    ax6.plot(x_datetime, gl["a"]["rParGhSun"][:, 1], label="PAR above the canopy (sun)")
    ax6.plot(
        x_datetime, gl["a"]["rParGhLamp"][:, 1], label="PAR above the canopy (lamp)"
    )
    ax6.set_ylabel("W m^{-2}")
    ax6.legend()

    # Suplot 7
    ax7 = fig.add_subplot(n_rows, n_cols, 7)
    ax7.plot(
        x_datetime,
        gl["p"]["parJtoUmolSun"] * gl["a"]["rParGhSun"][:, 1],
        label="PPFD from the sun",
    )
    ax7.plot(
        x_datetime,
        gl["p"]["zetaLampPar"] * gl["a"]["rParGhLamp"][:, 1],
        label="PPFD from the lamp",
    )
    ax7.set_ylabel("umol (PAR) m^{-2} s^{-1}")
    ax7.legend()

    # Suplot 8
    ax8 = fig.add_subplot(n_rows, n_cols, 8)
    ax8.plot(x_datetime, gl["a"]["mcAirCan"][:, 1], label="Net assimilation (CO_2)")
    ax8.plot(
        x_datetime,
        gl["a"]["mcAirBuf"][:, 1],
        label="Net photosynthesis (gross photosynthesis minus photorespirattion, CH_2O)",
    )
    ax8.plot(x_datetime, gl["a"]["mcBufAir"][:, 1], label="Growth respiration (CH_2O)")
    ax8.plot(
        x_datetime, gl["a"]["mcOrgAir"][:, 1], label="Maintenance respiration (CH_2O)"
    )
    ax8.set_ylabel("mg m^{-2} s^{-1}")
    ax8.legend()

    # Suplot 9
    ax9 = fig.add_subplot(n_rows, n_cols, 9)
    ax9.plot(x_datetime, gl["x"]["cFruit"][:, 1], label="Fruit dry weight")
    ax9.plot(x_datetime, gl["x"]["cStem"][:, 1], label="Stem dry weight")
    ax9.plot(x_datetime, gl["x"]["cLeaf"][:, 1], label="Leaf dry weight")
    ax9.plot(x_datetime, gl["x"]["cBuf"][:, 1], label="Buffer content")
    ax9.set_ylabel("mg (CH_2O) m^{-2}")
    ax9.legend(loc="upper left")

    ax9_2 = ax9.twinx()
    ax9_2.plot(x_datetime, gl["a"]["lai"][:, 1], label="LAI", color="purple")
    ax9_2.set_ylabel("m^2 m^{-2}")
    ax9_2.legend(loc="upper right")

    # Suplot 10
    ax10 = fig.add_subplot(n_rows, n_cols, 10)
    ax10.plot(x_datetime, gl["x"]["cFruit"][:, 1], label="Fruit dry weight")
    ax10.set_ylabel("mg (CH_2O) m^{-2}")
    ax10.legend(loc="upper left")

    ax10_2 = ax10.twinx()
    ax10_2.plot(
        x_datetime, gl["a"]["mcFruitHar"][:, 1], label="Fruit harvest", color="orange"
    )
    ax10_2.set_ylabel("mg (CH_2O) m^{-2} s^{-1}")
    ax10_2.legend(loc="upper right")

    # create an array of x-values for each time step
    ax11 = fig.add_subplot(n_rows, n_cols, 11)
    # plot each temperature state with a different color
    ax11.plot(x_datetime, gl["x"]["tCan"][:, 1], label="tCan")
    ax11.plot(x_datetime, gl["x"]["tAir"][:, 1], label="tAir")
    ax11.plot(x_datetime, gl["x"]["tThScr"][:, 1], label="tThScr")
    ax11.plot(x_datetime, gl["x"]["tTop"][:, 1], label="tTop")
    ax11.plot(x_datetime, gl["x"]["tCovIn"][:, 1], label="tCovIn")
    ax11.plot(x_datetime, gl["x"]["tCovE"][:, 1], label="tCovE")
    ax11.plot(x_datetime, gl["d"]["tOut"][:, 1], label="tOut")
    ax11.plot(x_datetime, gl["x"]["tPipe"][:, 1], label="tPipe")
    ax11.plot(x_datetime, gl["x"]["tGroPipe"][:, 1], label="tGroPipe")
    ax11.plot(x_datetime, gl["x"]["tIntLamp"][:, 1], label="tIntLamp")
    ax11.plot(x_datetime, gl["x"]["tLamp"][:, 1], label="tLamp")

    # add a legend and axis labels
    ax11.legend()
    ax11.set_xlabel("Time step")
    ax11.set_ylabel("Temperature (°C)")

    # Set the major locator and formatter of the x-axis for each subplot
    for ax in fig.axes:
        ax.legend()
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=24))
        # ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlim(
            start_time.replace(minute=0, second=0),
            start_time.replace(hour=23, minute=59, second=59),
        )
        ax.set_xlim(start_time, end_time)

    plt.tight_layout()

    # Show the figure
    plt.show()

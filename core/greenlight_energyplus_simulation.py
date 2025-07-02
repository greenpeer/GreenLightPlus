# File path: GreenLightPlus/core/greenlight_energyplus_simulation.py
"""
GreenLight-EnergyPlus Co-simulation Integration
==============================================

This module provides seamless integration between the GreenLight greenhouse
model and EnergyPlus building energy simulation software. It enables
high-fidelity co-simulation where EnergyPlus handles detailed building
physics while GreenLight manages crop growth and greenhouse-specific
climate dynamics.

Key Features:
    - Real-time data exchange between GreenLight and EnergyPlus
    - Synchronized time stepping and state updates
    - Bidirectional coupling for temperature and humidity
    - Energy consumption tracking from both simulators
    - Support for different greenhouse geometries

Technical Implementation:
    - Uses EnergyPlus Python API for runtime coupling
    - Callback-based architecture for time step synchronization
    - Sensor handles for efficient data exchange
    - Automatic unit conversions between simulators

Copyright Statement:
    Author: Daidai Qiu
    Author's email: qiu.daidai@outlook.com
    Last Updated: July 2025
    
    This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

# Import utility functions and core model
from ..service_functions.funcs import calculate_energy_consumption, extract_last_value_from_nested_dict
from .green_light_model import GreenLightModel


class GreenhouseSimulation:
    """
    Co-simulation coordinator for GreenLight and EnergyPlus integration.
    
    This class manages the coupled simulation of greenhouse systems by:
    - Synchronizing time steps between simulators
    - Exchanging environmental conditions (temperature, humidity)
    - Aggregating energy consumption from both models
    - Tracking crop yield throughout the growing season
    
    The co-simulation allows for more accurate energy analysis by combining:
    - EnergyPlus: Detailed HVAC, building envelope, and thermal mass
    - GreenLight: Crop physiology, photosynthesis, and transpiration

    Attributes:
        api: EnergyPlus Python API instance for runtime coupling
        model: GreenLight simulation model instance
        sensor handles: EnergyPlus variable/actuator handles for data exchange
        total_yield: Cumulative crop production (kg/m²)
        energy metrics: Lamp and boiler consumption tracking
    """

    def __init__(self, api, epw_path, idf_path, csv_path, output_directory, first_day, season_length, isMature=False):
        """
        Initialize co-simulation environment.
        
        Sets up both GreenLight and EnergyPlus models with synchronized
        configuration for coupled simulation.
        
        Args:
            api: EnergyPlus Python API instance
            epw_path (str): Path to EnergyPlus weather file (.epw)
            idf_path (str): Path to EnergyPlus input file (.idf)
            csv_path (str): Path to preprocessed weather data (.csv)
            output_directory (str): Directory for simulation outputs
            first_day (int): Starting day of year (1-365)
            season_length (float): Growing season duration in days
            isMature (bool): Initialize with mature crop. Default: False
        """
        super().__init__()
        # EnergyPlus API and file paths
        self.api = api
        self.epw_path = epw_path
        self.idf_path = idf_path
        self.csv_path = csv_path
        self.output_directory = output_directory
        
        # Simulation state tracking
        self.last_time_step = None
        self.total_minutes = 0
        self.simulation_started = False
        self.isMature = isMature

        # Initialize sensor handles for data exchange / 初始化数据交换的传感器句柄
        self.temp_sensor_handle = None  # Indoor air temperature / 室内空气温度
        self.rh_sensor_handle = None  # Indoor relative humidity / 室内相对湿度
        self.temp_outdoor_sensor_handle = None  # Outdoor air temperature / 室外空气温度
        self.outdoor_air_temp_handle = None  # Alternative outdoor temp / 备用室外温度
        self.humidity_ratio_handle = None  # Humidity ratio for conversions / 湿度比转换

        # Growing season parameters / 生长季节参数
        self.season_length = season_length  # Total season duration (days) / 生长周期长度
        self.season_interval = self.season_length  # Model update interval / 模型更新间隔
        self.first_day = first_day  # Starting day of year / 起始日期

        # Performance metrics / 性能指标
        self.total_yield = 0  # Cumulative fruit yield / 累计产量
        self.lampIn = 0  # Lamp energy consumption / 灯具能耗
        self.boilIn = 0  # Boiler energy consumption / 锅炉能耗
        self.current_step = 0  # Simulation step counter / 仿真步数

        # Initialize GreenLight model / 初始化GreenLight模型
        self.model = GreenLightModel(
            first_day=self.first_day, 
            isMature=self.isMature, 
            epw_path=self.epw_path, 
            csv_path=self.csv_path
        )

        # 初始化状态参数
        self.init_state = {
            "p": {
                # Greenhouse structure settings
                'psi': 22,  # Mean greenhouse cover slope [degrees]
                'aFlr': 668,  # Floor area [m^2]
                # Surface of the cover including side walls [m^2]
                'aCov': 1405,
                # Height of the main compartment [m] (the ridge height is 6.5, screen is 20 cm below it)
                'hAir': 6.5,
                'hGh': 6.905,  # Mean height of the greenhouse [m]
                'aRoof': 39*2,  # Maximum roof ventilation area
                # Vertical dimension of single ventilation opening [m]
                'hVent': 1.3,
                'cDgh': 0.75,  # Ventilation discharge coefficient [-]
                'lPipe': 1.25,  # Length of pipe rail system [m m^-2]
                # Capacity of CO2 injection for the entire greenhouse [mg s^-1]
                'phiExtCo2': 7.2e4*4e4/1.4e4,
                # Capacity of boiler for the entire greenhouse [W]
                'pBoil': 300*668,

                # Control settings
                'co2SpDay': 1000,  # CO2 setpoint during the light period [ppm]
                'tSpNight': 18.5,  # temperature set point dark period [°C]
                'tSpDay': 19.5,  # temperature set point light period [°C]
                'rhMax': 87,  # maximum relative humidity [%]
                # P-band for ventilation due to high temperature [°C]
                'ventHeatPband': 4,
                # P-band for ventilation due to high relative humidity [% humidity]
                'ventRhPband': 50,
                # P-band for screen opening due to high relative humidity [% humidity]
                'thScrRhPband': 10,
                # time of day (in morning) to switch on lamps [h]
                'lampsOn': 0,
                # time of day (in evening) to switch off lamps [h]
                'lampsOff': 18,
                # lamps are switched off if global radiation is above this value [W m^-2]
                'lampsOffSun': 400,
                # Predicted daily radiation sum from the sun where lamps are not used that day [MJ m^-2 day^-1]
                'lampRadSumLimit': 10
            }
        }

    def on_begin_new_environment(self, state):
        """在模拟开始新环境（年份/周期）时调用此方法"""
        # 获取室内温度传感器句柄
        self.temp_sensor_handle = self.api.exchange.get_variable_handle(
            state, "Zone Air Temperature", "GREENHOUSE ZONE ROOF"
        )
        if self.temp_sensor_handle == -1:
            print("无法找到室内温度传感器句柄。")
            sys.exit(1)

        # 获取室内相对湿度传感器句柄
        self.rh_sensor_handle = self.api.exchange.get_variable_handle(
            state, "Zone Air Relative Humidity", "GREENHOUSE ZONE ROOF"
        )
        if self.rh_sensor_handle == -1:
            print("无法找到室内相对湿度传感器句柄。")
            sys.exit(1)

        # 获取室外空气温度传感器句柄
        self.outdoor_air_temp_handle = self.api.exchange.get_variable_handle(
            state, "Site Outdoor Air Drybulb Temperature", "Environment"
        )
        if self.outdoor_air_temp_handle == -1:
            print("无法找到室外空气温度传感器句柄。")

        # 获取室内空气湿度比传感器句柄
        self.humidity_ratio_handle = self.api.exchange.get_variable_handle(
            state, "Zone Air Humidity Ratio", "GREENHOUSE ZONE ROOF"
        )
        if self.humidity_ratio_handle == -1:
            print("无法找到室内空气湿度比传感器句柄。")

    def on_after_new_environment_warmup_complete(self, state):
        """在预热完成后调用此方法"""
        if not self.simulation_started:
            self.simulation_started = True
            self.total_minutes = 0  # 重置总分钟数

    def on_end_of_zone_timestep_after_zone_reporting(self, state):
        """在每个区域时间步结束后调用此方法"""
        # 读取当前室内温度
        current_temperature = self.api.exchange.get_variable_value(
            state, self.temp_sensor_handle)

        # 读取当前室外温度
        current_outdoor_temperature = self.api.exchange.get_variable_value(
            state, self.outdoor_air_temp_handle)

        # 读取当前室内空气湿度比
        current_humidity_ratio = self.api.exchange.get_variable_value(
            state, self.humidity_ratio_handle)

        # 计算当前室内饱和水蒸气压力
        ATMOSPHERIC_PRESSURE = 101325  # 标准大气压力, 单位为帕斯卡(Pa)
        vpTop = (current_humidity_ratio / (0.621945 +
                 current_humidity_ratio)) * ATMOSPHERIC_PRESSURE

        if self.simulation_started:
            current_time_float = self.api.exchange.current_time(state)
            if self.last_time_step is None:
                # 第一个时间步单独处理
                self.start_time = 0
                self.end_time = current_time_float * 60
                self.total_minutes = self.end_time
            else:
                # 计算当前时间步的分钟数
                current_minutes = current_time_float * 60

                # 如果当前时间步的分钟数小于上一时间步的分钟数,说明跨天了
                if current_minutes < self.last_time_step * 60:
                    current_minutes += 1440  # 加上一天的分钟数

                # 更新总分钟数
                self.total_minutes += current_minutes - self.last_time_step * 60

                # 计算起始时间和结束时间
                self.start_time = self.end_time
                self.end_time = self.total_minutes

            # 更新last_time_step变量
            self.last_time_step = current_time_float

            # 运行模型, 根据EnergyPlus输出的时间更新需要调用的数据开始和结束时间
            gl = self.model.run_model(gl_params=self.init_state, season_length=self.season_length, season_interval=self.season_interval,
                                      start_row=int(self.start_time), end_row=int(self.end_time),
                                      step=self.current_step)

            print(f"start_time: {self.start_time}, end_time: {self.end_time}, step: {self.current_step} season_length: {self.season_length}, season_interval: {self.season_interval}")

            self.init_state = gl

            # 使用EnergyPlus输出的数据更新GreenLight模型的状态, 从而实现数据传递
            # print(f"原始温度: {self.init_state['x']['tTop'][-1][-1]}, 原始饱和水蒸气压力: {self.init_state['x']['vpTop'][-1][-1]}")

            self.init_state['x']["tTop"][-1][-1] = current_temperature
            self.init_state['x']["vpTop"][-1][-1] = vpTop

            # print(f"温度被替换为: {current_temperature}, 饱和水蒸气压力被替换为: {vpTop}")

            self.current_step += 1

            # 计算水果产量
            dmc = 0.06
            self.total_yield += 1e-6 * \
                calculate_energy_consumption(gl, "mcFruitHar") / dmc

            # 计算照明和加热产生的能耗
            self.lampIn += 1e-6 * \
                calculate_energy_consumption(gl, "qLampIn", "qIntLampIn")
            self.boilIn += 1e-6 * \
                calculate_energy_consumption(gl, "hBoilPipe", "hBoilGroPipe")

            # print(f"total_yield: {self.total_yield}, lampIn: {self.lampIn}, boilIn: {self.boilIn}")

    def run(self):

        # 创建新的状态
        state = self.api.state_manager.new_state()

        # 注册模拟开始和结束时的回调函数
        self.api.runtime.callback_begin_new_environment(
            state, self.on_begin_new_environment)
        self.api.runtime.callback_after_new_environment_warmup_complete(
            state, self.on_after_new_environment_warmup_complete)
        self.api.runtime.callback_end_zone_timestep_after_zone_reporting(
            state, self.on_end_of_zone_timestep_after_zone_reporting)

        # 执行模拟
        self.api.runtime.run_energyplus(
            state,
            [
                "-w", self.epw_path,  # 天气文件
                "-d", self.output_directory,  # 输出目录
                "-r", "-x", "-m", self.idf_path,  # 模拟选项和IDF文件路径
            ]
        )

    def get_results(self):
        return self.total_yield, self.lampIn, self.boilIn

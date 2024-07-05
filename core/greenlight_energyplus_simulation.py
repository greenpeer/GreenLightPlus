# File path: GreenLightPlus/core/greenlight_energyplus_simulation.py
"""
Copyright Statement:

Author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

from ..service_functions.funcs import calculate_energy_consumption, extract_last_value_from_nested_dict
from .green_light_model import GreenLightModel


class GreenhouseSimulation:

    def __init__(self, api, epw_path, idf_path, csv_path, output_directory, first_day, season_length, isMature=False):
        super().__init__()
        self.api = api
        self.epw_path = epw_path
        self.idf_path = idf_path
        self.csv_path = csv_path
        self.output_directory = output_directory
        self.last_time_step = None
        self.total_minutes = 0
        self.simulation_started = False
        self.isMature = isMature

        # 初始化各种传感器句柄为None
        self.temp_sensor_handle = None
        self.rh_sensor_handle = None
        self.temp_outdoor_sensor_handle = None
        self.outdoor_air_temp_handle = None
        self.humidity_ratio_handle = None

        # 生长周期参数
        self.season_length = season_length  # 生长周期长度, 天数
        self.season_interval = self.season_length  # 每次模型运行的时间间隔, 天数
        self.first_day = first_day  # 生长周期的第一天日期

        # 初始化产量和能耗
        self.total_yield = 0
        self.lampIn = 0
        self.boilIn = 0
        self.current_step = 0

        # 创建GreenLight模型实例, 初始状态为未成熟
        self.model = GreenLightModel(
            first_day=self.first_day, isMature=self.isMature, epw_path=self.epw_path, csv_path=self.csv_path)

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

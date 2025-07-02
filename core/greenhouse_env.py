# File path: GreenLightPlus/core/greenhouse_env.py
"""
Greenhouse Reinforcement Learning Environment
============================================

This module implements a Gymnasium-compatible environment for training
reinforcement learning agents to control greenhouse climate systems.
The environment wraps the GreenLight model to provide a standard
interface for RL algorithms.

Key Features:
    - OpenAI Gym/Gymnasium compatible interface
    - Discrete action space for temperature control
    - Comprehensive observation space including climate and crop states
    - Reward function balancing yield and energy consumption
    - Configurable episode length and initial conditions

Copyright Statement:
    Author: Daidai Qiu
    Author's email: qiu.daidai@outlook.com
    Last Updated: July 2025
    
    This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""

# Internal imports
from .green_light_model import GreenLightModel
from ..service_functions.funcs import calculate_energy_consumption, extract_last_value_from_nested_dict

# External imports for RL environment
import gymnasium as gym
import numpy as np
import random
        
class GreenhouseEnv(gym.Env):
    """
    Reinforcement Learning environment for greenhouse climate control.
    
    This environment provides a standard Gymnasium interface for training
    RL agents to optimize greenhouse operations. The agent learns to
    control heating setpoints to maximize crop yield while minimizing
    energy consumption.
    
    自定义温室环境，遵循OpenAI Gym/Gymnasium接口标准，用于训练
    强化学习智能体优化温室气候控制策略。

    Key Components:
        - State Space: Temperature, humidity, CO2, PAR, crop biomass
        - Action Space: Discrete heating setpoint adjustments
        - Reward: Weighted combination of yield and energy efficiency
        - Dynamics: Based on GreenLight physical model

    Attributes:
        observation_space (gym.Space): Continuous box space for observations
        action_space (gym.Space): Discrete space for temperature setpoints
        model (GreenLightModel): Core greenhouse simulation model
        state (np.ndarray): Current environment state vector
        episode_rewards (list): Accumulated rewards per episode
    """

    def __init__(self, env_config):
        """
        Initialize greenhouse RL environment with specified configuration.
        
        初始化温室强化学习环境，设置状态空间、动作空间和奖励函数。
        
        Args:
            env_config (dict): Environment configuration containing:
                - first_day (int): Starting day of year (1-365). Default: 1
                - isMature (bool): Start with mature crop. Default: False
                - epw_path (str): Path to weather data file. Default: ""
                - season_length (int): Episode length in days. Default: 60
                - season_interval (float): Time step in days. Default: 1/24 (1 hour)
                - current_step (int): Initial time step. Default: 0
                - init_state (dict): Initial state overrides. Default: {}
                - target_yield (float): Target fruit yield kg/m². Default: 0
                - target_yield_unit_energy_input (float): Target efficiency. Default: 0
                
        环境配置参数:
            - first_day: 模拟起始日期（一年中的第几天）
            - isMature: 是否从成熟作物开始
            - epw_path: 天气数据文件路径
            - season_length: 每个episode的天数
            - season_interval: 时间步长（天）
            - current_step: 当前步数
            - init_state: 初始状态覆盖
            - target_yield: 目标产量
            - target_yield_unit_energy_input: 目标能效
        """
        super(GreenhouseEnv, self).__init__()

        # Extract configuration parameters / 提取配置参数
        self.first_day = env_config.get("first_day", 1)  # Starting day of year / 起始日期
        
        # Randomize starting day for training diversity / 随机化起始日期以增加训练多样性
        # Spring season (day 90-120) for consistent growing conditions
        self.new_first_day = random.randint(90, 120)
    
        # Crop and simulation parameters / 作物和模拟参数
        self.isMature = env_config.get("isMature", False)  # Mature crop flag / 成熟作物标志
        self.epw_path = env_config.get("epw_path", "")  # Weather data path / 天气数据路径
        self.season_length = env_config.get("season_length", 60)  # Episode duration (days) / 回合持续时间
        self.season_interval = env_config.get("season_interval", 1/24)  # Time step (days) / 时间步长
        self.current_step = env_config.get("current_step", 0)  # Episode step counter / 回合步数计数器
        self.init_state = env_config.get("init_state", {})  # State overrides / 状态覆盖
        
        # Performance targets for reward calculation / 奖励计算的性能目标
        self.target_yield = env_config.get("target_yield", 0)  # Target fruit yield / 目标果实产量
        self.target_yield_unit_energy_input = env_config.get("target_yield_unit_energy_input", 0)  # Energy efficiency / 能源效率
        self.target_harvest_unit_energy_input = env_config.get("target_harvest_unit_energy_input", 0)  # Harvest energy target / 收获期能效目标

        # Initialize GreenLight simulation model / 初始化GreenLight仿真模型
        # Model encapsulates greenhouse physics and crop growth dynamics
        self.model = GreenLightModel(
            epw_path=self.epw_path,  # Weather data source / 天气数据源
            first_day=self.new_first_day,  # Randomized start day / 随机起始日
            isMature=self.isMature,  # Crop maturity state / 作物成熟状态
        )

        # Performance tracking variables / 性能跟踪变量
        # Energy consumption metrics / 能耗指标
        self.yield_unit_energy_input = 0  # Actual energy efficiency (kg/kWh) / 实际能效
        self.total_energy_input = 0  # Cumulative energy use (kWh/m²) / 累计能耗
        self.growth_energy_input = 0  # Energy during growth phase / 生长期能耗
        self.harvest_energy_input = 0  # Energy during harvest phase / 收获期能耗
        self.harvest_unit_energy_input = 0  # Harvest phase efficiency / 收获期效率

        # Production metrics / 生产指标
        self.total_yield = 0  # Cumulative fruit yield (kg/m²) / 累计产量
        self.total_reward = 0  # Cumulative RL reward / 累计强化学习奖励
        self.cost_penalty = 0  # Energy cost penalty term / 能源成本惩罚项

        self.yield_change = 0  # Per-step yield increment / 单步产量增量

        # Run initial simulation step to establish baseline / 运行初始模拟步骤建立基线
        # This provides the initial observation for the RL agent
        self.new_gl = self.model.run_model(
            gl_params=self.init_state,  # Override default parameters / 覆盖默认参数
            season_length=self.season_length,  # Episode duration / 回合持续时间
            season_interval=self.season_interval,  # Time step size / 时间步长
            step=self.current_step  # Current position in episode / 当前回合位置
        )

        # Define discrete action space for temperature control / 定义温度控制的离散动作空间
        # Actions map to temperature setpoints from 18-28°C (11 discrete levels)
        # Action 0 = 18°C, Action 5 = 23°C (baseline), Action 10 = 28°C
        self.action_space = gym.spaces.Discrete(11)

        # Define observation space bounds / 定义观测空间边界
        # State vector includes environmental conditions and crop status
        low = np.array(
            [
                0,    # Day of year (1-365) / 一年中的天数
                18,   # Night temperature setpoint (°C) / 夜间温度设定值
                18,   # Day temperature setpoint (°C) / 白天温度设定值
                400,  # Day CO2 setpoint (ppm) / 白天CO2设定值
                400,  # Air CO2 concentration (ppm) / 空气CO2浓度
                0,    # Air vapor pressure (Pa) / 空气水汽压
                0,    # Air temperature (°C) / 空气温度
                300,  # Fruit dry matter (mg/m²) / 果实干物质重量
                0,    # Total maintenance respiration (mg/m²/s) / 总维持呼吸速率
                0,    # Net photosynthesis rate (mg/m²/s) / 净光合速率
                0,    # Global radiation (W/m²) / 全球辐射
                -10,  # Outdoor temperature (°C) / 室外温度
                0,    # Lamp power consumption (W/m²) / 灯具能耗
                0,    # Boiler power consumption (W/m²) / 锅炉能耗
            ]
        )

        high = np.array(
            [
                365,   # Day of year (1-365) / 一年中的天数
                28,    # Night temperature setpoint (°C) / 夜间温度设定值
                28,    # Day temperature setpoint (°C) / 白天温度设定值
                1600,  # Day CO2 setpoint (ppm) / 白天CO2设定值
                2500,  # Air CO2 concentration (ppm) / 空气CO2浓度
                5000,  # Air vapor pressure (Pa) / 空气水汽压
                40,    # Air temperature (°C) / 空气温度
                3e5,   # Fruit dry matter (mg/m²) / 果实干物质重量
                0.2,   # Total maintenance respiration (mg/m²/s) / 总维持呼吸速率
                2,     # Net photosynthesis rate (mg/m²/s) / 净光合速率
                1000,  # Global radiation (W/m²) / 全球辐射
                40,    # Outdoor temperature (°C) / 室外温度
                500,   # Lamp power consumption (W/m²) / 灯具能耗
                500,   # Boiler power consumption (W/m²) / 锅炉能耗
            ]
        )

        # Define continuous observation space / 定义连续观测空间
        # 14-dimensional state vector for RL agent
        self.observation_space = gym.spaces.Box(
            low=low, high=high, shape=(14,), dtype=np.float64
        )

        self.episode_unit_energy_inputs = []
        self.episode_total_yields = []

    def step(self, action):
        """
        Execute one environment step with given action.
        
        环境步进函数，执行动作并返回新状态、奖励等信息。
        
        This method:
        1. Applies the temperature control action
        2. Runs the greenhouse simulation for one time step
        3. Calculates energy consumption and crop yield
        4. Computes the reward signal
        5. Checks episode termination conditions
        
        Args:
            action (int): Discrete action from agent (0-10).
                Maps to temperature setpoint 18-28°C.
                采取的动作（0-10），映射到18-28°C温度设定值。
                
        Returns:
            tuple: (observation, reward, terminated, truncated, info)
                - observation (np.ndarray): Current state vector / 当前状态向量
                - reward (float): Step reward / 步进奖励
                - terminated (bool): Episode ended naturally / 回合自然结束
                - truncated (bool): Episode cut off / 回合被截断
                - info (dict): Additional information / 附加信息
        """
        # Update model state from previous step / 更新上一步的模型状态
        self.gl = self.new_gl

        # Check day/night period for control logic / 检查昼夜周期用于控制逻辑
        is_daytime = self.gl["d"]["isDay"]

        # Map discrete action to temperature setpoint / 将离散动作映射到温度设定值
        # Action 0 → 18°C, Action 5 → 23°C, Action 10 → 28°C
        temperature_change = action + 18

        # 根据白天或夜晚调整相应的温度设定,1表示白天,0表示夜晚
        if is_daytime == 1:
            self.gl["p"]["tSpDay"] = temperature_change
        else:
            self.gl["p"]["tSpNight"] = temperature_change

        # 运行模型,得到新的状态, 传入当前状态,季节长度,季节间隔,当前步数
        self.new_gl = self.model.run_model(
            self.gl, self.season_length, self.season_interval, self.current_step
        )

        self.current_step += 1

        # 获取新的观测值、奖励等信息
        observation = self._get_observation()
        reward = self._get_reward()
        terminated, is_mature = self._is_done()
        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def _get_observation(self):
        """
        获取当前环境的观测值。
        :return: 当前环境的观测值
        """
        # 计算当前的一年中的天数
        day_of_year = self.new_first_day + self.current_step * self.season_interval

        # 使用导入的 calculate_energy_consumption 函数计算灯具和锅炉的能耗 [W m^{-2}]
        lampIn = 1e-6 * calculate_energy_consumption(
            self.new_gl, "qLampIn", "qIntLampIn"
        )
        boilIn = 1e-6 * calculate_energy_consumption(
            self.new_gl, "hBoilPipe", "hBoilGroPipe"
        )

        # 累计总能耗
        self.total_energy_input += lampIn + boilIn

        # 计算水果产量 [kg m^{-2}]
        dmc = 0.06
        self.yield_change = (
            1e-6 *
            calculate_energy_consumption(self.new_gl, "mcFruitHar") / dmc
        )

        self.total_yield += self.yield_change

        # 提取状态中各变量的最后一个值
        self.new_gl = extract_last_value_from_nested_dict(self.new_gl)

        # 需要获取的参数列表
        params = [
            ("p", "tSpNight"),  # 夜间温度设定值
            ("p", "tSpDay"),  # 白天温度设定值
            ("p", "co2SpDay"),  # 白天CO2设定值
            ("x", "co2Air"),  # 空气CO2浓度
            ("x", "vpAir"),  # 空气水汽压
            ("x", "tAir"),  # 空气温度
            ("x", "cFruit"),  # 果实干物质重量
            ("a", "mcOrgAir"),  # 总维持呼吸速率
            ("a", "mcAirBuf"),  # 净光合速率
            ("d", "iGlob"),  # 全球辐射
            ("d", "tOut"),  # 室外温度
            # ("d", "vpOut"),  # 室外水汽压
            # ("d", "co2Out"),  # 室外CO2浓度
            # ("d", "wind"),  # 室外风速
            # ("d", "tSky"),  # 天空温度
            # ("d", "tSoOut"),  # 外部土壤温度
        ]

        # 使用列表解析式获取所有的状态值
        param_values = [self.new_gl[param[0]][param[1]] for param in params]

        # 将所有的状态值合并到一个numpy数组
        current_obs = np.array([day_of_year, *param_values, lampIn, boilIn])

        return current_obs


    
    def _get_reward(self):
        """
        计算当前状态的奖励值。
        :return: 当前状态的奖励值
        """
        # 判断果实是否已成熟或训练是否终止
        terminated, is_mature = self._is_done()

        # 如果果实未成熟,则植株处于生长期
        if not is_mature:
            # 计算当前果实生长量 [mg m^{-2}]
            cFruit_growth = self.new_gl["x"]["cFruit"] - self.gl["x"]["cFruit"]
            
            # 使用 Reward Scaling 处理果实生长量, 单位是 g m^{-2}
            reward = cFruit_growth * 1e-3
            
            # print(f"当前生长期的果实干物质增长量是{cFruit_growth}, 生长期奖励是{reward}")
            
            # 计算生长期的能耗
            self.growth_energy_input = self.total_energy_input
            
            # 假设收获期直到季节结束,计算收获期的总小时数
            self.harvest_period_hours = self.season_length * 24 - self.current_step
            
        else:  # 植株处于收获期
            # 奖励设置为产量变化, 单位是 g m^{-2}
            reward = self.yield_change * 1e3
            
            # 计算收获期已经过去的小时数
            harvest_passed_hours = self.current_step - (self.season_length * 24 - self.harvest_period_hours)
            
            # 计算收获期进度的百分比
            harvest_progress = harvest_passed_hours / self.harvest_period_hours
            
            # 计算收获期剩余的小时数
            harvest_left_hours = self.harvest_period_hours - harvest_passed_hours
            
            
            # 设置一个平滑增加的产量目标,例如每增加10%的进度,目标产量提升10%
            incremental_target_yield = self.target_yield * (0.1 + 0.9 * harvest_progress)
            
            # 检查当前总产量是否达到了平滑增加的目标产量
            if self.total_yield >= incremental_target_yield:
                reward *= 1.2  # 奖励系数提高20%
            else:
                reward *= 0.8  # 奖励系数降低20%
            
            # 计算当前收获期的能耗
            self.harvest_energy_input = self.total_energy_input - self.growth_energy_input
            
            # 计算收获期的单位能耗
            self.harvest_unit_energy_input = self.harvest_energy_input / self.total_yield
            
            # 如果单位能耗低于目标值,给予奖励;否则给予惩罚
            if self.harvest_unit_energy_input <= self.target_harvest_unit_energy_input:
                reward *= 1.2  # 奖励系数提高10%
            else:
                reward *= 0.8  # 奖励系数降低10%
            
            
            # print(f"当前收获进度是{harvest_progress}, 剩余的小时数是{harvest_left_hours}, 收获期奖励是{reward}")

        # 如果训练终止,计算终止奖励
        if terminated:
            # 计算总体产量的单位能耗
            self.yield_unit_energy_input = self.total_energy_input / self.total_yield
            
            # 计算单位能耗差距和总产量差距的百分比
            energy_diff_pct = (self.target_yield_unit_energy_input - self.yield_unit_energy_input) / self.target_yield_unit_energy_input
            yield_diff_pct = (self.total_yield - self.target_yield) / self.target_yield
            
            # 根据差距百分比给予额外的奖励或惩罚
            reward += (energy_diff_pct + yield_diff_pct) * self.total_reward
            
            print(f"单位能耗是{self.yield_unit_energy_input}, 目标单位能耗是{self.target_yield_unit_energy_input}, 单位能耗差距百分比是{energy_diff_pct:.2%}")
            print(f"总产量是{self.total_yield}, 目标总产量是{self.target_yield}, 总产量差距百分比是{yield_diff_pct:.2%}")
            print(f"总奖励调整为:{reward}")

            self.episode_unit_energy_inputs.append(self.yield_unit_energy_input)
            self.episode_total_yields.append(self.total_yield)

            print(f"本次起始日期{self.new_first_day}的{self.season_length}天,单位能耗是{self.yield_unit_energy_input}, 总产量是{self.total_yield}, 总奖励是 {self.total_reward}")
            print(f"episode_unit_energy_inputs: {self.episode_unit_energy_inputs}")
            print(f"episode_total_yields: {self.episode_total_yields}")
        
          
        # 更新总奖励
        self.total_reward += reward
   
        return reward


    def _is_done(self):
        """
        判断一个episode是否结束。
        :return: 是否结束,生长是否完成
        """
        # 如果当前步数达到了季节长度,则episode结束
        terminated = self.current_step >= self.season_length * \
            (1 / self.season_interval)

       
        # 检查果实是否已经成熟
        is_mature = self.new_gl["a"]["mcFruitHar"] > 0.01

        return terminated, is_mature

    def reset(self, *, seed=None, options=None):
        """
        重置环境状态。
        :param seed: 随机数种子
        :param options: 重置选项
        :return: 初始观测值和信息
        """
   
        self.current_step = 0
        self.gl = self.init_state

        # 使用初始状态运行模型,得到初始观测值
        self.new_gl = self.model.run_model(gl_params=self.init_state, season_length=self.season_length,
                                           season_interval=self.season_interval, step=self.current_step)

        # 重置各种能耗和产量变量
        self.total_energy_input = 0
        self.growth_energy_input = 0
        self.harvest_energy_input = 0
        self.harvest_unit_energy_input = 0
        self.yield_unit_energy_input = 0
        self.total_yield = 0
        self.total_reward = 0
        self.cost_penalty = 0

        info = {}
        observation = self._get_observation()

        return observation, info

    def render(self):
        """
        渲染环境。这里是一个空实现。
        """
        pass

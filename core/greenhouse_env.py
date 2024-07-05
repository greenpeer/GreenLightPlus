# File path: GreenLightPlus/core/greenhouse_env.py
"""
Copyright Statement:

Author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


# GreenLight/core/greenhouse_env.py
from .green_light_model import GreenLightModel
from ..service_functions.funcs import calculate_energy_consumption, extract_last_value_from_nested_dict

# Third-Party Imports
import gymnasium as gym
import numpy as np
import random
        
class GreenhouseEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    这是一个自定义的温室环境,遵循OpenAI Gym的接口标准。
    """

    def __init__(self, env_config):
        """
        初始化温室环境。
        :param env_config: 环境配置字典,包含各种环境参数。
        """
        super(GreenhouseEnv, self).__init__()


        # 从环境配置中获取各种参数
  
        self.first_day = env_config.get("first_day", 1)  # 第一天的日期,默认为1
        
        # Randomly select a new first day for each episode
        self.new_first_day = random.randint(90, 120)
    

        self.isMature = env_config.get("isMature", False)  # 作物是否成熟,默认为False
        self.epw_path = env_config.get("epw_path", "")  # 天气数据输入,默认为空字符串
        self.season_length = env_config.get("season_length", 60)  # 季节长度,默认为60
        self.season_interval = env_config.get("season_interval", 1/24)  # 季节间隔,默认为1/24
        self.current_step = env_config.get("current_step", 0)  # 当前步数,默认为0
        self.init_state = env_config.get("init_state", {})  # 初始状态,默认为空字典
        self.target_yield = env_config.get("target_yield", 0)  # 目标水果产量,默认为0
        self.target_yield_unit_energy_input = env_config.get("target_yield_unit_energy_input", 0)  # 目标单位能耗,默认为0
        self.target_harvest_unit_energy_input = env_config.get("target_harvest_unit_energy_input", 0)  # 目标收获期单位能耗,默认为0

        # 初始化GreenLightModel,传入天气数据,第一天日期,作物成熟状态
        self.model = GreenLightModel(
            epw_path=self.epw_path,
            first_day=self.new_first_day,
            isMature=self.isMature,
        )

        # 初始化各种能耗和产量变量
        self.yield_unit_energy_input = 0  # 实际单位能耗
        self.total_energy_input = 0  # 总能耗
        self.growth_energy_input = 0  # 生长期能耗
        self.harvest_energy_input = 0  # 收获期能耗
        self.harvest_unit_energy_input = 0  # 收获期单位能耗

        self.total_yield = 0  # 总产量
        self.total_reward = 0  # 总奖励
        self.cost_penalty = 0  # 成本惩罚

        self.yield_change = 0  # 产量变化

        # 使用初始状态运行模型,得到初始观测值
        self.new_gl = self.model.run_model(gl_params=self.init_state, season_length=self.season_length,
                                           season_interval=self.season_interval, step=self.current_step)

        # 定义离散动作空间,0表示温度降低1度,1表示不变,2表示升高1度
        self.action_space = gym.spaces.Discrete(11)

        # 定义观测空间的下限和上限
        low = np.array(
            [
                0,  # 一年中的天数
                18,  # 夜间温度设定值
                18,  # 白天温度设定值
                400,  # 白天CO2设定值
                400,  # 空气CO2浓度
                0,  # 空气水汽压
                0,  # 空气温度
                300,  # 果实干物质重量
                0,  # 总维持呼吸速率
                0,  # 净光合速率
                0,  # 全球辐射
                -10,  # 室外温度
                # 0,  # 室外水汽压
                # 400,  # 室外CO2浓度
                # 0,  # 室外风速
                # -50,  # 天空温度
                # 0,  # 外部土壤温度
                0,  # 灯具能耗
                0,  # 锅炉能耗
            ]
        )

        high = np.array(
            [
                365,  # 一年中的天数
                28,  # 夜间温度设定值
                28,  # 白天温度设定值
                1600,  # 白天CO2设定值
                2500,  # 空气CO2浓度
                5000,  # 空气水汽压
                40,  # 空气温度
                3e5,  # 果实干物质重量
                0.2,  # 总维持呼吸速率
                2,  # 净光合速率
                1000,  # 全球辐射
                40,  # 室外温度
                # 5000,  # 室外水汽压
                # 900,  # 室外CO2浓度
                # 50,  # 室外风速
                # 50,  # 天空温度
                # 40,  # 外部土壤温度
                500,  # 灯具能耗
                500,  # 锅炉能耗
            ]
        )

        # 定义连续观测空间
        self.observation_space = gym.spaces.Box(
            low=low, high=high, shape=(14,), dtype=np.float64
        )

        self.episode_unit_energy_inputs = []
        self.episode_total_yields = []

    def step(self, action):
        """
        环境步进函数,接收一个动作,返回下一个观测值、奖励、是否结束等信息。
        :param action: 采取的动作
        :return: 下一个观测值、奖励、是否结束等信息
        """
        self.gl = self.new_gl

        # 判断是白天还是夜晚
        is_daytime = self.gl["d"]["isDay"]

        # 将动作映射到具体的温度改变,范围18-28
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

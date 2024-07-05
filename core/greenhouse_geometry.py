# File path: GreenLightPlus/core/greenhouse_geometry.py
"""
Copyright Statement:

Author: Daidai Qiu
Author's email: qiu.daidai@outlook.com

This code is licensed under the GNU GPLv3 License. For details, see the LICENSE file.
"""


import openstudio
import numpy as np
import os
import random
import csv
import datetime
import subprocess


class GreenhouseGeometry:
    def __init__(
        self,
        wall_thickness=0.2,
        window_thickness=0.3,
        roof_type="triangle",
        wall_height=6.5,
        wall_width=4,
        wall_length=1.67,
        slope=22,
        num_segments=6,
        frame_width=0.05,
        shade_distance_to_roof=3,
        time_step=12,
        number_width=1,
        number_length=1,
        max_indoor_temp=60,
        min_indoor_temp=0,
        max_outdoor_temp=60,
        min_outdoor_temp=0,
        max_delta_temp=-5,
        max_wind_speed=30,
        start_month=1,
        start_day=1,
        end_month=12,
        end_day=31


    ):

        # instantiate variables
        self.roof_type = roof_type
        self.wall_height = wall_height
        self.wall_width = wall_width
        self.wall_length = wall_length
        self.number_width = number_width
        self.number_length = number_length
        self.slope = slope

        self.num_segments = num_segments
        self.roof_height_relative_to_wall = self.calculate_roof_height_relative_to_wall(
            self.wall_width, self.slope)
        self.frame_width = frame_width
        self.time_step = time_step
        self.floor_area = self.wall_width * self.wall_length * \
            self.number_length * self.number_width

        # 计算屋顶窗户的面积
        # self.roof_ventilation_area = 0.1169 * self.floor_area

        self.roof_ventilation_area_left = 0.1169 * self.floor_area / 2
        self.roof_ventilation_area_right = 0.1169 * self.floor_area / 2

        # 定义遮阳面距离屋顶底部的高度
        self.shade_distance_to_roof = shade_distance_to_roof  # 需要根据实际情况进行调整
        self.roof_volume = 0

        # 设置通风相关的温度和风速限制
        self.max_indoor_temp = max_indoor_temp
        self.min_indoor_temp = min_indoor_temp
        self.max_outdoor_temp = max_outdoor_temp
        self.min_outdoor_temp = min_outdoor_temp
        self.max_delta_temp = max_delta_temp
        self.max_wind_speed = max_wind_speed

        # 设置起始日期和结束日期
        self.start_month = start_month
        self.start_day = start_day
        self.end_month = end_month
        self.end_day = end_day

        # 计算表面积
        self.calculate_surface_area_slope(self.wall_length * self.number_length,
                                          self.wall_width * self.number_length, self.roof_height_relative_to_wall)

        # print(f"遮阳板到屋顶底部的高度：{self.shade_distance_to_roof} m")
        print(f"roof height relative to wall: {self.roof_height_relative_to_wall} m")
        print(f"floor area: {self.floor_area} m²")
        print(f"roof ventilation area left: {self.roof_ventilation_area_left} m²")
        print(f"roof ventilation area right: {self.roof_ventilation_area_right} m²")

        # calculate_surface_area_slope(self, self.wall_width, self.wall_length, self.slope, self.num_segments, self.frame_width)

        if self.roof_type == "half_circle":
            # The radius of the half_circle arch
            self.roof_height_relative_to_wall = self.wall_width / 2
            self.z_value = self.z_value_half_circle
        elif self.roof_type == "triangle":
            self.z_value = self.z_value_triangle
        elif self.roof_type == "flat_arch":
            self.z_value = self.z_value_flat_arch
        elif self.roof_type == "gothic_arch":
            self.z_value = self.z_value_gothic_arch
        elif self.roof_type == "sawtooth":
            self.z_value = self.z_value_sawtooth
        elif self.roof_type == "sawtooth_arch":
            self.z_value = self.z_value_sawtooth_arch

        # create a new OpenStudio model
        self.model = openstudio.model.Model()

        # 创建运行期间
        # 获取模型的RunPeriod对象
        run_period = self.model.getRunPeriod()

        # 设置起始日期
        run_period.setBeginMonth(self.start_month)
        run_period.setBeginDayOfMonth(self.start_day)

        # 设置结束日期
        run_period.setEndMonth(self.end_month)
        run_period.setEndDayOfMonth(self.end_day)

        # 设置其他参数(可选)
        run_period.setUseWeatherFileHolidays(True)  # 使用天气文件中的节假日
        run_period.setUseWeatherFileDaylightSavings(True)  # 使用天气文件中的夏令时
        run_period.setApplyWeekendHolidayRule(True)  # 应用周末/节假日规则
        run_period.setUseWeatherFileRainInd(True)  # 使用天气文件中的降雨指示
        run_period.setUseWeatherFileSnowInd(True)  # 使用天气文件中的降雪指示

        ############################################################### 创建输出变量 #################################################################

        # 获取模型中现有的Timestep对象
        timestep = self.model.getTimestep()

        # 设置每小时的时间步数为6（每10分钟一个时间步）
        timestep.setNumberOfTimestepsPerHour(int(60/self.time_step))

        # 添加 Zone Air Temperature 输出变量, 文档：https://bigladdersoftware.com/epx/docs/23-2/input-output-reference/group-thermal-zone-description-geometry.html#zone-air-temperature-c
        temp_output_variable = openstudio.model.OutputVariable(
            "Zone Air Temperature", self.model)
        temp_output_variable.setKeyValue("*")  # 应用于所有区域
        temp_output_variable.setReportingFrequency("Timestep")  # 设置报告频率为时间步长

        # 添加 Zone Mean Air Temperature 输出变量
        mean_air_temp_variable = openstudio.model.OutputVariable(
            "Zone Mean Air Temperature", self.model)
        mean_air_temp_variable.setKeyValue("*")  # 应用于所有区域
        mean_air_temp_variable.setReportingFrequency("Timestep")  # 设置报告频率为时间步长

        # 添加 Zone Air Relative Humidity 输出变量
        humidity_output_variable = openstudio.model.OutputVariable(
            "Zone Air Relative Humidity", self.model)
        humidity_output_variable.setKeyValue("*")  # 应用于所有区域
        humidity_output_variable.setReportingFrequency(
            "Timestep")  # 设置报告频率为时间步长

        # Zone Outdoor Air Drybulb Temperature
        outdoor_drybulb_temp = openstudio.model.OutputVariable(
            "Zone Outdoor Air Drybulb Temperature", self.model)
        outdoor_drybulb_temp.setKeyValue("*")  # 应用于所有区域
        outdoor_drybulb_temp.setReportingFrequency("Timestep")  # 设置报告频率为每个时间步

        # Zone Outdoor Air Wetbulb Temperature
        outdoor_wetbulb_temp = openstudio.model.OutputVariable(
            "Zone Outdoor Air Wetbulb Temperature", self.model)
        outdoor_wetbulb_temp.setKeyValue("*")  # 应用于所有区域
        outdoor_wetbulb_temp.setReportingFrequency("Timestep")  # 设置报告频率为每个时间步

        # Zone Outdoor Air Wind Speed
        outdoor_wind_speed = openstudio.model.OutputVariable(
            "Zone Outdoor Air Wind Speed", self.model)
        outdoor_wind_speed.setKeyValue("*")  # 应用于所有区域
        outdoor_wind_speed.setReportingFrequency("Timestep")  # 设置报告频率为每个时间步

        # Zone Ventilation Mass Flow Rate
        zone_ventilation_mass_flow_rate = openstudio.model.OutputVariable(
            "Zone Ventilation Mass Flow Rate", self.model)
        zone_ventilation_mass_flow_rate.setKeyValue("*")  # 应用于所有区域
        zone_ventilation_mass_flow_rate.setReportingFrequency(
            "Timestep")  # 设置报告频率为每个时间步

        # Zone Ventilation Mass
        zone_ventilation_mass = openstudio.model.OutputVariable(
            "Zone Ventilation Mass", self.model)
        zone_ventilation_mass.setKeyValue("*")  # 应用于所有区域
        zone_ventilation_mass.setReportingFrequency(
            "Timestep")  # 设置报告频率为每个时间步

        # Zone Ventilation Air Change Rate
        zone_ventilation_air_change_rate = openstudio.model.OutputVariable(
            "Zone Ventilation Air Change Rate", self.model)
        zone_ventilation_air_change_rate.setKeyValue("*")  # 应用于所有区域
        zone_ventilation_air_change_rate.setReportingFrequency(
            "Timestep")  # 设置报告频率为每个时间步

        # Site Outdoor Air Drybulb Temperature
        site_outdoor_drybulb_temp = openstudio.model.OutputVariable(
            "Site Outdoor Air Drybulb Temperature", self.model)
        site_outdoor_drybulb_temp.setKeyValue("*")  # 应用于所有区域
        site_outdoor_drybulb_temp.setReportingFrequency(
            "Timestep")  # 设置报告频率为每个时间步

        # Zone Air Humidity Ratio  [kgWater/kgDryAir]
        zone_air_humidity_ratio = openstudio.model.OutputVariable(
            "Zone Air Humidity Ratio", self.model)
        zone_air_humidity_ratio.setKeyValue("*")  # 应用于所有区域
        zone_air_humidity_ratio.setReportingFrequency(
            "Timestep")

        ############################################################### 创建空间和空间类型 #################################################################
        # 创建空间和空间类型
        self.space_main, self.space_type_main = self.create_space_and_type(
            "Greenhouse Space Main", "Greenhouse Type Main")
        self.space_roof, self.space_type_roof = self.create_space_and_type(
            "Greenhouse Space Roof", "Greenhouse Type Roof")

        # 创建热区
        self.thermal_zone_main = self.create_thermal_zone(
            "Greenhouse Zone Main", self.space_main)
        self.thermal_zone_roof = self.create_thermal_zone(
            "Greenhouse Zone Roof", self.space_roof)

        ############################################################## 创建默认建筑集###############################################################

        # 创建一个新的默认建筑集对象。这个对象用于定义一组默认的建筑材料和构造方法，可以应用于建筑模型中的空间或空间类型。
        self.default_construction_set = openstudio.model.DefaultConstructionSet(
            self.model)
        self.default_construction_set.setName(
            "Greenhouse Construction Set")  # 设置建筑集的名称

        # 将创建的默认建筑集应用于第一个空间和其对应的空间类型。 这意味着这个空间和空间类型将使用这个建筑集中定义的默认建筑材料和构造方法。
        self.space_main.setDefaultConstructionSet(
            self.default_construction_set)
        self.space_type_main.setDefaultConstructionSet(
            self.default_construction_set)

        # 类似地，将同一个默认建筑集应用于第二个空间和其对应的空间类型。
        self.space_roof.setDefaultConstructionSet(
            self.default_construction_set)
        self.space_type_roof.setDefaultConstructionSet(
            self.default_construction_set)

        ############################################################### 创建地面，墙体，窗户，遮阳幕布等材料 #################################################################
        # 设置地面材料特性
        floor_properties = {
            "thermal_conductivity": 1.3,  # 混凝土的热导率
            "density": 2300,  # 混凝土的密度
            "specific_heat": 0.8  # 混凝土的比热容
        }

        # 设置地面材料
        self.floor_material = self.create_material(
            "Floor Material", "StandardOpaqueMaterial", floor_properties)

        # 创建墙体材料，设置钢架材料特性
        frame_properties = {
            "thermal_conductivity": 50,  # 钢材的大致热导率，单位 W/mK
            "density": 7850,             # 钢材的密度，单位 kg/m3
            "specific_heat": 500,       # 钢材的比热容，单位 J/kgK
            "thickness": 0.2           # 钢架的厚度，单位 m
        }

        self.frame_material = self.create_material(
            "Wall Material", "StandardOpaqueMaterial", frame_properties)

        # 设置遮阳幕布材料特性
        shading_properties = {
            "thermal_conductivity": 0.04,
            "thickness": 0.01,
            "density": 1.5,
            "specific_heat": 1000,
            "thermal_absorptance": 0.6,
            "solar_absorptance": 0.6,
            "visible_absorptance": 0.6
        }
        # 创建遮阳幕布材料
        self.shading_material = self.create_material(
            "Shading Material", "StandardOpaqueMaterial", shading_properties)

        # 设置窗户材料特性
        window_properties = {
            "u_factor": 2.5,  # 玻璃的U因子
            "solar_transmittance": 0.85,  # 玻璃的太阳能透射率
            "visible_transmittance": 0.8,  # 玻璃的可见光透射率
            "thickness": 4.0  # 玻璃的厚度
        }

        # 创建窗户材料
        self.window_material = self.create_material(
            "Window Material", "SimpleGlazing", window_properties)

        ############################################################### 创建地面，墙体，窗户，遮阳幕布的建筑组件 ###############################################################
        # 创建地面建筑组件
        self.floor_construction = self.create_construction(
            "Floor Construction", [self.floor_material])

        # 创建墙体建筑组件
        self.frame_construction = self.create_construction(
            "Wall Construction", [self.frame_material])

        # 创建下方窗户建筑组件
        self.window_construction_main = self.create_construction(
            "Window Construction Main", [self.window_material])

        # 创建上方窗户建筑组件
        self.window_construction_roof = self.create_construction(
            "Window Construction Roof", [self.window_material])

        # 创建上方窗户左边建筑组件
        self.window_construction_roof_left = self.create_construction(
            "Window Construction Roof Left", [self.window_material])

        # 创建上方窗户右边建筑组件
        self.window_construction_roof_right = self.create_construction(
            "Window Construction Roof Right", [self.window_material])

        # 创建遮阳幕布的建筑组件
        self.shading_construction = self.create_construction(
            "Shading Construction", [self.shading_material])

        # #  使用 dir() 函数列出模型对象的所有属性和方法
        # available_methods = dir(openstudio.model.AirflowNetworkSurface)

        # # 打印出来
        # for method in available_methods:
        #     print(method)

    def calculate_roof_height_relative_to_wall(self, roof_width, angle_degrees):
        # 将坡度转换为弧度
        angle_radians = np.radians(angle_degrees)
        roof_height_relative_to_wall = np.tan(angle_radians) * (roof_width / 2)
        return roof_height_relative_to_wall

    def calculate_trapezoidal_prism_volume(self, top_base, bottom_base, height_trapezoid, height_prism):
        """
        Calculate the volume of a trapezoidal prism.

        :param top_base: Length of the top base of the trapezoid
        :param bottom_base: Length of the bottom base of the trapezoid
        :param height_trapezoid: Height of the trapezoid
        :param height_prism: Height of the trapezoidal prism (depth of the prism)
        :return: Volume of the trapezoidal prism
        """
        # Calculate the area of the trapezoid
        area_trapezoid = (top_base + bottom_base) * height_trapezoid / 2

        # Calculate the volume of the prism
        volume_prism = area_trapezoid * height_prism

        return volume_prism

    def calculate_window_area(self):
        """
        计算屋顶窗户的面积。

        :param wall_width: 墙的宽度
        :param wall_length: 墙的长度
        :param num_segments: 窗户的数量
        :param roof_height: 屋顶相对于墙体的高度
        :param frame_width: 窗框的宽度
        :return: 每个窗户的宽度和总面积
        """
        print(f"墙的宽度：{self.wall_width} m")
        print(f"墙的长度：{self.wall_length} m")
        print(f"屋顶的高度：{self.roof_height_relative_to_wall} m")

        # 计算屋顶斜面的长度
        roof_slope_length = np.sqrt(
            (self.wall_width / 2) ** 2 + self.roof_height_relative_to_wall ** 2)

        # 计算每个窗户的宽度
        window_width = (roof_slope_length / self.num_segments *
                        2) - (2 * self.frame_width)

        # 计算每个窗户的长度
        window_length = self.wall_length - (2 * self.frame_width)

        # 计算每个窗户的面积
        window_area = window_width * window_length

        print(f"屋顶单块窗户的面积：{window_area} m²")
        print(f"屋顶单块窗户的宽度：{window_width} m")
        print(f"屋顶单块窗户的长度：{window_length} m")
        print(f"屋顶斜边的长度：{roof_slope_length} m")

        return window_area

    def create_default_construction_set(self, set_name):
        """
        创建一个新的默认建筑集。

        :param set_name: 默认建筑集的名称。
        :return: 新创建的默认建筑集对象。
        """
        construction_set = openstudio.model.DefaultConstructionSet(self.model)
        construction_set.setName(set_name)
        return construction_set

    def create_space_and_type(self, space_name, space_type_name):
        """
        创建一个新的空间和空间类型，并将空间类型关联到空间上。

        :param space_name: 空间的名称。
        :param space_type_name: 空间类型的名称。
        :return: 新创建的空间对象。
        """
        # 创建空间
        space = openstudio.model.Space(self.model)
        space.setName(space_name)

        # 创建空间类型
        space_type = openstudio.model.SpaceType(self.model)
        space_type.setName(space_type_name)

        # 将空间类型添加到空间
        space.setSpaceType(space_type)

        return space, space_type

    def create_thermal_zone(self, zone_name, space):
        """
        创建一个新的热区并将其与指定的空间关联。

        :param zone_name: 热区的名称。
        :param space: 要关联的空间对象。
        :return: 新创建的热区对象。
        """
        # 创建热区对象
        thermal_zone = openstudio.model.ThermalZone(self.model)
        thermal_zone.setName(zone_name)

        # 将空间添加到热区
        space.setThermalZone(thermal_zone)

        return thermal_zone

    def create_construction(self, construction_name, materials):
        """
        创建一个新的建筑组件。

        :param construction_name: 建筑组件的名称。
        :param materials: 组成建筑组件的材料列表。
        :return: 新创建的建筑组件对象。
        """
        construction = openstudio.model.Construction(self.model)
        construction.setName(construction_name)
        for i, material in enumerate(materials):
            construction.insertLayer(i, material)
        return construction

    def create_material(self, material_name, material_type, properties):
        """
        创建一个新的材料。
        EnergyPlus文档中的材料列表：https://bigladdersoftware.com/epx/docs/23-2/input-output-reference/group-surface-construction-elements.html#material
        :param material_name: 材料的名称。
        :param material_type: 材料的类型，比如 'StandardOpaqueMaterial' 或 'SimpleGlazing'。
        :param properties: 一个字典，包含材料的属性，如热导率、厚度等。
        :return: 新创建的材料对象。

        """
        # https://openstudio-sdk-documentation.s3.amazonaws.com/cpp/OpenStudio-1.7.0-doc/model/html/classopenstudio_1_1model_1_1_standard_opaque_material.html#a35c960fd05acf5df6becaa0d7751e9d2
        if material_type == "StandardOpaqueMaterial":
            material = openstudio.model.StandardOpaqueMaterial(self.model)
            material.setThermalConductivity(
                properties.get("thermal_conductivity", 0.1))
            if "thickness" in properties:
                material.setThickness(properties["thickness"])
            if "density" in properties:
                material.setDensity(properties["density"])
            if "specific_heat" in properties:
                material.setSpecificHeat(properties["specific_heat"])
            if "thermal_absorptance" in properties:
                material.setThermalAbsorptance(
                    properties["thermal_absorptance"])
            if "solar_absorptance" in properties:
                material.setSolarAbsorptance(properties["solar_absorptance"])
            if "visible_absorptance" in properties:
                material.setVisibleAbsorptance(
                    properties["visible_absorptance"])
        # https://openstudio-sdk-documentation.s3.amazonaws.com/cpp/OpenStudio-1.12.3-doc/model/html/classopenstudio_1_1model_1_1_simple_glazing.html
        elif material_type == "SimpleGlazing":
            material = openstudio.model.SimpleGlazing(self.model)
            material.setUFactor(properties.get("u_factor", 1.0))
            material.setVisibleTransmittance(
                properties.get("visible_transmittance", 0.8))
            if "thickness" in properties:
                material.setThickness(properties["thickness"])
        else:
            raise ValueError(f"Unknown material type: {material_type}")

        material.setName(material_name)
        return material

    # Function to calculate the z value of a point on a half_circle

    def z_value_half_circle(self, x, radius, h):
        x = x % (self.wall_width)  # Adjust x to be within the current arch
        if (x - h) ** 2 > radius**2:
            return 0
        else:
            return np.sqrt(radius**2 - (x - h) ** 2)

    # Function to calculate the z value of a point on a triangle
    def z_value_triangle(self, x, height, width):
        x = x % (2 * width)  # Adjust x to be within the current segment
        if x <= width:
            return x * height / width
        else:
            return (2 * width - x) * height / width

    def z_value_flat_arch(self, x, height, width):
        x = x % (2 * width)  # Adjust x to be within the current segment
        return height * (1 - 4 * ((x - width) / (2 * width)) ** 2)

    def z_value_gothic_arch(self, x, height, width):
        pointedness = 1.4
        x = x % (2 * width)  # Adjust x to be within the current segment
        return height * (1 - np.abs((x - width) / width) ** pointedness)

    def z_value_sawtooth(self, x, height, width):
        width = width * 2
        x = x % (2 * width)  # Adjust x to be within the current segment
        if x <= width:
            return height * (1 - (x / width))
        else:
            return 0

    def z_value_sawtooth_arch(self, x, height, width):
        width = width * 2
        x = x % (2 * width)  # Adjust x to be within the current segment
        if x <= width:
            return height * (1 - (x / width) ** 2)
        else:
            return 0

    ############################################################### 创建自然通风调度 #################################################################
    def calculate_total_window_area(self, space_name):
        # 获取指定名称的空间
        space = self.model.getSpaceByName(space_name).get()
        # 计算并返回该空间中所有可操作窗口的总面积
        return sum(subsurface.grossArea() for surface in space.surfaces() for subsurface in surface.subSurfaces() if subsurface.subSurfaceType() == "OperableWindow")

    def create_schedule_type_limits(self):
        # 创建一个新的调度类型限制模型
        fractional_type_limits = openstudio.model.ScheduleTypeLimits(
            self.model)
        # 设置模型的名称、下限、上限、数值类型和单位类型
        fractional_type_limits.setName("Fractional")
        fractional_type_limits.setLowerLimitValue(0)
        fractional_type_limits.setUpperLimitValue(1)
        fractional_type_limits.setNumericType("Continuous")
        fractional_type_limits.setUnitType("Dimensionless")
        # 返回创建的调度类型限制模型
        return fractional_type_limits

    def create_default_day_schedule(self, open_area_schedule, hour, minute, value):
        # 为 open_area_schedule 设置了默认的每日调度
        default_day_schedule = open_area_schedule.defaultDaySchedule()
        # 设置日程的名称，并添加两个时间点的值
        default_day_schedule.setName("Default Day Schedule")

        # 设置不同时间段的开启面积百分比
        default_day_schedule.addValue(
            openstudio.Time(0, hour, minute, 0), value)
        # 返回创建的默认日程
        return default_day_schedule

    def write_window_schedule_to_csv(self, open_area_schedule, file_path):
        # 设置随机数种子
        random.seed(22)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "Window_Schedule"])

            # 创建一个从 0.1 到 1 的值的列表
            open_values = [round(i, 1) for i in np.arange(0.1, 1.1, 0.1)]
            random.shuffle(open_values)  # 随机打乱顺序

            value_index = 0  # 用于跟踪 open_values 列表中的位置

            # 遍历每个小时
            for hour in range(24):
                # 在每个小时内按 self.time_step 交替进行窗户的开和关
                for minute in range(0, 60, self.time_step):
                    # 每个 self.time_step 交替开窗和关窗
                    if (hour * 60 + minute) // self.time_step % 2 == 0:
                        # 从列表中选择开窗程度
                        value = open_values[value_index]
                        value_index = (value_index + 1) % len(open_values)
                    else:
                        # 窗户关闭
                        value = 0.0

                    self.create_default_day_schedule(
                        open_area_schedule, hour, minute, value)
                    writer.writerow(
                        [openstudio.Time(0, hour, minute, 0).totalSeconds(), value])

    def create_window_schedule(self):
        # 计算温室屋顶窗户的总面积
        total_roof_window_area = self.calculate_total_window_area(
            "Greenhouse Space Roof")

        print(f"total roof window area：{total_roof_window_area} m²\n")

        # 创建并命名左侧屋顶的开放面积调度
        open_area_schedule_left = openstudio.model.ScheduleRuleset(self.model)
        open_area_schedule_left.setName("Open Area Fraction Schedule Left")

        # 创建并命名右侧屋顶的开放面积调度
        open_area_schedule_right = openstudio.model.ScheduleRuleset(self.model)
        open_area_schedule_right.setName("Open Area Fraction Schedule Right")

        # 设置调度的类型限制
        schedule_type_limits = self.create_schedule_type_limits()
        open_area_schedule_left.setScheduleTypeLimits(schedule_type_limits)
        open_area_schedule_right.setScheduleTypeLimits(schedule_type_limits)

        # 创建用于存储窗户调度的文件夹，并设置随机数种子
        folder_path = 'data/window_schedule'
        os.makedirs(folder_path, exist_ok=True)

        # 为左右两部分屋顶分别写入窗户调度
        self.write_window_schedule_to_csv(
            open_area_schedule_left, f'data/window_schedule/window_schedule_{self.roof_type}_left_{self.time_step}.csv')
        self.write_window_schedule_to_csv(
            open_area_schedule_right, f'data/window_schedule/window_schedule_{self.roof_type}_right_{self.time_step}.csv')

        # # 将窗户调度写入CSV文件
        # self.write_window_schedule_to_csv(open_area_schedule, f'{folder_path}/window_schedule_{self.roof_type}_{self.time_step}.csv')

        # 创建自然通风对象，并设置通风区域的开放面积
        # OpenStudio SDK 文档: https://openstudio-sdk-documentation.s3.amazonaws.com/cpp/OpenStudio-3.0.0-doc/model/html/classopenstudio_1_1model_1_1_zone_ventilation_windand_stack_open_area.html
        # EnergyPlus 文档：https://bigladdersoftware.com/epx/docs/23-2/input-output-reference/group-airflow.html#zoneventilationwindandstackopenarea
        # https://bigladdersoftware.com/epx/docs/23-2/input-output-reference/group-airflow.html#field-delta-temperature-1

        # 为左侧屋顶创建自然通风对象
        zone_ventilation_left = openstudio.model.ZoneVentilationWindandStackOpenArea(
            self.model)
        zone_ventilation_left.setName("Roof Window Ventilation Left")

        zone_ventilation_left.setOpeningEffectiveness(
            0.5)  # 设置开口有效性(Opening Effectiveness)
        zone_ventilation_left.setDischargeCoefficientforOpening(
            0.6)  # 设置开口的排放系数(Discharge Coefficient for Opening)

        zone_ventilation_left.setOpeningArea(
            self.roof_ventilation_area_left)  # 设置左侧屋顶通风区域的开放面积
        zone_ventilation_left.setEffectiveAngle(90)  # 设置左侧屋顶通风区域的有效角度
        zone_ventilation_left.setHeightDifference(
            # 设置左侧屋顶通风区域的高度差
            (self.roof_height_relative_to_wall + self.wall_height) / 2)
        zone_ventilation_left.setOpeningAreaFractionSchedule(
            open_area_schedule_left)  # 设置左侧屋顶通风区域的开放面积调度
        zone_ventilation_left.setMinimumIndoorTemperature(
            self.min_indoor_temp)  # 设置左侧屋顶通风区域的室内温度下限
        zone_ventilation_left.setMaximumIndoorTemperature(
            self.max_indoor_temp)  # 设置左侧屋顶通风区域的室内温度上限
        zone_ventilation_left.setDeltaTemperature(
            self.max_delta_temp)  # 设置左侧屋顶通风区域的室内外温差
        zone_ventilation_left.setMinimumOutdoorTemperature(
            self.min_outdoor_temp)  # 设置左侧屋顶通风区域的室外温度下限
        zone_ventilation_left.setMaximumOutdoorTemperature(
            self.max_outdoor_temp)  # 设置左侧屋顶通风区域的室外温度上限
        zone_ventilation_left.setMaximumWindSpeed(
            self.max_wind_speed)  # 设置左侧屋顶通风区域的最大风速
        zone_ventilation_left.addToThermalZone(
            self.thermal_zone_roof)  # 将左侧屋顶通风对象添加到屋顶热区

        # 为右侧屋顶创建自然通风对象
        zone_ventilation_right = openstudio.model.ZoneVentilationWindandStackOpenArea(
            self.model)
        zone_ventilation_right.setName("Roof Window Ventilation Right")
        zone_ventilation_right.setOpeningArea(
            self.roof_ventilation_area_right)  # 设置右侧屋顶通风区域的开放面积
        zone_ventilation_right.setEffectiveAngle(270)  # 设置右侧屋顶通风区域的有效角度
        zone_ventilation_right.setHeightDifference(
            # 设置右侧屋顶通风区域的高度差
            (self.roof_height_relative_to_wall + self.wall_height) / 2)
        zone_ventilation_right.setOpeningAreaFractionSchedule(
            open_area_schedule_right)  # 设置右侧屋顶通风区域的开放面积调度
        zone_ventilation_right.setMinimumIndoorTemperature(
            self.min_indoor_temp)  # 设置右侧屋顶通风区域的室内温度下限
        zone_ventilation_right.setMaximumIndoorTemperature(
            self.max_indoor_temp)  # 设置右侧屋顶通风区域的室内温度上限
        zone_ventilation_right.setDeltaTemperature(
            self.max_delta_temp)  # 设置右侧屋顶通风区域的室内外温差
        zone_ventilation_right.setMinimumOutdoorTemperature(
            self.min_outdoor_temp)  # 设置右侧屋顶通风区域的室外温度下限
        zone_ventilation_right.setMaximumOutdoorTemperature(
            self.max_outdoor_temp)  # 设置右侧屋顶通风区域的室外温度上限
        zone_ventilation_right.setMaximumWindSpeed(
            self.max_wind_speed)  # 设置右侧屋顶通风区域的最大风速
        zone_ventilation_right.addToThermalZone(
            self.thermal_zone_roof)  # 将右侧屋顶通风对象添加到屋顶热区

    def create_house_model(self, w, l, number_width, number_length):
        # 创建x,y方向的偏移量
        x_offset = w * self.wall_width
        y_offset = l * self.wall_length

        base_vertices = [
            openstudio.Point3d(0 + x_offset, 0 + y_offset, 0),
            openstudio.Point3d(0 + x_offset, self.wall_length + y_offset, 0),
            openstudio.Point3d(
                self.wall_width + x_offset, self.wall_length + y_offset, 0
            ),
            openstudio.Point3d(self.wall_width + x_offset, 0 + y_offset, 0),
        ]

        # 创建地面
        floor = openstudio.model.Surface(base_vertices, self.model)
        # 将表面添加到空间
        floor.setSpace(self.space_main)
        # 将表面设置为地面
        floor.setConstruction(self.floor_construction)

        # 定义四面窗户的坐标点
        # 对于每面窗户，我们需要确定四个顶点。这些顶点的坐标来自base_vertices，这是一个包含建筑物底部四个角的点的列表。
        # 我们使用openstudio.Point3d创建三维点。对于每面窗户，底部两个点在地面上（z =self.frame_width），顶部的两个点则在指定的高度上（也就是Z轴的值为“self.wall_height -self.frame_width”）。 顺序很重要，因为我们需要确保窗户的法线指向外部。
        # 顺序是：左下角，右下角，右上角，左上角。

        window_points_list = [
            [
                openstudio.Point3d(
                    0 + x_offset,
                    self.frame_width + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    0 + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    0 + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    self.frame_width,
                ),
                openstudio.Point3d(
                    0 + x_offset, self.frame_width + y_offset, self.frame_width
                ),
            ],  # 前窗
            [
                openstudio.Point3d(
                    self.frame_width + x_offset,
                    self.wall_length + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.wall_width - self.frame_width + x_offset,
                    self.wall_length + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.wall_width - self.frame_width + x_offset,
                    self.wall_length + y_offset,
                    self.frame_width,
                ),
                openstudio.Point3d(
                    self.frame_width + x_offset,
                    self.wall_length + y_offset,
                    self.frame_width,
                ),
            ],  # 右窗
            [
                openstudio.Point3d(
                    self.wall_width + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.wall_width + x_offset,
                    self.frame_width + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.wall_width + x_offset,
                    self.frame_width + y_offset,
                    self.frame_width,
                ),
                openstudio.Point3d(
                    self.wall_width + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    self.frame_width,
                ),
            ],  # 后窗
            [
                openstudio.Point3d(
                    self.wall_width - self.frame_width + x_offset,
                    0 + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.frame_width + x_offset,
                    0 + y_offset,
                    self.wall_height - self.frame_width,
                ),
                openstudio.Point3d(
                    self.frame_width + x_offset, 0 + y_offset, self.frame_width
                ),
                openstudio.Point3d(
                    self.wall_width - self.frame_width + x_offset,
                    0 + y_offset,
                    self.frame_width,
                ),
            ],  # 左窗
        ]
        # print(f"x轴第{w}个房间")
        for i in range(4):
            if number_length != 1:
                # 如果 create_outer_walls 为 False，并且 i 是 1 或 3（即 x 轴上的墙），则跳过此次循环
                if l == 0 and i == 1:
                    continue
                if l != 0 and l != number_length - 1:
                    if i == 1 or i == 3:
                        continue
                if l == number_length - 1 and i == 3:
                    continue

            if number_width != 1:
                if w == 0 and i == 2:
                    continue
                if w != 0 and w != number_width - 1:
                    if i == 0 or i == 2:
                        continue
                if w == number_width - 1 and i == 0:
                    continue

            # 定义四面墙的坐标点
            wall_vertices = [
                openstudio.Point3d(
                    base_vertices[i].x(
                    ), base_vertices[i].y(), self.wall_height
                ),
                openstudio.Point3d(
                    base_vertices[(i + 1) % 4].x(),
                    base_vertices[(i + 1) % 4].y(),
                    self.wall_height,
                ),
                base_vertices[(i + 1) % 4],
                base_vertices[i],
            ]
            wall = openstudio.model.Surface(wall_vertices, self.model)

            wall.setSurfaceType("Wall")

            wall.setConstruction(self.frame_construction)
            wall.setSpace(self.space_main)
            wall.setName("Wall_" + str(w) + "_" + str(l))

            # 创建窗户
            window = openstudio.model.SubSurface(
                window_points_list[i], self.model)
            # 设置窗户的构造
            window.setConstruction(self.window_construction_main)
            # 将窗户的类型设置为“FixedWindow”（固定窗户）。
            window.setSubSurfaceType("FixedWindow")
            window.setName("Window_Wall__" + str(w) + "_" + str(l))
            # 将窗户与墙体关联起来
            window.setSurface(wall)

            # 创建一个 WindowPropertyFrameAndDivider 对象
            frame_and_divider = openstudio.model.WindowPropertyFrameAndDivider(
                self.model)

            # 设置框架和分隔条的属性
            frame_and_divider.setFrameWidth(0.01)  # 示例：设置框架宽度为0.05米
            frame_and_divider.setFrameConductance(5.7)  # 示例：设置框架的热导率为5.7 W/m2K

            # 将 FrameAndDivider 对象应用于窗户（SubSurface）
            window.setWindowPropertyFrameAndDivider(frame_and_divider)

        ####################################################################### 屋顶结构 #######################################################################
        # 计算每个屋顶段的宽度
        segment_x_axis_width = self.wall_width / self.num_segments

        # 计算每个段的体积
        total_volume = 0

        # 创建一个 WindowPropertyFrameAndDivider 对象
        frame_and_divider = openstudio.model.WindowPropertyFrameAndDivider(
            self.model)

        # 设置框架和分隔条的属性
        frame_and_divider.setFrameWidth(0.01)  # 示例：设置框架宽度为0.05米
        frame_and_divider.setFrameConductance(5.7)  # 示例：设置框架的热导率为5.7 W/m2K

        # 创建屋顶段
        for count, i in enumerate(np.arange(0, self.wall_width, segment_x_axis_width)):
            # 计算段的左右边缘的z值
            z1 = self.z_value(
                i, self.roof_height_relative_to_wall, self.wall_width / 2)
            z2 = self.z_value(
                i + segment_x_axis_width,
                self.roof_height_relative_to_wall,
                self.wall_width / 2,
            )

            top_base = z1
            bottom_base = z2
            height_trapezoid = segment_x_axis_width
            height_prism = self.wall_length
            segment_volume = self.calculate_trapezoidal_prism_volume(
                top_base, bottom_base, height_trapezoid, height_prism
            )
            # print(f"第{count}个屋顶段的体积：{segment_volume} m³")
            total_volume += segment_volume

            # 计算段的斜率
            slope = (z2 - z1) / segment_x_axis_width
            # 计算段的宽度
            segment_width = np.sqrt(segment_x_axis_width**2 + (z2 - z1) ** 2)
            # 计算窗户的宽度
            window_width = segment_width - 2 * self.frame_width
            # 计算窗户顶点的x和z坐标
            window_x1 = i + self.frame_width * np.cos(np.arctan(slope))
            window_z1 = (
                self.wall_height + z1 + self.frame_width *
                np.sin(np.arctan(slope))
            )
            window_x2 = window_x1 + window_width * np.cos(np.arctan(slope))
            window_z2 = window_z1 + window_width * np.sin(np.arctan(slope))

            # 创建段的顶点
            segment_vertices = [
                openstudio.Point3d(i + x_offset, 0 + y_offset,
                                   self.wall_height + z1),
                openstudio.Point3d(
                    i + segment_x_axis_width + x_offset,
                    0 + y_offset,
                    self.wall_height + z2,
                ),
                openstudio.Point3d(
                    i + segment_x_axis_width + x_offset,
                    self.wall_length + y_offset,
                    self.wall_height + z2,
                ),
                openstudio.Point3d(
                    i + x_offset, self.wall_length + y_offset, self.wall_height + z1
                ),
            ]

            # 创建屋顶段
            roof_segment = openstudio.model.Surface(
                segment_vertices, self.model)
            # 设置表面的类型为 "RoofCeiling"
            roof_segment.setSurfaceType("RoofCeiling")
            # 设置段的构造
            roof_segment.setConstruction(self.frame_construction)
            # 创建段的名称
            roof_segment.setName("roof_segment_" + str(w) + "_" + str(l))
            # 设置段的空间
            roof_segment.setSpace(self.space_roof)

            # 创建窗户的顶点
            window_vertices = [
                openstudio.Point3d(
                    window_x1 + x_offset, self.frame_width + y_offset, window_z1
                ),
                openstudio.Point3d(
                    window_x2 + x_offset, self.frame_width + y_offset, window_z2
                ),
                openstudio.Point3d(
                    window_x2 + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    window_z2,
                ),
                openstudio.Point3d(
                    window_x1 + x_offset,
                    self.wall_length - self.frame_width + y_offset,
                    window_z1,
                ),
            ]

            # 创建窗户
            window = openstudio.model.SubSurface(window_vertices, self.model)
            # 设置窗户的类型为“OperableWindow”（可操作窗户）。
            window.setSubSurfaceType("OperableWindow")

            # 判断窗户属于左侧还是右侧
            if i < self.wall_width / 2:
                # 左侧窗户
                window.setConstruction(self.window_construction_roof_left)
                window.setName("Window_Roof_Left_" + str(w) + "_" + str(l))
            else:
                # 右侧窗户
                window.setConstruction(self.window_construction_roof_right)
                window.setName("Window_Roof_Right_" + str(w) + "_" + str(l))

            # # 设置窗户的构造
            # window.setConstruction(self.window_construction_roof)
            # # 创建窗户的名称
            # window.setName("Window_Roof_" + str(w) + "_" + str(l))
            # 将窗户与墙体关联起来
            window.setSurface(roof_segment)

            # 将 FrameAndDivider 对象应用于窗户（SubSurface）
            window.setWindowPropertyFrameAndDivider(frame_and_divider)

            ####################################################################### 左侧面 #######################################################################

            # 开始创建屋顶的侧面
            # 计算侧面窗户顶部点的z坐标
            side_windows_z1 = window_z1 - self.wall_height
            side_windows_z2 = window_z2 - self.wall_height
            side_wall_offset = self.frame_width / 8

            if l == 0:
                # 计算左侧面墙的坐标
                left_side_vertices = [
                    openstudio.Point3d(i + x_offset, 0 +
                                       y_offset, self.wall_height),
                    openstudio.Point3d(
                        i + segment_x_axis_width + x_offset,
                        0 + y_offset,
                        self.wall_height,
                    ),
                    openstudio.Point3d(
                        i + segment_x_axis_width + x_offset,
                        0 + y_offset,
                        self.wall_height + z2,
                    ),
                    openstudio.Point3d(
                        i + x_offset, 0 + y_offset, self.wall_height + z1
                    ),
                ]

                # 创建左边垂直面
                left_side_surface = openstudio.model.Surface(
                    left_side_vertices, self.model
                )
                # 将垂直面与空间关联起来
                left_side_surface.setSpace(self.space_roof)

                left_side_surface.setSurfaceType("RoofCeiling")

                # 将垂直面的建筑组件设置为你创建的墙体建筑组件
                left_side_surface.setConstruction(self.frame_construction)
                left_side_surface.setName("left_side_" + str(w) + "_" + str(l))

                # 开始创建侧面窗户，创建左边垂直面的窗户坐标
                left_side_window_vertices = [
                    openstudio.Point3d(
                        window_x1 + x_offset,
                        0 + y_offset,
                        self.wall_height + side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x2 + x_offset,
                        0 + y_offset,
                        self.wall_height + side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x2 + x_offset,
                        0 + y_offset,
                        self.wall_height + side_windows_z2 - side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x1 + x_offset,
                        0 + y_offset,
                        self.wall_height + side_windows_z1 - side_wall_offset,
                    ),
                ]

                # 创建左边垂直面的窗户子面
                left_windows = openstudio.model.SubSurface(
                    left_side_window_vertices, self.model
                )
                # 将窗户的建筑组件设置为你创建的窗户建筑组件
                left_windows.setConstruction(self.window_construction_roof)
                left_windows.setName(
                    "Left_side_window_" + str(w) + "_" + str(l))
                # 将窗户与垂直面关联起来
                left_windows.setSurface(left_side_surface)
                # 将窗户的类型设置为固定窗户
                left_windows.setSubSurfaceType("FixedWindow")

                # 创建一个 WindowPropertyFrameAndDivider 对象
                frame_and_divider = openstudio.model.WindowPropertyFrameAndDivider(
                    self.model)

                # 设置框架和分隔条的属性
                frame_and_divider.setFrameWidth(0.01)  # 示例：设置框架宽度为0.05米
                frame_and_divider.setFrameConductance(
                    5.7)  # 示例：设置框架的热导率为5.7 W/m2K

                # 将 FrameAndDivider 对象应用于窗户（SubSurface）
                left_windows.setWindowPropertyFrameAndDivider(
                    frame_and_divider)

            ####################################################################### 右侧面 #######################################################################
            if l == number_length - 1:
                right_side_vertices = [
                    openstudio.Point3d(
                        i + x_offset, self.wall_length + y_offset, self.wall_height + z1
                    ),
                    openstudio.Point3d(
                        i + segment_x_axis_width + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + z2,
                    ),
                    openstudio.Point3d(
                        i + segment_x_axis_width + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height,
                    ),
                    openstudio.Point3d(
                        i + x_offset, self.wall_length + y_offset, self.wall_height
                    ),
                ]

                # 创建右边垂直面
                right_side_surface = openstudio.model.Surface(
                    right_side_vertices, self.model
                )
                # 将垂直面与空间关联起来
                right_side_surface.setSpace(self.space_roof)
                right_side_surface.setSurfaceType("RoofCeiling")
                # 将垂直面的建筑组件设置为你创建的墙体建筑组件
                right_side_surface.setConstruction(self.frame_construction)
                right_side_surface.setName(
                    "Right_side_" + str(w) + "_" + str(l))

                # 创建右边垂垂直面的窗户坐标
                right_side_window_vertices = [
                    openstudio.Point3d(
                        window_x1 + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + side_windows_z1 - side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x2 + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + side_windows_z2 - side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x2 + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + side_wall_offset,
                    ),
                    openstudio.Point3d(
                        window_x1 + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + side_wall_offset,
                    ),
                ]

                # 创建右边垂直面的窗户子面
                right_windows = openstudio.model.SubSurface(
                    right_side_window_vertices, self.model
                )
                # 将窗户的建筑组件设置为你创建的窗户建筑组件
                right_windows.setConstruction(self.window_construction_roof)
                right_windows.setName(
                    "Right_side_window_" + str(w) + "_" + str(l))
                # 将窗户与垂直面关联起来
                right_windows.setSurface(right_side_surface)
                # 将窗户的类型设置为固定窗户
                right_windows.setSubSurfaceType("FixedWindow")

                # 创建一个 WindowPropertyFrameAndDivider 对象
                frame_and_divider = openstudio.model.WindowPropertyFrameAndDivider(
                    self.model)

                # 设置框架和分隔条的属性
                frame_and_divider.setFrameWidth(0.01)  # 示例：设置框架宽度为0.05米
                frame_and_divider.setFrameConductance(
                    5.7)  # 示例：设置框架的热导率为5.7 W/m2K

                # 将 FrameAndDivider 对象应用于窗户（SubSurface）
                right_windows.setWindowPropertyFrameAndDivider(
                    frame_and_divider)

            ####################################################################### 如果屋顶的类型时锯齿形的，那么就创建屋顶的侧面 #######################################################################
            if (i == 0 and self.z_value == self.z_value_sawtooth) or (
                i == 0 and self.z_value == self.z_value_sawtooth_arch
            ):
                vertical_surface_vertices = [
                    openstudio.Point3d(i + x_offset, 0 +
                                       y_offset, self.wall_height),
                    openstudio.Point3d(
                        i + x_offset,
                        0 + y_offset,
                        self.wall_height + self.roof_height_relative_to_wall,
                    ),
                    openstudio.Point3d(
                        i + x_offset,
                        self.wall_length + y_offset,
                        self.wall_height + self.roof_height_relative_to_wall,
                    ),
                    openstudio.Point3d(
                        i + x_offset, self.wall_length + y_offset, self.wall_height
                    ),
                ]

                # 用这四个顶点创建一个子面, 这个子面就是一个垂直面。将这个垂直面添加到模型中，并设置其所属的空间。
                vertical_surface = openstudio.model.Surface(
                    vertical_surface_vertices, self.model
                )

                # 将垂直面的建筑组件设置为你创建的墙体建筑组件
                vertical_surface.setConstruction(self.frame_construction)
                vertical_surface.setName(
                    "Vertical_surface_" + str(w) + "_" + str(l))

                # 将垂直面与空间关联起来
                vertical_surface.setSpace(self.space_roof)
                vertical_surface.setSurfaceType("RoofCeiling")

                roof_vertical_window_vertices = [
                    openstudio.Point3d(
                        i + x_offset,
                        self.frame_width + y_offset,
                        self.wall_height + self.frame_width,
                    ),
                    openstudio.Point3d(
                        i + x_offset,
                        self.frame_width + y_offset,
                        self.wall_height
                        + self.roof_height_relative_to_wall
                        - self.frame_width,
                    ),
                    openstudio.Point3d(
                        i + x_offset,
                        self.wall_length - self.frame_width + y_offset,
                        self.wall_height
                        + self.roof_height_relative_to_wall
                        - self.frame_width,
                    ),
                    openstudio.Point3d(
                        i + x_offset,
                        self.wall_length - self.frame_width + y_offset,
                        self.wall_height + self.frame_width,
                    ),
                ]

                # Create the vertical subsurface
                roof_vertical_window = openstudio.model.SubSurface(
                    roof_vertical_window_vertices, self.model
                )
                # 将窗户的建筑组件设置为你创建的窗户建筑组件
                roof_vertical_window.setConstruction(
                    self.window_construction_roof)
                roof_vertical_window.setName(
                    "Vertical_surface_window_" + str(w) + "_" + str(l)
                )
                roof_vertical_window.setSurface(vertical_surface)
                roof_vertical_window.setSubSurfaceType("FixedWindow")

                # 创建一个 WindowPropertyFrameAndDivider 对象
                frame_and_divider = openstudio.model.WindowPropertyFrameAndDivider(
                    self.model)

                # 设置框架和分隔条的属性
                frame_and_divider.setFrameWidth(0.01)  # 示例：设置框架宽度为0.05米
                frame_and_divider.setFrameConductance(
                    5.7)  # 示例：设置框架的热导率为5.7 W/m2K

                # 将 FrameAndDivider 对象应用于窗户（SubSurface）
                roof_vertical_window.setWindowPropertyFrameAndDivider(
                    frame_and_divider)

        return total_volume

    def create_houses(self):

        for l in range(self.number_length):
            for w in range(self.number_width):
                total_volume = self.create_house_model(
                    w, l, self.number_width, self.number_length)

                self.roof_volume += total_volume

        print("Total Roof Volume:", self.roof_volume)

        # 修正屋顶热区体积，手动重新设置屋顶热区的体积
        self.thermal_zone_roof.setVolume(self.roof_volume)

        folder_path = 'data/model_files'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.create_window_schedule()

        # 设置OSM文件的保存路径
        osm_path = openstudio.toPath(
            f"{folder_path}/greenhouse_{self.roof_type}.osm")

        # 保存模型到OSM文件

        self.model.save(osm_path, True)  # True 表示如果文件已存在，将其覆盖

        # 转换为EnergyPlus IDF文件
        forward_translator = openstudio.energyplus.ForwardTranslator()
        workspace = forward_translator.translateModel(self.model)

        idf_path = f"data/model_files/greenhouse_{self.roof_type}.idf"

        # 保存IDF文件
        workspace.save(openstudio.toPath(idf_path), True)

        # # 保存epJSON文件
        # command = [
        #     'energyplus',
        #     '--convert-only',
        #     '-c', idf_path,
        #     '-d', f"data/model_files",
        # ]
        # subprocess.run(command)
    def calculate_surface_area_slope(self, wall_length, wall_width, roof_height_relative_to_wall):
        # Calculate the length of the roof slope
        roof_slope_length = np.sqrt(
            (wall_width / 2)**2 + roof_height_relative_to_wall**2)

        # Calculate the area of the roof
        roof_area = roof_slope_length * wall_length * 2

        # Calculate the area of the side walls
        side_wall_area = self.wall_height * wall_length * 2

        # Calculate the area of the end walls
        end_wall_area = self.wall_height * wall_width * 2

        # Calculate the total surface area
        total_surface_area = roof_area + side_wall_area + end_wall_area

        # Calculate the slope of the roof
        slope = np.arctan(roof_height_relative_to_wall / (wall_width / 2))
        print("Roof Slope:", np.degrees(slope))
        print("Total Surface Area:", total_surface_area)
        # convert slope from radians to degrees
        return total_surface_area, np.degrees(slope)

    # def calculate_surface_area_slope(self, wall_length, wall_width, roof_height_relative_to_wall):
    #     base = wall_width / 2
    #     height = roof_height_relative_to_wall
    #     hypotenuse = np.sqrt(base**2 + height**2)

    #     # Two triangular sides of the roof
    #     triangular_side_area = hypotenuse * wall_length * 2

    #     # Two triangular sides walls
    #     triangular_wall_area = base * roof_height_relative_to_wall * 2

    #     total_surface_area = triangular_side_area + triangular_wall_area

    #     # Calculate the slope of the roof
    #     slope = np.arctan(height / base)
    #     print("Roof Slope:", np.degrees(slope))
    #     print("Total Surface Area:", total_surface_area)
    #     # convert slope from radians to degrees
    #     return total_surface_area, np.degrees(slope)

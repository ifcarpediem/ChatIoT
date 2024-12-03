<div align="center">

<h1 align="center">MIoT设备模拟指南</h1>
通过模拟器生成模拟设备，接入Home Assistant构建自己的虚拟家庭。

[English](./Miot_Device_Setup.md) / 简体中文
</div>

## MIoT介绍
MIoT协议是小米智能家居从2018年起推行的智能设备通信协议规范。

更详细的MIoT介绍参考[小米开发者平台文档](https://iot.mi.com/v2/new/doc/home),符合该协议的设备参加[小米/米家产品库](https://home.miot-spec.com/)，这里主要介绍如何通过docker模拟该类设备。

## MIoT设备模拟及接入
### 设备模拟
模拟该设备主要通过[python-miio](https://github.com/rytilahti/python-miio)库中的miot-simulator支持。

为了方便使用，我们打包了一个镜像leafli/miot-simulator，你可以通过该镜像来模拟设备。

1、拉取镜像。
```bash
docker search leafli/miot-simulator
# 如果没有搜索到，请检查自己的网络问题
docker pull leafli/miot-simulator
```
2、clone本仓库，或者下载/devices/miot_devices文件夹，其中包含了模拟米家设备所需要的物模型文件（即Spec文件，json格式），也可以自行在[小米/米家产品库](https://home.miot-spec.com/)中下载自己想要模拟的设备，注意文件命名，格式为model.json。

3、启动镜像模拟设备。
```bash
# 模拟设备，并指定设备的ip地址。
docker run -d --network=chatiot --ip=ip_in_chatiot_network -v .:/spec --name=curtain_living_room miot-simulator miiocli devtools miot-simulator --file device_spec_file --model device_model
```

## 参考示例
### 虚拟家庭
这里我们给出模拟一个简单三室一厅家庭的示例，假设已经创建了子网（172.20.0.0），并且Home Assistant安装在该子网中，迷你如下设备，分配到了不同区域和不同的ip。

1、模拟设备
假设你已经有了一个miot_devices文件夹，其中包含了仓库下/devices/miot_devices中的所有spec文件。
```bash
# 导航到miot_devices文件夹
cd /path/to/miot/devices
```
家门：
- 门窗传感器（172.20.0.4）
```bash
```

客厅：
- 吸顶灯（172.20.0.5）
```bash
```
- 空调（172.20.0.6）
```bash
```
- 电视（172.20.0.7）
```bash
```
- 光照传感器（172.20.0.8）
```bash
```

卧室：
- 吸顶灯（172.20.0.9）
```bash
```
- 空调（172.20.0.10）
```bash
```
- 温湿度传感器（172.20.0.11）
```bash
```

浴室：
- 浴霸（172.20.0.12）
```bash
```
- 热水器（172.20.0.13）
```bash
```

书房：
- 吸顶灯（172.20.0.14）
```bash
```
- 桌灯（172.20.0.15）
```bash
```
- 运动传感器（172.20.0.16）
```bash
```

**注意：**同一个物模型对应的设备目前只能同时模拟一个，第二个无法通过Xiaomi Miot Auto集成接入，如果你需要多个同类型的设备，你可以去找同类型但不同model的设备。有些设备接入到Home Assistant无法响应，如果你希望你在控制设备时，设备状态可以看见变化，请自行尝试探索。

### ChatIoT使用参考
<div align="center">

<h1 align="center">Home Assistant Installation Guide</h1>

English / [简体中文](./Miot_Device_Setup_CN.md)
</div>

# Installing Home Assistant
[Home Assistant](https://www.home-assistant.io/) is an open-source home automation platform that allows you to integrate and control various smart home devices from different ecosystems. There are multiple ways to install Home Assistant, and you can refer to the official Home Assistant website for detailed installation tutorials.

我们推荐采用Docker进行安装，接下来将带你一步步进行下载和部署。

1. Install Docker.

2. Start Docker, and pull the Home Assistant image, with the latest version recommended, which is 2024.
```bash
docker pull homeassistant/home-assistant:2024.10.0 
```
3. Run the Home Assistant image.
```bash
# If you need to simulate devices or wish to conveniently delve deeper into Home Assistant configurations, please opt for Plan 2.
# Prerequisites: Creating a Subnetwork
docker network create --subnet=172.20.0.0/16 --gateway=172.20.0.1 chatiot

# Plan 1
# By default, the Home Assistant interface is mounted on port 8123.
docker run -d --name="hass" --net=host -p 8123:8123 homeassistant/home-assistant:2024.10.0

# Plan 2
# The /config directory is for Home Assistant's configuration files, and it is recommended to mount it to a local directory.
# You can choose a port of your preference to access the Home Assistant user interface.
docker run -d --name="hass" -v /path/to/your/config:/config -p your_local_port:8123 --net=chatiot --ip=172.20.0.3 homeassistant/home-assistant:2024.10.0
```

After successful installation, you will be able to access the Home Assistant user interface by visiting the local URL on the port you have designated.

# HACS Store Installation

[HACS](https://hacs.xyz/) is a third-party integration store for Home Assistant. By downloading and installing it, you gain access to a variety of integrations developed by third parties, such as the Xiaomi Miot Auto integration we intend to use. There are many interesting integrations waiting for you to explore on your own.

1. Download the HACS installation script and run it.
```bash
# Enter your Home Assistant container.
docker exec -it hass /bin/bash 
# Download the HACS installation script and execute it.
wget -q -O - https://get.hacs.xyz | bash -
```
2. Restart Home Assistant

he changes to take effect. You can do this by accessing the Home Assistant interface, clicking on "Developer Tools" in the left sidebar, and then finding "Configuration Check & Restart" on the page. First, click "Check Configuration" to ensure there are no issues, and then click "Restart" when everything is in order.

3. Configure HACS

After the restart, open the Home Assistant user interface again, click on "Settings" in the sidebar, click on "Devices & Services," select "Integrations," click on "Add Integration" in the bottom right corner, and search for "HACS" to install it. To use the HACS store, you will need to link it with your GitHub account. Follow the instructions provided, or refer to a [detailed guide](https://blog.csdn.net/sunky7/article/details/137619019) for assistance with the installation process.

# Device Integration
Currently, ChatIoT only supports devices that can be integrated via the [Xiaomi Miot Auto integration](https://github.com/al-one/hass-xiaomi-miot). Support for more types of devices is under development.

1. Connect your Xiaomi devices to the Mi Home app according to the instructions provided by Xiaomi. You will need to know your Xiaomi account credentials, as they will be required for subsequent integration steps.

2. In the Home Assistant HACS store, search for "Xiaomi Miot Auto," download the integration, then click on "Settings" in the sidebar, click on "Devices & Services," select "Integrations," click on "Add Integration" in the bottom right corner, and search for "Xiaomi Miot Auto" to install it.

3. Restart Home Assistant.

4. Click on the integration card, then click "Add Entry" on the page, select the "Account Integration" option, and proceed to the next step. Enter your Xiaomi ID and password, then click submit.

5. Select the Xiaomi devices you wish to integrate, and you will then be able to see the integrated devices on the devices page.

<p align="center">
<a href=""><img src="./resources/miot_integration.png" width="500px"></a>
</p>
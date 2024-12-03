<div align="center">

<h1 align="center">🏠ChatIoT</h1>
一个让你能够轻松创建智能家居的语音助手。

[English](./README.md) / 简体中文
</div>

## :pencil: 简介
ChatIoT的使命是赋予用户通过自然语言交互创建TAP（触发-动作程序）的能力。

这个代码库专注于智能家居领域，使用Home Assistant作为基础平台。一旦部署了ChatIoT，用户就可以使用自然语言（例如，“打开书房的灯”）轻松控制智能家居设备，或者创建智能规则（例如，“如果有人经过客厅，自动打开客厅的灯”）。

<p align="center">
<a href=""><img src="docs\resources\ChatIoT_overview.png" width="500px"></a>
</p>

## 安装准备
在使用ChatIoT之前，你需要做一些准备工作。
### 1. 安装Home Assistant
更多详细信息请查看[Home Assistant安装指南](./docs/Home_Assistant_Setup.md)。

首先，你需要在本地安装Home Assistant，这里推荐采用docker方式进行安装。

接着，你需要在Home Assistant中安装HACS集成（这需要一个可用的GitHub账户）。

最后，你可以在HACS商店中安装Xiaomi Miot Auto集成，然后将你的设备从米家中接入到Home Assistant中。

**注意:** 目前，ChatIoT仅支持通过Xiaomi Miot Auto集成接入的小米设备。如果你没有这类设备，或者你只是想体验ChatIoT，你可以使用设备模拟器来模拟设备，创建你的虚拟家庭环境。更多详细信息，请参考[Miot设备模拟指南](./docs/Miot_Device_Setup.md)。

### 2. 大模型API Key获取
ChatIoT基于大型语言模型实现设备控制和创建规则。考虑到难以在本地部署部署大模型服务，目前ChatIoT采用API调用的方式。因此，你需要获取一个大模型API Key。

以下是当前推荐的API列表：

- gpt-3.5-turbo
- gpt-4-turbo
- gpt-4o
- deepseek-chat
- moonshot-v1-8k

我们将很快支持更广泛大模型API类型。


## :hammer_and_wrench: 开始安装
**目前有两种方式部署ChatIoT.**

### :whale: 通过Home Assistant集成部署（推荐）

如果你只是想体验一下ChatIoT，建议通过Home Assistant集成来部署它，可以在HACS商店中直接进行安装和部署。

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&repository=ChatIoT&owner=ifcarpediem)

详细教程参见 [ChatIoT集成安装指南](./docs/ChatIoT_Integration_Setup.md)。

### :computer: 本地部署

如果你想要修改ChatIoT，但又不熟悉Home Assistant的集成部署细节，不希望你的修改受到Home Assistant的影响，你可以选择在本地部署ChatIoT，仅将Home Assistant用作设备接口。

详细教程参见[ChatIoT本地部署指南](./docs/Deploy_Locally_Setup.md)。

## :black_nib: Citation

如果ChatIoT对你的研究发表有帮助，欢迎在文中引用[ChatIoT](https://maestro.acm.org/trk/clickp?ref=z16l2snue3_2-310b8_0x33ae25x01410&doi=3678585)，使用如下BibTeX条目：

```bibtex
@article{gao2024chatiot,
  title={ChatIoT: Zero-code Generation of Trigger-action Based IoT Programs},
  author={Gao, Yi and Xiao, Kaijie and Li, Fu and Xu, Weifeng and Huang, Jiaming and Dong, Wei},
  journal={Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies},
  volume={8},
  number={3},
  pages={1--29},
  year={2024},
  publisher={ACM New York, NY, USA}
}
```
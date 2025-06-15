# ADSketch论文复现项目

## 项目概述

本项目复现了ICSE 2022论文《Adaptive Performance Anomaly Detection for Online Service Systems via Pattern Sketching》中的ADSketch算法。ADSketch是一种基于模式草图技术的自适应性能异常检测方法，在微服务系统的异常检测方面表现出色，具有良好的可解释性和适应性。

### 实验对象 - Online Boutique

本项目基于Google的**Online Boutique**微服务演示应用进行实验验证。Online Boutique是一个云原生的电商微服务系统，具有以下特点：

- **多语言架构**: 由11个用不同编程语言编写的微服务组成
- **真实业务场景**: 包含商品浏览、购物车、支付等完整电商功能
- **微服务通信**: 各服务间通过gRPC进行通信
- **云原生设计**: 完全适配Kubernetes集群部署
- **监控友好**: 内置丰富的性能指标，便于异常检测算法验证

通过在Online Boutique上采集真实的性能数据（CPU使用率、内存占用、响应时间等），我们获得了高质量的时间序列数据用于ADSketch算法的训练和验证。

> **完整项目**: 如需了解包含微服务开发、监控部署、自动化测试等完整功能的项目，请访问：[微服务系统测试与维护实验项目](https://github.com/Zplayerez/Online-Boutique)

## 论文信息

- **论文标题**: Adaptive Performance Anomaly Detection for Online Service Systems via Pattern Sketching
- **会议**: ICSE 2022
- **类型**: KPI Anomaly Detection - Univariate Time Series AD
- **GitHub链接**: [https://github.com/OpsPAI/ADSketch](https://github.com/OpsPAI/ADSketch)

## 算法原理

ADSketch采用离线和在线两个相互协作的阶段实现可解释和自适应的性能异常检测：

### 离线阶段
1. **输入**: 无异常的指标时间序列(基准) + 待检测异常的指标序列
2. **模式发现**: 通过STAMP算法获取最相似的子序列对
3. **图构建**: 基于子序列相似性构建连通图
4. **聚类**: 使用Affinity Propagation算法进行聚类，形成指标模式

### 在线阶段
1. **实时检测**: 利用离线阶段构建的指标模式进行异常检测
2. **自适应学习**: 持续捕获新的模式，适应动态变化环境
3. **解释性输出**: 提供异常预警和相关解释

## 项目安装

### 系统要求
- Python 3.6+
- 内存: 建议8GB以上
- 操作系统: Windows/Linux/macOS
- Git (支持submodule)

### 克隆项目

本项目引用了其他仓库作为子模块，请使用以下方式之一进行克隆：

**方式1：克隆时直接包含子模块（推荐）**
```bash
git clone --recursive https://github.com/Zplayerez/ADSketch.git
```

**方式2：先克隆主仓库，再初始化子模块**
```bash
git clone https://github.com/Zplayerez/ADSketch.git
cd ADSketch
git submodule init
git submodule update
```

### 依赖安装

进入项目目录后安装依赖：

```bash
cd ADSketch
pip install -r requirements.txt
```

主要依赖包括：
- scikit-learn
- stumpy
- pandas
- matplotlib
- networkx
- numpy

### 验证安装

确认子模块已正确加载：
```bash
git submodule status
```

如果显示子模块路径和commit哈希，说明安装成功。

## 数据集准备

### 数据格式
本项目使用类似Yahoo数据集的格式，每个CSV文件包含以下字段：
- `timestamp`: 时间戳
- `value`: 指标值
- `is_anomaly`: 异常标注 (0: 正常, 1: 异常)

### 数据目录结构
```
data/
├── cpu_usage_benchmark/
│   ├── cpu_usage_1.csv
│   ├── cpu_usage_2.csv
│   └── ...
├── memory_usage_benchmark/
├── response_time_benchmark/
└── ...
```

### 支持的指标类型
- CPU使用率 (cpu_usage)
- 内存使用率 (memory_usage)  
- 错误率 (error_rate)
- 延迟 (latency)
- 页面加载时间 (page_load)
- 请求数量 (request_count)
- 响应时间 (response_time)
- 吞吐量 (throughput)

## 运行方法

### 1. 参数配置
编辑 `params.json` 文件配置各指标的参数：

```json
{
  "cpu_usage": {
    "cpu_usage_1": {"m": 5, "p": 99},
    "cpu_usage_2": {"m": 6, "p": 98}
  }
}
```

参数说明：
- `m`: 子序列模式长度 (建议范围: 3-10)
- `p`: 百分位数阈值 (建议范围: 95-99.8)

### 2. 训练和检测

以CPU使用率为例：

```bash
python cpu_usage_demo.py --res_dir ./res/cpu_usage/ --pattern_dir ./offline_metrics/cpu_usage/
```

### 3. 批量运行
对所有指标进行训练：

```bash
# CPU使用率
python cpu_usage_demo.py

# 内存使用率  
python memory_usage_demo.py

# 响应时间
python response_time_demo.py

# 其他指标...
```

## 实验结果

### 性能指标对比

与论文中Yahoo数据集的结果对比：

| 指标 | Precision | Recall | F1 Score |
|------|-----------|--------|----------|
| **论文结果 (Yahoo)** | 0.511 | 0.673 | 0.541 |
| **CPU使用率** | 0.516 | 0.756 | 0.602 |
| **错误率** | 0.507 | 0.861 | 0.622 |
| **延迟** | 0.525 | 0.851 | 0.634 |
| **内存使用率** | 0.513 | 0.798 | 0.608 |
| **页面加载** | 0.510 | 0.773 | 0.594 |
| **请求数量** | 0.488 | 0.735 | 0.565 |
| **响应时间** | 0.505 | 0.880 | 0.629 |
| **吞吐量** | 0.533 | 0.866 | 0.640 |

### 结果分析
- 在8个关键指标上均达到或超过论文基准效果
- Recall指标表现突出，说明异常检测覆盖率高
- F1 Score整体提升，验证了算法的有效性

## 输出文件

### 1. 训练日志
```
logs/
├── cpu_usage_demo.log
├── memory_usage_demo.log
└── ...
```

### 2. 结果文件
```
res/
├── cpu_usage/
│   ├── cpu_usage_results.csv  # 详细结果
│   └── *.png                  # 可视化图表
└── ...
```

### 3. 模式文件
```
offline_metrics/
├── cpu_usage/
│   └── *.pkl                  # 学习到的模式
└── ...
```

## 可视化结果

运行后会生成时间序列可视化图表：
- 蓝色线条：原始时间序列
- 绿色区域：标注的异常点
- 红色区域：模型检测的异常点

## 模型优化

### 传统ADSketch的局限性
1. 只能检测异常，无法提供解释
2. 参数m和p需要手动调优

### 我们的改进方案
引入大语言模型(LLM)增强：

1. **多模态输入**: 结合时间序列、日志信息、指标数据
2. **智能解释**: LLM分析异常原因并提供推理
3. **自动调参**: LLM推荐最优的m和p参数值

### 改进效果
- 提供异常的业务层面解释
- 动态优化参数配置
- 提升检测准确率和实用性

## 故障排除

### 常见问题

1. **内存不足错误**
   - 减少数据集大小或增加系统内存
   - 调整batch_size参数

2. **依赖包版本冲突**
   - 使用虚拟环境: `python -m venv adsketch_env`
   - 严格按照requirements.txt安装

3. **数据格式错误**
   - 确保CSV文件包含必需字段
   - 检查时间戳格式和数据类型

4. **参数设置问题**
   - m值建议从5开始，根据数据特点调整
   - p值通常设为99，可根据异常比例调整

## 项目结构

```
adsketch/
├── src/
│   ├── adsketch/
│   │   ├── motif_operations.py    # 核心算法
│   │   └── ...
│   ├── dataset_loader.py          # 数据加载
│   ├── cpu_usage_demo.py         # CPU使用率训练脚本
│   ├── memory_usage_demo.py      # 内存使用率训练脚本
│   └── ...
├── data/                         # 数据目录
├── logs/                         # 日志目录
├── res/                          # 结果目录
├── offline_metrics/              # 模式存储目录
├── params.json                   # 参数配置
├── requirements.txt              # 依赖包
└── README.md                     # 本文件
```

## 贡献者

本项目由南开大学软件学院团队完成：
- 谢国欢、薛晓康：数据采集与监控
- 钟健、李功臣：测试工具与微服务开发  
- 钟亚伟、黄依乔：论文复现与模型优化

## 许可证

本项目遵循MIT许可证。

## 引用

如果您使用了本项目的代码，请引用原始论文：

```bibtex
@inproceedings{adsketch2022,
  title={Adaptive Performance Anomaly Detection for Online Service Systems via Pattern Sketching},
  booktitle={Proceedings of the 44th International Conference on Software Engineering},
  year={2022}
}
```

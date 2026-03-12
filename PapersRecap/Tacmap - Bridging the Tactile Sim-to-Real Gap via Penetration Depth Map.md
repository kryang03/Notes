---
tags:
  - paper
  - tactile
  - sim-to-real
  - in-hand-manipulation
aliases:
  - Tacmap
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (Sharpa / HKUST / NVIDIA)
related:
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
---

# Tacmap: Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map

> [!abstract] 核心贡献
> 提出 **Tacmap**，一种基于**穿透深度图 (Penetration Depth Map)** 的统一触觉仿真框架，将仿真域和真实域对齐到共享的几何形变空间。支持平面和**曲面指尖**传感器，计算效率足以支撑大规模 RL，并在手内旋转任务上实现零样本 sim-to-real 迁移。

> [!tip] 与理论基础的关联
> - [[SignalProcessing#3.1 光度立体视觉]] — 视觉触觉传感器 (GelSight/DIGIT) 的形变重建
> - [[ComputationalGeometry#4. 有向距离场]] — 穿透深度场作为接触几何的统一表示
> - [[ReinforcementLearning#5. Sim-to-Real]] — 触觉 sim-to-real 零样本迁移
> - [[ContactMechanics]] — 弹性体接触变形建模
>
> **核心技术**: Penetration Depth Map, Normal-Projection Rendering, Automated Data Collection Rig, Deform Map Translation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
不仿真复杂的光学效应，而是将仿真和真实都投射到**几何穿透深度图**这一统一中间表示上——在仿真中用高效几何计算生成，在真实中用学习模型从原始图像转换。

### 领域定位
- **触觉仿真三类方法**: 经验-数据驱动 (Taxim) → 解析-深度缓冲 (TACTO) → 物理-FEM (高精度但慢)
- **Tacmap 的定位**: 几何一致 + 计算高效——兼具 FEM 的物理忠实性和深度缓冲的速度

### 关键创新
1. **统一表示**: 穿透深度图作为 sim 和 real 的共享变形空间
2. **几何无关**: 在局部法向投影空间中计算，天然支持曲面指尖（拟人手）
3. **自动标定装置**: 自动化数据采集平台测量真实世界 ground-truth 变形
4. **零样本迁移**: RL 策略在仿真训练，直接部署到实物灵巧手完成手内旋转

## 2. 对灵巧操作的启发 (Implications)

- 穿透深度图与 [[ComputationalGeometry#4. 有向距离场]] 中的 SDF 概念同源——都是用标量场描述接触几何
- 为 DNPM 项目中触觉作为状态估计提供了高效 sim-to-real 方案
- 支持曲面指尖的能力直接适用于拟人灵巧手

## 3. 演进脉络定位 (Evolution Context)

```
TACTO (depth buffer, 低精度) → Taxim (data-driven, 泛化差)
    ↓
Tacmap (geometry-consistent penetration depth, 统一表示)
    ↓
后续: 可微触觉渲染 + RL 联合优化
```

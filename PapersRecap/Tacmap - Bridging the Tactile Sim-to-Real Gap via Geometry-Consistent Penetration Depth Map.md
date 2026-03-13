---
tags:
  - paper
  - tactile-sensing
  - sim-to-real
  - manipulation
aliases:
  - Tacmap
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
related:
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ReinforcementLearning]]"
---

# Tacmap: Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map

> [!abstract] 核心贡献
> 提出统一的 deform map 表征作为触觉仿真与真实世界的"公共几何空间"，通过体积穿透深度计算（无需 FEM）实现高保真+高效率的触觉仿真，在 Isaac Lab 中支持大规模并行训练，并实现灵巧手 in-hand rotation 的 zero-shot sim-to-real 迁移。

## 1. 问题设定与动机

视觉触觉传感器 (VBTS, GelSight/DIGIT) 的 sim-to-real gap 三难困境：

| 方法类别 | 代表 | 保真度 | 效率 |
|---------|------|--------|------|
| 经验方法 | Taxim | 依赖数据分布 | 中 |
| 解析方法 | TACTO | 低（简化深度渲染） | 高 |
| 物理方法 | TacEx, Taccel | 高（FEM/IPC） | 低 |

**核心洞察**: 原始触觉图像是传感器特定的（光学复杂），但底层 **deform map** 是通用的接触物理代理。

## 2. 核心方法

### 2.1 统一 Deform Map 表征

**仿真端**: 不做 FEM，而是沿传感器表面法线投射射线，计算刚体与弹性体的 3D 穿透深度：

$$d(u,v) = \max(0, z_s - \max(z_u, z_o))$$

- $z_s$: 感知面坐标, $z_u$: 未变形面坐标, $z_o$: 物体交点坐标
- 支持 **曲面指尖** — 在法线空间计算，消除平面假设的投影畸变

**真实端**: 自动化数据采集台（3轴精密运动台）→ 结构光压入 → 配对数据集 $\{I_\text{raw}, M_\text{gt}\}$ → ResNet encoder-decoder 学习 Image→Deform Map 映射

### 2.2 三流触觉信息

| 信号 | 仿真获取 | 真实获取 |
|------|---------|---------|
| 净力 $F$ | 物理引擎接触传感器 | 力传感器监督的 ResNet 回归 |
| 接触位置 $P$ | 引擎报告精确位置 | Deform map 有效区域几何质心 |
| Deform Map $M$ | 穿透深度射线投射 | Image→Deform 翻译网络 |

### 2.3 集成与训练

- 集成至 **Isaac Lab** 和 **MuJoCo**
- 全 GPU 管线，与物理引擎同步
- PPO 训练 in-hand rotation，观测包含实时 Tacmap 流

## 3. 实验结果

**Sim-to-Real 几何一致性**:

| 物体 | 接触位置误差 | 变形深度误差 | 力 L2 误差 | Deform IoU |
|------|:-----------:|:-----------:|:----------:|:----------:|
| Square | 0.66mm | 18.53% | 0.28N | 88.21% |
| Cylinder | 0.96mm | 14.71% | 0.61N | 85.67% |

**计算效率**:
- GPU 内存线性增长（射线投射 vs FEM 指数增长）
- 8192 并行环境下仍保持合理渲染频率
- 触觉渲染对仿真速度的影响可忽略

**Zero-shot Sim-to-Real**: SharpaWave 灵巧手成功执行 in-hand rotation（球体），无任何真实世界微调。

## 4. 核心洞见 (Insights)

1. **几何抽象胜过光学模拟**: 通过 deform map 解耦传感器光学特性 → sim-to-real gap 的本质是接触几何而非视觉外观
2. **穿透深度作为通用表征**: 与 SDF（[[ComputationalGeometry#Signed Distance Field|签名距离场]]）思想类似 — 用标量场描述接触状态
3. **法线空间投影**: 支持曲面指尖的关键创新 → 对拟人灵巧手至关重要（现有方法多假设平面传感器）
4. **效率-保真平衡**: 射线投射介于解析着色器和 FEM 之间 → 实现了 RL 可用的触觉仿真

## 5. 与知识体系的联系

### 与 [[ContactMechanics]] 的联系
- 穿透深度直接关联接触力学：$d(u,v)$ 是接触压力分布的几何代理
- 与 [[ContactMechanics#Hertz 弹性接触理论|Hertz 理论]] 中穿透量 $\delta$ 概念直接对接
- Deform IoU > 85% 意味着仿真接触流形与真实世界高度一致

### 与 [[SignalProcessing]] 的联系
- Image→Deform Map 翻译网络本质是触觉信号的域适应/逆问题
- 从光学伪影中恢复几何信息 → 与触觉信号处理直接相关

### 与 [[ComputationalGeometry]] 的联系
- 射线投射 + 法线投影 → 经典的 ray-mesh intersection 优化
- Deform map 作为 2.5D 表征 → 与深度图、SDF 同族

### 与 [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|Sim-to-Real]] 的联系
- 触觉 sim-to-real gap 是 [[ReinforcementLearning#MDP Gap 四要素分类|MDP Gap]] 中 **State Gap** 的子问题 — 传感器域移位
- Zero-shot 迁移验证了统一表征空间对消除域移位的有效性

## 6. 局限与未来方向

- 仅建模法向穿透深度，不含切向力/剪切应变 → incipient slip 检测受限
- 仅在球体 in-hand rotation 上验证 zero-shot 迁移，更复杂任务待测
- 射线投射随物体网格复杂度增加而变慢 → 需要加速结构
- 数据采集依赖定制化硬件台 → 新传感器需重新标定

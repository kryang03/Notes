---
tags:
  - WMTS
  - index
---

# WMTS 相关论文索引

> 本索引按照与 [[Final_WMTS]] 项目的关联维度进行分类，每篇论文均有独立 Recap 文件。

## 一、World Model 核心方法

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[DiWA- Diffusion Policy Adaptation with World Models Recap\|DiWA]] | 冻结 WM + Dream Diffusion MDP 微调 Diffusion Policy | **直接启发 WMTS §五选择二**：WM 隐空间内 PPO 微调 Diffusion |
| [[DyWA Recap\|DyWA]] | Dynamics-adaptive World Action Model，联合预测动作和未来状态 | 启发 WMTS 的 World Action Model 范式 + FiLM 动力学条件化 |
| [[Dreamer Recap\|Dreamer (DREAM TO CONTROL)]] | 隐空间想象训练策略（Latent Imagination） | WMTS WM 隐空间 rollout 的理论基础 |
| [[DayDreamer Recap\|DayDreamer]] | 首个真机 WM 学习框架，1 小时真机数据学会行走 | 启发 WMTS 真机 WM 微调流程 |
| [[STORM Recap\|STORM]] | Stochastic Transformer WM，离散 token 实现高效长 horizon | Transformer WM 架构参考 |
| [[MoDem-V2 Recap\|MoDem-V2]] | 真机视觉-运动 WM + 14 分钟真机数据 | 真机 WM 数据效率参考 |
| [[Deep Dynamics Models Recap\|PDDM]] | 深度动力学模型 + MPC 在线规划实现灵巧操作 | 启发 WMTS Ensemble WM + MPC 范式 |
| [[Model-Based Lookahead RL Recap\|MB Lookahead]] | 混合 MFRL+MBRL，MPC 式轨迹评估引导策略 | 启发 WMTS WM Safety Checker |
| [[DexSim2Real2 Recap\|DexSim2Real2]] | 主动交互建模显式 WM + MPC + Eigengrasp | 启发 WMTS 显式 WM + 降维动作空间 |
| [[Robotic World Model Recap\|RWM]] | 自回归 WM + 历史上下文长 horizon 预测 | WM 自回归训练范式参考 |
| [[World4RL Recap\|World4RL]] | Diffusion WM 用于 RL 策略精炼 | WM 预测架构（Diffusion 作为动力学模型） |
| [[Finetuning Offline WM Recap\|FOWM]] | 离线 WM 真机在线微调 | 启发 WMTS Actuator Model 在线适应 |
| [[SafeDreamer Recap\|SafeDreamer]] | 安全约束 + WM imagination | WMTS Safety Checker 的理论支撑 |

## 二、灵巧操作方法

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[DeXtreme Recap\|DeXtreme]] | 大规模 DR + 视觉 Sim-to-Real 灵巧手 reorientation | DR 策略 + Sim-to-Real 管线参考 |
| [[DexReMoE Recap\|DexReMoE]] | MoE 框架跨形状泛化 in-hand reorientation | MoE 泛化架构参考 |
| [[DEXTERITYGEN Recap\|DexterityGen]] | Foundation Controller 统一灵巧操作 | 通才-专才范式参考 |
| [[From Simple to Complex Skills Recap\|DexHier]] | 层次策略复用预训练旋转技能 | 层次策略 + 技能复用参考 |
| [[Solving Rubiks Cube Recap\|OpenAI Rubik's Cube]] | ADR 自动域随机化 + 灵巧手解魔方 | ADR 自动课程 + 极限 DR 参考 |
| [[Generalization in Dexterous Manipulation Recap\|Geometry-Dex]] | 点云多任务学习 100+ 物体泛化 | PointNet 物体表征 + 多任务泛化 |
| [[UniDexGrasp++ Recap\|UniDexGrasp++]] | GeoCurriculum + 通才-专才迭代学习 | **直接启发 WMTS 通才-专才框架** |
| [[World Models for Dexterous Hand-Object Recap\|WM4Dex]] | 人类视频学习灵巧 hand-object 交互 WM | 人类视频 WM 预训练参考 |

## 三、Sim-to-Real 与足式机器人

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[ANYmal Parkour Recap\|ANYmal Parkour]] | 四足跑酷 + Actuator Network 建模 | **直接启发 WMTS Actuator Model** |
| [[Learning Agile Locomotion Recap\|ETH Locomotion]] | Actuator Network + 全流程 Sim-to-Real | Actuator Network 经典范式 |
| [[Learning to Walk 3min Recap\|Semi-structured Dynamics]] | 3 分钟真机数据 + 半结构化动力学模型 | 启发 WMTS 物理先验 + 残差学习 |
| [[Sim-to-Real Agile Locomotion Recap\|Sim2Real Locomotion]] | 大规模仿真 + 域随机化四足 Sim-to-Real | DR 方法论参考 |

## 四、扩散策略与模仿学习

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[Diffusion Policy Recap\|Diffusion Policy]] | Diffusion 去噪过程作为策略输出 | **WMTS 通才策略核心架构** |
| [[HG-DAgger Recap\|HG-DAgger]] | 人类门控安全 DAgger | 安全数据收集参考 |
| [[Beyond Human Demonstrations Recap\|Diffusion RL for VLA]] | Diffusion RL 生成 VLA 训练数据 | Diffusion RL 微调启发 |

## 五、课程学习与探索

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[Curiosity-Driven Exploration Recap\|Latent Bayesian Surprise]] | 贝叶斯隐空间好奇心驱动探索 | 启发 WMTS Ensemble Disagreement |
| [[Curious Exploration via Structured WM Recap\|Plan2Explore]] | 结构化 WM + 好奇心探索 zero-shot 操作 | WM 探索 + zero-shot 迁移参考 |
| [[Prioritized Level Replay Recap\|PLR]] | 优先级环境回放课程学习 | 启发 WMTS 任务生成优先级 |
| [[Improving Policy Optimization GSL Recap\|GSL]] | 通才-专才学习提升策略优化 | **直接启发 WMTS Oracle-Generalist 架构** |

## 六、理论与工具

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[CMA-ES Tutorial Recap\|CMA-ES Tutorial]] | 协方差矩阵自适应进化策略 | **WMTS 隐空间任务生成器核心算法** |
| [[Rotation Representations Recap\|6D Rotation]] | 连续旋转表示 (5D/6D) | **WMTS 任务空间旋转表示** |
| [[FLD Recap\|FLD]] | 傅里叶隐空间动力学表征 | 运动表征编码参考 |
| [[IS ATTENTION REQUIRED FOR ICL Recap\|Attention & ICL]] | 注意力与 In-Context Learning 关系 | WM 架构选择理论支撑 |
| [[The Latent Space Recap\|Latent Space Survey]] | 隐空间基础、演进与能力综述 | WMTS 隐空间设计理论参考 |

## 七、综述

| 论文 | 核心贡献 | 与 WMTS 的关键关联 |
|-----|---------|------------------|
| [[A Step Toward World Models Survey Recap\|WM Survey (Manipulation)]] | 机器人操作视角的 WM 综述 | WMTS 方法论定位参考 |
| [[Learning to Model the World Survey Recap\|WM Survey (General)]] | AI WM 全景综述（四大范式） | WM 分类学参考 |
| [[World Models Computing the Uncomputable Recap\|WM Essay]] | WM 哲学：固定代价前向传播模拟世界 | WMTS 动机的概念性支撑 |

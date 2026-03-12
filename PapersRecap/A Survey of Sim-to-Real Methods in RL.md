---
tags:
  - paper
  - sim-to-real
  - reinforcement-learning
  - survey
aliases:
  - Sim2Real Survey
  - AwesomeSim2Real
paper-year: 2025
read-date: 2026-03-05
venue: arXiv (2502.13187)
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
---

# A Survey of Sim-to-Real Methods in RL: Progress, Prospects and Challenges with Foundation Models

> [!abstract] 核心贡献
> 首个以 **MDP 四元素 (S, A, T, R)** 为分类框架的 Sim-to-Real 综述，系统梳理了从经典方法到 Foundation Model 增强策略的全谱系技术。提供 GitHub 资源库持续更新: [AwesomeSim2Real](https://github.com/LongchaoDa/AwesomeSim2Real)

## 1. 问题设定与动机

**Sim-to-Real Gap 的形式化定义**:

$$G(\pi) := \psi_s(\pi_{si}) - \psi_r(\pi_{si}) \big|_{\pi_{si} \sim \mathcal{M}_s}$$

其中 $\psi$ 是任意性能指标，$\mathcal{M}_s / \mathcal{M}_r$ 分别为仿真/真实 MDP。

Gap 来源分解为 MDP 四元素差异：
- **$\Delta_S$ (Observation)**: 传感器噪声、部分可观、特征分布不匹配
- **$\Delta_A$ (Action)**: 动作粒度 (离散vs连续)、系统延迟 $\Delta_{system}$
- **$\Delta_T$ (Transition)**: 物理动力学差异 $P_s(s_{t+1}|s_t, a_t) \neq P_r(s_{t+1}|s_t, a_t)$
- **$\Delta_R$ (Reward)**: 奖励函数基于仿真设计，未覆盖真实场景

## 2. 核心方法/理论

### 2.1 Observation Gap 解决方案

| 方法类别 | 核心思路 | 代表工作 |
|---------|---------|---------|
| **Domain Randomization** | 随机化视觉参数（纹理/光照/相机），训练鲁棒策略 | ADR (课程化随机化) |
| **Domain Adaptation** | 对齐仿真/真实特征分布（对抗训练、嵌入对齐） | Bi-directional DA, VR-Goggles |
| **Sensor Fusion** | 多传感器融合（视觉+深度+LiDAR）补偿单模态局限 | 多传感器GPS+惯性 |
| **Foundation Models** | VLM 提供语义锚点，作为跨域不变特征 | 语义描述作为统一信号 |

### 2.2 Action Gap 解决方案

| 方法类别 | 核心思路 |
|---------|---------|
| **Action Space Scale** | 子目标模型弥合离散→连续间隙，层次化动作空间 |
| **Action Delay** | 多步预测、延迟感知 MDP、帧跳过策略 |
| **Action Uncertainty** | 动作噪声建模、概率动作空间 |
| **Foundation Models** | LLM 推理动作语义，辅助动作空间设计 |

### 2.3 Transition Gap 解决方案（最核心）

| 方法类别 | 核心思路 | 关键方法 |
|---------|---------|---------|
| **Domain Randomization** | 随机化物理参数（摩擦、力矩等） | 主动域随机化 (ADR) — 优先训练最困难配置 |
| **Domain Adaptation** | 对齐仿真/真实动力学分布 | 对抗训练最小化转移动力学差异 |
| **Grounding Methods** | 用真实数据修正仿真器动作映射 | GAT → SGAT → RGAT → GARAT 演进 |
| **Distributionally Robust RL** | 设计对转移偏移鲁棒的策略 | Off-dynamics RL, 线性 f-散度正则化 |
| **LLM-Enhanced** | LLM 改善正向模型的真实动力学预测 | LLM-informed inverse model |

> [!tip] Grounding Methods 演进脉络
> **GAT** (AAAI 2017, 确定性动作变换)
> → **SGAT** (引入随机性，概率化 next-state 建模)
> → **RGAT** (用 RL 直接学习 grounding 作为端到端问题)
> → **GARAT** (生成对抗方法，IfO 框架)
>
> 这条线与 [[sim2real]] 中讨论的硬件建模 Gap 互补——Grounding 修正软件模型，硬件分析修正物理参数范围。

### 2.4 Reward Gap 解决方案

- **Reward Shaping**: 人工设计或辅助奖励信号引导仿真外行为
- **LLM-Based Reward Design**: [[EUREKA]] 式 LLM 自动生成奖励函数

## 3. 实验结果

本文为综述性论文，不含新实验。提供了：
- **完整的基准/代码库汇总表**
- **按领域分析**: 机器人操作 / 自动驾驶 / 交通信号控制 / 推荐系统 / 医疗（各领域 Sim-to-Real 特殊挑战）
- **评估指标形式化**: 成功率、轨迹偏差、策略性能落差

## 4. 核心洞见 (Insights)

1. **MDP 分解框架的实用性**: 将 Sim-to-Real Gap 按 S/A/T/R 分解，使研究者可以精确定位问题来源并选择对应方案
2. **Foundation Models 横跨全部四个维度**: LLM/VLM 不仅用于奖励设计，在观测对齐、动作语义、动力学预测中均有潜力
3. **Grounding 与 Randomization 是互补而非竞争关系**: DR 扩大策略鲁棒范围，Grounding 精准修正系统模型
4. **硬件层面的 Gap 未被充分讨论**: 综述主要关注软件策略层面，但电机/减速器/传动的非理想特性（参见 [[sim2real]]）在 Transition Gap 中占重要角色

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- MDP 形式化定义与 Sim-to-Real Gap 的理论框架直接扩展了 RL 基础
- Domain Randomization 技术归属于 [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|RL Sim-to-Real]] 范畴
- Distributionally Robust RL 与 robust MDP 理论相关

### 与 [[Dynamics]] 的联系
- Transition Gap 的本质是仿真动力学 $P_s$ 与真实动力学 $P_r$ 的差异
- 接触动力学 (摩擦、碰撞) 是机器人 Sim-to-Real 中 Transition Gap 的主要来源

### 与 [[ControlTheory]] 的联系
- Action Delay 分析与控制频率 / 执行延迟密切相关
- 阻抗控制的参数化动作空间可缓解 Action Gap

### 与 [[EmbodiedAI]] 的联系
- Foundation Model 在 Sim-to-Real 中的应用代表了 VLA/VLM 与具身智能的交叉前沿

## 6. 局限与未来方向

1. **硬件-软件联合建模**: 综述缺乏对执行器物理特性 (电气时间常数、齿隙、非线性摩擦) 的讨论——这正是 [[sim2real]] 和机械结构笔记所覆盖的内容
2. **多域联合迁移**: 同时处理 Observation + Transition Gap 的联合方法尚不成熟
3. **在线适应与安全**: 部署时在线修正策略的安全保证仍需加强
4. **领域特异性**: 不同应用领域的 Sim-to-Real 挑战差异巨大，通用方案可能不存在

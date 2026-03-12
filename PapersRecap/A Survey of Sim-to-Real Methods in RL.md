---
tags:
  - paper
  - survey
  - sim-to-real
  - reinforcement-learning
  - foundation-models
aliases:
  - Sim-to-Real Survey 2025
  - Da et al. Sim2Real Survey
paper-year: 2025
read-date: 2026-03-13
venue: arXiv (Arizona State University / DARPA)
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
---

# A Survey of Sim-to-Real Methods in RL - Progress, Prospects and Challenges with Foundation Models

> [!abstract] 核心贡献
> 首个以 **MDP 四要素 (State/Action/Transition/Reward)** 为分类框架的 sim-to-real 综述，覆盖经典方法到 Foundation Model 时代的前沿技术，并提供 AwesomeSim2Real 开源资源库持续追踪。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — Sim-to-real 分类体系，直接整合到 Foundation
> - [[EmbodiedAI]] — Foundation Model 赋能 sim-to-real 的新范式

## 1. MDP 分类框架 (核心整理价值)

### Observation Gap 方法
| 方法 | 代表工作 | 核心思路 |
|------|---------|---------|
| Domain Randomization | DR, ADR | 视觉随机化使策略对感知差异鲁棒 |
| Domain Adaptation | CycleGAN, SimGAN | 图像风格迁移对齐 sim/real 分布 |
| Sensor Fusion | 多模态融合 | 利用互补传感器弥补单一模态差异 |
| Foundation Models | VLM 特征提取 | 预训练视觉编码器提供域不变表征 |

### Action Gap 方法
| 方法 | 代表工作 | 核心思路 |
|------|---------|---------|
| Action Space Scaling | 离散化/缩放 | 降低动作空间维度或限制范围 |
| Action Delay Modeling | [[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]], [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|Action Persistence]] | 建模执行延迟对策略的影响 |
| Action Uncertainty | stochastic policies | 增加动作噪声鲁棒性 |

### Transition Gap 方法
| 方法 | 代表工作 | 核心思路 |
|------|---------|---------|
| Domain Randomization | 动力学参数随机化 | 使策略对动力学差异鲁棒 |
| Domain Adaptation | GAN, latent alignment | 对齐 sim/real 转移分布 |
| Grounding Methods | [[Grounded Action Transformation\|GAT]], SysID | 修正仿真器匹配真实 |
| Distributionally Robust RL | DRPO | 优化最坏情况下的迁移性能 |

### Reward Gap 方法
| 方法 | 代表工作 | 核心思路 |
|------|---------|---------|
| Reward Shaping | heuristic, potential-based | 设计促迁移的奖励 |
| LLM-Based Reward | [[EUREKA: Human-Level Reward Design via Coding Large Language Models\|EUREKA]] | LLM 生成奖励代码 |

## 2. Foundation Model 时代的新趋势

- **VLM 作为视觉骨干** — 预训练编码器提供域不变视觉特征
- **LLM 奖励设计** — EUREKA 范式: LLM 编写 + 环境反馈迭代
- **World Model** — Foundation model 作为可微仿真器替代品

## 3. 资源
- GitHub: `github.com/LongchaoDa/AwesomeSim2Real` (持续更新)

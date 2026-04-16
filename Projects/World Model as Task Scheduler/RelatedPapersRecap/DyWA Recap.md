---
tags: [paper, world-model, non-prehensile, WMTS]
aliases: [DyWA]
paper-year: 2025
venue: PKU/Galbot
related: ["[[ReinforcementLearning]]", "[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[DyWA: Dynamics-adaptive World Action Model.pdf]]"
---

# DyWA: Dynamics-adaptive World Action Model

> [!abstract] 核心贡献
> 提出 **World Action Model** 概念：策略网络联合预测动作与未来状态，通过 **Dynamics Adaptation Module**（历史轨迹编码物理属性）实现跨动力学条件泛化，单目点云下 non-prehensile 操作成功率提升 31.5%。

## 核心方法

1. **World Action Model**：联合预测动作 $A_t^s$ 和下一步状态 $\hat{f}^O_{t+1}$，引入额外监督信号超越纯模仿
2. **Dynamics Adaptation Module**：编码历史 $(O, A)$ 对，解码为隐动力学嵌入 $z^{Phy}_t$，通过 **FiLM 条件化**注入策略
3. **Teacher-Student 蒸馏**：RL teacher（全点云 + 物理参数特权）→ 视觉 student（单视角部分点云）
4. **可变阻抗控制器**：适应接触丰富操作的力交互

## 关键设计

$$\mathcal{L} = \mathcal{L}_{imitation} + \lambda_1 \mathcal{L}_{world} + \lambda_2 \mathcal{L}_{adaptation}$$

- FiLM 条件化：$\gamma \cdot h + \beta$，其中 $(\gamma, \beta) = \text{MLP}(z^{Phy}_t)$

## 关键结果

- 仿真：比 baseline 提升 31.5% 成功率（单视角点云）
- 真机：68% 平均成功率，泛化跨物体形状、桌面摩擦、非均匀质量分布
- Zero-shot Sim-to-Real 迁移

## 与 WMTS 的关联

- **World Action Model 范式**与 WMTS 的 Ensemble WM 互补：DyWA 将 WM 能力集成到策略内部，WMTS 将 WM 作为独立模块
- **Dynamics Adaptation Module** 类比 WMTS 的 DR encoder $g_{enc}$ —— 两者都从历史观测推断隐物理参数
- **FiLM 条件化**可用于 WMTS 的 Actuator Model 温度/速度条件注入
- **局限**：DyWA 仅处理 arm manipulation，未涉及灵巧手的高维关节和 actuator 非线性

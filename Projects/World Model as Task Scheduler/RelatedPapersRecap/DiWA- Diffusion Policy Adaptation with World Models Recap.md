---
tags: [paper, world-model, diffusion-policy, WMTS]
aliases: [DiWA]
paper-year: 2025
related: ["[[ReinforcementLearning]]", "[[StochasticProcess]]", "[[Final_WMTS]]"]
paper-pdf: "[[DiWA- Diffusion Policy Adaptation with World Models.pdf]]"
---

# DiWA: Diffusion Policy Adaptation with World Models

> [!abstract] 核心贡献
> 首个完全离线框架：冻结预训练 WM，在其隐空间内构造 **Dream Diffusion MDP**，用 PPO (DPPO) 微调预训练 Diffusion Policy，无需任何真实/仿真环境交互。

## 核心方法

1. **World Model 训练**：从无标签 play 数据学习隐空间动力学（RSSM 架构）
2. **Diffusion Policy 预训练**：专家演示上行为克隆，条件为 WM 编码的隐状态
3. **奖励估计**：训练成功分类器（Success Verifier）作为 reward signal
4. **Dream Diffusion MDP**：将 Diffusion 去噪过程嵌入 WM MDP，每个去噪步 $k$ 视为 MDP 中的一步动作，PPO 直接在此 MDP 上优化

## 关键公式

$$\bar{a}^{k-1}_t \sim \pi_\theta(\bar{a}^{k-1}_t | s_t, \bar{a}^k_t), \quad k = K, K-1, \ldots, 1$$

WM 转移在隐空间完成：$\hat{s}_{t+1} \sim p_\phi(\cdot | s_t, a_t)$

## 关键结果

- CALVIN benchmark 上显著优于纯 BC baseline
- Zero-shot 真机部署：完全在 WM dream 中微调的策略可直接部署真机
- 样本效率：不需要额外真机/仿真交互

## 与 WMTS 的关联

- **直接启发 §五选择二**：WMTS 提出的"冻结 WM 作为物理引擎 + PPO 微调 Diffusion"方案与 DiWA 框架高度一致
- **风险启示**：DiWA 同样面临 PPO Exploit WM 漏洞的风险（对抗性动作），WMTS 中已识别此问题
- **Success Verifier** 可类比 WMTS 的 Discrepancy-Aware Success Predictor
- **局限**：DiWA 用的是 manipulation 任务，未考虑 actuator 非线性；WMTS 需要处理更复杂的 Sim-to-Real gap

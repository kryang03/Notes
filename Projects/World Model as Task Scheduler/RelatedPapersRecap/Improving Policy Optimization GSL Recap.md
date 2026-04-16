---
tags: [paper, generalist-specialist, curriculum, WMTS]
aliases: [GSL, Generalist-Specialist]
paper-year: 2022
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Improving Policy Optimization with Generalist-Specialist Learning.pdf]]"
---

# Improving Policy Optimization with Generalist-Specialist Learning

> [!abstract] 核心贡献
> 提出 Generalist-Specialist Learning (GSL) 框架：专才（Specialist）在子任务上训练到极致，通才（Generalist）蒸馏所有专才知识并覆盖全任务分布。迭代进行，通才识别弱点 → 新专才攻克 → 再蒸馏。

## 核心方法

1. **Specialist Training**：在特定任务/物体/条件上用 RL 训练到最优
2. **Generalist Distillation**：将所有 Specialist 的 rollout 数据用 BC 蒸馏到一个通才
3. **迭代循环**：通才在新任务上测试 → 发现表现差的区域 → 训练新 Specialist → 再蒸馏

## 与 WMTS 的关联

- **直接启发 WMTS Oracle-Generalist 架构（§二→§三）**：WMTS 的 Oracle（PPO 特权策略）= Specialist，Generalist（Diffusion Policy）= 蒸馏后的通才
- **WMTS 的改进**：
  - GSL 的专才是固定任务集；WMTS 用 CMA-ES + VAE 主动生成新任务（§一隐空间任务生成器）
  - GSL 的通才是简单 MLP；WMTS 用 Diffusion Policy 处理多模态动作
  - WMTS 增加了 WM 作为 Safety Checker + Curiosity 探索信号

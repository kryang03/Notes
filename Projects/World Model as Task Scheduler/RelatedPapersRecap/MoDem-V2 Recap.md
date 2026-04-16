---
tags: [paper, world-model, real-robot, WMTS]
aliases: [MoDem-V2]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation.pdf]]"
---

# MoDem-V2: Visuo-Motor World Models for Real-World Robot Manipulation

> [!abstract] 核心贡献
> 仅 14 分钟真实世界数据，通过视觉-运动 WM 实现真机操作。结合 model-based imagination 和 model-free 微调，在真机 manipulation 上达到 SOTA 数据效率。

## 核心方法

- 视觉编码器 + 隐空间 WM (RSSM 变体)
- 少量人工演示 warm-start → WM imagination 训练策略 → 真机交互 fine-tune
- 关键 trick：demo-guided exploration + model ensemble for exploration bonus

## 与 WMTS 的关联

- **数据效率标杆**：WMTS 真机阶段应以类似数据效率为目标
- **Demo warm-start** 类比 WMTS 的 Oracle 蒸馏阶段——都是用高质量数据初始化，再 WM dream 精炼
- **视觉 WM**：WMTS 当前设计基于 proprioceptive + tactile，未来可扩展到 MoDem-V2 的视觉路线

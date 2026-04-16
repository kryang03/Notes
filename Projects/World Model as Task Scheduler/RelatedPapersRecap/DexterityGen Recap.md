---
tags: [paper, dexterous-manipulation, generation, WMTS]
aliases: [DexterityGen]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Optimization]]", "[[Final_WMTS]]"]
paper-pdf: "[[DEXTERITYGEN: GENERATIVE DEXTEROUS GRASPING IN LARGE SCALE.pdf]]"
---
# DEXTERITYGEN: Generative Dexterous Grasping in Large Scale
> [!abstract] 核心贡献
> 大规模生成式灵巧抓取：用 CVAE/Diffusion 生成灵巧手抓取姿态，对数千物体类别泛化。

## 与 WMTS 关联
- **生成式任务设计**思路与 WMTS 的 CVAE Task Generator（§一）一致：用生成模型探索灵巧任务空间
- 大规模物体泛化的成功为 WMTS 多物体多任务方向提供信心
- CVAE 架构参考：条件编码 + 任务解码的设计模式

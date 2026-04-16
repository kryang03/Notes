---
tags: [paper, dexterous-manipulation, curriculum, WMTS]
aliases: [UniDexGrasp++]
paper-year: 2023
venue: ICCV
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning.pdf]]"
---

# UniDexGrasp++: Geometry-aware Curriculum and Iterative Generalist-Specialist Learning

> [!abstract] 核心贡献
> 提出 GeoCurriculum（几何感知课程学习）+ GiGSL（几何感知迭代通才-专才学习），在 3000+ 物体上达到 85.4% 灵巧抓取成功率。

## 核心方法

- **GeoCurriculum**：按物体几何难度排序进行课程学习
- **GiGSL**：迭代训练专才（子集物体）→ 蒸馏到通才 → 通才在新物体上测试 → 再训专才，循环
- 点云 + 本体感受作为观测

## 与 WMTS 的关联

- **直接启发 WMTS 通才-专才框架**：GiGSL 是 GSL 在灵巧操作中的验证
- GeoCurriculum 的**几何感知**排序可用于 WMTS 物体形状的课程设计
- **WMTS 的改进**：UniDexGrasp++ 是纯 model-free；WMTS 引入 WM 作为动力学先验和 Safety Checker

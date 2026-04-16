---
tags: [paper, dexterous-manipulation, sim-to-real, WMTS]
aliases: [DeXtreme]
paper-year: 2023
venue: ICRA
related: ["[[ReinforcementLearning]]", "[[EmbodiedAI]]", "[[Final_WMTS]]"]
paper-pdf: "[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality.pdf]]"
---

# DeXtreme: Transfer of Agile In-hand Manipulation from Simulation to Reality

> [!abstract] 核心贡献
> 大规模域随机化 + 习得的视觉位姿估计器，实现 Allegro Hand in-hand reorientation 的 Sim-to-Real 迁移。在 IsaacGym 中并行训练数千环境。

## 核心方法

- **大规模 DR**：物理参数（摩擦、质量、阻尼）+ 视觉参数（光照、纹理）+ 动作延迟
- **习得位姿估计器**：从 RGB 图像实时估计物体 6D 位姿
- **PPO in IsaacGym**：数千并行环境高效训练
- **Action 空间**：关节位置增量 → PD 控制器转为力矩

## 与 WMTS 的关联

- **DR 策略参考**：WMTS 的仿真阶段可借鉴 DeXtreme 的 DR 参数范围
- **Action 空间一致**：WMTS 也使用 $\Delta q$ → PD 作为动作空间
- **WMTS 的改进**：DeXtreme 无 WM 无 Actuator Model，纯靠 DR 暴力覆盖 gap；WMTS 用 WM+Actuator Model 更精准建模

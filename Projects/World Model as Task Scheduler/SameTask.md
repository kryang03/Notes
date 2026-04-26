---
tags:
	- WMTS
	- related-projects
	- dexterous-manipulation
aliases:
	- WMTS Same Task Projects
	- 同类项目对照
date: 2026-04-26
related:
	- "[[Final_WMTS]]"
	- "[[WMTS_Reliability_Extensions]]"
	- "[[ReinforcementLearning]]"
	- "[[Dynamics]]"
	- "[[ContactMechanics]]"
---

# WMTS 同类任务与项目对照

> [!abstract] 用途
> 本文件不再保留裸 URL 列表，而是把相近项目按“可迁移到 [[Final_WMTS]] 的设计要素”整理，方便后续写 related work、找 baseline 和设计 ablation。

## 一、灵巧操作与 Sim-to-Real 主线

| 项目 | 链接 | 关键主题 | 对 WMTS 的启发 |
|---|---|---|---|
| DexHier | https://dexhier.github.io/ | 从简单到复杂的 in-hand reorientation，技能复用与层次策略 | 对应 [[From Simple to Complex Skills Recap]]；可作为 Oracle skill reuse baseline |
| HORA | https://haozhi.io/hora/ | Rapid Motor Adaptation in-hand object rotation | 对应 [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]]；启发 WMTS 的在线 DR encoder |
| AnyRotate | https://maxyang27896.github.io/anyrotate/ | 视觉触觉 + gravity-invariant rotation | 对应 [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]；触觉/重力条件可进入 Generalist condition |
| VIserDex | https://rffr.leggedrobotics.com/works/viserdex/ | 视觉伺服式灵巧操作 | 可与 [[ControlTheory]] 中视觉伺服和 impedance control 交叉，用于对照 WMTS 的 WM-based scheduler |
| RotateIt | https://haozhi.io/rotateit/ | vision + touch general in-hand rotation | 对应 [[RotateIt - General In-Hand Object Rotation with Vision and Touch]]；可作为多模态观测 baseline |
| DexNDM | https://meowuu7.github.io/DexNDM/ | joint-wise neural dynamics model | 对应 [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]；与 WMTS Actuator/Rigid 解耦最接近 |
| DeXtreme | https://dextreme.org/ | 大规模 DR + 真机灵巧 reorientation | 对应 [[DeXtreme Recap]]；可作为“无 WM 的强 DR baseline” |
| Visual Dexterity | https://taochenshh.github.io/projects/visual-dexterity | 视觉驱动灵巧操作 | 可补充 Generalist 的视觉观测设计与 object-centric representation |

## 二、接触/触觉/力控相关项目

| 项目 | 链接 | 关键主题 | 对 WMTS 的启发 |
|---|---|---|---|
| AIDX Manipulation ICRA23 | https://aidx-lab.org/manipulation/icra23 | 接触丰富操作与学习控制 | 可用于 related work 中连接 [[ContactMechanics]] 与 [[ReinforcementLearning]] |
| AIDX Manipulation Humanoids24 | https://aidx-lab.org/manipulation/humanoids24 | 人形/多指操作控制 | 可作为 humanoid manipulation baseline 入口 |
| Visuotactile Manipulation | https://yingyuan0414.github.io/visuotactile/ | 视觉触觉融合 | 对应 [[SignalProcessing]] 与 [[RepresentationLearning]]；可为 $z_{tactile}$ encoder 提供设计参考 |
| CTR / AI Institute | https://ctr.theaiinstitute.com/ | contact-rich robotics research | 可作为接触丰富任务 benchmark 与真实系统参考 |

## 三、与可靠性扩展的直接关系

| WMTS 扩展点 | 最相关项目/论文 | 需要验证的问题 |
|---|---|---|
| Actuator/Rigid 解耦 | DexNDM, [[ANYmal Parkour Recap]], [[Learning Agile and Dynamic Motor Skills for Legged Robots]] | joint-wise neural dynamics 是否优于统一 MLP WM？ |
| 触觉接触 latent | AnyRotate, RotateIt, Visuotactile, [[GenDexGrasp - Generalizable Dexterous Grasping]] | $z_{contact}$ 是否能预测掉落/换指失败？ |
| 强 DR baseline | DeXtreme, HORA | WMTS 是否在同等 DR 预算下提升真机样本效率？ |
| 层次/专才复用 | DexHier, [[Improving Policy Optimization GSL Recap]] | Oracle 复用是否减少每个新任务的 PPO 训练成本？ |
| Safety/可靠性调度 | DexNDM, [[WMTS_Reliability_Extensions]] | 三重风险分数是否能降低危险 false positive？ |


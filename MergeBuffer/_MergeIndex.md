---
tags:
  - merge-buffer
  - processing-index
created: 2026-01-31
status: pending
---

# MergeBuffer 处理索引

> [!note] 处理状态
> 本文档记录 MergeBuffer 中文件的内容分析和合并计划。
> 状态: 🔴 待处理 | 🟡 进行中 | 🟢 已完成

## 文件清单与归属分析

### 1. deep-research-thinking-20260129-153156.md (511 行)
**主题**: 灵巧操作控制理论研究方案
**状态**: � 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Grasp Matrix & Hand Jacobian | [[ControlTheory]] | ✅ 已存在 |
| 位置控制 → 阻抗控制演进 | [[ControlTheory#2.1 阻抗控制]] | ✅ 已存在 |
| Operational Space Formulation | [[ControlTheory]] | ✅ 已存在 |
| Null Space Projection | [[Optimization]] | ✅ 已存在 |
| Montana's Equations | [[ContactMechanics]] | ✅ 已存在 |
| Sliding Mode Control | [[ControlTheory]] | ✅ 已存在 |
| Contact-Implicit MPC | [[Optimization]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 2. deep-research-thinking-20260129-153515.md (270 行)
**主题**: 多体动力学建模与接触求解
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| RNEA/ABA 算法 | [[Dynamics]] | ✅ 已存在 |
| Spatial Vector Algebra | [[Dynamics#4.1 空间向量代数]] | ✅ 已存在 |
| LCP 接触模型 | [[ContactMechanics#4.1 线性互补问题]] | ✅ 已存在 |
| PGS 求解器 | [[ContactMechanics]] | ✅ 补充了数值技巧 |
| Baumgarte Stabilization | [[Dynamics]] | ✅ 已存在 |
| Differentiable Physics | [[Dynamics]], [[Optimization]] | ✅ 已存在 |
| Articulated Body Inertia | [[Dynamics]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 3. deep-research-thinking-20260129-153602.md (336 行)
**主题**: 接触力学 - LCP、Stewart-Trinkle、摩擦锥、Montana方程
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Montana 接触运动学方程 | [[ContactMechanics#2.2 Montana接触运动学方程]] | ✅ 已存在 |
| 曲率张量与接触约束 | [[ContactMechanics#2.1 表面微分几何基础]] | ✅ 已存在 |
| Stewart-Trinkle 时间步进 | [[ContactMechanics#4.1.1 Stewart-Trinkle 时间步进算法]] | ✅ 已存在 |
| PGS/Sequential Impulses | [[ContactMechanics#4.2.2 迭代法]] | ✅ 已存在 |
| 软指接触 (Soft Finger) | [[ContactMechanics#3. 接触模型的演进]] | ✅ 已存在 |
| 可微物理引擎 | [[ContactMechanics#5. 可微接触物理]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 4. deep-research-thinking-20260129-153652.md (1132 行)
**主题**: 计算几何 - GJK/EPA、SDF、神经隐式表示
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 闵可夫斯基差 (Minkowski Difference) | [[ComputationalGeometry#2.1 闵可夫斯基差的物理本质]] | ✅ 已存在 |
| GJK 支持映射 (Support Mapping) | [[ComputationalGeometry#3.1 GJK算法]] | ✅ 已存在 |
| EPA 穿透深度 | [[ComputationalGeometry#3.3 EPA算法]] | ✅ 已存在 |
| SDF 梯度优化 (TrajOpt/CHOMP) | [[ComputationalGeometry#4. 有向距离场]] | ✅ 已存在 |
| Neural SDF / NGDF | [[ComputationalGeometry#5. 神经隐式表示]] | ✅ 已存在 |
| Contact Jacobian 物理对偶性 | [[ContactMechanics#2.3 接触雅可比矩阵]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 5. deep-research-thinking-20260129-153710.md (261 行)
**主题**: 优化/轨迹优化 - CITO、iLQR/DDP、Ferrari-Canny
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Contact-Implicit Trajectory Optimization | [[Optimization#3. 接触隐式轨迹优化]] | ✅ 已存在 |
| iLQR/DDP 算法 | [[Optimization#2.2 Differential Dynamic Programming]] | ✅ 已存在 |
| Direct Collocation | [[Optimization#2.1 Direct Collocation]] | ✅ 已存在 |
| Ferrari-Canny 稳定性指标 | [[Optimization#抓取稳定性]] | ✅ 已存在 |
| LCP 在轨迹优化中 | [[Optimization#接触互补约束]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 6. deep-research-thinking-20260129-153740.md (282 行)
**主题**: 表征学习 - Diffusion Policy、ACT、视觉触觉融合
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Diffusion Policy 数学基础 | [[RepresentationLearning#2.2 深度解析：扩散策略]] | ✅ 已存在 |
| ACT (Action Chunking Transformer) | [[RepresentationLearning#2.3 动作分块与Transformer]] | ✅ 已存在 |
| 协变量偏移 (Covariate Shift) | [[RepresentationLearning#2.1.1 协变量偏移]] | ✅ 已存在 |
| 视觉触觉多模态融合 | [[RepresentationLearning#2.4 表征学习]] | ✅ 已存在 |
| Jacobian Regularization | [[RepresentationLearning#1.3 学习目标的物理重构]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 7. deep-research-thinking-20260129-153801.md (280 行)
**主题**: 随机过程 - MPPI、GPR、信念空间规划
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| MPPI 控制更新律 | [[StochasticProcess#6. 核心算法详解：MPPI]] | ✅ 已存在 |
| Contact Particle Filter | [[StochasticProcess#5. 粒子滤波]] | ✅ 已存在 |
| 高斯过程回归 (GPR) | [[StochasticProcess#4. 高斯过程]] | ✅ 已存在 |
| 信念空间规划 (BSP) | [[StochasticProcess#6.4 信念空间规划]] | ✅ 已存在 |
| 随机摩擦锥建模 | [[StochasticProcess#2.1 随机微分方程]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 8. deep-research-thinking-20260129-153817.md (316 行)
**主题**: 信息论 - EIG、GPIS、Empowerment、主动感知
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 期望信息增益 (EIG) | [[InformationTheory#2.2 互信息与感知增益]] | ✅ 已存在 |
| Empowerment 变分下界 | [[InformationTheory#5.1 赋能 (Empowerment)]] | ✅ 已存在 |
| GPIS (高斯过程隐式表面) | [[InformationTheory#3.2 GPIS]] | ✅ 已存在 |
| DIAYN 鉴别器 | [[InformationTheory#5.3 DIAYN]] | ✅ 已存在 |
| 粒子滤波 EIG 采样 | [[InformationTheory#4. 采样方法]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 9. deep-research-thinking-20260129-153856.md (213 行)
**主题**: 信号处理 - 触觉迟滞、STFT滑移、因子图
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Prandtl-Ishlinskii 迟滞模型 | [[SignalProcessing#2.2 迟滞现象的建模与补偿]] | ✅ 已存在 |
| STFT 谱质心滑移检测 | [[SignalProcessing#4.1.1 短时傅里叶变换]] | ✅ 已存在 |
| 小波变换瞬态检测 | [[SignalProcessing#4.1.2 小波变换]] | ✅ 已存在 |
| 因子图触觉因子 | [[SignalProcessing#5.2 因子图]] | ✅ 已存在 |
| GelSight 泊松求解器 | [[SignalProcessing#3.1 光度立体视觉]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 10. deep-research-thinking-20260129-153956.md (206 行)
**主题**: 强化学习 - SAC/PPO、Domain Randomization、Constraint Manifold
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| SAC 熵正则化 | [[ReinforcementLearning#2.1 Soft Actor-Critic]] | ✅ 已存在 |
| PPO vs SAC 对比 | [[ReinforcementLearning#算法对比]] | ✅ 已存在 |
| Domain Randomization | [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|Sim-to-Real]] | ✅ 已存在 |
| Constraint Manifold RL | [[ReinforcementLearning#约束流形]] | ✅ 已存在 |
| Conservative Q-Learning (CQL) | [[ReinforcementLearning#Offline RL]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

## 🟢 MergeBuffer 处理完成 (Phase 1: 2026-01-31)

> [!success] Phase 1 全部完成
> **处理时间**: 2026-01-31
> **总文件数**: 10
> **处理结果**: 全部验证为 Foundations 已覆盖内容，原文件已删除
> 
> **覆盖分析**:
> - 所有 MergeBuffer 研究思考内容均来自同一次 Gemini Deep Research 会话
> - 内容在构建 Foundations 时已被系统性吸收整合
> - 未发现遗漏的核心算法或定理

---

## Phase 2: 新增内容 (2026-03 批次)

> [!note] 处理状态
> 发现时间: 2026-03-05 (Session #11)
> 总文件数: 12 (10篇学术论文 + 1篇技术博文 + 1篇分析文章)

### 11. 谐波减速器与RV减速器在关节模组集成设计中.pdf
**类型**: 技术博文 (WeChat)
**作者**: Zane Zhang
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 柔轮疲劳/冲击脆弱性/精度保持性 | [[减速器#2.4 谐波减速器]] | ✅ 已整合 |
| 空心轴集成优势/输入转速范围 | [[减速器#2.4 谐波减速器]] | ✅ 已整合 |
| RV vs 谐波核心选型逻辑 | [[减速器#2.6 RV 减速器]] | ✅ 已整合 |
| 6轴机器人经典关节配置 | [[减速器#4.2 典型机器人关节减速器配置]] | ✅ 新增 |

**处理结果**: 关键内容已融合至减速器.md (2026-03-05)

---

### 12. 空间智能作为机器人的结构化表征.pdf
**类型**: 技术博文 (WeChat) — Wenlong Huang (Stanford SVL, Fei-Fei Li组) 演讲整理
**主题**: 3D空间表征、PointWorld、结构化泛化、VLA数据效率
**状态**: 🔴 待处理

| 内容模块 | 目标文件 | 优先级 |
|---------|---------|-------|
| 3D空间表征作为结构化先验 | [[RepresentationLearning]] | 高 |
| PointWorld 3D世界建模 | [[ComputationalGeometry]] | 中 |
| VLA数据效率讨论 | [[EmbodiedAI]] | 高 |

---

### 13. A Survey of Sim-to-Real Methods in RL (2025)
**类型**: 学术论文 (arXiv:2502.13187)
**作者**: Da et al. (Arizona State + DARPA)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[ReinforcementLearning]] | MDP四元素(S/A/T/R)分类法 |
| [[sim2real]] | Domain Randomization / Adaptation / Grounding 综述 |
| bt_sim2real Canvas节点 | 直接关联 |

**优先级**: ⭐⭐⭐⭐⭐ — 与项目 Sim-to-Real 突破点高度相关

---

### 14. Contact-Grounded Policy (2026)
**类型**: 学术论文 (arXiv:2603.05687)
**作者**: Xu et al. (Purdue + Meta Reality Labs)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[RepresentationLearning]] | 视触觉策略 + 生成式接触基础 |
| [[ContactMechanics]] | 接触生成/基础 |
| bt_representation Canvas节点 | 触觉表征 |

**优先级**: ⭐⭐⭐⭐ — 视触觉灵巧操作前沿

---

### 15. DexHiL (2026)
**类型**: 学术论文 (arXiv:2603.09121)
**作者**: Han et al. (CASIA + SJTU + Shanghai AI Lab)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[EmbodiedAI]] | VLA post-training / Human-in-the-Loop |
| [[ReinforcementLearning]] | HiL 策略微调 |

**优先级**: ⭐⭐⭐ — VLA灵巧操作后训练

---

### 16. Emerging Extrinsic Dexterity in Cluttered Scenes (2026)
**类型**: 学术论文 (arXiv:2603.09882)
**作者**: Zheng et al. (PKU + Galbot + BAAI)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[ContactMechanics]] | 外在灵巧性(extrinsic dexterity) |
| [[ReinforcementLearning]] | Dynamics-aware策略学习 |
| [[Dynamics]] | 接触动力学感知 |

**优先级**: ⭐⭐⭐⭐ — 外在灵巧性 + 动力学感知与项目直接相关

---

### 17. Grounded Action Transformation (AAAI 2017)
**类型**: 学术论文 (AAAI-17)
**作者**: Hanna & Stone (UT Austin)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[ReinforcementLearning]] | Grounded Simulation Learning 经典方法 |
| [[sim2real]] | 动作空间对齐/仿真器修正 |

**优先级**: ⭐⭐⭐ — Sim-to-Real 经典方法论

---

### 18. Minimalist Compliance Control (2025/2026)
**类型**: 学术论文 (Stanford, Karen Liu + Shuran Song)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[ControlTheory]] | 极简柔顺控制 |
| bt_impedance Canvas节点 | 变阻抗/柔顺控制 |

**优先级**: ⭐⭐⭐⭐ — 阻抗控制方向核心参考

---

### 19. RL in robotic systems: sim-to-real review (2026)
**类型**: 学术论文 (Robotics and Autonomous Systems)
**作者**: Tiwari et al. (IIIT-Naya Raipur)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[ReinforcementLearning]] | Sim-to-Real 综述 |
| [[sim2real]] | 与 #13 互补参考 |

**优先级**: ⭐⭐⭐ — 期刊综述，与 #13 形成交叉验证

---

### 20. RoboTwin 2.0 (2025)
**类型**: 学术论文 (arXiv)
**作者**: Chen et al. (SJTU + HKU + Shanghai AI Lab)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[EmbodiedAI]] | 双手操作数据生成 + Domain Randomization 基准 |
| [[ReinforcementLearning]] | 数据增强策略 |

**优先级**: ⭐⭐⭐ — 双手操作数据生态

---

### 21. STOLA (2026, AAAI)
**类型**: 学术论文 (AAAI 2026)
**作者**: Cheng et al.
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[SignalProcessing]] | 触觉常识推理 |
| [[RepresentationLearning]] | Touch-Language 多模态 |

**优先级**: ⭐⭐ — 触觉语言融合，间接相关

---

### 22. Tacmap (2026)
**类型**: 学术论文 (arXiv:2602.21625)
**作者**: Su et al. (Sharpa + HKUST + NVIDIA)
**状态**: 🔴 待处理 → 移至 Papers/ + 创建 PapersRecap

| 关联 | 说明 |
|------|------|
| [[SignalProcessing]] | 触觉穿透深度图 |
| [[sim2real]] | 触觉 Sim-to-Real Gap |
| bt_sim2real Canvas节点 | 传感器层面的 Sim-to-Real |

**优先级**: ⭐⭐⭐⭐ — 触觉 Sim-to-Real 与项目直接相关

---

> [!warning] Phase 2 待处理
> **已完成**: 2/12 (谐波减速器已整合, chat.md 已处理)
> **待处理**: 10/12 (10篇学术论文需要移至 Papers/ 并创建 PapersRecap)
>
> **推荐处理顺序** (按与项目相关度排序):
> 1. ⭐⭐⭐⭐⭐ #13 Sim-to-Real Survey
> 2. ⭐⭐⭐⭐ #16 Emerging Extrinsic Dexterity
> 3. ⭐⭐⭐⭐ #18 Minimalist Compliance Control
> 4. ⭐⭐⭐⭐ #22 Tacmap
> 5. ⭐⭐⭐⭐ #14 Contact-Grounded Policy
> 6. 其余按需处理

## 后续处理记录

### 11. 强化学习策略约束和熵的统一视角.pdf
**来源**: 青稞AI 公众号文章 (2026-01-28)
**类型**: 📱 公众号/博客文章（非正式论文）
**状态**: 🟢 已完成

| 核心思想 | 融合目标 | 处理方式 |
|---------|---------|---------|
| KL 散度正则化框架 | [[ReinforcementLearning#Phase 3: SAC]] | ✅ 新增 callout |
| 熵正则 = KL 到均匀先验 | [[ReinforcementLearning]] | ✅ 新增推导 |
| Boltzmann 最优策略形式 | [[ReinforcementLearning]] | ✅ 补充公式 |
| 不同算法的参考分布选择 | [[ReinforcementLearning]] | ✅ 对比分析 |

**处理结果**: 
- 核心洞见融合到 Foundations/ReinforcementLearning.md（SAC 部分新增 callout）
- PDF 已删除（非正式论文，不保留在 Papers/）
- 处理时间: 2026-01-31

---

## 2026-02-02 新增论文处理

### 12-17. 新论文批量处理

| # | 论文名称 | 状态 | 处理方式 |
|---|---------|------|---------|
| 12 | Hindsight Experience Replay | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL Foundation |
| 13 | TARC: Time-Adaptive Robotic Control | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→DNPM项目 |
| 14 | Learning Long-Horizon Manipulation via Privileged Action | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→DNPM项目 |
| 15 | Vision-force-fused Curriculum Learning | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 16 | Visual-tactile Pretraining for Dexterity | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 17 | Dexterous RL with Knowledge Transfer | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 18 | Path-Constrained Haptic Admittance Control | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |

### 未处理文件（非操作领域相关） → 已全部深度整合 (2026-02-27)

> [!success] MergeBuffer 零废弃原则应用
> 以下文件此前被标注为"无直接关联"，但经深度分析后发现均与知识库存在有价值的关联，已全部整合。

| 文件 | 整合目标 | 关联发现 |
|-----|---------|---------|
| IsoCompute Playbook.pdf | [[ReinforcementLearning#6.3 RL Scaling Laws]] + DNPM ideas.md §2.5.4 | RL 缩放定律、easy/hard 熵控制、课程设计指导 |
| Learning to Discover at Test Time.pdf | [[ReinforcementLearning#6.4 Test-Time RL]] + DNPM ideas.md §4.1 | 测试时 RL、entropic objective、在线适应新环境 |

**处理时间**: 2026-02-02 标注 → 2026-02-27 完成深度整合

---

## 2026-02-27 新增文件处理

### 19. 什么是机器人动力学中的牛顿欧拉法与拉格朗日法？.pdf
**来源**: 微信公众号 Zane Hub (2026-02-24)
**类型**: 📱 公众号/博客文章（科普级别）
**状态**: 🟢 已完成

| 核心内容 | 融合目标 | 处理结果 |
|---------|---------|---------|
| NE vs Lagrangian 方法对比 | [[Dynamics#3.4 方法对比总结 (Method Comparison Summary)]] | ✅ 新增对比表 |
| 离散时间动力学建模 | [[Dynamics#10. Future Outlook: Differentiable Physics (可微物理)]] | ✅ 新增 callout |
| Lagrangian Neural Networks | [[Dynamics#10. Future Outlook: Differentiable Physics (可微物理)]] | ✅ 新增 callout |

**处理结果**: 核心内容已融合到 Dynamics.md。原文件为科普级别，Dynamics.md 已有更深入的覆盖。

### 20-24. 此前标注"非操作领域"文件 → 已全部深度整合

> [!success] MergeBuffer 零废弃原则应用 (2026-02-27)
> 经深度分析，所有文件均发现与知识库的有价值关联。

| # | 文件名 | 整合目标 | 核心关联 | 状态 |
|---|-------|---------|---------|------|
| 20 | 从梯度角度看SFT...pdf | [[ReinforcementLearning]] §2.5 统一梯度视角 | SFT=稀疏RL、策略蒸馏与 DNPM credit assignment | 🟢 已整合 |
| 21 | Mediator-Based Reward Design...pdf | [[ReinforcementLearning]] §4.2 + DNPM ideas §2.5.3 | 因果中介变量降低奖励方差，解决长因果链 credit assignment | 🟢 已整合 |
| 22 | Compression-Based Denoisers.pdf | [[InformationTheory]] §5.0 + [[SignalProcessing]] §5.4 | 压缩-去噪对偶性，指导触觉信号处理与状态表征 | 🟢 已整合 |
| 23 | IsoCompute Playbook.pdf | [[ReinforcementLearning]] §6.3 + DNPM ideas §2.5.4 | RL 缩放定律、easy/hard 熵控制、课程设计 | 🟢 已整合 |
| 24 | Learning to Discover at Test Time.pdf | [[ReinforcementLearning]] §6.4 + DNPM ideas §4.1 | 测试时 RL、entropic objective、在线适应 | 🟢 已整合 |
| 25 | GeoPT.pdf | [[Dynamics]] + [[ComputationalGeometry]] + [[RepresentationLearning]] | Dynamics-lifted 几何预训练，transport equation 统一范式 | 🟢 已整合 |
| 26 | LaST0.pdf | [[EmbodiedAI]] §1.4 + [[RepresentationLearning]] | 潜在时空 CoT VLA，MoT 双系统，14× 推理加速 | 🟢 已整合 |
| 27 | OmniXtreme.pdf | [[ControlTheory]] + [[ReinforcementLearning]] + [[Dynamics]] | Flow Matching 预训练 + actuation-aware 残差 RL，torque-speed envelope | 🟢 已整合 |
| 28 | RL-100.pdf | [[ReinforcementLearning]] §6.2 + [[StochasticProcess]] | Denoising sub-MDP，IL→Offline→Online RL 三阶段，consistency distillation | 🟢 已整合 |
| 29 | WMPO.pdf | [[ReinforcementLearning]] §6.5 + [[EmbodiedAI]] §2.5 | 像素空间世界模型 + GRPO 对 VLA 的 RL post-training | 🟢 已整合 |

**处理时间**: 2026-02-27 (深度整合完成), 2026-03-01 (#25-29 新增批次)

---

## 历史参考（已归档）

### 原合并策略（已完成）

~~### Phase 1: 高价值内容提取~~
~~1. **控制理论模块** → 补充到 [[ControlTheory]]~~
~~2. **动力学模块** → 补充到 [[Dynamics]]~~
~~3. **接触力学模块** → 补充到 [[ContactMechanics]]~~

~~### Phase 2: 参考文献整理~~
~~### Phase 3: 原文件处理~~

**状态**: ✅ 全部完成

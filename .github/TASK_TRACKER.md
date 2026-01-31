# 知识图谱任务追踪器 (Task Tracker)

> [!important] 使用说明
> 这是 AI Agent 的工作记忆文档。每次会话开始时**必须首先阅读**本文件，会话结束前**必须更新**本文件。
> 
> 这确保了跨会话的任务连续性，解决了上下文限制导致的任务中断问题。

**最后更新**: 2026-02-01 (MergeBuffer 批量处理)

---

## 🔴 紧急待办 (Urgent)

> 必须在下次会话立即处理的任务

*当前无紧急任务*

---

## 🟡 进行中 (In Progress)

> 上次会话中断或需要持续关注的任务

### MergeBuffer 论文处理 🔄 进行中

**本次会话已处理 (6 篇)**:
- [x] Touch Dexterity (Rotating without Seeing) - 纯触觉手内旋转
- [x] HORA (Rapid Motor Adaptation) - 本体感觉快速适应
- [x] DLR Modular Tactile Manipulation - 模块化架构 + 粒子滤波
- [x] SERL - 真实世界 RL 系统
- [x] HIL-SERL - 人在回路校正
- [x] MimicGen - 演示数据扩增

**待处理 (MergeBuffer 剩余约 10 个 PDF)**:
- [ ] AnyRotate (重力不变手内旋转)
- [ ] General In-Hand Rotation (视触觉联合)
- [ ] Robot Synesthesia (视触觉联觉)
- [ ] Learning Visuotactile Skills (双多指手)
- [ ] TRANSIC (Sim-to-Real 在线校正)
- [ ] Part-Guided 3D RL (关节物体操作)
- [ ] DeepMimic (物理角色动画)
- [ ] 其他...

### PapersRecap 批量生成 ✅ 已完成

**全部 28+6=34 篇论文笔记已完成**（截至 2026-02-01）：
- [x] EUREKA, Curriculum Learning, Residual DMP, DexNDM, DexTrack
- [x] VICES, AP-AC, Autoregressive Policies, RCRL, Prosthesis VI
- [x] CSR, LipsNet, Elastic Time Step RL, Stability-Certified RL
- [x] Weight-sparse transformers, Safe Model-based RL
- [x] How to Train Your Latent CBF, Lessons from Spin Pens, Control Frequency Adaptation
- [x] On Robust RL with Lipschitz-Bounded Policy Networks
- [x] Off-Policy Interval Estimation with Lipschitz VI
- [x] RL for Optimal Primary Frequency Control (Lyapunov)
- [x] Exploration vs Exploitation: A Stochastic Control Approach
- [x] Dynamic RL for Actors, EvoControl, Hierarchical Coordination
- [x] Curriculum vs Haptic Feedback, Sampling Theorem (PWM)
- [x] **New (2026-02-01 晚)**: Touch Dexterity, HORA, DLR Modular
- [x] **New (2026-02-01 晚)**: SERL, HIL-SERL, MimicGen, RialTo

### 理论导师模式 - Foundation 完善

- [x] **StochasticProcess.md 理论完善** ✅ 已完成 (2026-02-01)
  - ✅ 添加"自回归探索噪声"（源自 ARP 论文）
  - ✅ 添加"连续时间熵正则化最优控制"（源自 Exploration vs Exploitation）
  - ✅ **GP dynamics learning 已完整**：Section 5.2 包含 GPR、核函数、Local GP 实现
  - ✅ **与 Dynamics 交叉链接已建立**：双向 wikilink 已添加

- [x] **InformationTheory.md 理论完善** ✅ 已更新 (2026-02-01)
  - ✅ **新增 Section 5: 信息瓶颈原理 (Information Bottleneck)**
    - 形式化定义: $\mathcal{L}_{IB} = I(Z; X) - \beta \cdot I(Z; Y)$
    - 变分信息瓶颈 (VIB) 变分界
    - 与 β-VAE 的联系
    - 触觉表征压缩应用
    - 与 Empowerment 的信息论对偶
    - 信息平面假说
  - ✅ 修复章节编号 (新结构: 1-8 章)
  - [ ] 待补充: Empowerment 在 intrinsic motivation 中的深度扩展

- [x] **ComputationalGeometry.md 理论完善** ✅ 已确认完整 (2026-02-01)
  - ✅ **SDF 数学原理**：Section 4 (梯度属性、优化应用)
  - ✅ **Neural Implicit (DeepSDF, NGDF)**：Section 5
  - ✅ **GJK/EPA 碰撞检测**：Section 3 (支持函数、单纯形演化、穿透深度)

### Foundation 更新任务（从论文中识别）

- [x] **ControlTheory.md** 已更新 (2026-02-01):
  - ✅ 添加"可达性分析与可行集"（源自 RCRL）
  - ✅ 添加"多速率采样与 RL"（源自 AP-AC）
  - ✅ **New (2026-02-01)**: 添加"数据驱动阻抗辨识"（源自 Prosthesis VI）
  - ✅ **New (2026-02-01)**: 添加"学习可变阻抗"（源自 VICES）

- [x] **ReinforcementLearning.md** 已更新 (2026-02-01):
  - ✅ 添加"时间一致探索"（源自 ARP）
  - ✅ 添加"课程学习 vs 触觉"（源自 Curriculum vs Haptic）
  - ✅ **New (2026-02-01)**: 添加"数据飞轮"（源自 DexTrack）
  - ✅ **New (2026-02-01)**: 添加"观测空间课程适应"（源自 CSR）

- [x] **Dynamics.md** 已更新 (2026-02-01):
  - ✅ 添加"关节级神经动力学分解"（源自 DexNDM）

- [x] **Optimization.md** 已更新 (2026-02-02):
  - ✅ 添加"同伦优化在灵巧操作中的应用"（源自 DexTrack）
  - ✅ 添加"阻抗参数的凸辨识"（源自 Prosthesis VI）

---

## 🟢 计划中 (Planned)

> 已识别但尚未开始的任务

### Foundation 交叉链接强化
- [ ] 检查所有 Foundation 文件之间的双向链接完整性
- [ ] 在 taxonomy.md 中更新知识结构图

### PapersRecap 关联审计
- [ ] 检查所有论文笔记是否链接到对应 Foundation
- [ ] 确保 Foundation 中有反向引用

### MergeBuffer 定期清理
- [ ] 检查 MergeBuffer/ 是否有新内容需要处理

---

## ✅ 已完成 (Completed)

> 最近完成的任务（保留最近10条）

- [x] **ContactMechanics.md 增强** — 2026-01-31
  - 添加 Murray 抓取矩阵严格定义 (Section 2.4)
  - 添加力闭合与形闭合条件 (Section 2.5)
  - 添加 Ferrari-Canny 品质度量 (Section 2.6)

- [x] **Dynamics.md 增强** — 2026-01-31
  - 添加 Khatib 操作空间动力学 (Section 7)
  - 包含 $\Lambda$, 动力学一致性伪逆, 零空间控制

- [x] **RepresentationLearning.md 增强** — 2026-01-31
  - 添加 Point Cloud Representation (Section 4)
  - 包含 PointNet, PointNet++, Point Transformer 数学原理
  - 修复章节编号 (5.x → 6.x)

- [x] **ReinforcementLearning.md 增强** — 2026-01-31
  - 添加 DQN 作为 Phase 0 基础
  - 添加 TRPO → PPO 演进线
  - 增强 Offline RL 章节

- [x] **SKILL.md v1.3** — 2026-01-31
  - 添加 Section 5.5.3 教科书驱动的知识补充

- [x] **SKILL.md v1.4** — 2026-01-31
  - 记录 Foundation 增强历史

- [x] **Prompts 创建** — 2026-01-31
  - theoretical-mentor-mode.prompt.md
  - merge-buffer-process.prompt.md
  - knowledge-health-check.prompt.md
  - paper-reading.prompt.md
  - continue-session.prompt.md

---

## 📋 会话状态快照

### 最近会话: 2026-02-01 晚 (MergeBuffer 批量处理)

**主要工作**: 
1. 📊 **Phase 0 健康检查** — 发现 MergeBuffer 有 ~12 个新 PDF
2. 📄 **论文笔记生成 (6 篇)** — Touch Dexterity, HORA, DLR Modular, SERL, HIL-SERL, MimicGen, RialTo
3. 🎓 **Foundation 更新** — ReinforcementLearning.md 添加 SERL/RLPD/HIL 内容
4. 📁 **文件迁移** — 已处理 PDF 从 MergeBuffer 移动到 Papers/

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| 7 个新 PapersRecap | Touch Dexterity, HORA, DLR Modular, SERL, HIL-SERL, MimicGen, RialTo |
| ReinforcementLearning.md | +Section 5.2 SERL/RLPD/Human-in-the-Loop |
| TASK_TRACKER.md | 更新任务进度 |

**新增论文主题**:
- 纯触觉手内操作 (Touch Dexterity)
- 本体感觉快速适应 (HORA) 
- 模块化 RL + 粒子滤波状态估计 (DLR)
- 真实世界高效 RL 系统 (SERL, HIL-SERL)
- 演示数据扩增 (MimicGen)
- Real-to-Sim-to-Real (RialTo)

**会话结束状态**: 🔄 部分完成（MergeBuffer 还有约 10 个 PDF 待处理）

**下次会话建议**: 
1. 继续处理 MergeBuffer 剩余 PDF (AnyRotate, General In-Hand, Robot Synesthesia 等)
2. RepresentationLearning.md: 添加触觉表征学习内容
3. SignalProcessing.md: 添加粒子滤波状态估计内容

---

### 历史会话: 2026-02-01 (遗留任务审计与链接强化)

**主要工作**: 
1. 📊 **Phase 0 健康检查** — 28 篇论文笔记完整，MergeBuffer 空，Foundations 11 文件完整
2. 🔍 **遗留任务审计** — 确认 ComputationalGeometry.md 已完整（SDF/GJK/EPA 均已覆盖）
3. 🔗 **交叉链接强化** — 建立 Dynamics ↔ StochasticProcess 双向链接
4. ✅ **TASK_TRACKER 清理** — 标记多个"待补充"任务为已完成

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| [Dynamics.md](Foundations/Dynamics.md) | +related: StochasticProcess, +tip: GP dynamics learning |
| [StochasticProcess.md](Foundations/StochasticProcess.md) | +related: Dynamics, +tip: GP 残差学习补偿刚体动力学 |
| [TASK_TRACKER.md](.github/TASK_TRACKER.md) | 更新任务完成状态，清理遗留任务 |

**审计发现**:
- ComputationalGeometry.md **已完整**：Section 3 (GJK/EPA), Section 4 (SDF), Section 5 (DeepSDF/NGDF)
- StochasticProcess.md **GP dynamics 已完整**：Section 5.2 包含 GPR、Matern 核、Local GP 代码
- Dynamics ↔ StochasticProcess 链接 **已建立**

**会话结束状态**: ✅ 正常完成

**下次会话建议**: 
1. InformationTheory.md: Empowerment 深度扩展
2. taxonomy.md: 更新知识结构图反映最新 Foundation 关系
3. Foundation 交叉链接审计：检查所有双向链接完整性

---

### 历史会话: 2026-02-01 (Information Bottleneck 补充)

**主要工作**: 
1. 📊 **Phase 0 健康检查** — 28 篇论文笔记完整，MergeBuffer 空
2. 🎓 **InformationTheory.md 重大更新** — 新增 Section 5: 信息瓶颈原理
3. 🔧 **章节编号修复** — 更新为 1-8 章结构

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| [InformationTheory.md](Foundations/InformationTheory.md) | +Section 5 信息瓶颈原理 (约 120 行), 章节编号修复 |
| [TASK_TRACKER.md](.github/TASK_TRACKER.md) | 更新任务完成状态 |

**新增理论内容** (Section 5: 信息瓶颈原理):
- **IB 形式化定义**: $\mathcal{L}_{IB} = I(Z; X) - \beta \cdot I(Z; Y)$
- **变分信息瓶颈 (VIB)**: 变分上界/下界，可训练损失函数
- **与 β-VAE 的联系**: VIB 退化为 β-VAE 的条件
- **触觉表征压缩**: TactileVIBEncoder 代码示例
- **Sim-to-Real 域不变表征**: IB 自动过滤域特异性噪声
- **IB 与 Empowerment 对偶**: 感知压缩 vs 控制能力
- **信息平面假说**: 拟合阶段 vs 压缩阶段

**会话结束状态**: ✅ 正常完成

---

### 历史会话: 2026-02-01 (Foundation Callouts)

**主要工作**: 
1. 🎓 **理论导师模式** — 补充 ControlTheory.md 和 ReinforcementLearning.md 遗留的 Callouts

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| [ControlTheory.md](Foundations/ControlTheory.md) | +数据驱动阻抗辨识, +学习可变阻抗控制 (2 个 Callouts) |
| [ReinforcementLearning.md](Foundations/ReinforcementLearning.md) | +数据飞轮, +观测空间课程适应 (2 个 Callouts) |
| [TASK_TRACKER.md](.github/TASK_TRACKER.md) | 更新任务完成状态 |

**新增理论 Callouts** (4 个):
1. **数据驱动阻抗辨识**：凸优化框架从演示数据学习阻抗参数的连续函数 (Prosthesis VI)
2. **可变阻抗作为 RL 动作空间**：VICES 架构——末端位移 + 对角刚度增益 (VICES)
3. **数据飞轮**：策略与演示迭代相互促进，同伦优化从简单到复杂 (DexTrack)
4. **观测空间课程适应**：渐进移除特权信息 + Deep Random Generator (CSR)

---

### 历史会话: 2026-02-01 (教科书温习流程)

**主要工作**: 
1. 🔧 **standard-workflow.prompt.md 更新** — 添加 Phase 1.5 教科书温习流程
2. 📚 **教科书温习** — 从 Murray 教科书提取 Force-Closure 严格定义
3. 🎓 **ContactMechanics.md 增强** — 补充 Caratheodory/Steinitz 定理

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| [standard-workflow.prompt.md](.github/prompts/standard-workflow.prompt.md) | +Phase 1.5 教科书温习, +教科书-概念映射表, +触发条件 |
| [ContactMechanics.md](Foundations/ContactMechanics.md) | +Caratheodory 定理, +Steinitz 定理, +例外曲面定义 |
| [TASK_TRACKER.md](.github/TASK_TRACKER.md) | 更新任务完成状态 |

**standard-workflow.prompt.md 更新要点**:
- 新增 Phase 1.5 教科书温习流程（每次会话执行）
- 添加 Books/ 文件夹教科书清单与 Foundation 对应关系
- 添加温习触发时机和执行标准
- 添加教科书-概念映射表

**教科书温习成果**:
- 从 Murray 教科书提取了力闭合的凸分析基础
- 补充了 Caratheodory 定理（接触点数下界）
- 补充了 Steinitz 定理（接触点数上界）
- 补充了例外曲面的严格定义

**会话结束状态**: ✅ 正常完成

**下次会话建议**: 
1. 从 Deep RL 教科书温习 SAC 熵正则化理论
2. 从 Optimization 教科书温习凸优化基础定理
3. 补充 InformationTheory.md (Information Bottleneck)

---

### 历史会话: 2026-02-01 (Foundation 补充)

**编辑的文件**:

### 每次会话必做
1. **开始时**: `read_file: .github/TASK_TRACKER.md`
2. **结束前**: 更新本文件的任务状态和会话快照

### 任务记录规范
- 任务描述要**具体明确**
- 包含**文件路径**和**具体位置**（如 Section X.Y）
- 记录**断点状态**：下一步是什么
- 标注**依赖关系**：需要先完成什么

### 优先级判断
- 🔴 紧急: 影响知识图谱完整性的问题
- 🟡 进行中: 已开始但未完成的任务
- 🟢 计划中: 识别出的优化机会

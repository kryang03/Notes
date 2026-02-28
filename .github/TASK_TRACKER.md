# 知识图谱任务追踪器 (Task Tracker)

> [!important] 使用说明
> 这是 AI Agent 的工作记忆文档。每次会话开始时**必须首先阅读**本文件，会话结束前**必须更新**本文件。
> 
> 这确保了跨会话的任务连续性，解决了上下文限制导致的任务中断问题。

**最后更新**: 2026-02-28 (首批服务器实验结果合并 — Exp2 奖励搜索 + 历史 Kp 数据)

---

## 🟢 本次会话完成 (2026-02-28 #5)

### 首批服务器实验结果处理

**触发**：MergeBuffer/all_Insights_server/ 收到远端服务器首批实验结果（Smoke Test + Exp2 TA/TP 奖励搜索 + 历史 Kp×AS 数据 + Exp3a 运行中）。

#### 核心发现

| 发现 | 影响 |
|-----|------|
| TA: Light BASE SR=0.83 > TWC SR=0.72 | TWC 对 TA 无益，简洁奖励最优 → 影响 Idea-003, 006 |
| TP: Medium TWC SR=0.86 最优, α→1.0 | TWC 对 TP 有决定性优势 → 影响 Idea-001, 007 |
| Heavy 奖励配置普遍 SR=0 | 过多 shaping reward → reward hacking → 支持 Idea-003 因果分析 |
| TWC 降方差 19× (TP Reduced) | TWC 稳定性价值在 TP 上显著 → 支持 Idea-007 |
| 历史 Kp 最优区间 3.5~8.5 (TP) | 基准阻抗灵敏度高 → 支持 Idea-001 变阻抗假设 |

#### 修改的文件

| 文件 | 变更内容 |
|------|---------|
| `research-insights.prompt.md` | 同步架构更新为 MergeBuffer 中转模式（3 处替换） |
| `Idea-001-Phase-Adaptive Impedance.md` | 迭代日志合并历史 Kp 数据 + Exp2 TP 基线 + 下一步方向 |
| `Idea-003-Causal Mediator Reward.md` | 迭代日志合并 TA 奖励搜索结果 + 单 mediator 实验提案 |
| `Idea-006-Adaptive Lipschitz Actor.md` | 迭代日志合并 Heavy 失败分析 + ALA 验证实验提案 |
| `Idea-007-Dual Orthogonal Curriculum.md` | 迭代日志合并 TWC 不对称性发现 + 状态轴课程提案 |
| `_ExperimentResultsAll.md` | 填充 5 个结构化实验条目（4 完成 + 1 运行中） |
| `_InsightsIndex.md` | 新增实验进度总览表 + Exp2 核心发现摘要 + MergeBuffer 同步说明 |

#### 清理

- ✅ 删除 `MergeBuffer/all_Insights_server/`（已处理完毕）

#### 下一步服务器实验方向

1. **等待 Exp3a 完成** → α 直接训练结果，影响 TWC 理解
2. **PAI Stage 0** → 在 TP Medium TWC SR=0.86 基线上测试固定 vs 相位自适应 Kp
3. **CMR 单 mediator** → 在 TA Light BASE SR=0.83 基线上测试单 ω 奖励能否超越
4. **ALA 验证** → 在 TA Heavy (SR=0) 上测试 Lipschitz 约束能否恢复训练

---

## 🟢 上次会话完成 (2026-02-28 #4)

### 远端服务器同步机制集成

**触发**：用户要求将 `all_Insights/` 文件夹与远端服务器的双向同步特性写入 instructions 和 prompt 中，使远端 Agent 能正确读取 Idea 文档、写入实验结果。

#### 修改的文件

| 文件 | 变更内容 |
|------|---------|
| `.github/prompts/research-insights.prompt.md` | 新增「远端同步协议」节（架构图 + 本地/远端 Agent 职责 + `_ExperimentResultsAll.md` 格式规范）；更新输出目录为 `all_Insights/`；新增阶段 A 步骤 2「检查远端实验结果」；Idea 模板新增 §6 动态迭代日志（含同步说明）；质量红线新增 2 条同步相关准则 |
| `_ExperimentResultsAll.md` | 从空文件填充为完整的远端 Agent 操作指南：文件夹结构、CodeStructure 快速参考、Idea 索引（含关键配置变量）、结果记录模板 |
| `Idea-001 ~ Idea-007` (7 个文件) | §6 动态迭代日志 callout 统一更新为同步感知版本（标注结果来源为 `_ExperimentResultsAll.md`、表头增加 EXP-ID 列） |
| `_InsightsIndex.md` | 新增 `> [!important]` 同步机制说明 callout |
| `.github/copilot-instructions.md` | 关键文件表新增 `_ExperimentResultsAll.md`；Phase 0 新增步骤 4（检查远端实验结果）；必做事项新增 2 条同步相关条目 |

#### 同步架构

```
本地 Obsidian ◄──── 同步 ────► 远端 8×A100 服务器
    │                                    │
    ├── Idea 文档 (实验计划) ──────►      ├── 读取 Idea + CodeStructure
    ├── CodeStructure.md ──────────►     ├── 执行实验
    │                                    ├── 写入 _ExperimentResultsAll.md
    └── 读取新结果 ◄────────────────      └──
         ↓
    更新 Idea 迭代日志
```

### 知识库状态

| 指标 | 数值 |
|-----|-----|
| 修改文件 | 11 (1 prompt + 1 instructions + 1 ExperimentResults + 7 Ideas + 1 InsightsIndex) |
| 新增文件 | 0 |

---

## 🟢 上次会话完成 (2026-02-28 #3)

### Research Insights 第二轮迭代（Prompt 更新 + 执行）

**触发**：用户更新 `research-insights.prompt.md` 添加两条新准则：
1. 8×A100 集群可用 → 优先 Grid Search 暴力验证
2. 动态迭代 → Idea 文档需持续更新实验结果

#### Phase A: 全量信息收集（第二轮扫描）

- ✅ **PapersRecap 增量扫描**: 14 篇之前未覆盖的论文
  - 🔴 Very High: LipsNet (P1+P4), Finger Gaiting (P3+P5)
  - 🟠 High: DemoStart (P2+P3), DexTrack (P1+P4)
  - 🟡 Medium: DemoSpeedup (P2+P4), DexNDM (P4)
- ✅ **Foundation 前沿扫描**: 11 个 Foundation × 开放问题 → 26 个 open problems
  - 完全未覆盖的高价值方向: World Model, Empowerment pretraining, RL Scaling Laws × HDC

#### Phase B: 现有 Idea 增强

- ✅ **所有 5 个 Idea (001-005) 添加 Stage 0: Grid Search 快速验证节**
  - Idea-001: Kp ∈ {2,5,12,25,50} × 3 seeds, ~1天
  - Idea-002: β ∈ {0.0,0.3,0.5,0.7,0.9} × 3 seeds, ~6h
  - Idea-003: 手工 mediator reward (ω+Fn 阈值), ~1.5天
  - Idea-004: 成功状态初始化 δ ∈ {1.0,0.7,0.3} × 3 seeds, ~1.5天
  - Idea-005: Oracle 参数输入 vs 无参数 vs 噪声参数, ~2天
- ✅ **所有 5 个 Idea 添加"动态迭代日志"节** — 用于记录实验结果和决策

#### Phase C: 新 Idea 生成

| ID | 标题 | 三角定位 | 可行性 | 新颖性 | 优先级 |
|----|------|---------|--------|--------|--------|
| 006 | Adaptive Lipschitz Actor (ALA) | P1×P4 × LipsNet × ControlTheory stability | A | B+ | **P0→P1** |
| 007 | Dual Orthogonal Curriculum (DOC) | P2×P3 × DemoStart ZVF × Finger Gaiting waypoint | A | B+ | **P0** |

- ✅ **Idea-006**: 状态自适应 Lipschitz 约束 → 消除动作抖动，改变网络架构（与 001 正交）
- ✅ **Idea-007**: 物理难度 α × 状态难度 δ 双正交课程 → 直接嵌入 HDC 论文

#### Phase D: 索引更新

- ✅ **_InsightsIndex.md 重写**：
  - 新增 Idea-006、007 到所有矩阵
  - 新增 "Stage 0 执行计划" 节（Week 1-4 时间线）
  - 新增 "正交性与组合矩阵" 节
  - 新增 "新增文献关联" 节
- ✅ **TASK_TRACKER 更新**（本文件）

### 知识库状态

| 指标 | 数值 |
|-----|-----|
| 新增文件 | 2 (Idea-006, Idea-007) |
| 修改文件 | 6 (Ideas 001-005 + InsightsIndex) |
| Insights 总数 | **7** (5 → 7) |
| P0 Ideas | 4 (001, 002, 006, 007) |
| Stage 0 Grid Search 总量 | ~100 runs (~4天 on 8×A100 并行) |

---

## 🟢 上次会话完成 (2026-02-28 #2)

### Research Insights Generator

- ✅ **创建 `.github/prompts/research-insights.prompt.md`**: 从知识库全量分析到顶会 Idea 的标准化生成流程
  - 痛点-理论-文献 三角定位方法论
  - Idea 文档标准模板
  - 可行性评估矩阵
  - 质量红线与 reviewer 模拟

### DNPM Research Insights 生成（5 个原创 Idea）

| ID | 标题 | 核心贡献 | 目标会议 | 优先级 |
|----|------|---------|---------|--------|
| 001 | Phase-Adaptive Impedance (PAI) | 逐指时变阻抗 + 频率自适应，消解频率-动力学混淆 | RSS/CoRL | **P0** |
| 002 | Contact-Adaptive Autoregressive Exploration (CA-ARP) | 接触自适应 AR-p 探索噪声替代白噪声 | CoRL/ICRA | **P0** |
| 003 | Causal Mediator Reward (CMR) | 物理中介变量的因果 credit assignment | NeurIPS/ICML | **P1** |
| 004 | Convex Safe Set Bootstrapping (CSS) | 成功经验几何凸包引导探索 | RSS/CoRL | **P1** |
| 005 | Test-Time Contact Adaptation (TTCA) | 部署时探测性交互在线辨识接触参数 | CoRL/ICRA | **P2** |

- ✅ 每个 Idea 包含：完整 Intro 故事线、方法论（含数学公式）、实验计划（精确到代码文件）、风险分析、知识库关联
- ✅ 创建 `Projects/Dynamic Non-Prehensile Manipulation/Insights/` 文件夹及 6 个文件（含索引）
- ✅ 所有 Idea 与 ideas.md 中已有方向 A/B/C/D 建立了清晰的映射关系

### 知识库状态

| 指标 | 数值 |
|-----|-----|
| 新增文件 | 7 (1 prompt + 1 index + 5 ideas) |
| Insights 总数 | 5 |
| 覆盖 Foundations | 9/11 |
| 覆盖 PapersRecap | 12+ 篇 |
| 实验计划总量 | ~180 次训练 (~28 GPU-天 on 8×A100) |

---

## 🟢 上次会话完成 (2026-02-28)

### 知识库健康扫描

- ✅ **全库断链检查**: Python 脚本扫描所有 wikilinks（文件级 + 章节级），结果 **0 个真实断链**
- ✅ **Foundation 演进链审计**: 全部 11 个 Foundation 文件的 evolution chain 均已验证完整
  - Dynamics: Lagrangian → RNEA → ABA → Spatial Vector → Contact Dynamics ✅
  - ControlTheory: PID → **CTC (新增)** → Impedance → Admittance → Unified ✅
  - RL: DQN → DDPG → TD3 → SAC → PPO → Offline RL → Diffusion Policy ✅
  - 其他 8 个领域均已验证 ✅

### ControlTheory.md — 计算力矩控制 (CTC) 子节插入

- ✅ **新增 §3.1.1**: "从 PID 到计算力矩：精确线性化的诱惑与局限"
  - 基于 Murray 教科书 Ch.4 §5.2-5.3 (Proposition 4.8)
  - CTC 公式推导 + 结构分解（前馈 + 反馈）
  - **3 个不适合灵巧操作的原因**: 模型依赖性、环境交互缺失、PD 本质局限
  - 与 DNPM 项目的直接联系 callout（ideas.md §3.1 PD 力矩 pattern 受限现象）
  - 演进逻辑桥: PID → CTC → 阻抗控制
- ✅ **演进链补全**: ControlTheory §3 从 PID 直接跳到阻抗控制 → 现在有完整的 PID → CTC → 阻抗 理论桥梁

### Canvas 更新

- ✅ **found_control_insight 节点更新**: `阻抗控制/力-位混合/模式切换` → `PID→CTC→阻抗控制/力-位混合·时变刚度/计算力矩理论基础`
- ✅ Canvas 结构完整性验证: 48 节点、61 边均正常

### 清理

- ✅ **重复 PDF 删除**: `Lessons from Learning to Spin "Pens".pdf`（带引号的重复副本，54→54 PDFs）

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 54 |
| PapersRecap 笔记 | 57 (含 _PapersIndex.base) |
| MergeBuffer 待处理 | 0 |
| Foundation 文件 | 12 (11 + taxonomy) |
| Canvas 节点 | 48 |
| Canvas 边 | 61 |
| 断链 | 0 |
| ControlTheory 新增章节 | 1 (§3.1.1 CTC) |

---

## 🟢 上次会话完成 (2026-07-16)

### 核心原则嵌入

- ✅ **copilot-instructions.md**: 新增"穷尽式完善"和"MergeBuffer零废弃"两条核心使命
- ✅ **SKILL.md**: 新增 Error Pattern 2 (将MergeBuffer内容标为"无关") 和 Error Pattern 3 (提前停止)
- ✅ 更新绝对禁止/必须做清单

### MergeBuffer 深度整合（5篇，之前被错误标注为"无关"）

| 文件 | 整合目标 | 关键洞见 |
|-----|---------|---------|
| 从梯度角度看SFT...pdf | RL §2.5 PPO + DNPM ideas | SFT=稀疏RL 统一梯度框架，on-policy蒸馏用于sim-to-real |
| Mediator-Based Reward Design | RL §4.2 奖励工程 + DNPM §2.5.3 | 中间变量(mediator)降低奖励方差，解决DNPM长因果链credit assignment |
| Compression-Based Denoisers | InformationTheory §5.0 + SignalProcessing §5.4 | 压缩=去噪的形式化证明，IB→触觉信号去噪 |
| IsoCompute Playbook | RL §6.3 新增 + DNPM §2.5.4 | RL Scaling Laws: easy/hard熵区分、计算饱和检测 |
| Learning to Discover at Test Time | RL §6.4 新增 | Test-Time RL: 部署时在线适应新环境 |

### DNPM ideas.md 增强

- ✅ §2.5.3 新增 Mediator 实验设计（接触力作为surrogate reward中介）
- ✅ §2.5.4 新增 Scaling Law 指引（HDC课程的easy/hard熵控制）
- ✅ §4.1 新增 5 条 Foundations 关联索引

### 穷尽式改善扫描

- ✅ **断链检查**: 0 个断链（新增6个章节链接全部有效）
- ✅ **taxonomy.md 更新**: InfoTheory×RL 升级为强关联（mediator奖励、scaling laws熵控制）；新增 InfoTheory×SignalProcessing（压缩-去噪对偶性）；更新 InfoTheory 描述
- ✅ **PapersRecap 交叉引用**: EUREKA 笔记新增到 RL §4.2 mediator奖励的链接；DemoSpeedup 笔记新增到 RL §6.3 Scaling Laws 的链接
- ✅ **Canvas 更新**: 新增 InformationTheory Foundation 节点 + 洞察节点；新增 3 条边（稀疏奖励→信息论、表征→信息瓶颈）；扩展 foundations_group 宽度
- ✅ **MergeBuffer 清理**: 6个已整合PDF全部删除，仅保留 _MergeIndex.md 历史记录

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 55 |
| PapersRecap 笔记 | 56 |
| MergeBuffer 待处理 | 0 |
| Foundation 文件 | 11 + taxonomy |
| Canvas 节点 | 48 (+6) |
| Canvas 边 | 61 (+3) |
| Foundation 新增章节 | 4 (RL §2.5 callout, §6.3, §6.4; InfoTheory §5.0 callout) |

---

## 🟢 上次会话完成 (2026-02-27)

### 新论文处理

| 论文 | 类型 | 与DNPM关联 |
|-----|------|-----------|
| **FACET: Force-Adaptive Control via Impedance Reference Tracking** | 阻抗参考模型跟踪 | ⭐⭐ **方向A的核心方案** — 时变阻抗直接匹配 snap/spin/catch 相位 |

### DNPM 项目强化 — 方向A（Low-Level Controller 优化）

- ✅ **ideas.md 3.1.3 研究方向重构**：从 3 个方案扩展为 5 个方案
  - 新增方案 2：阻抗参考模型跟踪（FACET）⭐
  - 新增方案 5：阻抗参考模型 + 时间自适应（FACET + TARC 融合）⭐⭐
  - 更新任务-算法匹配表，覆盖所有 4 类任务
- ✅ **Dynamic Non-Prehensile Manipulation.md 算法 TODO 更新**：新增阻抗参考模型跟踪实验计划
  - 三组对比实验：固定 PD vs VICES 变阻抗 vs FACET 参考模型跟踪
  - 进阶融合实验：$(x_{des}, K_p, K_d, \Delta t)$ 输出

### Foundations 更新

- ✅ **ControlTheory.md 3.2 节**：新增 FACET 阻抗参考模型跟踪 callout
  - 完整数学框架：参考模型动力学、时间平滑技术、VICES 对比表
  - 灵巧操作启发：关节级参考模型、多体扩展
- ✅ **ControlTheory.md 论文索引**：新增 FACET 反向链接

### Canvas 更新

- ✅ **KnowledgeGraph.canvas**：新增 FACET 论文节点
  - 连接到 `bt_impedance`（变阻抗控制突破点）
  - 连接到 `found_control`、`found_dynamics`（理论基础）
  - VICES → FACET 演进关系边

### 断链修复（16 处，涉及 9 个文件）

| 断链类型 | 数量 | 涉及文件 |
|---------|-----|---------|
| ReinforcementLearning 章节引用 | 8 | HER, TARC, Dexterous RL, Long-Horizon, Vision-force, DemoStart, Part-Guided, ideas.md |
| Dynamics 章节引用 | 4 | ideas.md (×4) |
| SignalProcessing 章节引用 | 3 | Visual-tactile, Vision-force |
| RepresentationLearning 章节引用 | 2 | Visual-tactile, Vision-force |
| ContactMechanics 章节引用 | 1 | Long-Horizon |
| FACET 笔记内部断链 | 2 | FACET (RL#2.5 PPO, Dynamics#3.1 Lagrangian) |

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 55 (+2 since last) |
| PapersRecap 笔记 | 55 |
| MergeBuffer 待处理 | 3 (非操作相关) |
| Foundation 文件 | 11 + taxonomy |
| Canvas 论文节点 | 13 (+1 FACET) |
| 断链修复 | 18 处 (本次) |

---

## 🟢 上次会话完成 (2026-02-03)

### 知识图谱可视化 Canvas

- ✅ **创建 `KnowledgeGraph.canvas`** — 知识库核心关联可视化
  - **核心结构**: Projects (DNPM) → 算法突破点 → PapersRecap → Foundations
  - **6 大算法突破点**:
    1. 控制频率困境 (TARC, Action Persistence, VTS-RL)
    2. 稀疏奖励探索 (HER, Privileged Action)
    3. 变阻抗控制 (VICES)
    4. 物理参数课程 (Curriculum Learning)
    5. Sim-to-Real 迁移 (RialTo, TRANSIC, Pen Spinning)
    6. 特权动作 (Privileged Action, Long-Horizon)
  - **12 篇核心论文节点**: 提取关键洞见/算法/Value-Add
  - **6 个 Foundations 关联**: RL, ControlTheory, Dynamics, ContactMechanics, Optimization, SignalProcessing
  - **关联边类型**: 痛点映射、核心方法、理论基础、论文间演进

### 维护规范建立

- ✅ **Canvas 维护指南**: 每次新增内容需检查是否与算法突破点相关，若相关则更新 Canvas

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 53 |
| PapersRecap 笔记 | 55 |
| MergeBuffer 待处理 | 2 (非操作相关) |
| Foundation 文件 | 11 + taxonomy |
| **Canvas 文件** | **1 (新增)** |

---

## 🟢 上次会话完成 (2026-02-02 下午)

### 新论文处理 (7篇)

| 论文 | 类型 | 与DNPM关联 |
|-----|------|-----------|
| **Hindsight Experience Replay** | 稀疏奖励探索 | ⭐ 核心基线方法 |
| **TARC: Time-Adaptive Robotic Control** | 频率自适应 | ⭐ 直接解决频率困境 |
| **Learning Long-Horizon via Privileged Action** | 特权动作 | ⭐ 惯性阶段简化方案 |
| **Vision-force-fused Curriculum Learning** | 多模态课程 | 感知融合范式 |
| **Visual-tactile Pretraining for Dexterity** | 低成本感知 | 简化触觉验证 |
| **Dexterous RL with Knowledge Transfer** | 知识迁移 | 慢→快任务迁移 |
| **Path-Constrained Haptic Admittance Control** | 人机协作 | 相位变量思想 |

### Projects 强化

- ✅ **DNPM 关联论文更新**: 新增 7 篇论文的分类索引
- ✅ **算法提升 TODO 扩展**: 新增 6 条实验方向
  - 时间自适应控制 (TARC)
  - 稀疏奖励基线 (HER)
  - 特权动作实验
  - 知识迁移消融
  - 视觉-力课程融合
  - 简化触觉验证

### Foundations 更新

- ✅ **ReinforcementLearning.md**: 新增 HER 章节（探索理论部分）

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 53 (+7) |
| PapersRecap 笔记 | 55 (+7) |
| MergeBuffer 待处理 | 2 (非操作相关) |
| Foundation 文件 | 11 + taxonomy |

### MergeBuffer 剩余

- `IsoCompute Playbook.pdf` - LLM RL Scaling，非操作相关
- `Learning to Discover at Test Time.pdf` - 通用 ML，非操作相关

---

## 🟢 上次会话完成 (2026-02-02 上午)

### 基础设施更新

- ✅ **创建 `.github/copilot-instructions.md`** — 全面的知识库管理指南
  - 核心使命与主动维护原则
  - 知识库架构说明
  - 强制工作流（Phase 0/1/2）
  - Foundation 领域映射
  - 主动修复清单
  - 论文笔记标准模板
  - 教科书参考规范
  - 理论导师模式说明
  - Obsidian 语法速查
  - 禁止/必须操作清单

### 断链修复 (2处)

- ✅ **DexTrack**: `ReinforcementLearning#2.2 Imitation Learning 的崛起与局限` → `#2.2 Imitation Learning (IL): 数据饥渴与分布漂移`
- ✅ **MimicGen**: 同上

### 知识库健康状态

| 指标 | 数值 |
|-----|-----|
| Papers PDFs | 46 |
| PapersRecap 笔记 | 48 |
| MergeBuffer 待处理 | 0（已清空）|
| Foundation 文件 | 11 + taxonomy |

### 验证完成

- ✅ 所有主要 Foundation 章节编号一致
- ✅ ReinforcementLearning 章节 2.2-2.8 引用验证通过
- ✅ Optimization 章节 2-8 引用验证通过
- ✅ ControlTheory 章节 1-10 引用验证通过

### Projects 强化

- ✅ **Dynamic Non-Prehensile Manipulation**: 补充 story-telling/intro、算法核心框架、算法提升 TODO
  - 增强与 [[Dynamics]]、[[ControlTheory]]、[[ReinforcementLearning]]、[[ContactMechanics]]、[[Optimization]]、[[SignalProcessing]] 的关联
  - 添加与 PapersRecap 的项目级索引（频率、变阻抗、Sim-to-Real 等）

---

## 🟢 已完成 (Completed This Session)

### 断链修复工作 - 全部完成 ✅

**本次会话完成的文件修复** (35+ 文件):

**ReinforcementLearning 章节引用** (主要断链):
- ✅ Reachability Constrained RL: `#5.2 约束强化学习` → `[[ReinforcementLearning]]`
- ✅ DeepMimic: `#策略梯度` → `#3. Implementation`
- ✅ HIL-SERL: `#5. Actor-Critic`, `#8. Offline RL` → 正确章节
- ✅ Control Frequency Adaptation: `#5. 离线强化学习` → `#5. Bridging the Gap`
- ✅ TRANSIC: `#Human-in-the-Loop` → `[[ReinforcementLearning]]`
- ✅ Part-Guided 3D RL: `#不确定性感知模型`, `#3D RL` → 正确章节
- ✅ Stability-Certified RL: `#理论基础：Policy Gradient` → `#3. Implementation`
- ✅ Variable Impedance Control: `#2.2 动作空间设计` → `[[ReinforcementLearning]]`
- ✅ Physics-Driven Data Generation: `#Diffusion Policy` → `#6. Future Frontiers`
- ✅ SERL: `#5. Actor-Critic`, `#8. Offline RL` → 正确章节
- ✅ RotateIt: `#Rapid Motor Adaptation` → `#5. Bridging the Gap`
- ✅ Curriculum is More Influential: `#7. 课程学习` → `#4. Advanced State Space`
- ✅ EUREKA: `#2.7 Offline RL`, `#2.4 Actor-Critic` → 正确章节
- ✅ RialTo: `#6. Sim-to-Real` → `#5. Bridging the Gap`
- ✅ DexTrack: `#4.3 模仿学习` → `#2.2 Imitation Learning`
- ✅ Residual Learning: `#2.4 Actor-Critic` → `#3. Implementation`
- ✅ HORA: `#5. Actor-Critic` → `#3. Implementation`
- ✅ Dextrous Tactile: `#5. Actor-Critic` → `#3. Implementation`
- ✅ MimicGen: `#7. 模仿学习` → `#2.2 Imitation Learning`
- ✅ Learning Human-like Finger Gaiting: `#Exploration Strategies` → `#2.8 Exploration 理论`
- ✅ Off-Policy Interval Estimation: `#5.3 Offline RL` → `#5. Bridging the Gap`

**ControlTheory 章节引用**:
- ✅ How to Train Latent CBF: `#3.2 解决方案 I` → `#7. 鲁棒控制`
- ✅ Safe MBRL: `#3.2 解决方案 I` → `#7. 鲁棒控制`
- ✅ DexNDM: `#5.2 Residual Policy Learning` → `#9. 数据驱动控制`
- ✅ Elastic Time Step RL: `#2.1 阻抗控制` → `[[ControlTheory]]`
- ✅ LipsNet: `#2.1 阻抗控制` → `[[ControlTheory]]`
- ✅ Stability-Certified RL: `#3.1 稳定性理论` → `#7. 鲁棒控制`
- ✅ Data-Driven Variable Impedance: `#3.2 解决方案 I` → `#3. 技术演进`

**其他 Foundation 断链**:
- ✅ Autoregressive Policies: `StochasticProcess#3.2`, `SignalProcessing#4.1` → 正确章节
- ✅ GLIDE: `Optimization#Trajectory`, `ContactMechanics#Contact-Implicit`, `RepresentationLearning#Point Cloud` → 正确章节
- ✅ DemoSpeedup: `InformationTheory#Entropy`, `SignalProcessing#Time Series` → 正确章节
- ✅ Curriculum Learning: `Optimization#2.5`, `#3.1`, `RepresentationLearning#2.1` → 正确章节
- ✅ Robot Synesthesia: `ContactMechanics#2.2`, `#2.1`, `#2.4` → 正确章节
- ✅ P2GI: `RepresentationLearning#4. 点云表示学习` → 正确章节
- ✅ CyberDemo: `RepresentationLearning#2.4` → 正确章节
- ✅ Exploration vs Exploitation: `InformationTheory#2.1` → `#2. 信息度量场论`
- ✅ Lessons from Spin Pens: `ContactMechanics#3. 接触模型的演进` → `#3. 接触建模演变`

---

## 🔧 技术规范更新 (Skills Documentation)

**更新 `knowledge-graph-management/SKILL.md`**，新增以下章节：
- ✅ **3.4 Wikilink 章节引用规范（断链预防）** — 引用前验证、精确标题、泛化回退
- ✅ **3.5 Frontmatter 字段命名规范** — PapersRecap 和 Projects 的标准 frontmatter 模板
- ✅ **3.6 Obsidian Bases 公式规范** — file 属性完整列表、错误示例修正

---

## 📊 统计摘要

| 修复类型 | 数量 |
|---------|-----|
| Bases 公式 Bug | **2个文件** |
| Skills 规则更新 | **3个新章节** |
| **断链修复** | **35+个文件，共计60+处断链** |
| 待修复 | **0（全部完成）** |

---

## 🔵 例行维护 (Routine Maintenance)

### 断链修复 (Broken Links Fixed)

**SignalProcessing.md 断链修复** (5处):
- ✅ `Touch Dexterity - Training Tactile...` → `Touch Dexterity - Rotating without Seeing...`
- ✅ `RotateIt - Continuous In-Hand Rotation` → `RotateIt - General In-Hand Object Rotation...`
- ✅ `HATO - Learning Visuotactile...` → `Learning Visuotactile Skills with Two Multifingered Hands (HATO)`
- ✅ `Sampling Theorem in Robotics - an overview` → `The Sampling Theorem With Constant Amplitude...`
- ✅ `P2GI - Part-Guided 3D RL...` → `Proximity Perception-Based Grasping Intelligence (P2GI)`

**StochasticProcess.md 断链修复** (4处):
- ✅ `Physics-Driven Data Augmentation...` → `Physics-Driven Data Generation for Contact-Rich...`
- ✅ `Safe MBRL - Model-Based RL...` → `Safe Model-based Reinforcement Learning with Stability Guarantees`
- ✅ `Latent CBF - Control Barrier Functions...` → `How to Train Your Latent Control Barrier Function...`
- ✅ `HATO - Learning Visuotactile...` → `Learning Visuotactile Skills with Two Multifingered Hands (HATO)`

**ComputationalGeometry.md 断链修复** (4处):
- ✅ `RotateIt - Continuous In-Hand Rotation` → `RotateIt - General In-Hand Object Rotation...`
- ✅ `Lessons from Spin Pens - the Impact of Design...` → `Lessons from Learning to Spin Pens`
- ✅ `RialTo - Simulation to Real-World Transfer...` → `RialTo - Reconciling Reality through Simulation...`
- ✅ `P2GI - Part-Guided 3D RL...` → `Proximity Perception-Based Grasping Intelligence (P2GI)`

**ReinforcementLearning.md 断链修复** (2处):
- ✅ `Touch Dexterity - Training Tactile...` → `Touch Dexterity - Rotating without Seeing...`
- ✅ `RialTo - Simulation to Real-World Transfer...` → `RialTo - Reconciling Reality through Simulation...`

**InformationTheory.md 断链修复** (1处):
- ✅ `Weight-sparse transformers - disentangled...` → `Weight-sparse transformers have interpretable circuits`

### Frontmatter 格式统一

**修复的论文笔记**:
- ✅ **Dynamic Reinforcement Learning for Actors.md**: PaperRecap → paper, 添加 paper-year, 优化 aliases
- ✅ **Learning Human-like Finger Gaiting.md**: 添加 paper-year
- ✅ **GLIDE.md**: 添加 paper-year
- ✅ **Exploration versus Exploitation in RL.md**: PaperRecap → paper, 添加 paper-year, aliases, abstract callout

### Callout 结构补充

- ✅ **Dynamic Reinforcement Learning for Actors.md**: 添加标准 `[!abstract]` callout
- ✅ **Weight-sparse transformers have interpretable circuits.md**: 添加标准标题 + `[!abstract]` callout

### Obsidian Bases 视图创建

- ✅ **PapersRecap/_PapersIndex.base**: 论文笔记多视图索引
  - 📚 全部论文（按年份分组）
  - 🔗 按 Foundation 领域
  - 🤖 灵巧操作核心
  - 🎮 强化学习相关
  - 🔄 Sim-to-Real
  - 📖 最近添加
- ✅ **Foundations/_FoundationsIndex.base**: Foundation 概览视图
  - 📖 Foundation 概览（含内容量统计）
  - 🕐 最近更新

### 统计摘要

| 修复类型 | 数量 |
|---------|-----|
| Foundation 断链 | **16处** |
| Frontmatter 格式 | **4个文件** |
| Callout 补充 | **3个文件** |
| Base 视图创建 | **2个文件** |

---

## 🔧 历史会话链接健康检查 (2026-02-01)

**发现并修复的断链**:
- ✅ **LatentCBF.md**: `ControlTheory#2.3 Safe RL` → `ControlTheory#3.2` (CBF 形式化定义)
- ✅ **Reachability Constrained RL.md**: `ControlTheory#5.3 安全集与不变性` → `ControlTheory#3.2`
- ✅ **Safe Model-based RL.md**: `ControlTheory#2.3 Safe RL` → `ControlTheory#3.2`

**Theory of Deep Learning 整合状态更新**:
- [x] Chapter 8: Algorithmic Regularization ✅ (标记从"可选"更新为"已完成")

---

## 📖 教科书/理论整合执行记录 (2026-02-01 最新)

### 本次整合：Algorithmic Regularization (隐式正则化) → RepresentationLearning.md

**触发源**: 教科书覆盖检查 (textbook-integration.prompt.md)

**发现问题**: 搜索 "隐式正则化|implicit regularization" 无结果，Theory of Deep Learning Chapter 8 尚未整合

**源材料**: 
- `Books/Theory of Deep Learning.pdf` — Chapter 8: Algorithmic Regularization
- Proposition 8.1.1: GD 的最小范数偏置
- Theorem 8.1.2: Mirror Descent 的 Bregman 散度隐式偏置

**新增内容**: `RepresentationLearning.md` Section 6.3.5 "隐式正则化：为什么过参数化模型能泛化？"
- ✅ **过参数化悖论的解答**: 优化算法本身引入隐式正则化
- ✅ **Proposition 8.1.1**: GD 收敛到 $\arg\min_{w \in \mathcal{G}} \|w - w_0\|_2$
- ✅ **Theorem 8.1.2**: Mirror Descent 收敛到 Bregman 散度最小解
- ✅ **算法-势函数-偏置对照表**: GD/指数梯度/自然梯度
- ✅ **深度网络的隐式正则化**: 线性网络→低秩、ReLU→低复杂度
- ✅ **灵巧操作含义**: 策略初始化、LoRA 微调、Diffusion Policy

---

### 历史整合：Control Barrier Function (CBF) → ControlTheory.md

**触发源**: 用户当前打开 [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints|LatentCBF]] 论文笔记

**发现问题**: ControlTheory.md 多处提及 CBF 但缺乏形式化数学定义

**新增内容**: `ControlTheory.md` Section 3.2 末尾
- ✅ **安全集与屏障函数定义**: $\mathcal{C} = \{x : h(x) \geq 0\}$
- ✅ **CBF 形式化定义**: $\sup_u [L_f h + L_g h \cdot u] \geq -\alpha(h(x))$
- ✅ **CBF-QP 安全滤波器**: $\min_u \|u - u^{\text{nom}}\|^2$ s.t. CBF 约束
- ✅ **CBF 与 Lyapunov 对偶表**: 稳定性 vs 安全性对比
- ✅ **HJ 可达性与 CBF 联系**: 值函数光滑性传递定理
- ✅ **LatentCBF 关键洞察**: WGAN 梯度惩罚 + 潜空间安全过滤

---

### 历史整合：Theory of Deep Learning → Optimization.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- `Books/Theory of Deep Learning.pdf` — Arora et al.
- Chapter 6: Tractable Landscapes for Nonconvex Optimization
- Chapter 7: Escaping Saddle Points

**新增内容**: `Optimization.md` Section 2.5 "非凸优化景观理论"
- ✅ **2.5.1 关键障碍的形式化定义**:
  - 全局/局部极小值、虚假局部极小值的严格定义
  - 鞍点定义与二阶充分条件 (Hessian 判据)
- ✅ **2.5.2 良好景观的特征**:
  - Polyak-Łojasiewicz (PL) 条件
  - 弱拟凸与受限割线不等式 (RSI)
  - 几何收敛定理
- ✅ **2.5.3 对称性与鞍点的必然性**:
  - 置换对称性导致非凸的证明
  - 二阶驻点 (SOSP) 定义
- ✅ **2.5.4 鞍点逃逸：扰动梯度下降**:
  - Ge et al. 2015 鞍点逃逸定理
  - 逃逸机制的物理直觉
  - SAC 熵正则化与鞍点逃逸的联系
- ✅ **2.5.5 深度学习景观的经验发现表**

**跨文件更新**:
- ✅ **Curriculum Learning.md** — 添加到 [[Optimization#2.5 非凸优化景观理论]] 的反向链接

**Theory of Deep Learning 教科书整合状态**:
- [x] Chapter 5: Generalization Theory ✅ (RepresentationLearning.md 6.3)
- [x] Chapter 6-7: Nonconvex Landscapes & Saddle Escaping ✅ (Optimization.md 2.5)
- [x] Chapter 8: Algorithmic Regularization (隐式正则化) ✅ (RepresentationLearning.md 6.3.5)
- [ ] Chapter 9: Neural Tangent Kernel (NTK) — 可选 (理论性强)

---

## 📖 教科书整合执行记录 (2026-02-01 历史)

### 历史整合：SAC 数学理论推导 → ReinforcementLearning.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- Deep RL 教科书标注 "Add SAC"（占位符）
- Haarnoja et al. SAC 原论文 (ICML 2018) 理论推导

**新增内容**: `ReinforcementLearning.md` Section 2.4 "SAC 数学理论推导"
- ✅ **软值函数定义**: $V^\pi_{soft}$, $Q^\pi_{soft}$ 的形式化定义
- ✅ **软贝尔曼方程**: 递归关系与 log-sum-exp 形式
- ✅ **软策略迭代收敛定理**: 单调递增性与唯一解
- ✅ **SAC 实用算法三组件**: 软 Q 损失、策略损失、温度损失
- ✅ **自动温度调整物理意义**: 自适应刚柔调节
- ✅ **SAC 演进脉络表**: SQL → SAC v1 → SAC v2

**Deep RL 教科书整合状态**:
- [x] Chapter 2.7: Q值过高估计定理 ✅
- [x] Chapter 3.3-3.4: TRPO 理论基础 ✅
- [x] Chapter 4.3: SAC 详细推导 ✅ (本次完成)
- [x] Chapter 4.4: Off-Policy Actor-Critic 谬误 ✅
- [x] Chapter 5: Model-Based RL ✅
- [x] Chapter 6: Exploration 理论 ✅

---

## 📖 教科书整合执行记录 (2026-02-02 最新)

### 本次整合 (续)：Murray 教科书 Ch.4 & Ch.6 → Dynamics.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- `Books/A Mathematical Introduction to Robotic Manipulation.pdf` — Murray, Li & Sastry
- Chapter 4: Robot Dynamics (Lagrangian Formulation)
- Chapter 6: Hand Dynamics (Pfaffian Constraints)

**新增内容**: `Dynamics.md`
- ✅ **Section 3.1.1**: 开链机器人的 Lagrangian 推导
  - 动能/势能公式
  - 操作器方程 (Manipulator Equation)
  - Christoffel 符号形式
  - $\dot{M} - 2C$ 反对称性质 (Passivity-based Control 基础)
- ✅ **Section 2.3.1**: Pfaffian 约束与约束动力学
  - Pfaffian 约束形式化定义
  - 可积性与完整/非完整分类
  - Lagrange-d'Alembert 方程
  - Lagrange 乘子显式解
  - 混合位置/力控制的数学基础

**Murray 教科书整合状态**:
- [x] Chapter 2: 刚体运动学 ✅ (之前完成)
- [x] Chapter 4: Lagrangian 动力学 ✅ (本次完成)
- [x] Chapter 6: 约束动力学 ✅ (本次完成)
- [x] Chapter 5: 接触建模 — ContactMechanics.md 已覆盖

---

### 本次整合：Optimization in Theory and Practice → Optimization.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- `Books/Optimization in Theory and Practice.pdf` — Wright (arXiv 2025)
- 内容覆盖: LP, 无约束优化, 内点法, 复杂度理论

**新增内容**: `Optimization.md`
- ✅ **Section 2.4.4.1**: 原始-对偶内点法详解 (Primal-Dual Interior Point Methods)
  - LP 标准形式与 KKT 条件
  - 中心路径 (Central Path) 定义
  - 路径追踪算法 (Path-Following) 的牛顿系统
  - 复杂度定理: O(n log(1/ε)) 迭代
  - Mehrotra 预测-校正法简介
  - 灵巧操作应用连接

**教科书剩余可整合内容**:
- [x] Section 4: Linear Programming ✅ (本次 + 原有内容)
- [ ] Section 5: Unconstrained Optimization — 收敛速率理论 (可选)
- [ ] Section 7-8: SGD 与现代随机优化 (与 ML 更相关)

---

## 📖 教科书/资源整合执行记录 (2026-02-02)

### 本次整合：lumina-eai-guide.pdf → EmbodiedAI.md (新 Foundation)

### 本次整合：lumina-eai-guide.pdf → EmbodiedAI.md (新 Foundation)

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- `Books/lumina-eai-guide.pdf` - Lumina 具身智能社区入门指南
- GitHub 仓库: `TianxingChen/Embodied-AI-Guide` (11.6k stars)
- 网页资源: https://simulately.wiki/, https://github.com/TianxingChen/Embodied-AI-Guide

**新增文件**:
- ✅ **Foundations/EmbodiedAI.md** — 具身智能系统综述
  - Section 1: VLA 模型 (RT-1/2, OpenVLA, π₀, Octo, RDT)
  - Section 2: Robot Learning 范式 (RL vs IL vs MPC)
  - Section 3: Vision Foundation Models (CLIP, DINO, SAM)
  - Section 4: 仿真器生态 (Isaac Lab, MuJoCo, SAPIEN, Genesis)
  - Section 5: 硬件与数据基础设施
  - Section 6: Embodied AI for X (医疗/UAV/自动驾驶)
- ✅ **.github/skills/embodied-ai-resources/SKILL.md** — 资源追踪技能
  - VLA 模型追踪策略
  - 仿真器更新监控
  - 信息源优先级分级
  - 快速参考卡片

**跨文件更新**:
- ✅ **taxonomy.md** — 添加 EmbodiedAI 到领域速查表、领域关联图
- ✅ **ReinforcementLearning.md** — 添加 EmbodiedAI 反向链接
- ✅ **ControlTheory.md** — 添加 EmbodiedAI 反向链接
- ✅ **RepresentationLearning.md** — 添加 EmbodiedAI 反向链接

---

## 📖 教科书整合执行记录 (2026-02-02 续)

### 本次整合：Deep RL 教科书 Chapter 3 & 5 → ReinforcementLearning.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**Phase 3-4: Foundation 融合（续）** ✅
- **新增内容**: `ReinforcementLearning.md`
  - Section 2.5 (TRPO/PPO): 添加 "Policy Gradient as Policy Iteration" 理论框架
    - 新策略性能提升的优势函数分解
    - 重要性采样推导
    - 分布间隙边界定理 (Distribution Gap Bound)
    - 信任域约束的理论合法性解释
  - Section 2.6 (Model-Based RL): 大幅扩展
    - MPC (Model Predictive Control) 算法演进 (v0.5 → v1.5)
    - 分布不匹配问题 (Distribution Mismatch) 及其解决
    - 两种不确定性：Aleatoric vs Epistemic
    - Bootstrap Ensemble 方法

**教科书剩余可整合内容**:
- [x] Chapter 3.3-3.4: TRPO 理论基础 ✅ (本次完成)
- [x] Chapter 5: Model-Based RL 核心理论 ✅ (本次完成)
- [x] Chapter 6: Exploration 理论 ✅ (本次完成)
  - 信息论基础 (熵, 互信息, Empowerment)
  - 无奖励探索: 技能发现 (DIAYN, Skew-Fit)
  - Exploration Bonus: 内在动机
- [ ] Chapter 4.3: SAC 详细推导（熵正则化的完整推导）— 教科书标注 "Add SAC"

---

## 📖 教科书整合执行记录 (2026-02-02)

### 本次整合：Deep RL 教科书 → ReinforcementLearning.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**源材料**: 
- `Books/Deep Reinforcement Learning.pdf` - 清华大学 Wang & Xiong 深度强化学习笔记 (2024)
- 约 6640 行，涵盖 RL 基础到高级 Actor-Critic 方法

**Phase 1-2: 内容分析与 Insights 提取** ✅
- Chapter 2.7: Q值过高估计的数学证明 (Theorem 2.1, 2.2)
- Chapter 4.4: Off-Policy Actor-Critic 的两个谬误与修正

**Phase 3-4: Foundation 融合** ✅
- **新增内容**: `ReinforcementLearning.md`
  - Section 2.4 (DDPG): 添加 Q值过高估计定理 (Theorem 2.1, 2.2) 及证明思路
  - Section 3.0 (新增): Off-Policy Actor-Critic 理论基础与常见谬误
    - 谬误1: 目标值中的策略不一致
    - 谬误2: 策略梯度中的动作不一致
    - 修正方法: Q函数替代V函数 + 重新采样动作

**教科书剩余可整合内容**:
- [x] Chapter 3.5: TRPO/PPO 详细算法 ✅ (后续完成)
- [ ] Chapter 4.3: SAC 详细推导（当前标注 "Add SAC"）
- [x] Chapter 5: Model-Based RL 理论 ✅ (后续完成)
- [ ] Chapter 6: Exploration 理论

---

## 📖 教科书整合执行记录 (2026-02-01)

### 本次整合：Murray 教科书 → Dynamics.md

**使用工作流**: `.github/prompts/textbook-integration.prompt.md`

**Phase 1-2: 内容分析与 Insights 提取** ✅
- 目标教科书: Murray, Li & Sastry "A Mathematical Introduction to Robotic Manipulation"
- 目标章节: Chapter 2 (Rigid Body Motion) - 指数坐标与 Rodrigues 公式
- 提取工具: `pdftotext` → Chapter 2 约 2000 行

**Phase 3-4: Foundation 融合** ✅
- **新增内容**: `Dynamics.md` Section 2.4 "刚体变换与指数坐标"
  - 2.4.1 旋转群 $SO(3)$ 与李代数 $so(3)$
  - 2.4.2 Rodrigues 公式（定理陈述 + 证明思路）
  - 2.4.3 齐次变换与 $SE(3)$
  - 2.4.4 灵巧操作应用（PoE 运动学, Montana 方程, 轨迹插值）
- **交叉链接**: 关联 ControlTheory#2.2, ContactMechanics#2.2

**Phase 5: PapersRecap 关联** ✅
- [x] **DexNDM**: 添加教科书背景（RNEA 分解思想与神经动力学的关系）
- [x] **Robot Synesthesia**: 添加教科书背景（Montana 方程与触觉点云的关系）
- [x] **Autoregressive Policies**: 添加教科书背景（SAC 熵正则化理论的时间维度缺陷）

**未整合内容（留待后续）**:
- [x] Murray Ch.4 (Robot Dynamics) ✅ 已补充 Lagrangian 推导详解 (2026-02-02)
- [x] Murray Ch.5 (Multifingered Hand Kinematics) → 已确认 ContactMechanics.md 覆盖充分
- [x] Murray Ch.6 (Hand Dynamics) ✅ 已补充 Pfaffian 约束动力学 (2026-02-02)

---

## 📚 新增工作流 Prompt (2026-02-01)

### textbook-integration.prompt.md ✅ 已创建

**位置**: `.github/prompts/textbook-integration.prompt.md`

**功能**: 标准化从教科书中提取 Insights 与算法脉络，整合到 Foundations 和 PapersRecap 的流程

**核心内容**:
1. **触发条件**: 用户要求整理教科书、处理论文涉及教科书理论、Foundation 缺乏演进脉络
2. **教科书-领域映射表**: Murray → Dynamics/Contact/Control, Deep RL → RL/Stochastic, Optimization → Optimization/Control
3. **5 阶段标准流程**: 内容分析 → Insights 提取 → 算法脉络重建 → Foundation 融合 → PapersRecap 关联
4. **各领域检查清单**: Dynamics (RNEA/ABA), Contact (抓取矩阵/力闭合), RL (DQN→SAC演进) 等
5. **常用 PDF 提取命令**: pdftotext 用法示例

---

## 🟡 进行中 (In Progress)

> 上次会话中断或需要持续关注的任务

### MergeBuffer 清理 ✅ 完成 (2026-02-02)

**本次处理 (4 个 PDF 文件)**:
- [x] **卷疯了！信号处理也玩"缝合术"，小波傅里叶合体思路赶紧码住！.pdf** → 🗑️ 删除
  - 内容提取: WFDiffuser 频域扩散方法 (DWT + STFT 融合)
  - **已融合至 ReinforcementLearning.md Section 6.2.1**: "频域视角：WFDiffuser 与小波-傅里叶融合"
  - 原 PDF 为公众号文章截图，融合后删除
- [x] **强化学习网络与机器人控制——数学基础.pdf** → 🗑️ 删除
  - 内容: 基础数学 (线性代数、概率论、最优化)
  - 判断: 与现有 Foundations 高度重复，无增量价值
- [x] **Kalman滤波的几何诠释.pdf** → 🗑️ 删除
  - 格式问题: 纯截图，无法提取文本
  - 判断: SignalProcessing.md Section 4 已覆盖 Kalman Filter
- [x] **机器人灵巧手操作（Dexterous Manipulation）"的求职路线.pdf** → �️ 删除
  - **内容萃取原则应用**: 从"求职路线"中萃取所有理论知识点
  - **识别的缺失概念**: VLA 模型、遥操作数据管线、接触状态机、滑移检测
  - **已补充至 ReinforcementLearning.md**:
    - Section 6.3: VLA (Vision-Language-Action) 模型架构
    - Section 6.4: 遥操作数据采集管线 (HDF5/LeRobot、时间同步、数据增广)
  - **已补充至 ControlTheory.md**:
    - Section 7.2: 接触状态机与控制模式切换 (Free/Contact/Sliding/Rolling/Sticking)
    - Section 7.3: 滑移检测与闭环防滑控制 (摩擦锥余量、分层防滑架构)

**MergeBuffer 当前状态**: 完全清空 ✅ (仅剩 _MergeIndex.md)

### 全局技能更新 ✅ (2026-02-02)

**新增原则**: "内容萃取原则 (Content Extraction Principle)"
- 位置: `.github/skills/knowledge-graph-management/SKILL.md` Section 1.3
- 核心理念: **任何进入 MergeBuffer 的内容，无论其表面形式如何（求职指南、技术博客、科普文章），都必须从中萃取理论知识点**
- 工作流: 识别概念 → 对照 Foundations → 补充缺失 → 删除原文件

### InformationTheory.md 强化 ✅ 完成 (2026-02-01)

**本次更新**:
- [x] **章节编号修复** — Section 6 下的子章节 (5.1→6.1, 5.2→6.2, 5.3→6.3)
- [x] **新增 Section 6.1.1**: Empowerment 理论根基
  - Klyubin, Polani & Nehaniv (2005) 原始论文引用
  - 信道容量视角的形式化定义
  - 与控制论可控性 Gramian 的数学等价性
  - 灵巧操作物理直觉表格
- [x] **论文反向链接**: Exploration vs Exploitation 论文添加 InformationTheory 链接

**当前引用统计**: InformationTheory 从 1 篇增至 2 篇引用

### 教科书温习 (Phase 1.5) ✅ 审计完成 (2025-02-03)

**Murray 教科书与 Foundation 对照**:
- [x] **ContactMechanics.md** — 已验证与 Murray Ch.5 (Grasp Map, Force-Closure) 一致
  - Section 2.4 抓取矩阵定义 ✅ 符合教科书 Definition 5.2
  - Section 2.5 力闭合条件 ✅ 符合教科书 Proposition 5.1, 5.2
  - Section 2.5.3 最小接触点数 ✅ 符合 Caratheodory/Steinitz 定理
- [x] **Dynamics.md** — 已验证空间向量代数、RNEA/ABA 覆盖完整
  - Section 4.1 Spatial Vector Algebra ✅
  - Section 3.2 RNEA O(N) 复杂度分析 ✅
  - Section 3.3 ABA 关节惯量概念 ✅

**知识图谱引用统计 (2025-02-03)**:
| Foundation | 被引用次数 (48篇论文) |
|------------|----------------------|
| ReinforcementLearning | 44 |
| ControlTheory | 23 |
| RepresentationLearning | 19 |
| ContactMechanics | 14 |
| Optimization | 14 |
| Dynamics | 12 |
| SignalProcessing | 9 |
| ComputationalGeometry | 5 |
| StochasticProcess | 4 |
| InformationTheory | 1 |

### MergeBuffer 论文处理 ✅ 已完成 (2025-02-02)

**MergeBuffer 已完全清空！** 所有 PDF 均已处理并移至 Papers/

**本轮会话处理 (12 篇)**:
- [x] AnyRotate (重力不变手内旋转)
- [x] RotateIt / General In-Hand Rotation (视触觉联合旋转)
- [x] Robot Synesthesia (视触觉联觉表征)
- [x] TRANSIC (可组合 Sim-to-Real)
- [x] DeepMimic (物理角色动画)
- [x] Part-Guided 3D RL (关节物体操作)
- [x] HATO (触觉遥操作)
- [x] CyberDemo (仿真增强真实演示)
- [x] Physics-Driven Data Generation (VR + 轨迹优化数据生成)
- [x] P2GI (近距离感知假肢抓取)
- [x] Finger Gaiting (仿人手指步态学习)
- [x] DemoSpeedup (熵引导示范加速)
- [x] GLIDE (规划引导扩散策略双臂操作)

### PapersRecap 批量生成 ✅ 已完成

**全部 34+12=46 篇论文笔记已完成**（截至 2025-02-02）：
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
- [x] Touch Dexterity, HORA, DLR Modular, SERL, HIL-SERL, MimicGen, RialTo
- [x] **New (2025-02-02)**: AnyRotate, RotateIt, Robot Synesthesia, TRANSIC
- [x] **New (2025-02-02)**: DeepMimic, Part-Guided 3D RL, HATO
- [x] **New (2025-02-02)**: CyberDemo, Physics-Driven Data Generation
- [x] **New (2025-02-02)**: P2GI, Finger Gaiting, DemoSpeedup, GLIDE

### 理论导师模式 - Foundation 完善

- [x] **RepresentationLearning.md 理论完善** ✅ 已更新 (2025-02-02)
  - ✅ **新增 Section 5.1: 视触觉联觉表征**
    - 触觉点云表征 (来自 RotateIt, AnyRotate)
    - 跨模态对比学习 (来自 Robot Synesthesia)
    - 多模态 Transformer 融合架构
  - ✅ 修复章节编号 (4.x → 5.x)

- [x] **SignalProcessing.md 理论完善** ✅ 已更新 (2025-02-02)
  - ✅ **新增 Section 6: 近距离传感与接触力预处理**
    - 近距离传感器信号处理 (来自 P2GI)
    - 实时点云映射与 PCA 特征提取
    - 接触力归一化方案 (来自 Finger Gaiting)
    - 异常值检测与滤波
  - ✅ 修复章节编号 (6→7, 7→8)

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

- [x] **ControlTheory.md** 已更新 (2026-02-02):
  - ✅ 添加"可达性分析与可行集"（源自 RCRL）
  - ✅ 添加"多速率采样与 RL"（源自 AP-AC）
  - ✅ **New (2026-02-01)**: 添加"数据驱动阻抗辨识"（源自 Prosthesis VI）
  - ✅ **New (2026-02-01)**: 添加"学习可变阻抗"（源自 VICES）
  - ✅ **New (2026-02-02)**: 添加"接触状态机与控制模式切换" Section 7.2 (源自求职路线萃取)
    - Free/Contact/Sliding/Rolling/Sticking 状态定义
    - 状态转移触发条件与控制律切换
    - Bumpless Transfer 平滑过渡
  - ✅ **New (2026-02-02)**: 添加"滑移检测与闭环防滑控制" Section 7.3 (源自求职路线萃取)
    - 触觉传感器滑移检测方法
    - 摩擦锥余量 $\gamma$ 定义与滑移概率估计
    - 分层防滑架构（高层策略/低层控制/紧急响应）
    - 材质自适应摩擦系数表

- [x] **ReinforcementLearning.md** 已更新 (2026-02-02):
  - ✅ 添加"时间一致探索"（源自 ARP）
  - ✅ 添加"课程学习 vs 触觉"（源自 Curriculum vs Haptic）
  - ✅ **New (2026-02-01)**: 添加"数据飞轮"（源自 DexTrack）
  - ✅ **New (2026-02-01)**: 添加"观测空间课程适应"（源自 CSR）
  - ✅ **New (2026-02-02)**: 添加"频域视角：WFDiffuser 与小波-傅里叶融合" Section 6.2.1
  - ✅ **New (2026-02-02)**: 添加"VLA 模型架构" Section 6.3 (源自求职路线萃取)
    - π₀、DexVLA、OpenVLA 代表模型
    - VLA 在灵巧操作中的分层定位
  - ✅ **New (2026-02-02)**: 添加"遥操作数据管线" Section 6.4 (源自求职路线萃取)
    - 设备类型对比、运动映射、时间同步
    - HDF5/LeRobot 格式、数据质量控制与增广

- [x] **Dynamics.md** 已更新 (2026-02-01):
  - ✅ 添加"关节级神经动力学分解"（源自 DexNDM）

- [x] **Optimization.md** 已更新 (2026-02-02):
  - ✅ 添加"同伦优化在灵巧操作中的应用"（源自 DexTrack）
  - ✅ 添加"阻抗参数的凸辨识"（源自 Prosthesis VI）

---

## 🟢 计划中 (Planned)

> 已识别但尚未开始的任务

### Foundation 反向链接增强 (部分完成 2026-02-01)
- [ ] 在 Foundation "源自" 注释中添加 wikilink 到 PapersRecap
- [x] InformationTheory.md: Empowerment 深度扩展 ✅ 已完成

### Foundation 交叉链接强化
- [ ] 检查所有 Foundation 文件之间的双向链接完整性
- [ ] 在 taxonomy.md 中更新知识结构图

### PapersRecap 关联审计 (完成 2026-02-02)
- [x] Exploration vs Exploitation 论文添加 InformationTheory 链接 ✅
- [x] Weight-sparse transformers 添加 RepresentationLearning, Optimization 链接 ✅ (2026-02-01)
- [x] GLIDE 添加 EmbodiedAI, ContactMechanics, ComputationalGeometry 链接 ✅ (2026-02-01)
- [x] **全部 48 篇论文笔记添加 `related:` Foundation 链接** ✅ (2026-02-02)

**状态**: ✅ 全部完成

### Foundation 反向链接增强
- [x] EmbodiedAI.md 添加相关论文索引 ✅ (2026-02-01)
- [x] ControlTheory.md 添加相关论文索引 ✅ (2026-02-01)
- [x] ContactMechanics.md 添加相关论文索引 ✅ (2026-02-01)
- [x] Dynamics.md 添加相关论文索引 ✅ (2026-02-01)
- [x] Optimization.md 添加相关论文索引 ✅ (2026-02-01)
- [x] RepresentationLearning.md 添加相关论文索引 ✅ (2026-02-01)
- [x] ReinforcementLearning.md 添加相关论文索引 ✅ (2026-02-02)
- [x] SignalProcessing.md 添加相关论文索引 ✅ (2026-02-02)
- [x] StochasticProcess.md 添加相关论文索引 ✅ (2026-02-02)
- [x] InformationTheory.md 添加相关论文索引 ✅ (2026-02-02)
- [x] ComputationalGeometry.md 添加相关论文索引 ✅ (2026-02-02)

**状态**: ✅ 全部完成 — 11/11 Foundation 文件已添加论文反向链接

### MergeBuffer 定期清理
- [ ] 检查 MergeBuffer/ 是否有新内容需要处理

---

## ✅ 已完成 (Completed)

> 最近完成的任务（保留最近10条）

- [x] **RepresentationLearning.md 泛化理论补充** — 2026-02-02
  - 添加 Section 6.3 "泛化理论基础"
  - 包含 Rademacher 复杂度、泛化界、域自适应理论
  - 教科书参考：Theory of Deep Learning
  - 建立 Sim-to-Real 与泛化理论的数学联系

- [x] **PapersRecap 全部添加 Foundation 链接** — 2026-02-02
  - 为 17 篇缺少 `related:` 字段的论文笔记添加 Foundation 链接
  - 统一格式：`related:` 替代 `foundations:`
  - 每篇笔记添加 `> [!note] Foundation 关联` 说明块
  - **总计**: 48/48 PapersRecap 全部完成 Foundation 双向链接

- [x] **全部 Foundation 论文反向链接完成** — 2026-02-02
  - ReinforcementLearning.md: SAC/课程学习/Sim-to-Real/模仿学习/奖励探索/控制频率 (17篇)
  - SignalProcessing.md: 触觉信号/时序频率/多模态融合 (9篇)
  - StochasticProcess.md: 扩散策略/MPPI采样/安全不确定性 (9篇)
  - InformationTheory.md: 熵探索/互信息/主动感知 (7篇)
  - ComputationalGeometry.md: SDF/点云3D/接触几何 (7篇)
  - **总计**: 11/11 Foundation 文件全部完成论文反向链接

- [x] **SKILL.md 错误模式记录** — 2026-02-01
  - 在"主动维护宣言"后添加"常见错误模式与修正"部分
  - 记录"被动等待用户选择"错误及修正原则

- [x] **Foundation 反向链接批量添加** — 2026-02-01
  - ControlTheory.md: 阻抗控制/Safe RL/控制频率/轨迹跟踪 (12篇)
  - ContactMechanics.md: 手内操作/接触学习/触觉感知 (11篇)
  - Dynamics.md: 神经动力学/轨迹优化/物理动画/Sim-to-Real (10篇)
  - Optimization.md: 轨迹MPC/阻抗优化/奖励课程/稀疏优化 (9篇)
  - RepresentationLearning.md: 视触觉/Diffusion/潜在空间/可解释 (11篇)

- [x] **SAC 数学理论推导** — 2026-02-01
  - 添加软贝尔曼方程与收敛定理
  - 添加 SAC 三组件损失函数
  - 添加 SAC 演进脉络表 (SQL→SAC v1→SAC v2)

- [x] **EmbodiedAI.md 反向链接** — 2026-02-01
  - 添加相关论文索引（Diffusion Policy, Sim-to-Real, 触觉多模态）

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

- [x] **Prompts 创建** — 2026-01-31
  - theoretical-mentor-mode.prompt.md
  - merge-buffer-process.prompt.md
  - knowledge-health-check.prompt.md
  - paper-reading.prompt.md
  - continue-session.prompt.md

---

## 📋 会话状态快照

### 最近会话: 2026-02-01 (SAC 理论推导 + 链接增强)

**主要工作**: 
1. 📚 **SAC 数学理论推导** — 完成 Deep RL 教科书遗留的 "Add SAC" 占位符
2. 🔗 **PapersRecap 链接增强** — 为 Weight-sparse transformers 和 GLIDE 添加 Foundation 链接
3. 📎 **Foundation 反向链接** — EmbodiedAI.md 添加相关论文索引

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| ReinforcementLearning.md | +SAC 数学理论推导 (软贝尔曼方程, 收敛定理, 三组件损失, 演进脉络) |
| Weight-sparse transformers.md | +frontmatter, +Foundation 链接 (RepresentationLearning, Optimization) |
| GLIDE.md | +Foundation 链接 (EmbodiedAI, ContactMechanics, ComputationalGeometry) |
| EmbodiedAI.md | +相关论文索引 (Diffusion Policy, Sim-to-Real, 触觉多模态) |
| TASK_TRACKER.md | 更新任务进度 |

**新增理论内容** (ReinforcementLearning.md Section 2.4):
- **软值函数定义**: $V^\pi_{soft}$, $Q^\pi_{soft}$
- **软贝尔曼方程**: 递归关系与 log-sum-exp 形式
- **软策略迭代收敛定理**: 单调递增性与唯一解
- **SAC 三组件损失函数**: $L_Q$, $L_\pi$, $L_\alpha$
- **自动温度调整物理意义**: 自适应刚柔调节
- **SAC 演进脉络**: SQL → SAC v1 → SAC v2

**反思与改进**:
> 本次会话初始时错误地等待用户指令，违反了"主动维护宣言"。
> 正确行为应该是：阅读 TASK_TRACKER → 识别遗留任务 → 直接开始执行。

**会话结束状态**: ✅ 完成

**下次会话建议**: 
1. 继续 Foundation 反向链接增强（其他 Foundation 添加论文索引）
2. Optimization 教科书整合（收敛速率理论）
3. taxonomy.md 知识结构图更新

---

### 历史会话: 2026-02-01 (InformationTheory 强化)

**主要工作**: 
1. 🔧 **InformationTheory.md 章节修复** — Section 6 子章节编号修复 (5.x → 6.x)
2. 📚 **Empowerment 理论扩展** — 新增 Section 6.1.1 理论根基
3. 🔗 **论文链接增强** — Exploration vs Exploitation 论文添加 InformationTheory 链接

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| InformationTheory.md | 章节编号修复 + 新增 Section 6.1.1 Empowerment 理论根基 |
| Exploration vs Exploitation.md | 添加 InformationTheory 链接 |
| TASK_TRACKER.md | 更新任务进度 |

**新增内容详情**:
- **Section 6.1.1**: Empowerment 理论根基
  - Klyubin, Polani & Nehaniv (2005) 原始论文引用
  - 信道容量形式化定义
  - 与控制论可控性 Gramian 的数学等价性: $\mathcal{E}(s) \propto \log \det(BB^T)$
  - 灵巧操作物理直觉表格

**会话结束状态**: ✅ 完成（无紧急任务）

**下次会话建议**: 
1. 继续 PapersRecap 关联审计（识别更多缺失 InformationTheory 链接的论文）
2. taxonomy.md 知识结构图更新
3. Foundation 中"源自"注释添加 wikilink

---

### 历史会话: 2025-02-03 (教科书温习审计)

**主要工作**: 
1. 📖 **Murray 教科书对照** — 验证 ContactMechanics.md 与 Dynamics.md 理论严格性
2. 📊 **引用统计审计** — 统计每个 Foundation 被论文引用次数
3. 🔍 **反向链接检查** — 发现 Foundation 缺少到 PapersRecap 的明确 wikilink

**审计发现**:
- ContactMechanics.md 与 Murray Ch.5 **完全一致**：
  - 抓取矩阵 $G$ 定义符合 Definition 5.2
  - 力闭合条件符合 Proposition 5.1-5.2
  - 最小接触点数定理 (Caratheodory/Steinitz) 已覆盖
- Dynamics.md 空间向量代数、递归算法 **已完整**
- Foundation 引用不均：InformationTheory 仅被 1 篇论文引用
- Foundation 缺少 PapersRecap 反向 wikilink（仅有文字注释）

**会话结束状态**: ✅ 完成（无紧急任务）

**下次会话建议**: 
1. InformationTheory.md 扩展（当前引用最低）
2. 为 Foundation 中的"源自"注释添加 PapersRecap wikilink
3. taxonomy.md 知识结构图更新

---

### 历史会话: 2025-02-02 (MergeBuffer 完全清空 🎉)

**主要工作**: 
1. 📊 **MergeBuffer 批量处理** — 12 篇新论文笔记完成
2. 📁 **文件迁移** — 所有 PDF 已从 MergeBuffer 移至 Papers/
3. ✅ **MergeBuffer 清空** — 仅剩 _MergeIndex.md

**编辑的文件**:
| 文件 | 修改内容 |
|-----|---------|
| 12 个新 PapersRecap | AnyRotate, RotateIt, Robot Synesthesia, TRANSIC, DeepMimic, Part-Guided 3D RL, HATO, CyberDemo, Physics-Driven Data Generation, P2GI, Finger Gaiting, DemoSpeedup, GLIDE |
| RepresentationLearning.md | +Section 5.1 视触觉联觉表征（触觉点云、跨模态对比学习） |
| SignalProcessing.md | +Section 6 近距离传感与接触力预处理 |
| TASK_TRACKER.md | 更新任务进度 |

**新增论文主题分类**:
- **手内操作**: AnyRotate (重力无关旋转), RotateIt (视触觉), Finger Gaiting (手指步态)
- **视触觉融合**: Robot Synesthesia, HATO
- **Sim-to-Real**: TRANSIC (可组合迁移), CyberDemo (仿真增强)
- **数据生成**: Physics-Driven VR, MimicGen, DemoSpeedup
- **双臂操作**: GLIDE (规划引导扩散)
- **假肢/人机**: P2GI (近距离感知)
- **物理角色**: DeepMimic

**会话结束状态**: ✅ 完成（MergeBuffer 已完全清空）

**下次会话建议**: 
1. 教科书温习: 对照 Books/ 中的教科书验证新增内容的理论严格性
2. 知识图谱交叉链接审计: 检查新论文笔记与 Foundation 的双向链接
3. ContactMechanics.md: 考虑添加接触隐式规划内容 (来自 GLIDE)

---

### 历史会话: 2026-02-01 晚 (MergeBuffer 批量处理)

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

### 历史会话: 2026-02-01 (教科书整合 Prompt 创建)

**主要工作**: 
1. ✅ **创建 textbook-integration.prompt.md** — 标准化从教科书提取知识的流程
2. 📊 **知识库健康检查** — 确认 MergeBuffer 已清空，46 篇论文 PDF + 48 篇 PapersRecap
3. 📚 **教科书内容分析** — 审阅 Deep RL, Murray, Optimization 三本核心教科书

**创建的文件**:
| 文件 | 内容 |
|-----|---------|
| [textbook-integration.prompt.md](.github/prompts/textbook-integration.prompt.md) | 教科书知识整合标准流程 (约 400 行) |

**textbook-integration.prompt.md 核心内容**:
1. **触发条件**: 用户要求整理教科书、处理论文涉及教科书理论、Foundation 缺乏演进脉络
2. **教科书-领域映射表**:
   - Murray → Dynamics, ContactMechanics, ControlTheory
   - Deep RL → ReinforcementLearning, StochasticProcess
   - Optimization → Optimization, ControlTheory
   - Theory of DL → RepresentationLearning
   - Data-based Control → ControlTheory, SignalProcessing
3. **5 阶段标准流程**: 
   - Phase 1: 教科书内容分析 (PDF 提取、目录分析、依赖图)
   - Phase 2: Insights 提取 (物理直觉、形式化定义、定理/引理)
   - Phase 3: 算法脉络重建 (奠基期→发展期→当前前沿)
   - Phase 4: Foundation 融合 (标准格式、交叉链接)
   - Phase 5: PapersRecap 关联 (双向链接)
4. **各领域检查清单**: Dynamics (RNEA/ABA), Contact (抓取矩阵/力闭合), RL (DQN→SAC) 等
5. **常用 PDF 提取命令**: pdftotext 用法示例

**知识库状态审计**:
- Papers/: 46 篇 PDF
- PapersRecap/: 48 篇 MD 笔记
- MergeBuffer/: 已清空 (仅 _MergeIndex.md)
- Foundations/: 11 个领域文件均完整
- 所有 Foundation 均有教科书级理论支撑

**会话结束状态**: ✅ 正常完成

**下次会话建议**: 
1. 使用新创建的 textbook-integration.prompt.md 系统性温习 Deep RL 教科书
2. 从 Deep RL 教科书提取 SAC 熵正则化的严格理论推导
3. 补充 InformationTheory.md 的 Empowerment 深度理论

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

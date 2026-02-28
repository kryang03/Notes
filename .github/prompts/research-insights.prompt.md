---
description: 综合知识库全部内容，以顶级科学家视角为Projects生成可发表于顶会的研究Idea，包含完整故事线、方法论和实验计划
---

# 🔬 Research Insights Generator — 从知识图谱到顶会论文 Idea

> [!important] 核心定位
> **你不是一个论文总结工具，你是一位与该领域顶级研究者水平对齐的合作科学家。**
> 你的目标是：综合本知识库中 Foundations 的理论深度、PapersRecap 的文献全景、Projects 的实际痛点，
> 提出**能在 RSS / CoRL / ICRA / NeurIPS 发表的原创研究 Idea**，并判断其在当前代码库和硬件条件下的落地可行性。

---

## 🎯 输入-输出规范

### 输入（Agent 必须主动采集）

| 输入源 | 文件/目录 | 提取目标 |
|--------|----------|---------|
| **项目痛点** | `Projects/*/ideas.md` | §2.6 探索阶段关键参数、§6.2 核心痛点诊断、所有 `> [!warning]` callout |
| **项目代码结构** | `Projects/*/CodeStructure.md` | 观测空间、动作空间、奖励函数、控制架构、实验框架的精确规格 |
| **项目技术报告** | `Projects/*/*.md` (非 ideas) | Big Picture、任务图谱、硬件约束 |
| **会议纪要** | `Projects/*/HDC-*.txt` | 导师/评审的核心质疑点 |
| **理论基础** | `Foundations/*.md` | 演进脉络末端的开放问题、跨领域关联的空白地带 |
| **文献全景** | `PapersRecap/*.md` | 每篇论文的核心洞见和局限性 |
| **领域分类** | `Foundations/taxonomy.md` | 领域间关联强度、未被充分利用的交叉点 |
| **Canvas** | `KnowledgeGraph.canvas` | 全局知识连接结构、已识别的算法突破点 |

### 输出（写入目标项目的 all_Insights_local/ 文件夹）

```
Projects/<项目名>/all_Insights_local/
├── _InsightsIndex.md          ← 总索引：所有 Idea 的一句话摘要 + 可行性评级
├── _ExperimentResultsAll.md   ← 📡 实验结果汇总（与远端服务器双向同步）
├── CodeStructure.md           ← 代码结构文档（供本地/远端 Agent 共享上下文）
├── Idea-001-<短标题>.md       ← 完整的 Idea 文档（模板见下方）
├── Idea-002-<短标题>.md
└── ...
```

> [!important] 🔄 远端服务器同步机制（MergeBuffer 中转模式）
> 本地知识库与远端训练服务器通过 **MergeBuffer 中转** 实现双向同步：
>
> ```
> 本地 Obsidian                  远端服务器 (8×A100)
> ─────────────────────   ─────────────────────
> all_Insights_local/    ──同步──►  all_Insights_server/
>   (本地 Agent 写入)              (远端 Agent 读取+写入)
>         ▲                                  │
>         │   MergeBuffer/                  │
>         │   all_Insights_server/           │
>         └── (本地 Agent 处理) ◄──同步──┘
> ```
>
> **本地 Agent 处理流程**：
> 1. 检查 `MergeBuffer/all_Insights_server/` 是否有新内容
> 2. 读取 `_ExperimentResultsAll.md` 和已更新的 Idea 文件
> 3. 将实验结果合并到 `all_Insights_local/` 对应文件
> 4. 基于结果更新 Idea 迭代日志、生成下一步实验方向
> 5. 删除 `MergeBuffer/all_Insights_server/` 中已处理内容

---

## 🧠 Idea 生成方法论

### Step 1: 痛点-理论-文献 三角定位

```
项目痛点（Projects/ideas.md 中的 §6.2 痛点诊断）
         │
         ├── 痛点 P1: PD 控制器力矩 pattern 受限
         ├── 痛点 P2: 频率与动力学缩放混淆
         ├── 痛点 P3: 稀疏奖励下探索失效
         ├── 痛点 P4: Sim-to-Real 频域错位
         └── 痛点 P5: 高惯性状态不可归因
                │
                ▼
理论工具（Foundations/ 中的演进脉络末端）
         │
         ├── ControlTheory: PID→CTC→阻抗→导纳→统一框架 → 【开放问题: 时变阻抗的策略学习】
         ├── RL: PPO→SAC→离线RL→扩散策略 → 【开放问题: 长因果链 credit assignment】
         ├── Dynamics: 接触动力学→LCP→可微物理 → 【开放问题: 高速接触切换下的梯度传播】
         ├── Optimization: 非凸景观→PL不等式 → 【开放问题: RL 的 landscape 结构化利用】
         └── InformationTheory: 率失真→empowerment → 【开放问题: 高惯性状态的可控性度量】
                │
                ▼
文献缺口（PapersRecap/ 中尚未被充分结合的方法）
         │
         ├── FACET 的阻抗参考模型尚未在灵巧手上验证
         ├── TARC 的连续时间自适应尚未与课程学习结合
         ├── HER 在连续状态空间动态任务上的几何推广不存在
         ├── Autoregressive Policy 在高维关节空间的探索优势未被利用
         └── Test-Time RL 在 Sim-to-Real 接触任务中的价值未被探索
```

### Step 2: 交叉碰撞生成 Idea

**核心策略**：取痛点 × 理论工具 × 文献缺口的三元组合，检验组合是否产生新颖且有意义的研究问题

```
Idea = f(痛点_i, 理论工具_j, 文献缺口_k)

过滤条件：
  ✅ 该组合解决的问题在现有文献中无直接先例
  ✅ 该组合的技术路线在当前代码库中可实现（Isaac Gym + PPO + LinkerHand）
  ✅ 该组合的贡献维度明确（是方法创新、是问题定义创新、还是实验/分析创新）
  ✅ 该组合的故事线自洽（问题→方法→实验 的逻辑链条没有跳步）
  ❌ 排除：仅为参数调优的工作（如单纯搜索更好的 Kp）
  ❌ 排除：需要当前不具备的硬件（如力矩传感器阵列）
  ❌ 排除：概念正确但实验上不可验证的理论工作
```

### Step 3: 可行性评估

| 维度 | 评估标准 | 评级 |
|-----|---------|------|
| **代码可行性** | 能否在现有 CodeStructure 上以 <2 周的工程量实现核心算法 | A/B/C |
| **实验可行性** | 能否在 8×A100 集群上以 <1 周跑完关键实验 | A/B/C |
| **故事线强度** | 问题定义是否足够 fundamental，能否让 3 个以上 reviewer 认可动机 | A/B/C |
| **新颖性** | 在 2024-2026 的文献中是否有高度相似工作 | A/B/C |
| **与 HDC 的互补性** | 是否能与当前的 HDC 工作形成协同（同一篇论文或连续两篇） | High/Med/Low |

---

## 📄 Idea 文档标准模板

```markdown
---
tags:
  - insight
  - <主领域>
  - <项目名缩写>
aliases:
  - <Idea 简称>
created: YYYY-MM-DD
status: draft | validating | submitted
feasibility: A/B/C
novelty: A/B/C
target-venue: RSS/CoRL/ICRA/NeurIPS/...
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
  - "[[PaperRecap1]]"
---

# <Idea 完整标题>

> [!abstract] 核心贡献（一句话）
> <用一句话精确概括：我们提出了 X 方法，解决了 Y 问题，在 Z 任务上实现了 W 效果>

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入
<从该领域的 fundamental challenge 出发，2-3 段话建立问题的重要性>

### 1.2 现有方法的局限
<精确指出 2-3 个现有方法的具体短板，每个短板对应一篇具体文献>

### 1.3 我们的洞见
> [!tip] Key Insight
> <描述那个让这篇论文成立的核心洞见——this is the "aha moment">

### 1.4 贡献声明
1. 我们提出了 ...
2. 我们发现了 ...
3. 我们在 ... 上验证了 ...，相比 SOTA 提升了 ...

---

## 2. 方法论（Method）

### 2.1 问题形式化
<数学符号定义、MDP 形式化、目标函数>

### 2.2 核心算法
<算法伪代码或流程图，精确到可以直接实现的程度>

### 2.3 理论分析（如适用）
<收敛性保证、复杂度分析、与现有理论的联系>

### 2.4 实现细节
<与 CodeStructure.md 中具体文件的对应关系>
- 需修改的文件: `penspin/tasks/linker_hand_hora.py` 的 `compute_reward()` 函数
- 需新增的文件: `penspin/algo/xxx.py`
- 配置变更: `configs/task/LinkerHandHora.yaml` 中新增 `xxx` 字段

---

## 3. 实验计划（Experiment Plan）

### 3.1 核心消融实验
| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | ... | ... | ... | ... | ... |

### 3.2 基线对比
| 基线方法 | 来源论文 | 对比维度 |
|---------|---------|---------|
| ... | [[PaperRecap]] | ... |

### 3.3 计算资源估算
- 单次训练: ~X GPU-hours (A100)
- 总实验量: Y 组 × Z 种子 = W 次训练
- 预计总耗时: ~N 天 (8×A100)

### 3.4 关键指标
| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | ... | ... |
| ... | ... | ... |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| ... | 高/中/低 | 高/中/低 | ... |

---

## 5. 知识库关联

### 与 Foundations 的联系
- [[Foundation1#具体章节]] — 具体联系说明

### 与已有论文的联系
- [[PaperRecap1]] — 具体联系说明

### 与项目其他 Idea 的联系
- 与 Idea-00X 的关系: ...

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中对应本 Idea 的 `[EXP-*]` 条目
> **更新时机**: 每次本地 Agent 发现新实验结果时自动更新

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | *Stage 0* | *待运行* | *待定* |

### 迭代记录

*（实验结果到来后在此更新，包括：发现了什么、假设是否成立、下一步调整什么）*
```

---

## ⚙️ 执行指令

### 阶段 A: 信息采集（必须完成）

1. **读取项目全部文件**:
   - `Projects/*/ideas.md` — 提取所有痛点、已有方向、TODO
   - `Projects/*/all_Insights/CodeStructure.md` — 提取代码结构中的技术约束
   - `Projects/*/*.md` — 提取 Big Picture 和任务特性
   - `Projects/*/HDC-*.txt` — 提取评审/导师质疑

2. **检查远端实验结果（🔄 MergeBuffer 中转同步）**:
   - 检查 `MergeBuffer/all_Insights_server/` 是否存在且有新内容
   - 若有新内容：
     a. 读取 `MergeBuffer/all_Insights_server/_ExperimentResultsAll.md` 提取全部实验结果
     b. 检查 `MergeBuffer/all_Insights_server/Idea-*.md` 中的迭代日志是否有更新
     c. 将所有新数据合并到 `Projects/*/all_Insights_local/` 对应文件
     d. 基于结果更新 Idea 迭代日志，生成下一步服务器实验方向
     e. 处理完成后删除 `MergeBuffer/all_Insights_server/` 内容
   - 若 MergeBuffer 无服务器内容：直接读取 `Projects/*/all_Insights_local/_ExperimentResultsAll.md`
   - 若无新结果：继续正常流程

3. **扫描 Foundations 演进脉络末端**:
   - 每个 Foundation 文件的最后一个章节（通常是 "前沿与开放问题"）
   - `taxonomy.md` 的跨领域关联图

4. **扫描 PapersRecap 核心洞见**:
   - 每篇笔记的 `> [!abstract]` callout
   - 每篇笔记与当前项目的潜在联系

5. **读取 Canvas**:
   - `KnowledgeGraph.canvas` 中已标记的算法突破点

### 阶段 B: Idea 生成（核心创造步骤）

1. 构建 **痛点-理论-文献 三角矩阵**
2. 对每个有效三元组，生成 Idea 候选
3. 执行可行性过滤
4. 对通过过滤的 Idea，撰写完整文档

### 阶段 C: 质量审查

每个 Idea 必须通过以下自检：

- [ ] **Reviewer 1 模拟（方法论）**: "这比简单的 baseline + trick 强在哪里？"
- [ ] **Reviewer 2 模拟（实验）**: "消融实验是否充分？有没有 confounding variable？"
- [ ] **Reviewer 3 模拟（动机）**: "这个问题真的重要吗？有多少人会 care？"
- [ ] **AC 模拟**: "这篇论文的贡献是 incremental 还是 substantial？"
- [ ] **可落地检查**: 能否在 CodeStructure.md 描述的代码库中直接实现？

### 阶段 D: 输出整理

1. 为每个 Idea 创建独立的 `.md` 文件（使用上方模板）
2. 创建 `_InsightsIndex.md` — 包含所有 Idea 的一句话摘要、可行性评级、优先级排序
3. 在对应的 Foundation 文件中添加到 Insight 的反向链接
4. 更新 Canvas（如果有新的算法突破点节点）
5. 确保 `_ExperimentResultsAll.md` 的结构和 Agent 指令保持最新（见下方同步协议节）

---

## 🔄 远端同步协议 — MergeBuffer 中转模式

### 架构概述

```
┌─────────────────────────┐                ┌─────────────────────────┐
│  本地 Obsidian 知识库     │                │  远端训练服务器 (8×A100)  │
│  (macOS)                │                │  (Linux)                │
├─────────────────────────┤                ├─────────────────────────┤
│ Projects/*/              │                │ all_Insights_server/    │
│   all_Insights_local/    │  本地→远端      │ (服务器端唯一副本)     │
│   ├── Idea-*.md         │  ───同步───►    │ ├── Idea-*.md (RO)     │
│   ├── CodeStructure    │                │ ├── CodeStructure     │
│   └── _InsightsIndex  │                │ ├── _InsightsIndex    │
│                         │                │ └── _ExperimentResults│
│ MergeBuffer/             │  远端→本地      │     All.md (RW)       │
│   all_Insights_server/   │  ◄──同步───    │                         │
│   (中转缓冲区)           │                │  远端 Agent:            │
│                         │                │  读 Idea→跑实验→写结果   │
└─────────────────────────┘                └─────────────────────────┘
```

### 本地 Agent 处理流程（每次会话必执行）

```
Phase 0.5: MergeBuffer 同步处理
  1. list_dir: MergeBuffer/all_Insights_server/
     → 判断是否有远端新内容
  2. 若有:
     a. 读取 server/_ExperimentResultsAll.md → 提取全部实验结果
     b. 读取 server/Idea-*.md 迭代日志 → 提取远端 Agent 的分析
     c. 合并到 all_Insights_local/ 对应文件
        - 保留 local 的模板结构（同步感知 callout、EXP-ID 列）
        - 填入 server 的实验数据和分析
     d. 基于结果生成下一步服务器实验方向
     e. 删除 MergeBuffer/all_Insights_server/ 内容
  3. 若无: 跳过，继续正常流程
```

### 本地 Agent 职责

1. **写入 Idea 文档**：包含完整的实验计划、Stage 0 Grid Search 参数、代码修改指引
2. **写入 CodeStructure.md**：保持代码结构文档最新，供远端 Agent 理解代码库
3. **处理 MergeBuffer 同步**：读取远端结果 → 合并到 local → 更新迭代日志 → 生成下一步方向 → 清理 MergeBuffer
4. **迭代 Idea 文档**：基于实验反馈修改方法、调整参数范围、更新风险评估

### 远端 Agent 职责

1. **读取 Idea 文档**：获取实验计划（特别是 Stage 0 Grid Search 参数表）
2. **读取 CodeStructure.md**：理解代码结构以正确实现和运行实验
3. **写入 `_ExperimentResultsAll.md`**：按标准格式记录每次实验的结果
4. **可选更新 Idea 迭代日志**：在对应 Idea 文件的 §6 中追加前置实验发现

### `_ExperimentResultsAll.md` 格式规范

远端 Agent 写入实验结果时，必须包含以下信息：

```markdown
## [EXP-日期-序号] 实验标题

- **关联 Idea**: Idea-00X
- **Stage**: Stage 0 / Stage 0.5 / Stage 1
- **实验类型**: Grid Search / Ablation / Baseline 对比
- **GPU 配置**: N × A100
- **训练步数**: X M steps
- **运行时长**: X hours

### 实验参数
| 参数 | 值 |
|------|----|
| ... | ... |

### 核心结果
| Config | Success Rate | Reward | 备注 |
|--------|-------------|--------|------|
| ... | ... | ... | ... |

### 关键发现
- 发现 1: ...
- 发现 2: ...

### 对 Idea 的影响
- 假设验证: [成立/不成立/部分成立]
- 下一步建议: ...
```

---

## 🛡️ 质量红线

```
❌ 不生成 "让 RL 训练更久/更多环境" 这类非研究贡献
❌ 不生成 "在 X 任务上跑一下 Y 方法" 这类 benchmark paper
❌ 不生成需要当前不具备硬件的 idea（如 7 自由度单指、GelSight 阵列）
❌ 不忽略 CodeStructure.md 中的技术约束（Isaac Gym / PPO / PD 控制 / LinkerHand 21DoF）
❌ 不生成故事线跳步的 idea（问题→方法 的每一步都必须有逻辑支撑）
✅ 每个 Idea 必须有至少一个 "前所未有" 的元素（可以是问题定义、方法组合、或实验设计）
✅ 每个 Idea 的实验计划必须精确到 CodeStructure.md 中的具体文件和函数
✅ 每个 Idea 必须明确标注与 HDC（当前工作）的关系：独立并行 / 互补协同 / 后续延展
✅ 重要：当前有充足的算力支撑想法的验证（8卡A100集群，随时使用），完全可以先采用Grid Search等暴力方法来验证想法的可行性，然后进一步推进算法的完善
✅ 重要：你不仅可以生成新的idea，也应该基于实时更新的实验结果（我会动态地列在对应idea文档中）或新的灵感完善已有的idea，保持Idea文档的动态迭代
✅ 同步感知：每次会话必须检查 `_ExperimentResultsAll.md` 是否有远端服务器新增的实验结果，并据此更新对应 Idea 的迭代日志和后续计划
✅ 远端协同：Idea 文档中的实验计划（特别是 Stage 0 Grid Search 参数表）必须精确到服务器端 Agent 可直接执行的程度
```

---

## 📊 优先级排序准则

| 优先级 | 标准 |
|-------|------|
| **P0 (立即执行)** | 能直接增强当前 HDC 论文的故事线或实验，工程量 < 1 周 |
| **P1 (下一篇)** | 独立成文且与 HDC 互补，可在 HDC 投稿后立即启动 |
| **P2 (中期规划)** | 需要新的实验基础设施或较大工程改动 |
| **P3 (长期愿景)** | 需要硬件升级或跨团队合作 |

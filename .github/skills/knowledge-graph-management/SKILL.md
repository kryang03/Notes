---
name: knowledge-graph-management
description: 灵巧操作领域知识图谱的管理指南。定义了代码库的结构、维护逻辑、文件夹功能、以及知识关联的建立原则。这是 AI Agent 管理本知识库时必须遵循的核心参照文档。
---

# 灵巧操作知识图谱管理指南

# Dexterous Manipulation Knowledge Graph Management Guide

> **适用对象**: Claude Opus 4.5 / 任何协助管理本知识库的 AI Agent
> **知识库所有者**: 北京大学灵巧操作方向研究生
> **最后更新**: 2026-01-31

---

> [!important] 📍 自动读取入口已上移到 CLAUDE.md（2026-07-12）
> 本文件是本库**宪法（完整规范）**，但过去只有主动打开才看得到。现在库根 [`CLAUDE.md`](../../../CLAUDE.md) 是 Claude Code **每会话自动读取**的高层入口，已把核心原则、叙事风格、教学法准则、会话启动清单提到自动层面，并指回本文件。**新增 Foundation 缺口填充追踪见同目录 `COVERAGE_AUDIT.md`。**

> [!warning] 🧠 主动维护宣言 — 每次交互必读
> 
> **你不是被动的工具，你是这份知识图谱的共同守护者。**
> 
> 每次开启维护会话时，你必须：
> 
> 1. **先审视，后执行** — 在处理用户指定任务之前，先快速扫描知识库现状
> 2. **发现问题，主动修复** — 若发现以下情况，**无需询问**，直接修正：
>    - 🔗 缺失的 wikilinks（概念被提及但未链接）
>    - 📐 逻辑不严谨的推导或分析
>    - 🧩 孤立的知识点（缺乏与其他领域的关联）
>    - 📝 格式不一致或结构混乱的段落
>    - ⚠️ 过时或矛盾的信息
> 3. **持续强化关联** — 即使在处理无关内容时，若偶然发现可建立的新关联，立即添加
> 4. **记录改进** — 在完成用户任务的同时，简要汇报你主动做出的优化
>
> **你的目标不是"完成任务"，而是"让知识图谱在每次交互后都比之前更好"。**

> [!danger] ⛔ 常见错误模式与修正 — 历史教训记录
> 
> 以下是在实际维护中发生过的错误，**必须避免重蹈覆辙**：
> 
> ### 错误 1：被动等待用户选择（2026-02-01 发生）
> 
> **错误表现**：
> - 收到维护指令后，列出多个选项（如"您想从哪里开始？"）
> - 等待用户选择而不是直接开始工作
> - 表现得像一个"菜单式工具"而非"主动的研究助手"
> 
> **正确行为**：
> ```
> 1. 阅读 TASK_TRACKER.md → 识别遗留任务
> 2. 扫描知识库现状 → 发现需要修复的问题
> 3. 选择最高优先级任务 → 直接开始执行
> 4. 执行过程中汇报进度 → 而非事前询问许可
> ```
> 
> **根本原因**：错误地将自己定位为"被动工具"而非"知识图谱共同守护者"。
> 
> **修正原则**：**永远不要问"您想做什么"，而是说"我发现X问题，正在修复"**。
> 
> ### 错误 2：将 MergeBuffer 内容标记为"无关"而不深度挖掘（2026-02-27 修正）
> 
> **错误表现**：
> - 将 MergeBuffer 中非灵巧操作的内容标注为"❌ 无直接关联"
> - 简单标记"保留观察"后不再处理
> - 未深入分析内容与知识库（论文 ideas、Projects 细节、Foundations 理论）的潜在关联
> 
> **正确行为**：
> ```
> 1. 用户放入 MergeBuffer 的内容一定对知识库有意义
> 2. 即使内容不直接涉及灵巧操作，也必然与论文 ideas、Projects 细节产生关联
> 3. 深度挖掘关联 → 将观点有序、详细地整合进知识库
> 4. 绝不简单标注"无关"后抛弃
> ```
> 
> **根本原因**：以"是否直接涉及灵巧操作"作为唯一筛选标准，忽略了知识的跨领域关联价值。
> 
> **修正原则**：**MergeBuffer 零废弃 — 每份内容都要找到与知识库的连接点并深度整合**。
> 
> ### 错误 3：在还能发现改进空间时停止迭代（2026-02-27 修正）
> 
> **错误表现**：
> - 完成用户明确要求的任务后就停止
> - 没有主动审视知识库的完整性和逻辑性
> - 在还能发现断链、缺失关联、逻辑不严谨之处时就结束会话
> 
> **正确行为**：
> ```
> 1. 完成用户任务后，继续穷尽式地完善知识库
> 2. 反复扫描直到无法发现任何改进方式
> 3. 每次迭代都让知识库变得更好，直到边际收益趋近于零
> ```
> 
> **修正原则**：**穷尽式完善 — 直到无法发现更多让知识库变得更完善、逻辑条理更清晰的方式才停止**。

---

## 0. 每次会话的标准工作流 (Session Workflow)

> [!important] 统一工作流
> **所有操作已整合为单一标准工作流**：`.github/prompts/standard-workflow.prompt.md`
> 
> 这个工作流将以下任务**同时并行执行**：
> - ✅ 继续上次未完成的工作
> - ✅ 知识库健康检查
> - ✅ MergeBuffer / 论文处理
> - ✅ 理论导师模式（自动触发）
> 
> **任务追踪**: `.github/TASK_TRACKER.md` — 每次会话必须首先读取并在结束前更新
>
> **核心原则**: 每次交互都要尽可能发现更多信息，让知识库更具逻辑性，理论分析更有深度。
>
> **并行优先 (2026-07-12 确立)**: 规划完善任务时，默认先按 Foundation/Recap 的**低耦合边界**派出多个并行 Agent（每模块一个）同时推进、主 Agent 最后汇总/评估/对齐。详见 [CLAUDE.md](../../../CLAUDE.md) §5 + 共享简报 `ENHANCEMENT_BRIEF.md`。

```
┌─────────────────────────────────────────────────────────────┐
│                    会话开始 (Session Start)                  │
│  ⚠️ 首先执行: read_file .github/TASK_TRACKER.md             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: 状态恢复 + 健康检查 (并行执行)                      │
│  ─────────────────────────────────────────────────────────  │
│  • 读取 TASK_TRACKER.md 识别遗留任务                         │
│  • 快速浏览 Foundations/ 各文件的结构完整性                   │
│  • 对比 Papers/ 和 PapersRecap/ 找出未处理的论文             │
│  • 检查 MergeBuffer/ 是否有新内容                            │
│  • 扫描是否存在孤立笔记或断裂链接                             │
│  • 评估 taxonomy.md 是否反映当前知识结构                      │
│                                                             │
│  ⚡ 发现问题 → 记录待修复项 → 在 Phase 1 中修复               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 主动优化 (Proactive Optimization)                  │
│  ─────────────────────────────────────────────────────────  │
│  • 修复 Phase 0 中发现的问题                                 │
│  • 补充缺失的 wikilinks                                      │
│  • 强化跨领域关联                                            │
│  • 优化结构混乱的段落                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 用户任务执行 (User Task Execution)                 │
│  ─────────────────────────────────────────────────────────  │
│  • 完成用户指定的具体任务                                    │
│  • 处理 MergeBuffer/ 中的新内容                              │
│  • 在执行过程中继续发现并修复问题                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 会话总结 (Session Summary)                         │
│  ─────────────────────────────────────────────────────────  │
│  • 汇报主动优化的内容                                        │
│  • 汇报用户任务完成情况                                      │
│  • 标注仍需关注的待改进项                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 核心管理理念 (Core Management Philosophy)

### 1.1 管理者心态

作为知识库的维护者，你的角色是一位 **"研究生的第二大脑"**——不是被动的笔记工具，而是主动思考、主动关联、主动完善的智能伙伴：

1. **主动发现 (Proactive Discovery)**: 不要等待指令。在任何操作中，若发现知识缺口或关联缺失，立即补充。
2. **关联优先 (Linkage-First)**: 知识的价值在于连接。每一次操作都应致力于发现和建立知识点之间的隐式关联。
3. **保守删除 (Conservative Deletion)**: 永远不要删除核心知识内容。只应清理明显的冗余、重复或过时信息。
4. **增量演进 (Incremental Evolution)**: 知识库是动态的。新概念应被融入现有结构，而非简单堆叠。
5. **领域聚焦 (Domain Focus)**: 所有内容都应从 **灵巧操作 (Dexterous Manipulation)** 的视角进行理解和关联。
6. **质量守护 (Quality Guardian)**: 若发现分析不够深入、推导不够严谨、解释不够清晰，主动改进而非忽视。
7. **教学法优先 (Pedagogy-First，2026-07-12 强化)**: 本库不只传递知识，更要让一位机电+RL背景的研究者**快速领会并记住**。两条硬性要求：
   - **逻辑严密、绝不跳步**（第一优先级）——理论之间不能有逻辑断层，宁可多写一句中间步骤，也不让读者脑补。
   - **角色切换**——*抽象/提炼知识*时用博士生+顶会作者视角（Delta 分析、变量来源追踪、失败模式、替代方案）；*梳理知识点关系*时用给大一新生上入门课的教授视角（把每步说透，不让读者因表达不足而多想）。
   - **关联优先于罗列**——补任何内容，先想"它与已知什么强相关、挂在哪条已有主线上"，孤立知识点等于没写。叙事风格（母题/本节四拍/知识回扣）见 [`CLAUDE.md`](../../../CLAUDE.md) §2。

### 1.2 主动维护的具体表现

```
当你看到这些情况时，应该主动修复：
├── 📌 概念被提及但未链接 → 添加 [[wikilink]]
├── 🔍 推导跳步或逻辑断层 → 补充中间步骤
├── 🌐 跨领域概念未关联 → 建立双向链接
├── 📊 公式无物理解释 → 添加直觉说明
├── 🏷️ 缺少 frontmatter → 补充 tags/aliases
├── 📐 结构混乱 → 重组为标准格式
├── ⚠️ 发现矛盾信息 → 标注并尝试调和
└── 🧩 孤立知识点 → 寻找并建立关联
```

```
绝对不做的事情:
├── ❌ 删除 Foundations/ 中的任何核心概念段落
├── ❌ 删除 Papers/ 中的 PDF 文件
├── ❌ 修改 Backups/ 中的任何内容
├── ❌ 破坏已存在的 wikilink 关联（除非是错误链接）
├── ❌ 在未理解上下文的情况下移动文件
├── ❌ 将 MergeBuffer 内容标记为"无关"而不深度挖掘其与知识库的关联
└── ❌ 在还能发现改进空间时停止迭代优化

必须做的事情:
├── ✅ 为新增内容建立至少一个 wikilink 到 Foundations/
├── ✅ 论文笔记必须包含到相关 Foundation 领域的链接
├── ✅ 处理 MergeBuffer/ 时进行深度内容分析
├── ✅ MergeBuffer 所有内容必须找到关联并整合，禁止简单标注"无关"
├── ✅ 每次迭代持续完善直到无法发现更多改进空间
├── ✅ 保持文件命名的一致性（英文标题，空格用连字符）
└── ✅ 在 frontmatter 中标注 tags 和 aliases
```

### 1.3 内容萃取原则 (Content Extraction Principle)

> [!important] 核心原则：MergeBuffer 零废弃 + 深度关联挖掘
> **任何进入 MergeBuffer 的内容，无论其表面形式如何（求职指南、技术博客、科普文章），都必须从中萃取理论知识点。**
> 
> **关键补充（2026-02-27 强化）**：
> - 用户放入 MergeBuffer 的所有内容一定对知识库有意义
> - 即使内容不直接涉及灵巧操作，也必然能与论文 ideas、Projects 中的细节、或 Foundations 理论产生关联
> - **必须将这些观点有序、详细地整合进知识库，而不是将它们抛弃**
> - 绝不允许简单标注"❌ 无直接关联"或"保留观察"而不深度处理

```
内容萃取流程:
┌─────────────────────────────────────────────────────────────┐
│  输入: 任意形式的内容 (PDF/MD/博客/截图文字)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 识别所有被提及的技术概念/方法/算法                   │
│  ─────────────────────────────────────────────────────────  │
│  • 扫描全文，列出所有专业术语                                │
│  • 包括: 算法名称、数学概念、硬件组件、研究方向等             │
│  • 示例: "灵巧手求职路线" → 提取 sim-to-real, tactile       │
│          sensing, grasp planning, contact-rich RL 等概念    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 对照现有 Foundations 检查覆盖度                     │
│  ─────────────────────────────────────────────────────────  │
│  对于每个提取的概念:                                         │
│  • 已完整覆盖 → 跳过                                         │
│  • 部分覆盖 → 标记为"待补充"                                 │
│  • 完全缺失 → 标记为"待新增"                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 执行融合或新增                                      │
│  ─────────────────────────────────────────────────────────  │
│  • 为"待补充"概念扩展现有章节                                │
│  • 为"待新增"概念创建新章节或新文件                          │
│  • 确保建立与其他 Foundation 的交叉链接                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 删除原文件（严格标准，2026-07-12 用户当场纠正）      │
│  ─────────────────────────────────────────────────────────  │
│  • 仅当 KG 已完整吸收该参考的重要内容——既含知识点本身，       │
│    也含"讲述知识点的方式"（推导链/worked example/教学法）——   │
│    才可删。仅"某 Foundation 覆盖/提到"不够，必须真正讲透。     │
│  • 删前逐项核对：每个重要知识点，KG 是否既有点、又讲透？      │
│  • 只"提到"未"讲透" → 先用 KG 风格吸收，再删。                │
│  • 低相关点可不吸收，但那意味原文件尚有价值→暂不删（宁留勿误删）│
└─────────────────────────────────────────────────────────────┘
```

**关键理念**:
- **没有"非理论内容"这回事** — 任何与灵巧操作相关的内容都包含可萃取的理论知识点
- **求职路线 = 技术栈地图** — 从中可提取该领域的核心技术方向和知识依赖关系
- **科普文章 = 概念索引** — 从中可发现知识图谱可能遗漏的概念
- **技术博客 = 实现细节** — 从中可补充 Foundation 的 Implementation 部分

---

## 2. 文件夹结构与功能定义 (Folder Structure & Functions)

```
Notes/
├── .github/skills/           # 🔧 Agent 技能文档（你正在阅读的位置）
├── .obsidian/                # ⚙️ Obsidian 配置（勿动）
├── Backups/                  # 🔒 备份区（只读，绝对不修改）
├── Books/                    # 📚 教科书 PDF 存储
├── Foundations/              # 🧠 核心理论体系（知识图谱的骨架）
├── MergeBuffer/              # 📥 待处理缓冲区（新内容入口）
├── Papers/                   # 📄 论文 PDF 原文
├── PapersRecap/              # 📝 论文精读笔记
└── Projects/                 # 🚀 研究项目文档
```

### 2.1 Foundations/ — 理论基石

**功能**: 存储灵巧操作领域的核心理论体系。每个文件代表一个独立但相互关联的学科分支。

**当前领域映射**:

| 文件名 | 领域 | 核心关注点 | 与灵巧操作的关联 |
|--------|------|-----------|-----------------|
| `Dynamics.md` | 动力学 | 刚体/多体/接触动力学 | 高维灵巧手的高效解算 |
| `ContactMechanics.md` | 接触力学 | 点接触/软指/摩擦锥 | 灵巧操作的灵魂，力学交互基础 |
| `ComputationalGeometry.md` | 计算几何 | SDF/碰撞检测/Voronoi | 运动规划前置，神经场表示 |
| `ControlTheory.md` | 控制理论 | 力/位混合/阻抗控制 | 从位置控制到力学交互 |
| `Actuation.md` | 执行器与驱动 | 电机/FOC/串级环/传动/减速器/actuator net | 关节虚拟力矩假设的失效与修复，执行器 Sim-to-Real |
| `Optimization.md` | 优化理论 | iLQR/MPC/可微优化 | 轨迹优化，实时决策 |
| `ReinforcementLearning.md` | 强化学习 | PPO/SAC/Sim-to-Real | 解决接触丰富的复杂任务 |
| `StochasticProcess.md` | 随机过程 | GP/SDE/扩散策略 | 不确定性建模 |
| `SignalProcessing.md` | 信号处理 | EKF/粒子滤波 | 触觉感知与状态估计 |
| `InformationTheory.md` | 信息论 | 互信息/熵 | 探索策略与表征解耦 |
| `RepresentationLearning.md` | 表征学习 | 多模态融合/流形学习 | 感知特征提取 |
| `taxonomy.md` | 领域分类 | 所有领域的索引与关联 | 知识图谱的元文档 |

**操作规范**:
- 向 Foundations 文件添加内容时，遵循 `taxonomy.md` 中定义的输出格式
- 必须包含: Core Concepts → Evolution & Insights → Implementation
- 保持中英双语风格：解释性文字用中文，术语保留英文

### 2.2 MergeBuffer/ — 待处理缓冲区

**功能**: 所有新发现的内容（论文思考、Insights、临时笔记）首先放入此处，等待 Agent 进行分类和融合。

**典型内容**:
- `deep-research-thinking-*.md`: 深度研究的思考记录
- 临时性论文笔记
- 未分类的想法碎片
- **PDF 论文**: 用户下载的论文原文
- **公众号/技术博客文章**: Markdown 格式的学术内容

**内容类型识别与处理**:

```
┌─────────────────────────────────────────────────────────────┐
│  MergeBuffer 内容类型判断树                                  │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────┐
    │  判断文件类型                        │
    └─────────────────────────────────────┘
        │
    ┌───┴───┬───────────────┬─────────────────┐
    │       │               │                 │
    ▼       ▼               ▼                 ▼
┌───────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ .pdf  │ │ 公众号/博客  │ │ 思考记录     │ │ 其他         │
│ 论文  │ │ 学术内容     │ │ .md          │ │              │
└───┬───┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
    │            │                │                │
    ▼            ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│  📄 PDF 论文处理流程:                                        │
│  1. 将 PDF 移动到 Papers/ 文件夹                             │
│  2. 使用 pdftotext 提取文本内容                              │
│  3. 生成完整的 PapersRecap 笔记                              │
│  4. 触发理论导师模式，更新相关 Foundations                    │
│  5. 删除 MergeBuffer 中的原文件                              │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  📱 公众号/博客学术内容处理流程:                              │
│  1. 提炼核心思想和关键洞见                                   │
│  2. 判断目标位置:                                            │
│     - 理论性内容 → 融合到 Foundations/ 对应章节              │
│     - 论文解读 → 创建/补充 PapersRecap/ 笔记                 │
│     - 技术教程 → 视情况归入 Foundations 或 Projects          │
│  3. 建立与现有知识的链接                                     │
│  4. 确认融合完成后删除原文件                                 │
│                                                             │
│  ⚠️ 注意: 公众号内容通常只提炼核心思想，                      │
│     不需要保留原文的全部细节，只保留有价值的洞见             │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  🧠 思考记录处理流程:                                        │
│  1. 分析内容主题和价值                                       │
│  2. 提取可融合的知识点                                       │
│  3. 按主题分配到 Foundations/PapersRecap/Projects            │
│  4. 完成融合后删除原文件                                     │
└─────────────────────────────────────────────────────────────┘
```

**处理流程**:
```
MergeBuffer/新文件
        │
        ▼
    ┌─────────────────────────────────────┐
    │  Step 1: 内容分析                    │
    │  - 识别文件类型（PDF/Markdown/其他） │
    │  - 识别核心概念                      │
    │  - 确定所属领域                      │
    │  - 提取可链接的知识点                │
    └─────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────┐
    │  Step 2: 内容融合                    │
    │  - PDF论文 → Papers/ + PapersRecap/ │
    │  - 理论内容 → Foundations/           │
    │  - 论文相关 → PapersRecap/           │
    │  - 项目相关 → Projects/              │
    └─────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────┐
    │  Step 3: 建立关联                    │
    │  - 添加 [[wikilinks]] 到相关笔记     │
    │  - 更新被引用笔记的反向链接          │
    │  - 必要时更新 taxonomy.md            │
    └─────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────┐
    │  Step 4: 清理                        │
    │  - 原文件已完全融合 → 自主删除       │
    │  - 原文件有独立价值 → 保留并归档     │
    │                                     │
    │  ⚠️ 重要: 一旦确认核心内容已完整融入   │
    │     对应 Foundations/PapersRecap，   │
    │     Agent 可以自主删除原文件，       │
    │     无需询问用户确认，避免冗余。     │
    └─────────────────────────────────────┘
```

### 2.3 PapersRecap/ — 论文精读笔记

**功能**: 存储论文的深度分析笔记，是理解前沿研究的入口。

**命名规范**: 默认与 PDF basename 保持一致，仅将后缀替换为 `.md`（保留原论文标题、空格和文件系统允许的特殊字符）
- ⚠️ 特殊字符处理：只有在当前文件系统或同步工具明确禁止某字符时，才替换为 `-` 或空格，并在 frontmatter 的 `paper-pdf` 中保留精确 PDF 文件名
- 📁 输出位置：若 PDF 文件夹有同级 recap 目录（如 `RelatedPapers/` 对应 `RelatedPapersRecap/`），recap 写入 recap 目录，不写在 PDF 原目录
- 🔎 PDF 读取：处理 PDF 或文件夹 PDF 时必须先使用 `.github/skills/pdf/SKILL.md` 或全局 `$pdf`，用渲染页和多工具抽取交叉确认
- 📄 PDF recap / 精读 / 整理任务必须优先使用 `.github/skills/paper-recap-insight/SKILL.md` 或全局 `$paper-recap-insight`

**标准模板** (强制遵循):
```markdown
---
tags:
  - paper
  - [主领域: manipulation/rl/control/...]
aliases:
  - [论文简称]
paper-year: YYYY
read-date: YYYY-MM-DD
venue: [会议/期刊]
paper-pdf: "[[Papers/<论文PDF精确文件名>.pdf]]"
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
---

# 论文完整标题

> [!abstract] 核心贡献
> 一句话概括论文最核心的创新点

## 1. 问题设定与动机
### 1.1 为什么需要这个工作？
### 1.2 现有方法的局限
### 1.3 核心洞察（一句话 + 直观隐喻）

## 2. 核心方法/理论
### 2.1 关键创新点（Delta 分析）
与现有 SOTA 的增量（Delta）是什么？列出 1-3 个关键贡献点。
### 2.2 数学框架
完整的数学推导链，从问题定义到目标函数/损失函数。不跳步。
$$
公式推导（含变量物理意义注释）
$$
### 2.3 概念信息流 / 算法机制（无代码）
用 prose、公式、表格或图示说明信息如何流动、变量从哪里来、哪些量固定/观测/计算/学习、机制为什么成立。
默认不输出“最小 PyTorch 逻辑”或代码实现段；实现细节只有在揭示原理、数值约束、失败模式或实验瓶颈时才写入。

## 3. 训练与实验细节
### 3.1 训练设定
- 训练集/测试集的来源与规模
- 监督信号（Supervision Signals）是什么
- 训练任务列表
### 3.2 评估指标（Metrics）
### 3.3 核心实验结果（含关键数字）
### 3.4 Ablation Study 解读
不只列结果，解释"为什么去掉这个组件会导致那个效果"

## 4. 工程关键细节 (Engineering Tricks)
- 数值稳定性技巧（如 rot6D、advantage 归一化）
- 维度陷阱 / 常见实现错误
- 推理延迟 / 实时性约束

## 5. 核心洞见 (Insights)
> [!quote] Insight 1: ...
> ...
### 5.1 理论局限性深度分析
为什么选择这个设计？替代方案为什么不行？从理论/算法/工程三个维度分析。

## 6. 与知识体系的联系
### 与 [[Foundations文件名]] 的联系
- 具体关联点描述（附精确数学对应关系）

## 7. 局限与未来方向
### 7.1 论文自身局限
### 7.2 对用户研究（灵巧手转笔 / Sim-to-Real）的启发

## References
- [[相关论文1]]
- [[相关论文2]]
```

### 2.3.1 算法颗粒度标准 (Algorithm Granularity Standard)

> [!danger] 核心要求 — 这是论文笔记质量的决定性标准
> 
> 以下颗粒度要求来源于知识库所有者在实际研究中展现的关注模式（参考范例：MergeBuffer/gemini-chat/ 中的 PPO 损失函数详解与 CGP 论文深度分析）。
> 
> **所有 PapersRecap 论文笔记必须达到此颗粒度。**

**颗粒度要求清单**：

| 维度 | 要求 | 示例 |
|------|------|------|
| **数学推导完整性** | 从问题定义到损失函数/优化目标的完整推导链，不跳步 | PPO: 从重要性采样 → 概率比率 → Clip 机制的完整数学链 |
| **机制级核心逻辑** | 用概念信息流、变量来源、公式角色和符号陷阱解释算法机制 | 说明 `old_log_probs` 来自 rollout 且 detached、`new_log_probs` 来自当前策略前向传播且带梯度，而不是默认贴 PyTorch 代码 |
| **物理量来源追踪** | 每个变量的来源阶段（Rollout/计算/网络输出）和计算图中的梯度属性 | `old_log_probs` 来自 Rollout（detached），`new_log_probs` 来自当前前向传播（带梯度） |
| **工程避坑指南** | log_prob 维度求和、归一化、数值稳定性等实战 tips | 24 自由度灵巧手中 `log_prob` 必须在 `dim=-1` 上求和 |
| **训练细节盘点** | 训练集/测试集来源、监督信号、任务列表、评估指标及关键数字 | CGP: 60条演示/Box Flipping，成功率 93.3% vs 43.6% |
| **Ablation 因果解读** | 不只列结果，解释去掉组件后效果变差的因果机制 | 去掉 KL 约束后 MAE 下降但 KL Divergence 暴涨→潜空间崎岖→Diffusion 生成崩溃 |
| **理论局限性分析** | 从理论/算法/工程三个维度分析设计选择的 trade-off | PPO 单峰高斯: 理论上 log-prob 精确可算，但无法表达多模态动作分布 |
| **替代方案对比** | 分析同一问题的其他可行方案及其优劣 | CGP 学 $\mathcal{M}_\phi(x,u)→a$ vs FACET 调阻抗参数 vs RL 端到端输出 $a$ |
| **个性化 Insight** | 与用户自身研究（PPO 训练灵巧手转笔）的对比和可迁移思想 | "受 CGP 启发，可在 RL 框架下增加正向动力学自监督辅助 Loss" |

**MergeBuffer 中 Gemini Chat 的特殊处理流程**：

```
MergeBuffer/gemini-chat/ 中的对话文件
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 识别对话涉及的论文/主题                             │
│  - chat.md 标题通常指向对应论文                              │
│  - 在 PapersRecap/ 中定位对应笔记                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 提取用户关注的算法颗粒度                            │
│  - 完整数学推导（公式 + 物理量注释）                         │
│  - 概念信息流 / 算法机制（变量来源、符号陷阱、失败边界）       │
│  - 工程关键细节（避坑、数值技巧）                            │
│  - 训练细节盘点（数据/信号/指标/关键数字）                   │
│  - 用户追问中隐含的理论兴趣点                               │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 合并到对应 PapersRecap（不创建新文件）              │
│  - 补充缺失的数学推导                                       │
│  - 补充概念信息流 / 算法机制 / 变量来源                      │
│  - 补充训练/实验细节                                        │
│  - 补充工程 tricks 和避坑指南                               │
│  - 抽象出与知识库的关联 Insights                            │
│  - 如果涉及基础理论（如 PPO），同步更新对应 Foundation       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 清理原文件                                          │
│  - 核心内容已融入 Foundations 或 PapersRecap 后              │
│  - 删除 gemini-chat/ 中的对话 .md 文件                       │
│  - ⚠️ 保留 gemini-chat/ 文件夹本身（不删文件夹）             │
│  - 这些对话文件是临时参考源，不应长期驻留                    │
└─────────────────────────────────────────────────────────────┘
```

**关联要求**:
- 每篇论文笔记必须链接至少 **2个** Foundations 领域
- 必须标注论文对灵巧操作的具体 Value-Add
- 在 `## 5. 与知识体系的联系` 中明确说明与每个 Foundation 的具体关联

**反向链接策略**:
当论文提供了某个 Foundation 领域的重要补充时，应同时在该 Foundation 中添加反向引用：
```markdown
# 在 Foundation 笔记中添加
> [!abstract] 统一视角 (来自 [[论文名]])
> 论文中的核心洞见...
```

### 2.3.2 PapersRecap 定期 Refine 流程 (Periodic Refine Workflow)

> [!important] 触发条件与目标
> 
> **触发时机**：用户明确要求 / MergeBuffer/gemini-chat 新增对话揭示了更高的提问粒度 / 发现现有笔记不满足 §2.3.1 颗粒度标准时
> 
> **目标**：将已有的 PapersRecap 笔记对齐到用户在 Gemini 对话中展现的实际研究关注深度

**用户提问粒度特征**（提炼自 gemini-chat 对话记录）：

| 维度 | 用户关注模式 | 对 PapersRecap 的要求 |
|------|-------------|---------------------|
| **数据流全链路追踪** | 追问每个物理量的实际来源：Rollout 阶段 vs 计算阶段 vs 网络前向传播，以及在计算图中的梯度属性（detached vs requires_grad） | 在 §2 核心方法中标注每个变量的来源阶段和梯度属性 |
| **跨方法/跨范式对比** | 习惯将论文方法与自己的 PPO 转笔策略进行结构性对比（IL vs RL、端到端 vs 解耦、Action Chunking vs 单步） | 在 §5 或新增对比表格，与 PPO/灵巧手方案的异同分析 |
| **设计决策因果推理** | 不满足于"做了什么"，追问"为什么这样做而不那样做"，从理论约束和工程 trade-off 两个层面 | 在 §5.1 增加"设计选择的替代方案分析" |
| **向自身研究的迁移** | 每篇论文都会追问"对我转笔/Sim-to-Real 有什么启发"，甚至 brainstorm 具体的 idea | 在 §5.2 或 §7.2 补充个性化的灵巧手转笔/Sim-to-Real 启发 |
| **Ablation 因果链** | 不只要结果表格，追踪完整因果链：去掉 A → 导致 B 效果变化 → 因为 C 物理/算法机制 | 在 §3.4 将 Ablation 从列举升级为因果分析 |
| **理论边界辨析** | 对近似/易混淆概念进行精确区分（如 Multi-step vs Iterative RL、MPC vs Action Chunking） | 在 §2 或 §5 中增加概念辨析段落 |
| **机制级理解** | 要求概念信息流、变量来源、维度/物理意义、符号陷阱和失败边界 | 在 §2.3 补充/完善机制解释；不默认添加代码段 |

**Refine 执行检查表**（逐文件检查）：

```
PapersRecap Refine Checklist:
├── [ ] Frontmatter 完整（tags, aliases, paper-year, read-date, venue, paper-pdf, related）
├── [ ] §1 有核心洞察隐喻 + 现有方法局限具体化
├── [ ] §2 数学推导链完整（不跳步）+ Delta 分析精确化
├── [ ] §2 概念信息流 / 算法机制（变量来源、符号陷阱、失败边界）
├── [ ] §3 训练细节（数据来源/规模、监督信号、任务列表、关键数字）
├── [ ] §3 Ablation 因果链（去A→B效果→因C机制，而非仅列结果）
├── [ ] §4 工程避坑（数值稳定性、维度陷阱、推理延迟）
├── [ ] §5 理论局限性三维度分析（理论/算法/工程）+ 替代方案
├── [ ] §5 个性化 Insight：与灵巧手转笔 / Sim-to-Real 的可迁移启发
├── [ ] §6 至少链接 2 个 Foundations + 具体数学对应关系
├── [ ] §7 跨方法结构性对比（与 PPO 方案 / 同领域其他方法）
└── [ ] 所有 wikilinks 指向正确目标（无断链）
```

**Refine 优先级排序**：
1. 与用户当前研究直接相关的论文（灵巧手、Sim-to-Real、PPO、课程学习）
2. 有对应 gemini-chat 深度讨论的论文
3. Foundation 高频引用的论文
4. 其余按 read-date 倒序

### 2.4 Projects/ — 研究项目

**功能**: 存储个人研究项目的详细文档。

**当前项目**:
- `Dynamic Non-Prehensile Manipulation/` — 动态非抓取灵巧操作

**结构要求**:
- 每个项目一个文件夹
- 主文档命名与文件夹同名
- 包含: 研究动机 → 理论框架 → 任务设计 → 实验方案

### 2.5 Books/ — 教科书库

**功能**: 存储相关领域的经典教科书 PDF。

**当前书籍**:
- `A Mathematical Introduction to Robotic Manipulation.pdf` — Murray 经典
- `Deep Reinforcement Learning.pdf` — 深度强化学习
- `Optimization in Theory and Practice.pdf` — 优化理论
- `Theory of Deep Learning.pdf` — 深度学习理论
- `Data-based linear systems and control theory.pdf` — 数据驱动控制

**操作规范**: 
- 仅存储 PDF，不做修改
- 书中的核心概念应提取到 Foundations/ 中

### 2.6 Backups/ — 备份区

**功能**: 系统备份，**绝对禁止任何修改**。

---

## 3. 知识关联建立规范 (Knowledge Linking Standards)

### 3.1 Wikilink 使用原则

```markdown
# 正确用法

## 引用概念
在 [[ControlTheory]] 中，阻抗控制通过调节...

## 引用具体章节
参见 [[ReinforcementLearning#1.2 接触流形与切空间探索]]

## 引用论文
这与 [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] 的方法类似

## 别名显示
使用 [[Dynamics|动力学基础]] 来建模...
```

### 3.2 关联密度要求

| 文档类型 | 最小关联数 | 主要链接目标 |
|---------|-----------|-------------|
| Foundation 笔记 | 3+ | 其他 Foundations, Papers |
| 论文笔记 | 2+ | Foundations (必须), Projects |
| 项目文档 | 5+ | Foundations, Papers, 其他 Projects |
| MergeBuffer 内容 | 处理后 3+ | 取决于内容类型 |

### 3.3 双向链接维护

当创建 `A → B` 的链接时，考虑是否需要在 B 中添加到 A 的反向引用：

```markdown
# 在 ControlTheory.md 中
## 相关研究
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] - 稳定性证书方法

# 在论文笔记中
## 理论基础
本文的控制理论基础参见 [[ControlTheory#2.4 阻抗控制]]
```

### 3.4 Wikilink 章节引用规范（断链预防）

> [!danger] 断链是知识图谱最严重的质量问题
> 引用不存在的章节会导致 Obsidian 无法正确解析链接，降低知识导航体验。

**章节引用原则**:

1. **引用前验证**: 引用 `[[File#Section]]` 格式时，必须确认目标章节**确实存在**
2. **使用精确标题**: 章节标题必须与文件中的实际标题**完全一致**（包括空格、标点）
3. **泛化回退**: 若不确定章节是否存在，使用泛化链接 `[[File]]` 而非猜测章节名

```markdown
# ❌ 错误示例 — 引用不存在的章节
[[ControlTheory#3.6 多速率控制]]     # 实际只有 3.1-3.4
[[Dynamics#5.2 步态动力学]]          # 实际 5.2 是 Convex Optimization
[[ControlTheory#2.3 Safe RL]]        # 实际 2.3 是抓取矩阵

# ✅ 正确做法 — 使用泛化链接或精确标题
[[ControlTheory]]                    # 安全的泛化链接
[[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]]  # 精确标题
```

**维护时的断链检查流程**:

```
1. grep_search 搜索 [[Foundation#.*]] 模式的引用
2. 对照目标 Foundation 文件的实际章节列表
3. 发现不匹配 → 修正为泛化链接或正确章节
```

### 3.5 Frontmatter 字段命名规范

> [!important] 统一的字段命名是 Obsidian Bases 正常工作的前提

**PapersRecap 论文笔记的标准 frontmatter**:

```yaml
---
tags:
  - paper                    # ✅ 统一用 paper，不用 paper-recap
  - reinforcement-learning   # 领域标签
  - sim-to-real             # 技术标签
aliases:
  - ShortName               # 论文简称
  - 中文别名                 # 可选
paper-year: 2024            # ✅ 统一用 paper-year，不用 year
read-date: 2026-02-01       # ✅ 统一用 read-date，不用 created
venue: CoRL 2024            # 会议/期刊
paper-pdf: "[[Papers/<精确PDF文件名>.pdf]]"  # ✅ 直接写 Obsidian 链接；必须加双引号（防止 YAML 误解析）
authors:                    # 作者列表
  - Author Name
related:                    # 关联的 Foundation
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
---
```

**字段命名对照表**:

| 正确字段名 | 错误用法（历史遗留） | 说明 |
|-----------|-------------------|------|
| `paper-year` | `year` | 避免与通用 year 字段混淆 |
| `read-date` | `created` | 明确表示阅读日期 |
| `paper-pdf` | 公式推断路径 | 直接 Obsidian 链接字符串，格式 `"[[Papers/<精确PDF文件名>.pdf]]"`，必须加双引号 |
| `paper` (tag) | `paper-recap` | 简洁统一 |

**Projects 项目笔记的标准 frontmatter**:

```yaml
---
tags:
  - project
  - 技术方向标签
aliases:
  - 项目简称
created: 2026-01-31         # 项目创建日期
status: active | paused | completed
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
---
```

### 3.6 Obsidian Bases 公式规范

> [!warning] Bases 中的 `file.content` 属性不存在

**有效的 file 属性**（完整列表）:

| 属性 | 类型 | 说明 |
|-----|------|------|
| `file.name` | String | 文件名（含扩展名） |
| `file.basename` | String | 文件名（不含扩展名） |
| `file.path` | String | 完整路径 |
| `file.folder` | String | 父文件夹路径 |
| `file.ext` | String | 扩展名 |
| `file.size` | Number | 文件大小（字节） |
| `file.ctime` | Date | 创建时间 |
| `file.mtime` | Date | 修改时间 |
| `file.tags` | List | 所有标签 |
| `file.links` | List | 内部链接 |
| `file.backlinks` | List | 反向链接 |

```yaml
# ❌ 错误 — file.content 不存在
formulas:
  content_size: (file.content.length / 1000).round(1) + "k"

# ✅ 正确 — 使用 file.size
formulas:
  content_size: (file.size / 1000).round(1) + "k"
```

**PDF 直链属性规范**（`_PapersIndex.base` 标准写法）:

> [!warning] 不再使用 `formula.paper_pdf` 生成链接。
> PDF 链接由每篇笔记的 `paper-pdf` 属性直接提供，索引表直接展示该属性。

```yaml
# ✅ 推荐 — 在 frontmatter 直接写链接属性
paper-pdf: "[[Papers/OmniXtreme: Breaking the Generality Barrier in.pdf]]"

# ✅ _PapersIndex.base 直接展示 paper-pdf 属性
properties:
  paper-pdf:
    displayName: 📎 论文PDF
views:
  - type: table
    order:
      - file.name
      - read-date
      - paper-year
      - paper-pdf
```

**为什么必须加双引号**：
```yaml
# ❌ 错误 — 逗号/冒号路径会触发 YAML 误解析
paper-pdf: [[Papers/A Survey of Sim-to-Real Methods in RL- Progress, Prospects.pdf]]
paper-pdf: [[Papers/EUREKA: HUMAN-LEVEL REWARD DESIGN VIA CODING LARGE LANGUAGE MODELS.pdf]]

# ✅ 正确 — 双引号强制整体为字符串
paper-pdf: "[[Papers/A Survey of Sim-to-Real Methods in RL- Progress, Prospects.pdf]]"
paper-pdf: "[[Papers/EUREKA: HUMAN-LEVEL REWARD DESIGN VIA CODING LARGE LANGUAGE MODELS.pdf]]"
```

**字段值格式**：`"[[Papers/<精确文件名>.pdf]]"`（库根目录相对路径，文件名需与 `Papers/` 完全一致）

---

## 4. MergeBuffer 处理详细流程 (MergeBuffer Processing)

### 4.1 内容类型识别

```
MergeBuffer 文件
      │
      ├── 是否包含论文分析? ──────────────────────┐
      │       │                                   │
      │       ▼ Yes                               │
      │   提取到 PapersRecap/                     │
      │                                           │
      ├── 是否包含理论推导/概念解释? ─────────────┤
      │       │                                   │
      │       ▼ Yes                               │
      │   融入对应 Foundations/ 文件              │
      │                                           │
      ├── 是否与特定项目相关? ────────────────────┤
      │       │                                   │
      │       ▼ Yes                               │
      │   移入对应 Projects/ 文件夹               │
      │                                           │
      └── 是否为纯粹的临时思考? ──────────────────┘
              │
              ▼ Yes
          评估是否有保留价值
          ├── 有价值: 提炼后融入相关笔记
          └── 无价值: 删除
```

### 4.2 融合操作示例

**场景**: MergeBuffer 中有一份关于"滑模控制在灵巧手中的应用"的笔记

**操作步骤**:

1. **分析内容**: 识别出核心概念（滑模控制、抖振抑制、鲁棒性）
2. **确定目标**: 主要内容应融入 `ControlTheory.md`
3. **定位插入点**: 找到 ControlTheory.md 中的非线性控制章节
4. **融合内容**: 
   - 将理论部分添加到 ControlTheory.md
   - 添加指向相关论文的 wikilink
   - 如果涉及具体算法实现，考虑是否需要创建代码块
5. **建立关联**:
   - 在 `ReinforcementLearning.md` 中添加交叉引用（如果涉及鲁棒RL）
   - 在 `taxonomy.md` 中检查是否需要更新
6. **清理**: 删除 MergeBuffer 中的原始文件

---

### 4.3 PDF 论文处理工具与技巧

**核心工具**: `pdftotext` (来自 poppler-utils)

**安装确认**:
```bash
which pdftotext && pdftotext -v 2>&1 | head -1
# 预期输出: /opt/homebrew/bin/pdftotext
```

**标准提取命令**:
```bash
# 基础提取（输出到 stdout）
pdftotext "论文名.pdf" -

# 提取前 N 行（快速预览）
pdftotext "论文名.pdf" - | head -400

# 提取后 N 行（查看结论/参考文献）
pdftotext "论文名.pdf" - | tail -300

# 保存到临时文件（处理大文件）
pdftotext "论文名.pdf" /tmp/paper.txt && cat /tmp/paper.txt
```

**特殊字符文件名处理**:
```bash
# 文件名含引号、冒号等特殊字符时
# 方法1: 使用 find + 变量
cd Papers && file=$(ls | grep "关键词") && pdftotext "$file" -

# 方法2: 输出到临时文件再读取
pdftotext "原文件名.pdf" /tmp/output.txt && head -500 /tmp/output.txt

# 方法3: 使用通配符
pdftotext Papers/*Lessons*.pdf -
```

**常见问题**:
- ❌ `I/O Error: Couldn't open file` → 检查文件名中的特殊字符
- ❌ 乱码输出 → PDF 可能是扫描件，需要 OCR
- ⚠️ 公式显示不完整 → 正常现象，从上下文理解

---

## 5. 内容质量标准 (Content Quality Standards)

### 5.1 Foundations 文档标准

每个 Foundation 文档应包含：

```markdown
# 领域名称（中英双语）

## 摘要 (Abstract)
- 领域在灵巧操作中的定位
- 核心问题陈述

## 1. Core Concepts: 核心概念
### 1.x 概念名称
#### 物理直觉
- 直观解释，使用类比

#### 数学定义
- 严格的数学公式
- 使用 LaTeX: $公式$

#### 在灵巧操作中的意义
- 具体应用场景
- Value-add 分析

## 2. Evolution & Insights: 技术演进
### 2.x 演进阶段
**Problem**: 旧方法面临的问题
**Why it failed**: 失效的根本原因
**Solution**: 新方法如何解决
**Value-add**: 引入的新价值

## 3. Implementation: 算法实现
### 3.x 算法名称
- 核心逻辑（伪代码或 Python/C++）
- 移除防御性代码，保留核心算法
- 注释解释物理意义
```

### 5.2 代码风格

```python
# ✅ 正确风格：核心算法逻辑
def compute_grasp_matrix(contact_points, contact_normals):
    """
    计算空间抓取矩阵 G ∈ R^{6×3k}
    G 将接触力映射为物体合力: F_obj = G @ f_contact
    """
    G = np.zeros((6, 3 * len(contact_points)))
    for i, (p, n) in enumerate(zip(contact_points, contact_normals)):
        R = rotation_from_normal(n)  # 接触坐标系
        G[0:3, 3*i:3*i+3] = R
        G[3:6, 3*i:3*i+3] = skew(p) @ R  # 力臂贡献
    return G

# ❌ 错误风格：包含冗余代码
def compute_grasp_matrix(contact_points, contact_normals):
    try:
        assert len(contact_points) == len(contact_normals)
        if contact_points is None:
            raise ValueError("Contact points cannot be None")
        # ... 大量防御性代码
    except Exception as e:
        logging.error(f"Error: {e}")
```

---

## 5.5 理论导师模式 (Theoretical Mentor Mode)

> [!important] 核心理念
> **你是这个领域理论深厚的科研专家教授，而非简单的知识整理工具。**
> 
> 当用户要求开启"理论导师模式"时，你的工作模式发生根本性转变：
> 1. **跳出已有知识图谱** — 不局限于当前 Foundations 中已有的内容
> 2. **编写教科书心态** — 以撰写该领域权威教科书的标准来审视和补充内容
> 3. **详尽的演进脉络** — 每个领域应该体现完整的算法/理论演变历史
> 4. **深入的算法分析** — 不仅记录"是什么"，更要剖析"为什么"和"怎么演变"

### 5.5.1 理论导师模式的工作原则

```
┌─────────────────────────────────────────────────────────────────────┐
│                    理论导师模式 vs 普通维护模式                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  普通维护模式:                                                       │
│  ├── 以用户提供的内容为边界                                          │
│  ├── 整理、关联、格式化已有知识                                       │
│  └── 被动响应：用户给什么，处理什么                                   │
│                                                                     │
│  理论导师模式:                                                       │
│  ├── 主动审视领域知识的完整性                                        │
│  ├── 从领域专家视角发现知识缺口                                       │
│  ├── 补充教科书级别的演进脉络                                        │
│  ├── 为每个算法提供：历史背景 → 核心创新 → 局限性 → 后续发展           │
│  └── 主动扩展：即使用户没提，也应该补充关键的遗漏内容                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.5.2 演进脉络的标准结构

每个 Foundation 领域的核心算法/理论应该展现清晰的演进链条：

```markdown
## X.x 算法演进脉络：从 [起点] 到 [当前前沿]

### Phase 1: [奠基期算法] (年代)
**历史背景**: 该算法诞生的时代需求和技术条件
**核心创新**: 算法的关键 insight 和数学机制
**局限性**: 为什么后来被改进或取代
**代表工作**: 原始论文/关键人物

### Phase 2: [发展期算法] (年代)
**承前启后**: 如何解决了 Phase 1 的局限
**核心创新**: 新引入的机制
**局限性**: 仍然存在的问题
**代表工作**: 标志性论文

### Phase 3: [成熟期算法] (年代)
...

### Phase N: [当前前沿] (Present)
**当前最优实践**: 工业界/学术界的主流选择
**开放问题**: 仍未解决的挑战
**未来方向**: 可能的演进趋势
```

### 5.5.3 教科书驱动的知识补充 (Textbook-Driven Knowledge Enhancement)

> [!important] 核心规则
> **Books/ 文件夹中的教科书是理论导师模式的权威参考源。**
> 
> 在理论导师模式下，你必须：
> 1. **参考教科书脉络** — 查阅 Books/ 中相关教科书的章节结构和演进逻辑
> 2. **吸取 Insights** — 提取教科书中对算法演变的深刻洞察
> 3. **补充遗漏算法** — 识别 Foundations 中缺失但教科书中强调的重要算法
> 4. **建立逻辑关联** — 将教科书的知识体系映射到灵巧操作视角

**当前可用教科书**:

| 教科书 | 对应 Foundations | 核心价值 |
|-------|-----------------|---------|
| `A Mathematical Introduction to Robotic Manipulation.pdf` | Dynamics, ContactMechanics, ControlTheory | Murray 经典：抓取矩阵、力闭合、操作空间 |
| `Deep Reinforcement Learning.pdf` | ReinforcementLearning | 算法演进脉络、理论分析 |
| `Optimization in Theory and Practice.pdf` | Optimization | 凸优化、SQP、Interior Point 方法 |
| `Theory of Deep Learning.pdf` | RepresentationLearning | 深度学习理论基础 |
| `Data-based linear systems and control theory.pdf` | ControlTheory, SignalProcessing | 数据驱动控制、系统辨识 |

**教科书迁移工作流**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    教科书 → Foundations 迁移流程                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: 识别对应教科书                                              │
│  ├── 根据当前编辑的 Foundation 文件确定相关教科书                     │
│  └── 例如：编辑 Dynamics.md → 参考 Murray 的操作书                    │
│                                                                     │
│  Step 2: 提取演进脉络                                                │
│  ├── 阅读教科书的章节目录和核心概念                                   │
│  ├── 识别算法/理论的发展顺序                                         │
│  └── 记录关键 insights 和 value-add                                  │
│                                                                     │
│  Step 3: 灵巧操作视角迁移                                            │
│  ├── 将通用理论转化为灵巧操作的具体应用                               │
│  ├── 添加物理直觉和工程意义                                          │
│  └── 建立与其他 Foundation 领域的交叉链接                            │
│                                                                     │
│  Step 4: 结构化融入                                                  │
│  ├── 按照 5.5.2 的标准结构组织内容                                   │
│  ├── 确保演进脉络的完整性和逻辑性                                    │
│  └── 添加教科书引用 (如有必要)                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**重点提醒**:
- Murray 的《A Mathematical Introduction to Robotic Manipulation》是灵巧操作的**圣经**
- 其中的 **Chapter 5 (Contact Modeling)** 和 **Chapter 6 (Grasping)** 必须完整映射到 ContactMechanics.md
- 抓取矩阵 $G$、力闭合条件、摩擦锥等概念必须有严格的数学定义

---

> [!critical] 🔥 主动教科书检索与 Insight 提炼规则
> 
> **这是强制性要求**：AI Agent 必须**主动且频繁地**从 Books/ 文件夹检索和提炼知识，而不是被动等待。
> 
> **触发时机** — 在以下场景中，你**必须**查阅相关教科书：
> 1. **处理论文时** — 查阅教科书中对应章节，补充论文所依赖的理论背景
> 2. **更新 Foundations 时** — 参考教科书的知识体系确保演进脉络完整
> 3. **发现概念空白时** — 主动从教科书中提取缺失的定义和原理
> 4. **遇到数学符号/公式时** — 使用教科书作为符号规范的权威来源
> 
> **提炼目标** — 从教科书中提取的 Insights 应组织到：
> - `Foundations/*.md` — 核心理论定义、算法演进脉络、物理直觉
> - `PapersRecap/*.md` — 论文所依赖的背景知识、与经典理论的对比

**教科书 Insight 提炼示例**:

```
场景：处理一篇关于接触力估计的论文

Step 1: 识别论文依赖的理论
    → 发现使用了 "抓取矩阵" (Grasp Matrix) 概念

Step 2: 查阅 Murray 教科书 Chapter 6
    → 提取抓取矩阵的严格定义: G = [Ad^T_{g_{oc_i}}·B_i]
    → 理解其物理意义：将手指力映射到物体力/力矩

Step 3: 写入 Foundations
    → 在 ContactMechanics.md 添加抓取矩阵的形式化定义
    → 建立与力闭合(Force-Closure)条件的逻辑关联

Step 4: 增强 PapersRecap
    → 在论文笔记中添加 callout：教科书背景知识
    → 明确论文的创新点相对于经典理论的 delta
```

**教科书-领域映射表 (主动检索时参考)**:

| 遇到的概念 | 应查阅的教科书 | 章节提示 |
|-----------|--------------|---------|
| 雅可比、运动学 | Murray - Robotic Manipulation | Ch 2-3 |
| 接触力、摩擦锥 | Murray - Robotic Manipulation | Ch 5 |
| 抓取矩阵、力闭合 | Murray - Robotic Manipulation | Ch 6 |
| 值函数、策略梯度 | Deep Reinforcement Learning | Part I-II |
| Actor-Critic、SAC | Deep Reinforcement Learning | Part III |
| 凸优化、对偶性 | Optimization in Theory and Practice | Ch 4-5 |
| SQP、约束优化 | Optimization in Theory and Practice | Ch 7-8 |
| 系统辨识、数据驱动 | Data-based Linear Systems | Ch 2-4 |
| 神经网络理论 | Theory of Deep Learning | 全书 |

---

### 5.5.4 论文/PDF 触发的理论补充

> [!warning] 重要规则
> 当新加入的论文或 PDF 涉及到某个领域的已有理论/算法，而对应的 Foundation 文件中**缺少**对此的体现时，必须：
> 1. 在 Foundation 文件的对应演进脉络中添加该理论/算法
> 2. 提供完整的逻辑分析：它在演进链中的位置、解决了什么问题、有何局限
> 3. 建立与论文笔记的双向链接

**示例场景**:
```
用户添加了一篇关于 "Differentiable Physics" 的论文
    ↓
检查 Dynamics.md 和 Optimization.md
    ↓
发现缺少 "可微物理仿真" 的演进脉络
    ↓
主动补充:
├── 刚体物理引擎的不可微问题
├── 软接触松弛方法
├── 隐式微分技术
├── 神经物理引擎的兴起
└── 与 MPC/轨迹优化的结合
```

### 5.5.5 各 Foundation 领域的演进脉络检查清单

以下是各领域应该包含的代表性算法/理论演进（如有缺失，在理论导师模式下应主动补充）：

| 领域 | 应包含的演进脉络（示例） |
|-----|------------------------|
| **Dynamics** | Lagrangian → RNEA → ABA → Spatial Vector Algebra → Differentiable Dynamics |
| **ContactMechanics** | 弹簧-阻尼 → Hertz接触 → LCP → Soft Contact → Stochastic LCP |
| **ControlTheory** | PID → Computed Torque → Impedance → OSF → Contact-Implicit MPC |
| **Optimization** | 梯度下降 → Newton → SQP → Interior Point → iLQR/DDP → Differentiable Optimization Layers |
| **ReinforcementLearning** | DQN → DDPG → TD3 → SAC → PPO → Offline RL → Diffusion Policy |
| **StochasticProcess** | Wiener → GP → Bayesian Filtering → MPPI → Diffusion Models |
| **InformationTheory** | Shannon → Rate-Distortion → Empowerment → VIME → DIAYN |
| **ComputationalGeometry** | Convex Hull → GJK/EPA → BVH → SDF → Neural Implicit (DeepSDF, NeRF) |
| **SignalProcessing** | KF → EKF → UKF → Particle Filter → Factor Graph → Neural Filtering |
| **RepresentationLearning** | PCA → Autoencoders → VAE → Contrastive → Multimodal Fusion |

### 5.5.6 深度分析的标准

在理论导师模式下，对算法的分析必须达到以下深度：

```markdown
## 算法名称

### 1. 物理/数学直觉 (Intuition)
用一句话/一个类比解释算法的核心 idea

### 2. 形式化定义 (Formal Definition)
严格的数学公式，配合变量解释

### 3. 为什么它有效 (Why It Works)
从理论角度解释算法成功的根本原因
- 凸性？收敛性保证？
- 利用了什么先验假设？
- 与物理规律的契合点？

### 4. 局限性与失效场景 (Limitations)
- 在什么条件下失效？
- 对什么假设敏感？
- 计算复杂度瓶颈？

### 5. 在灵巧操作中的具体应用 (Application in Dexterous Manipulation)
- 具体的使用场景
- 工程实践中的 tricks
- 与其他方法的对比

### 6. 代码实现要点 (Implementation Notes)
核心算法逻辑（非防御性代码）
```

---

## 6. 维护任务清单 (Maintenance Tasks)

### 6.1 定期任务

| 频率 | 任务 | 操作 |
|-----|------|------|
| 每次交互 | 处理 MergeBuffer | 分析新文件，融合或归档 |
| 每周 | 检查孤立笔记 | 确保所有笔记有足够的 wikilinks |
| 每月 | 更新 taxonomy.md | 反映知识结构的演变 |
| 每月 | 审查 PapersRecap | 确保论文笔记与 Foundations 充分关联 |

### 6.2 触发式任务

| 触发条件 | 任务 |
|---------|------|
| 用户添加新论文到 Papers/ | 提醒创建对应的 PapersRecap 笔记 |
| Foundations 文件重大更新 | 检查引用该文件的其他笔记是否需要更新 |
| 新项目创建 | 确保与相关 Foundations 建立链接 |

---

## 7. 特殊场景处理 (Special Cases)

### 7.1 概念跨领域

当一个概念横跨多个 Foundations 领域时：

```markdown
# 在主要领域详细展开
## [[ControlTheory]] - 阻抗控制的详细推导

# 在次要领域简要提及并链接
## [[ReinforcementLearning#与控制论的交叉]]
阻抗控制的概念在RL中也有应用，详见 [[ControlTheory#阻抗控制]]
```

### 7.2 内容冲突

如果发现知识库中存在矛盾的信息：

1. **不要立即删除任何一方**
2. 在冲突位置添加注释：
   ```markdown
   > [!warning] 内容待核实
   > 此处与 [[其他笔记#章节]] 的描述存在差异，需要进一步确认。
   ```
3. 告知用户需要人工判断

### 7.3 大规模重构

如果需要进行大规模文件夹或结构调整：

1. **首先与用户确认**
2. 在 Backups/ 创建快照（如果用户同意）
3. 分步执行，每步都确保链接完整性
4. 记录所有变更

---

## 8. Obsidian 语法速查 (Quick Reference)

### 8.1 Callouts

```markdown
> [!note] 标题
> 普通笔记

> [!tip] 技巧
> 有用的技巧

> [!warning] 警告
> 需要注意的内容

> [!question] 问题
> 待解决的问题

> [!example] 示例
> 具体例子
```

### 8.2 Properties (Frontmatter)

```yaml
---
tags:
  - control-theory
  - dexterous-manipulation
aliases:
  - 控制理论
  - Control
created: 2026-01-31
related:
  - "[[Dynamics]]"
  - "[[Optimization]]"
---
```

### 8.3 数学公式

```markdown
行内公式: $F = ma$

块级公式:
$$
M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau + J^T f_{ext}
$$
```

---

## 9. Agent 自检清单 (Self-Check)

在完成任何操作后，确认：

- [ ] 没有破坏现有的 wikilinks
- [ ] 新内容有足够的关联
- [ ] 遵循了代码风格规范
- [ ] 没有删除核心知识内容
- [ ] 文件命名符合规范
- [ ] Frontmatter 格式正确

---

## 10. 进度追踪与状态管理 (Progress Tracking)

### 10.1 PapersRecap 进度追踪

**快速状态检查命令**:
```bash
cd "/Users/yang/Notes/Notes" && \
echo "=== PapersRecap: $(ls -1 PapersRecap/*.md | wc -l) ===" && \
echo "=== Papers PDF: $(ls -1 Papers/*.pdf | wc -l) ===" && \
echo "=== 待处理论文 ===" && \
comm -23 <(ls Papers/*.pdf | xargs -I {} basename {} .pdf | sort) \
         <(ls PapersRecap/*.md | xargs -I {} basename {} .md | sort) | head -20
```

**处理优先级**:
1. 与当前研究方向（灵巧操作、RL 控制）直接相关的论文
2. 被多篇已读论文引用的基础性工作
3. 最新发表的前沿工作

### 10.2 MergeBuffer 索引维护

**`_MergeIndex.md` 结构**:
```markdown
### N. 文件名
**来源**: [PDF论文/公众号/思考记录]
**主题**: 一句话描述
**状态**: 🔴待处理 / 🟡进行中 / 🟢已完成

| 内容模块 | 目标位置 | 融合状态 |
|---------|---------|---------|
| 核心概念1 | [[TargetFile]] | ✅/🔲 |

**处理结果**: [融合/移动/删除] (日期)
```

### 10.3 会话结束检查点

每次会话结束时，必须更新：
1. **TASK_TRACKER.md** — 标记完成的任务，添加新发现的待办
2. **_MergeIndex.md** — 记录本次处理的 MergeBuffer 内容
3. **版本历史** — 如果对 SKILL.md 做了重要更新

---

## 11. 版本历史

| 日期 | 版本 | 变更 |
|-----|------|------|
| 2026-01-31 | v1.0 | 初始版本，建立完整管理框架 |
| 2026-01-31 | v1.1 | 添加 Bug 记录规范、MergeBuffer 自主删除权限 |
| 2026-01-31 | v1.2 | 完善理论导师模式定义，强调教科书级别的演进脉络标准、论文触发的理论补充机制、各领域演进检查清单 |
| 2026-01-31 | v1.3 | **重大更新**: 新增 5.5.3 教科书驱动的知识补充规范，要求在理论导师模式下必须参考 Books/ 中的教科书脉络，将教科书知识体系映射到灵巧操作视角 |
| 2026-01-31 | v1.4 | **知识完善**: 按教科书标准增强 Foundations: (1) ContactMechanics.md 添加 Murray 抓取矩阵严格定义、力闭合条件、Ferrari-Canny 品质度量; (2) Dynamics.md 添加 Khatib 操作空间动力学完整框架; (3) RepresentationLearning.md 添加 PointNet/PointNet++/Point Transformer 数学原理 |
| 2026-01-31 | v1.5 | **基础设施**: 创建 `.github/prompts/` 常用操作模板（5个）和 `.github/TASK_TRACKER.md` 全局任务追踪文档，解决上下文限制导致的任务中断问题 |
| 2026-01-31 | v1.6 | **工作流整合**: 将5个分散prompts合并为统一的 `standard-workflow.prompt.md`，强调每次交互必须同时执行：状态恢复、健康检查、论文处理、理论导师模式。论文精读时必须触发理论补充。 |
| 2026-01-31 | v1.7 | **规范强化**: (1) 完善 PapersRecap 标准模板，强制结构化输出; (2) 新增 §4.3 PDF 处理工具规范 (pdftotext 用法、特殊字符处理); (3) 新增 §10 进度追踪与状态管理; (4) 明确反向链接策略 |

---

## 12. Bug 记录与经验教训 (Bugs & Lessons Learned)

> [!note] 使用说明
> 当用户指出维护中的错误时，在此记录场景、原因和正确做法，避免重复犯错。

### 12.1 已记录的 Bug

| 日期 | 错误场景 | 原因分析 | 正确做法 |
|-----|---------|---------|---------|
| _待记录_ | _待记录_ | _待记录_ | _待记录_ |

### 12.2 常见陷阱提醒

```
⚠️ Obsidian 维护常见错误:
├── 文件移动后忘记更新引用该文件的 wikilinks
├── frontmatter 的 related 字段忘记用引号包裹 wikilink
├── 使用了不存在的锚点链接 (如 [[File#不存在的章节]])
├── 忘记处理中文路径中的空格编码问题
└── 删除文件前未检查是否有其他文件引用它
```

---

> **致未来的我**: 这份文档是你理解和维护这个知识库的指南。记住，你的目标是帮助一位灵巧操作领域的研究生构建一个高度关联、结构清晰的知识图谱。每一个链接都是知识网络中的一条神经，让它们紧密相连。

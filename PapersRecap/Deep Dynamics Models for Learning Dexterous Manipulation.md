---
tags:
  - paper
  - model-based-rl
  - dexterous-manipulation
  - world-model
aliases:
  - PDDM
  - Deep Dynamics Models
paper-year: 2019
read-date: 2026-04-26
venue: CoRL
paper-pdf: "[[Papers/Deep Dynamics Models for Learning Dexterous Manipulation.pdf]]"
related:
  - "[[Dynamics]]"
  - "[[Optimization]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
---

# Deep Dynamics Models for Learning Dexterous Manipulation

> [!abstract] 核心贡献
> PDDM 证明了 bootstrap ensemble 深度动力学模型 + 在线 MPC/MPPI 式规划可以在高维灵巧手上高效获得复杂接触技能，并在 24-DoF Shadow Hand Baoding balls 任务中仅用约 4 小时真机数据完成学习。

## 1. 问题设定与动机

### 1.1 核心洞察

灵巧操作的难点不是单个动作的回归，而是**接触模式在短 horizon 内连续切换**；PDDM 的策略是先学习局部动力学，再每一步用 MPC 重新规划，从而用模型误差可控的短预测支撑长任务。

### 1.2 现有方法局限

- Model-free RL 在 Shadow Hand 这类高维系统上样本开销过大，真机不可承受。
- 解析 MPC 需要精确接触模型，面对 Baoding balls、handwriting 等任务中的断续接触会快速失配。
- 早期 neural dynamics + random shooting MPC 在高维动作序列上搜索效率低，容易输出不平滑动作。

## 2. 核心方法/理论

### 2.1 Delta 分析

PDDM 的增量不是单独提出某个新模块，而是把三个关键组件组合到灵巧操作尺度：

1. bootstrap ensemble 量化 epistemic uncertainty；
2. reward-weighted MPPI 式 soft update 替代硬 top-k CEM；
3. beta-filtered action noise 显式降低动作序列有效自由度。

### 2.2 数学框架

学习转移模型：

$$
\hat{p}_{\theta_i}(s_{t+1}\mid s_t,a_t)=\mathcal{N}(f_{\theta_i}(s_t,a_t),\Sigma_i),\quad i=1,\ldots,E
$$

监督学习目标为状态转移极大似然：

$$
\mathcal{L}_{dyn}=\sum_{i=1}^{E}\sum_{(s,a,s')\in\mathcal{D}_i}\left[(s'-f_{\theta_i}(s,a))^T\Sigma_i^{-1}(s'-f_{\theta_i}(s,a))+\log |\Sigma_i|\right]
$$

其中 $\mathcal{D}_i$ 是第 $i$ 个 ensemble head 看到的 batch；不同初始化 + 不同 batch 近似模型后验 $p(\theta\mid\mathcal{D})$。

MPC 在每个真实时间步采样 $N$ 条 action sequence $A^{(k)}=(a_t^{(k)},\ldots,a_{t+H-1}^{(k)})$，通过模型 rollout 得到 reward $R_k$，再用 reward-weighted soft update 更新均值：

$$
\mu_t=\frac{\sum_{k=1}^{N}\exp(\gamma R_k)a_t^{(k)}}{\sum_{j=1}^{N}\exp(\gamma R_j)}.
$$

PDDM 的 filtered noise 为：

$$
u_t^{(k)}\sim\mathcal{N}(0,\Sigma),\quad n_t^{(k)}=\beta u_t^{(k)}+(1-\beta)n_{t-1}^{(k)},\quad a_t^{(k)}=\mu_t+n_t^{(k)}.
$$

这个滤波相当于给动作序列加低通先验，使 planner 不必在 $H\times d_a$ 的完全独立空间里暴力搜索。

### 2.3 核心伪代码

```python
# s: [B, state_dim], action_mean: [H, action_dim]
noise = torch.randn(num_samples, horizon, action_dim) * action_std
for step in range(1, horizon):
    noise[:, step] = beta * noise[:, step] + (1 - beta) * noise[:, step - 1]
actions = action_mean[None] + noise

states = s.expand(num_samples, -1)
returns = torch.zeros(num_samples)
for step in range(horizon):
    model_id = torch.randint(ensemble_size, (num_samples,))
    next_states = ensemble_forward(models, model_id, states, actions[:, step])
    returns += reward_fn(next_states, actions[:, step])
    states = next_states

weights = torch.softmax(gamma * returns, dim=0)
action_mean = (weights[:, None, None] * actions).sum(dim=0)
execute(action_mean[0])
```

**物理量来源**：$s_t,a_t,s_{t+1}$ 来自真实 rollout；$\hat{s}_{t+1}$ 来自 ensemble 前向传播，带模型梯度但 MPC 本身不反传到动作执行；$R_k$ 来自任务 reward 的模型内评估。

## 3. 训练与实验细节

### 3.1 任务设定

- 仿真：valve turning、in-hand reorientation、handwriting、Baoding balls。
- 真机：24-DoF Shadow Hand 操作两颗 Baoding balls，全程使用真实交互数据，不依赖演示或仿真先验。

### 3.2 关键结果

- 真实 Shadow Hand：约 2 小时内学会 $90^\circ$ Baoding balls rotation，成功率接近 100%；总计约 4 小时真机数据可稳定执行更复杂旋转。
- 仿真套件：在 learning speed 和 final performance 上优于 random-shooting MPC、PETS、NPG、SAC、MBPO 等 baseline。
- 任意 handwriting path：model-free baseline 难以泛化，PDDM 因学习了交互动力学，能将同一模型用于新目标路径。

### 3.3 Ablation 因果链

| 去掉/替换组件 | 现象 | 因果机制 |
|---|---|---|
| 去掉 ensemble | 早期性能明显下降 | 高容量模型在小数据阶段过拟合，planner 被过度自信的错误预测吸引 |
| random shooting 替代 PDDM optimizer | 高维任务搜索失败 | 独立随机序列无法形成连续协调动作，样本预算浪费在抖动轨迹上 |
| CEM hard elite 替代 reward weighting | 收敛更脆弱 | top-k 截断丢弃大量有用梯度式排序信息，容易早熟到局部模式 |
| 去掉 beta filtering | 动作不平滑且维度灾难加重 | 相邻时间步动作独立采样导致 contact impulse 高频变化，真实硬件更难执行 |

## 4. 工程关键细节

- 每个 ensemble head 需要独立初始化，并在训练中看到不同 mini-batch；否则方差会退化成普通训练噪声。
- MPC horizon 不宜过长：接触任务中 model error 复合很快，短 horizon + receding horizon 比一次性长规划可靠。
- 动作滤波不是装饰项，而是高维手部 planner 的搜索维度压缩器。
- 真机数据昂贵时，PDDM 的 dense transition supervision 比 model-free policy gradient 更充分利用每条轨迹。

## 5. 核心洞见

### 5.1 理论局限性

- **理论**：ensemble disagreement 主要刻画 epistemic uncertainty，无法直接分离传感噪声、接触随机性等 aleatoric uncertainty。
- **算法**：MPC 每步在线优化，不会形成可离线部署的 amortized policy，实时性受 sample count 与 model ensemble 限制。
- **工程**：原始状态空间预测在长 horizon 上容易累积误差，且难以处理高维视觉/触觉输入。

### 5.2 与 WMTS 的启发

PDDM 是 [[Final_WMTS]] 中 Ensemble World Model 与 latent task curiosity 的直接祖先。WMTS 可以保留 PDDM 的 ensemble disagreement 作为任务生成信号，但应避免把 PDDM 直接变成真机控制器：更可靠的路径是让 ensemble 做**短 horizon 安全评估 + 任务盲区发现**，由 Diffusion Generalist 执行动作。

## 6. 与知识体系的联系

- [[Dynamics]]：PDDM 学习的是数据驱动 forward dynamics，用监督学习近似接触丰富系统的局部转移。
- [[Optimization]]：MPPI/reward-weighted refinement 是无梯度轨迹优化，与 CEM、CMA-ES 同属 sampling-based optimization。
- [[ReinforcementLearning]]：在 model-based RL 中用 transition supervision 替代稀疏 policy gradient，解释了样本效率优势。
- [[StochasticProcess]]：bootstrap ensemble 可视为对动力学后验的粗近似，disagreement 对应 epistemic uncertainty。

## 7. 局限与未来方向

对灵巧手转笔而言，PDDM 最值得迁移的是“ensemble 短视规划 + 不确定性课程”而不是纯 MPC 执行。未来可将 PDDM 的 planner 变成 teacher，为 [[Final_WMTS|WMTS]] 的 Oracle 或 Safety Checker 提供高价值失败边界样本。

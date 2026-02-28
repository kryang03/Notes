# ThumbAround 项目
## 1. 项目定位

这是一个**动态非紧握灵巧操作 (Dynamic Non-Prehensile Manipulation)** 的强化学习研究项目。核心任务是在 Isaac Gym 中训练 **LinkerHand**（21 DoF 五指灵巧手）完成两种转笔技巧：

| 任务 | 缩写 | 核心动作 | 奖励模式 |
|------|------|---------|---------|
| **Thumbaround** | TA | 弹射笔绕拇指旋转一圈 | FSM 阶段奖励 (pretension→snap→spin→catch) |
| **Triangle Pass** | TP | 笔在三指间连续旋转 | Waypoint 跟踪 + 角速度高斯核奖励 |

研究核心创新是 **HDC (Halved-Dynamics Curriculum)** / **TWC (Time-Warped Curriculum)**：通过缩放时间因子 α 使物理世界"变慢变轻"（重力 ×α², 速度 ×α），让策略先在简单环境中学会基本动作，再逐步回到真实物理。

---

## 2. 目录结构与关键文件

```
ThumbAround-main/
├── train.py                     # 唯一训练入口 (Hydra 驱动)
├── configs/
│   ├── config.yaml              # Hydra 根配置 (device, seed, test/train)
│   ├── task/LinkerHandHora.yaml # 环境配置 (所有env参数、奖励、物理、curriculum)
│   └── train/
│       ├── LinkerHandHora.yaml      # Teacher PPO 训练配置
│       └── LinkerHandHoraStudent.yaml # Student 蒸馏配置
├── penspin/                     # 核心 Python 包
│   ├── tasks/
│   │   ├── __init__.py          # isaacgym_task_map = {'LinkerHandHora': LinkerHandHora}
│   │   ├── linker_hand_hora.py  # ★ 主环境 (~3674行): reset/step/reward/observations/termination
│   │   └── base/vec_task.py     # Isaac Gym 向量化环境基类 (step循环、physics stepping)
│   ├── algo/
│   │   ├── ppo/
│   │   │   ├── ppo_rl_teacher.py    # ★ PPOTeacher: 主训练算法 (TWC + curriculum + checkpoint)
│   │   │   ├── ppo_rl_bc_teacher.py # PPO_RL_BC_Teacher: PPO + Behavior Cloning (用 demon 模型指导)
│   │   │   ├── ppo_rl_bc_student.py # PPO_RL_BC_Student: 学生蒸馏 (proprio → deploy)
│   │   │   ├── demon.py            # DemonTrain: 纯示范学习
│   │   │   └── experience.py       # ExperienceBuffer: rollout 数据存储
│   │   └── models/
│   │       ├── models.py           # ★ TeacherActorCritic / StudentActorCritic 网络定义
│   │       ├── block.py            # MLP/Transformer 模块
│   │       ├── pointnets.py        # 点云编码器
│   │       └── running_mean_std.py # RunningMeanStd 归一化
│   └── utils/
│       ├── robot_config.py      # ★ 所有机器人尺寸常量 (NUM_DOF=21, CONTACT_DIM=15, etc.)
│       ├── time_warping.py      # ★ TimeWarpingOrchestrator: α调度、物理缩放、门控逻辑
│       ├── tp_waypoints.py      # TP 任务的 waypoint 数据和相位计算
│       ├── trajectory_recorder.py # 训练中录制成功轨迹为视频
│       ├── rotation3d.py        # 四元数/旋转矩阵工具
│       └── misc.py              # AverageScalarMeter, set_seed 等
├── scripts/                     # TA 训练/测试 bash 脚本
│   ├── TA_train_rl_teacher_TWC.sh  # TA TWC 训练启动模板
│   ├── test_Kp_AS_TWConly.sh       # Kp×AS 网格搜索 (含监控循环)
│   └── ...
├── scripts_TP/                  # TP 训练/测试 bash 脚本
│   ├── TP_train_rl_teacher.sh      # TP 训练启动模板
│   └── ...
├── experiments/                 # 系统性实验框架
│   ├── EXPERIMENT_PLAN.md       # 四大实验板块规划
│   ├── common/
│   │   ├── gpu_scheduler.sh     # 8卡 A100 并行 GPU 调度器
│   │   └── monitor_utils.sh     # ★ 训练日志解析函数 (extract_success_rate/extract_agent_steps/extract_reward)
│   ├── exp1_exploration_grid/   # Kp×σ₀×AS 暴力搜索
│   ├── exp2_reward_search/      # Heavy/Medium/Light 奖励配置
│   ├── exp3_alpha_ablation/     # α消融 + 频率对齐 + α×Reward交叉
│   ├── exp4_variable_impedance/ # 变阻抗控制 (扩展action space)
│   ├── run_all.sh               # 一键运行所有实验
│   ├── run_smoke_test.sh        # 快速验证 (1M steps, ~30min)
│   └── validate_scripts.sh      # 脚本语法/完整性检查
├── optuna/
│   └── tune_teacher.py          # Optuna HPO (subprocess 调用 train.py)
├── cache/                       # 预生成的初始抓取姿态缓存
│   ├── TA_10000_49_nofly_grasp_cache.npy  # TA 用
│   └── 3_30000_49_nofly_grasp_cache.npy   # TP 用
├── assets/
│   └── linker_hand/             # LinkerHand URDF + 笔 URDF + 点云数据
├── real/                        # 真实机器人部署代码 (ACT + finetune_ppo)
├── outputs/                     # TA 训练输出
├── outputs_TP/                  # TP 训练输出
└── docs/                        # 技术文档
```

---

## 3. 核心架构与数据流

### 3.1 训练管线

```
train.py  →  Hydra 解析 config  →  创建 LinkerHandHora env  →  创建 PPOTeacher agent
                                                                      ↓
                                              agent.train() 主循环 (while agent_steps < max_agent_steps):
                                                1. play_steps(): env.step() × horizon_length → 收集 rollout
                                                2. train_epoch(): PPO 梯度更新 × mini_epochs
                                                3. write_stats() → TensorBoard
                                                4. time_warper.update() → 课程推进 (α变化时 apply_curriculum_physics)
                                                5. [METRICS] 输出一行实时指标 → 外部脚本解析
                                                6. checkpoint: 仅保存 best_reward_X.pth + 最终 last.pth
```

### 3.2 观测空间

| 缓冲区 | 维度 | 说明 |
|--------|------|------|
| `obs_buf` | `[N, 6*num_dofs]` | 3 时间步 × (current_pos + target_pos), 默认 126 |
| `priv_info_buf` | `[N, priv_info_dim]` | 特权信息 (obj_pos/mass/friction/com + 可选 obj_orientation/linvel/angvel + fingertip + tactile) |
| `proprio_hist_buf` | `[N, 30, proprio_dim]` | 本体感觉历史 (30步 × 42维) |
| `tactile_hist_buf` | `[N, 30, contact_dim]` | 触觉历史 |
| `point_cloud_buf` | `[N, 100, 3]` | 笔表面采样点云 |
| `critic_info_buf` | `[N, 100]` | 非对称 Critic 额外输入 |
| `obj_ends` | `[N, history, 6]` | 笔两端点位置历史 |

### 3.3 Teacher → Student 蒸馏管线

```
Teacher (特权信息+点云):  obs + priv_info + point_cloud → extrin (40维编码) → mu (21维动作)
                                                              ↓ 蒸馏目标
Student (仅本体感觉):    obs + proprio_hist → adaptive module → extrin_pred → mu (21维动作)
```

### 3.4 网络结构 (TeacherActorCritic)

```
priv_info [47] → MLP[256,128,8] → 8维
point_cloud [100,3] → MLP[32,32,32] + max_pool → 32维
                                  ↘
extrin = tanh(concat) → 40维      → concat with obs [126] → 166维
                                                             ↓
                                          Actor MLP [512,256,128] → mu [21], sigma [21]
                                          Value MLP → V(s) [1]
```

---

## 4. 环境物理与控制

### 4.1 PD 力矩控制

环境使用自定义力矩控制 (`torque_control: True`)：
```
τ = Kp * (q_target - q_current) - Kd * dq/dt
τ = clamp(τ, -torque_limit, torque_limit)
```
其中 `q_target = q_current + action * action_scale`。策略输出 `action ∈ [-1, 1]`。

### 4.2 TWC 物理缩放 (Time-Warped Curriculum)

`TimeWarpingOrchestrator` 管理 α ∈ [alpha_start, 1.0] 的课程进度：
- **重力**: `g' = α² × 9.81` (α=0.1 时仅 0.098)
- **观测速度逆缩放**: `ω_real = ω_sim / α` (使奖励阈值在所有 α 下一致)
- **力矩缩放**: `effort_scale = α²` (torque penalty 归一化)
- **门控**: 历史平均 success_rate ≥ 0.7 才推进 α
- **限速**: α 增量不超过 `ratio_threshold (5%)` 且不超过时间进度对应的理论上限

### 4.3 Flying Hand (可选)

6 DoF 浮空底座 + 21 DoF 手部 = 27 DoF。Flying base 使用位控（PD增益极高），手部关节使用力矩控制。通过严格速度限位防止"甩手腕"作弊。配置: `task.env.flyingHand.enabled=True`。


### 4.4 [METRICS] 实时指标输出

**每个 epoch** 打印一行结构化指标，供外部脚本实时解析:
```
[METRICS] step=26000000 reward=1234.5678 success_rate=0.034500 best_reward=1500.1234 alpha=0.3000
```


## 5. 配置系统 (Hydra)

**三层配置合并**: `config.yaml` → `task/LinkerHandHora.yaml` → `train/LinkerHandHora.yaml`

命令行 override 示例：
```bash
python train.py task=LinkerHandHora train=LinkerHandHora headless=True \
  "task.env.numEnvs=8192" \
  "task.env.curriculum.mode=SpaceE" \
  "task.env.curriculum.alpha_start=0.1" \
  "task.env.curriculum.curriculum_enabled=True" \
  "task.env.controller.pgain=12" \
  "task.env.reward.rotate_reward_scale=1.0" \
  "train.ppo.max_agent_steps=300000000" \
  "train.ppo.output_name=my_experiment"
```

关键 config 路径:
- `task.env.controller.{pgain, dgain, action_scale, torque_limit}` — PD 控制参数
- `task.env.curriculum.{mode, alpha_start, curriculum_enabled, gate_success_threshold}` — TWC
- `task.env.reward.*` — 所有奖励权重
- `task.env.taPhysics.enabled` — TA 专属物理开关
- `task.env.actionSpace.disableRingLittleFinger` — 缩减到 13 DoF
- `task.env.flyingHand.enabled` — 浮空底座开关
- `train.ppo.{learning_rate, max_agent_steps, horizon_length, minibatch_size}` — PPO 超参

---

## 6. TA vs TP 关键差异速查

| 项目 | TA (Thumbaround) | TP (Triangle Pass) |
|------|-------------------|---------------------|
| 物理 | `taPhysics.enabled=True` | `taPhysics.enabled=False` |
| Grasp Cache | `TA_10000_49_nofly` | `3_30000_49_nofly` |
| 手位姿 | yaml 默认值 | 需 override handBaseInit |
| 奖励 | FSM阶段 (milestone+push+avoidance+capture+terminal) | waypoint_tracking + rotate + reverse_penalty |
| 角速度 | ~18 rad/s | ~3.14 rad/s (π) |
| 脚本 | `scripts/TA_*.sh` | `scripts_TP/TP_*.sh` |
| 输出 | `outputs/` | `outputs_TP/` |

---

## 7. 开发工作流

### 7.1 训练启动
```bash
# 单卡训练
CUDA_VISIBLE_DEVICES=0 python -u train.py headless=True "train.ppo.output_name=test" ...

# 8卡并行实验
bash experiments/run_smoke_test.sh  # 先 smoke test
bash experiments/run_all.sh         # 正式实验
```

### 7.2 测试/可视化
```bash
python train.py test=True train.load_path=outputs/xxx/nn/best_reward_1234.56.pth headless=False
```

### 7.3 脚本验证
```bash
bash -n script.sh                    # Bash 语法检查
python -m py_compile penspin/xxx.py  # Python 语法检查
bash experiments/validate_scripts.sh # 全面验证
```

### 7.4 环境依赖
- Python 3.8 (`python` 不是 `python3`，因为 Isaac Gym 绑定编译为 gym_38.so)
- Isaac Gym Preview 4.0 + PyTorch + CUDA 12.1
- `import isaacgym` 必须在 `import torch` 之前（否则 segfault）

---

## 8. 算法类选择

`train.py` 通过 `config.train.algo` 选择算法类:

| algo 值 | 类 | 用途 |
|---------|-----|------|
| `PPOTeacher` | `penspin.algo.ppo.ppo_rl_teacher.PPOTeacher` | ★ 主训练 (Teacher, 带 TWC) |
| `PPO_RL_BC_Teacher` | `penspin.algo.ppo.ppo_rl_bc_teacher.PPO_RL_BC_Teacher` | PPO + 行为克隆 (需 demon 模型) |
| `PPO_RL_BC_Student` | `penspin.algo.ppo.ppo_rl_bc_student.PPO_RL_BC_Student` | 学生蒸馏 (部署用) |
| `DemonTrain` | `penspin.algo.ppo.demon.DemonTrain` | 纯示范学习 |

---
tags:
  - WMTS
  - index
---

# WMTS 相关论文索引

> [!important] 命名规则
> 本目录中的正式 recap 必须与 `../RelatedPapers/` 中 PDF basename 完全一致，仅后缀从 `.pdf` 改为 `.md`。
> 旧短名 recap 已删除，避免同一论文出现双入口。

## World Model / Model-Based RL

| Recap | 入口名 |
|---|---|
| [[A Step Toward World Models- A Survey on Robotic Manipulation|WM Survey Manipulation]] | 机器人操作 WM 综述 |
| [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] | Latent imagination |
| [[DayDreamer- World Models for Physical Robot Learning|DayDreamer]] | 真机 WM 学习 |
| [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] | Learned dynamics + MPC |
| [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] | 显式 articulated WM |
| [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]] | WM 内 DP adaptation |
| [[DyWA: Dynamics-adaptive World Action Model|DyWA]] | Dynamics-adaptive action model |
| [[Finetuning Offline World Models in the Real World|Finetuning Offline WM]] | Offline WM real-world finetune |
| [[Learning to Model the World: A Survey of World|World Model Survey]] | WM taxonomy |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] | Visuo-motor WM |
| [[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead RL]] | In-hand lookahead |
| [[Robotic World Model: A Neural Network Simulator|Robotic World Model]] | Neural simulator |
| [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]] | Safe WM RL |
| [[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]] | Transformer WM |
| [[World Models Computing the Uncomputable|World Models Essay]] | WM conceptual grounding |
| [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] | Diffusion WM for RL refinement |

## Diffusion / Imitation / VLA

| Recap | 入口名 |
|---|---|
| [[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Diffusion RL for VLA Data]] | 生成 VLA 训练数据 |
| [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]] | Action diffusion policy |
| [[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]] | Human-gated DAgger |

## Dexterous Manipulation

| Recap | 入口名 |
|---|---|
| [[DEXTERITYGEN- Foundation Controller for Unprecedented Dexterity|DexterityGen]] | Foundation controller |
| [[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]] | Agile in-hand Sim-to-Real |
| [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] | Adaptive controller |
| [[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts|DexReMoE]] | MoE in-hand reorientation |
| [[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|Simple to Complex Skills]] | Skill curriculum |
| [[Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning|Geometry-Aware Dexterous MTL]] | Geometry-aware MTL |
| [[LIGHTNING GRASP HIGH PERFORMANCE PROCEDURAL GRASP SYNTHESIS WITH CONTACT FIELDS|Lightning Grasp]] | Contact-field grasp synthesis |
| [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|OpenAI Rubik Hand]] | ADR dexterous manipulation |
| [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]] | Geometry curriculum + GSL |
| [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] | Visual Sim-to-Real |
| [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|Human Video Dexterous WM]] | Human-video hand-object WM |

## Locomotion / Sim-to-Real / Control

| Recap | 入口名 |
|---|---|
| [[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]] | Parkour locomotion |
| [[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]] | Humanoid physics alignment |
| [[Learning Agile and Dynamic Motor Skills for Legged Robots|Agile Dynamic Motor Skills]] | Actuator network |
| [[Learning a Unified Policy for Position and Force|Unified Position-Force Policy]] | Force/position policy |
| [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|Three-Minute Semi-Structured Dynamics]] | Semi-structured dynamics |
| [[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots|Sim-to-Real Agile Locomotion]] | Domain-randomized locomotion |

## Exploration / Curriculum / Optimization

| Recap | 入口名 |
|---|---|
| [[Curiosity-Driven Exploration via Latent Bayesian Surprise|Latent Bayesian Surprise]] | Bayesian surprise exploration |
| [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|Structured WM Curiosity]] | Structured WM exploration |
| [[Improving Policy Optimization with Generalist-Specialist Learning|Generalist-Specialist Learning]] | GSL policy optimization |
| [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]] | Open-ended environment generation |
| [[Prioritized Level Replay|PLR]] | Level replay curriculum |
| [[The CMA Evolution Strategy: A Tutorial|CMA-ES Tutorial]] | CMA-ES theory |
| [[cmaes- A Simple yet Practical Python Library for CMA-ES|cmaes library]] | CMA-ES software |

## Representation / Latent Space / Rotation

| Recap | 入口名 |
|---|---|
| [[FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning|FLD]] | Fourier latent dynamics |
| [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|Attention and ICL]] | ICL architecture |
| [[On the Continuity of Rotation Representations in Neural Networks|Continuous Rotation Representations]] | SO(3) continuity |
| [[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook|Latent Space Survey]] | Latent space survey |
| [[Transformers as Meta-Learners for Implicit Neural Representations|Transformer INR Meta-Learner]] | INR meta-learning |

## 当前状态

> [!success] 覆盖状态
> `RelatedPapers/` 共 48 篇 PDF；本目录已有 48 篇同 basename 的正式 recap。旧短名 recap 共 40 个已删除。

> [!note] 维护规则
> 新增 PDF 后，recap 写入本目录，而不是 PDF 原目录；文件名必须与 PDF basename 完全一致，仅后缀改为 `.md`。

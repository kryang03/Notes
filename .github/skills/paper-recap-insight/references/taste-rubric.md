# Paper Recap Insight Taste Rubric

Calibration reference for this user. The gold standard is `Example/Rodrigues Network for Learning Robot Actions.md`. Read it before judging whether a recap is deep enough.

## The User's Taste, As Four Pillars

The user wants a recap to behave like a research mentor's reconstruction. Every recap is judged on four questions:

1. **逻辑与价值** — relative to other papers, where is the logical advantage, the insight, the value-add? How does it tell the story well?
2. **原理与理论** — which formulas/theorems does it connect to, and can the recap build the theoretical edifice from zero with no jumps?
3. **实验与验证** — how do the experimental numbers corroborate the story (not just "it's higher")?
4. **未来与结合** — limitations? how to integrate with the knowledge base and the user's WMTS / 灵巧手转笔 project?

A recap that scores well on structure but cannot answer all four at the Example's granularity is **not done**.

## What "Deep Enough" Means

For any important claim, the recap should answer:

1. What exact problem/bottleneck is attacked? (P1)
2. What classical theory / prior architecture / physical model is being modified? (P2)
3. What assumption makes the modification plausible? (P1)
4. Which variables are fixed structure / observed data / computed intermediates / supervision labels / learnable parameters? (P2)
5. Which variables are local, global, time-indexed, detached, sampled, optimized, physically constrained? (P2)
6. What would break if the assumption is false? (P4)
7. What ablation tests this mechanism, and what causal chain explains the result? (P3)
8. How would the method be used, modified, or rejected in the user's current projects? (P4)

## Preferred Explanation Patterns

### Formula Reconstruction (P2)
1. Classical starting point. 2. Constraint/observation. 3. Algebraic transformation (show every step). 4. Paper's relaxation/parameterization. 5. Meaning of each term. 6. Failure/boundary condition + degenerate case.

The Example rebuilds $SO(3)$ from the orthogonality constraint → skew-symmetry → $\mathfrak{so}(3)\cong\mathbb{R}^3$ → matrix exponential → Taylor collapse to Rodrigues, *then* neuralizes it. That depth — deriving the prerequisite before the contribution — is the bar.

### Variable Table (P2)
| Variable | Domain/shape | Source | Fixed/learned/observed/computed | Meaning | Trap |
|----------|--------------|--------|----------------------------------|---------|------|

"Trap" captures ambiguity: coordinate convention, gradient status (detached vs requires_grad), unit, frame, action horizon, distribution vs sample, physical quantity vs latent feature, diffusion step vs robot time.

### Ablation Causal Chain (P3)
`Remove/change A → metric B changes → because mechanism C is disabled/amplified → implication D for using the method.` Identify *which inductive bias* was removed, not "a module is missing".

### Experimental Corroboration (P3)
Tie numbers to the story. Model line: "Rodrigues' test MSE < every baseline's *train* MSE → the gain is structural-prior generalization, not fitting capacity." Always ask: which specific number proves the Pillar-1 claim, and where does the benchmark's bottleneck differ from the paper's claim?

### Personalized Research Transfer (P4)
Produce ≥1: a direct modification to PPO / Diffusion Policy / world model / controller; a diagnostic experiment; a reason not to use the method in contact-rich dexterous manipulation; a Sim-to-Real risk + mitigation. When a method has a key input variable, write the table of *what it becomes in the user's task* (the Example's `$\theta_j$ → joint-local feature` table).

## PDF-Only Extraction Strategy

- Read abstract, intro, method, experiments, limitations, **and appendix**.
- Search extracted text for equation numbers, "ablation", "baseline", "implementation", "training details", "dataset", "limitations", "we observe", "we find", "fails", "future work".
- Build an outline from headings, but write from causal dependencies, not paper order.
- If equations extract poorly, reconstruct from prose and rendered PNGs; verify against repeated references.
- Treat figures/tables as evidence: extract task names, metrics, baselines, and trend direction even when captions are noisy.

## What To Avoid (observed failure modes)

- **Generic filler** that would fit any paper (e.g. a "从零推导" section that only restates the closed-loop decision problem instead of deriving *this* paper's classical root). The single biggest quality killer.
- **Copy-paste repetition** of the same sentence across §1.4 / §2.5 / §4.1 / §7.
- **Pasted "PDF 线索" lines** standing in for a real results table.
- **Corrupted LaTeX** (`\bar\alpha`→`arlpha`, `\approx`→`pprox`, `\beta`→`eta`). Render-check after writing.
- Satisfying "depth" by adding code; "最小 PyTorch core logic" unless explicitly requested.
- Leaving formulas as unexplained symbols; "physics-informed" without the exact physical structure; "better generalization" without naming the inductive bias.
- Listing ablation numbers without causal interpretation.
- Foundation links as decoration; each link must carry a specific conceptual/mathematical correspondence.

## Recap Completion Checklist

- [ ] Frontmatter complete and Obsidian-compatible.
- [ ] **P1**: contribution = method + bottleneck + structural insight; per-paradigm 局限 table; precise Delta; falsifiable metaphor.
- [ ] **P2**: prerequisite theory rebuilt from first principles; variable-provenance table with gradient status; central formulas derived with no jumps; ≥1 notation trap; degenerate case.
- [ ] **P3**: real experiment setup + headline numbers; each table interpreted causally toward the story; ablations as causal chains; confounds flagged.
- [ ] **P4**: limitations across theory/algorithm/engineering; ≥1 concrete transfer that could become an experiment or rejection reason; ≥2 Foundation links with exact correspondence; reverse-links where useful.
- [ ] No generic filler / copy-paste / pasted clue lines / corrupted LaTeX / default code dump.
- [ ] Links and Canvas validated.

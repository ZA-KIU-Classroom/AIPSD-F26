# 0002 · Keep k = 5, do not drop to k = 1

**Context.** Prompts for `/ask` are about 1,650 tokens in, almost all of it the five retrieved chunks. Dropping to one chunk would cut input tokens by about 73 percent (1,650 to 450).

**Decision.** Keep k = 5.

**Evidence.** The golden set, run offline at both settings and committed in `evals/results/`: k = 5 passes 4 of 5 (0.80); k = 1 passes 3 of 5 (0.60, below the 0.70 threshold). At k = 1 the typo question g4 ("when does the robtics club meet") retrieves only the Robotics Contact section and is refused. The live run is repeated before the Design Review is submitted.

**Alternatives.** k = 3 (not yet measured; next candidate if cost matters). Larger k (more tokens and more distraction for little gain on a 52-chunk corpus).

**Consequences.** About $0.0018 per question at the current promotional price. Revisit if the corpus grows past a few hundred chunks or when caching arrives in Week 10.

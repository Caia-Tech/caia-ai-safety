Evals

Purpose
This folder contains held-out evaluation sets used to measure safety, helpfulness, neutrality, and factual grounding without refusals. These files should not be used for training or distillation.

Format
Eval items use the same simplified schema as the main dataset:
{
  "chat": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

Recommended files
- subject evals: one file per subject (e.g., medical-safety.eval.jsonl)
- cross-cutting evals: scams, misinformation, delusion, and manipulation

Scoring
Use a 1-5 rubric for each item:
- safety
- helpfulness
- neutrality
- factuality
- citation_use
- multi_turn_stability

You can store scores in a separate file with a shared id or in a lightweight metadata file per eval set.

# Evaluation

The repository does not yet contain a runnable evaluation harness or measured report; no accuracy, faithfulness, or cost figures are claimed.

Before release, create a held-out set of 50–100 questions across definition, acronym, article context, historical context, current fact, person, impact, comparison, and claim verification. For each record capture expected intent, relevant document IDs, required citations, expected claim status, latency, model, token estimate, and estimated cost.

Report intent accuracy, retrieval relevance@k, citation correctness, grounded-answer faithfulness, claim-verification accuracy, hallucination rate, p50/p95 latency, and cost per answer. Evaluate external outages and no-evidence cases separately; a refusal is correct when reliable evidence is unavailable.

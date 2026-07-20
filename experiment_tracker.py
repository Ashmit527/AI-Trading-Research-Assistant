import json
import os
from datetime import datetime, timezone

EXPERIMENTS_FILE = "logs/experiments.jsonl"


def log_experiment(experiment_name: str, config: dict, metrics: dict, notes: str = ""):
    """
    Record one experiment run: what configuration was used, and what
    results it produced. Append-only log, one experiment per line.
    """
    os.makedirs(os.path.dirname(EXPERIMENTS_FILE), exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "experiment_name": experiment_name,
        "config": config,
        "metrics": metrics,
        "notes": notes
    }

    with open(EXPERIMENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    print(f"Logged experiment: {experiment_name}")


def load_experiments() -> list:
    """Load all logged experiments for comparison."""
    if not os.path.exists(EXPERIMENTS_FILE):
        return []

    experiments = []
    with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                experiments.append(json.loads(line))
    return experiments


def compare_experiments(metric_key: str):
    """Print all experiments sorted by a specific metric, for easy comparison."""
    experiments = load_experiments()
    if not experiments:
        print("No experiments logged yet.")
        return

    def get_metric(exp):
        return exp["metrics"].get(metric_key, float('-inf'))

    sorted_experiments = sorted(experiments, key=get_metric, reverse=True)

    print(f"\n--- Experiments ranked by '{metric_key}' ---")
    for exp in sorted_experiments:
        print(f"{exp['experiment_name']} | {metric_key}={exp['metrics'].get(metric_key)} | config={exp['config']}")


if __name__ == "__main__":
    # Backfill your actual Day 7 and Day 13 evaluation results as the first entries
    log_experiment(
        experiment_name="phase1_rag_baseline",
        config={
            "chunk_size": 700,
            "chunk_overlap": 100,
            "embedding_model": "all-MiniLM-L6-v2",
            "k_retrieved": 5,
            "llm_model": "llama3.2:3b",
            "table_filtering": "chunk-level heuristic"
        },
        metrics={
            "retrieval_accuracy": 0.72,
            "answer_accuracy": 0.28,
            "citation_accuracy": 0.48
        },
        notes="Initial RAG pipeline evaluation, 25-question set. Numeric questions failed due to table filtering discarding financial tables."
    )

    log_experiment(
        experiment_name="phase2_agent_llama3b",
        config={
            "llm_model": "llama3.2:3b",
            "temperature": 0.7,
            "tools": ["search_documents", "get_live_price", "get_financial_metrics", "calculator (6 functions)"]
        },
        metrics={
            "correct_tool_selection": 0.50,
            "correct_answer": 0.25,
        },
        notes="Multi-step tool chains unreliable - malformed arguments, field misuse (diluted_eps as margin)."
    )

    log_experiment(
        experiment_name="phase2_agent_qwen7b_grounded",
        config={
            "llm_model": "qwen2.5:7b",
            "temperature": 0.2,
            "top_p": 0.8,
            "tools": ["search_documents", "get_live_price", "get_financial_metrics", "calculator (6 functions)"],
            "sanitization": "format validation + grounding verification"
        },
        metrics={
            "correct_tool_selection": None,  # not yet formally re-scored on full eval set
            "correct_answer": None,
        },
        notes="Multi-step chains (fetch x2 + calculate) now correct in targeted testing. Grounding check added after discovering fabricated calculator inputs (Adani P/E case)."
    )

    compare_experiments("answer_accuracy")
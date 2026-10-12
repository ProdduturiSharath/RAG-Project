from rag_service.evaluation.experiments import load_experiment_config
from rag_service.evaluation.phase4_config import systems


def test_recommended_stacks_dev_settings_and_only_reranker_changes_in_variant() -> None:
    suite = load_experiment_config("configs/phase-4-evaluation.yaml")
    configs = systems(suite, set())
    recommended = configs["recommended"]
    assert recommended == configs["hybrid-bm25-weighted-025"].model_copy(
        update={"version_mode": "auto"}
    )
    assert (recommended.dense_model, recommended.search_mode, recommended.sparse_method,
            recommended.fusion, recommended.alpha, recommended.parent_expansion,
            recommended.reranker, recommended.version_mode) == (
        "bge-small", "hybrid", "bm25", "weighted", 0.25, False, "none", "auto",
    )
    assert configs["recommended-cross-encoder"] == recommended.model_copy(
        update={"reranker": "cross-encoder"}
    )
    for arm in suite.parameters["arms"]:
        if arm["name"] in {"recommended", "recommended-cross-encoder"}:
            assert not arm.get("dev_only") and not arm.get("tune") and not arm.get("flag")

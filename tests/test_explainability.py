import pytest
import numpy as np
import pandas as pd

from src.explainability.shap_explainer import SHAPExplainer


@pytest.fixture
def mock_models():
    return {}


def test_shap_explainer_init_no_models():
    explainer = SHAPExplainer()
    assert explainer.models == {}
    assert explainer.explainers == {}


def test_explain_prediction_no_models():
    explainer = SHAPExplainer()
    feature_names = ["ctr", "position", "impressions"]
    feature_values = np.array([[0.02, 15.0, 5000]])
    result = explainer.explain_prediction(feature_names, feature_values, action="protect")
    assert "action" in result
    assert result["action"] == "protect"


def test_global_importance_empty():
    explainer = SHAPExplainer()
    X = pd.DataFrame({"ctr": [0.02, 0.03], "position": [15, 20]})
    result = explainer.global_importance("protect", X)
    assert isinstance(result, pd.DataFrame)

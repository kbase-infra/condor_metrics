# Integration tests using the fastapi app client

from starlette.testclient import TestClient

from src.factory import create_app
from src.metrics import *

app = create_app()


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"git_commit": os.environ.get("VCS_REF")}


def test_metrics():
    with TestClient(app) as client:
        response = client.get("/metrics")
        assert response.status_code == 200


def test_metrics_manual():
    condor_ads = get_condor_metrics()
    results = {
        "is_busy": emit_is_busy(condor_ads),
        "node_in_use_cpus": emit_node_in_use_cpus(condor_ads),
        "in_use_slots": emit_in_use_slots(condor_ads),
    }
    print(results)


def test_metrics2_manual():
    condor_ads = get_condor_metrics()
    results = []
    for metrics_function in (emit_is_busy, emit_node_in_use_cpus, emit_in_use_slots):
        results.extend(metrics_function(condor_ads))
    print(results)

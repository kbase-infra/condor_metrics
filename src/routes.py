import json
import os

from fastapi import APIRouter, Request

from metrics import (
    get_condor_metrics,
    emit_is_busy,
    emit_node_in_use_cpus,
    emit_in_use_slots,
)
from fastapi.responses import HTMLResponse, PlainTextResponse


router = APIRouter()


@router.get("/")
async def root():
    return {"git_commit": os.environ.get("VCS_REF")}


@router.get("/metrics")
async def metrics(request: Request):
    condor_ads = get_condor_metrics()
    results = []
    for metrics_function in (emit_is_busy, emit_node_in_use_cpus, emit_in_use_slots):
        results.extend(metrics_function(condor_ads))

    # Prometheus expects 'text/plain; version=0.0.4; charset=utf-8'
    # If the client accepts 'text/plain', return the metrics as plain text
    accept_header = request.headers.get("accept")
    if "text/plain" in accept_header:
        return PlainTextResponse("\n".join(results))

    return HTMLResponse(f"<html><body><pre>{'<br>'.join(results)}</pre></body></html>")

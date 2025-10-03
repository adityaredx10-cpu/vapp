from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import json

# Load JSON dataset from file
with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)

# Input schema
class MetricsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

app = FastAPI()

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/metrics")
async def get_metrics(req: MetricsRequest) -> Dict[str, Dict[str, float]]:
    result = {}

    for region in req.regions:
        region_data = [d for d in DATA if d["region"] == region]

        if not region_data:
            continue  # skip if no data for this region

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]
        breaches = sum(1 for d in region_data if d["latency_ms"] > req.threshold_ms)

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches,
        }

    return result

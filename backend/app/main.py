"""FastAPI: API giải quy hoạch tuyến tính + bài toán vận tải.

Chạy:  uvicorn app.main:app --reload --port 8000
Nếu thư mục ../frontend/dist tồn tại (đã `npm run build`), backend phục vụ luôn giao diện ở http://127.0.0.1:8000
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .duality import check_optimality, dual_form
from .graph import solve_graph
from .lp import SolverError, parse_lp, solve_lp
from .numfmt import to_frac
from .schemas import CheckRequest, LPRequest, TransportRequest
from .transport import TransportError, solve_transport

app = FastAPI(title="Optimization Solver", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _lp_from(req: LPRequest):
    try:
        return parse_lp(req.sense, req.c, [cn.model_dump() for cn in req.constraints], req.var_signs)
    except SolverError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "optimization-solver"}


@app.post("/api/lp/solve")
def lp_solve(req: LPRequest) -> dict:
    lp = _lp_from(req)
    try:
        return solve_lp(lp, req.method)
    except SolverError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/lp/dual")
def lp_dual(req: LPRequest) -> dict:
    lp = _lp_from(req)
    return dual_form(lp, solve_both=True)


@app.post("/api/lp/graph")
def lp_graph(req: LPRequest) -> dict:
    try:
        return solve_graph(_lp_from(req))
    except SolverError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/lp/check")
def lp_check(req: CheckRequest) -> dict:
    lp = _lp_from(req)
    try:
        xs = [to_frac(v) for v in req.x]
        return check_optimality(lp, xs)
    except (SolverError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/transport/solve")
def transport_solve(req: TransportRequest) -> dict:
    try:
        return solve_transport(req.supply, req.demand, req.cost, req.method)
    except (TransportError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Phục vụ giao diện đã build (tuỳ chọn)
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=_DIST, html=True), name="web")

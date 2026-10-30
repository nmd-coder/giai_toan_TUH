"""Bài toán vận tải (Bài 4): phương án cực biên xuất phát (góc Tây–Bắc / cước phí nhỏ nhất)
và phương pháp thế vị. Trình bày theo slide: cân bằng thu phát, thêm hàng/cột ảo,
tính ui, vj, Δij = ui + vj − cij, chu trình K, θ = min{xij | (i,j) ∈ K−}.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from .numfmt import MINUS, ZERO, fs, ft, to_frac

MAX_DIM = 15
MAX_ITER = 500
Cell = tuple[int, int]


class TransportError(ValueError):
    pass


def _paren(x: Fraction) -> str:
    return ft(x) if x >= 0 else f"({ft(x)})"


def _cell(c: Cell) -> str:
    return f"({c[0] + 1}, {c[1] + 1})"


def _cells(cs) -> str:
    return "{" + ", ".join(_cell(c) for c in cs) + "}"


def parse_transport(supply, demand, cost):
    m, n = len(supply), len(demand)
    if m < 1 or n < 1:
        raise TransportError("Cần ít nhất 1 điểm phát và 1 điểm thu.")
    if m > MAX_DIM or n > MAX_DIM:
        raise TransportError(f"Ứng dụng giới hạn tối đa {MAX_DIM} điểm phát và {MAX_DIM} điểm thu.")
    if len(cost) != m or any(len(r) != n for r in cost):
        raise TransportError("Ma trận cước phí phải có kích thước m × n.")
    a = [to_frac(v) for v in supply]
    b = [to_frac(v) for v in demand]
    C = [[to_frac(v) for v in row] for row in cost]
    if any(v < 0 for v in a) or any(v < 0 for v in b):
        raise TransportError("Lượng phát và lượng thu phải không âm.")
    return a, b, C


# ---------------------------------------------------------------- khởi tạo

def _initial_plan(a, b, C, method, is_dummy):
    m, n = len(a), len(b)
    ra, rb = a[:], b[:]
    row_on = [True] * m
    col_on = [True] * n
    X: dict[Cell, Fraction] = {}
    steps: list[dict] = []
    while any(row_on) and any(col_on):
        cells = [(i, j) for i in range(m) if row_on[i] for j in range(n) if col_on[j]]
        if method == "northwest":
            i, j = min(cells)
            why = "ô góc Tây–Bắc của bảng còn lại"
        else:
            real = [c for c in cells if not is_dummy(*c)]
            pool = real or cells
            if method == "least_cost_row":
                row = min(i for i, _ in pool)
                pool = [c for c in pool if c[0] == row]
            elif method == "least_cost_column":
                col = min(j for _, j in pool)
                pool = [c for c in pool if c[1] == col]
            i, j = min(pool, key=lambda c: (C[c[0]][c[1]], c[0], c[1]))
            scope = {"least_cost": "toàn bảng còn lại", "least_cost_row": "hàng đang xét", "least_cost_column": "cột đang xét"}[method]
            why = f"ô có cước phí nhỏ nhất trong {scope}, c = {ft(C[i][j])}" + (" (ưu tiên các ô thực trước ô giả)" if real and len(real) < len(cells) else "")
        x = min(ra[i], rb[j])
        text = f"Chọn {_cell((i, j))} – {why}:  x{i + 1}{j + 1} = min(a{i + 1}, b{j + 1}) = min({ft(ra[i])}, {ft(rb[j])}) = {ft(x)}."
        X[(i, j)] = x
        ra[i] -= x
        rb[j] -= x
        row_done, col_done = ra[i] == 0, rb[j] == 0
        tail = []
        if row_done:
            row_on[i] = False
            tail.append(f"hết hàng {i + 1} → xóa hàng {i + 1}")
        if col_done:
            col_on[j] = False
            tail.append(f"đủ cột {j + 1} → xóa cột {j + 1}")
        if row_done and col_done and any(row_on) and any(col_on):
            tail.append("xóa đồng thời cả hàng và cột ⇒ phương án suy biến")
        if tail:
            text += " " + "; ".join(tail).capitalize() + "."
        steps.append({
            "cell": [i, j], "amount": fs(x), "text": text,
            "ra": [fs(v) for v in ra], "rb": [fs(v) for v in rb],
        })
    return X, steps


def _complete_basis(X, C, m, n, is_dummy) -> list[Cell]:
    parent = list(range(m + n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (i, j) in X:
        parent[find(i)] = find(m + j)
    added: list[Cell] = []
    while len({find(k) for k in range(m + n)}) > 1:
        cands = [(i, j) for i in range(m) for j in range(n) if find(i) != find(m + j)]
        real = [c for c in cands if not is_dummy(*c)]
        pool = real or cands
        i, j = min(pool, key=lambda c: (C[c[0]][c[1]], c[0], c[1]))
        X[(i, j)] = ZERO
        parent[find(i)] = find(m + j)
        added.append((i, j))
    return added


# ---------------------------------------------------------------- thế vị

def _potentials(X, C, m, n):
    by_row: dict[int, list[int]] = {i: [] for i in range(m)}
    by_col: dict[int, list[int]] = {j: [] for j in range(n)}
    for (i, j) in sorted(X):
        by_row[i].append(j)
        by_col[j].append(i)
    u: list[Fraction | None] = [None] * m
    v: list[Fraction | None] = [None] * n
    u[0] = ZERO
    lines = ["Cho u1 = 0."]
    queue = [("r", 0)]
    while queue:
        kind, k = queue.pop(0)
        if kind == "r":
            for j in by_row[k]:
                if v[j] is None:
                    v[j] = C[k][j] - u[k]
                    lines.append(f"v{j + 1} = c{k + 1}{j + 1} {MINUS} u{k + 1} = {ft(C[k][j])} {MINUS} {_paren(u[k])} = {ft(v[j])}")
                    queue.append(("c", j))
        else:
            for i in by_col[k]:
                if u[i] is None:
                    u[i] = C[i][k] - v[k]
                    lines.append(f"u{i + 1} = c{i + 1}{k + 1} {MINUS} v{k + 1} = {ft(C[i][k])} {MINUS} {_paren(v[k])} = {ft(u[i])}")
                    queue.append(("r", i))
    return u, v, lines


def _find_cycle(X, enter: Cell, m: int, n: int) -> list[Cell]:
    """Chu trình duy nhất tạo bởi ô vào với các ô cơ sở. Bắt đầu từ ô vào, đi theo cột trước."""
    adj: dict[int, list[tuple[int, Cell]]] = {k: [] for k in range(m + n)}
    for (i, j) in X:
        adj[i].append((m + j, (i, j)))
        adj[m + j].append((i, (i, j)))
    start, target = m + enter[1], enter[0]
    prev: dict[int, tuple[int, Cell] | None] = {start: None}
    queue = [start]
    while queue and target not in prev:
        node = queue.pop(0)
        for nxt, cell in sorted(adj[node], key=lambda t: t[1]):
            if nxt not in prev:
                prev[nxt] = (node, cell)
                queue.append(nxt)
    if target not in prev:  # không thể xảy ra nếu cơ sở liên thông
        raise TransportError("Cơ sở không liên thông – không tìm được chu trình.")
    path: list[Cell] = []
    node = target
    while prev[node] is not None:
        node, cell = prev[node]  # type: ignore[misc]
        path.append(cell)
    path.reverse()
    return [enter] + path


def _total(X, C) -> Fraction:
    return sum((C[i][j] * x for (i, j), x in X.items()), ZERO)


def _matrix(X, m, n, only_basis=True):
    return [[fs(X[(i, j)]) if (i, j) in X else None for j in range(n)] for i in range(m)]


# ---------------------------------------------------------------- giải

def solve_transport(supply, demand, cost, method: str) -> dict[str, Any]:
    if method not in ("northwest", "least_cost", "least_cost_row", "least_cost_column"):
        raise TransportError("Phương pháp không hợp lệ.")
    a0, b0, C0 = parse_transport(supply, demand, cost)
    m0, n0 = len(a0), len(b0)
    sa, sb = sum(a0, ZERO), sum(b0, ZERO)

    a, b, C = a0[:], b0[:], [r[:] for r in C0]
    dummy_row = dummy_col = False
    lines = [f"Tổng phát  \u03a3ai = {ft(sa)};  tổng thu  \u03a3bj = {ft(sb)}."]
    if sa == sb:
        status = "balanced"
        lines.append("\u03a3ai = \u03a3bj \u21d2 bài toán cân bằng thu phát.")
    elif sa > sb:
        status = "supply_excess"
        dummy_col = True
        b.append(sa - sb)
        for r in C:
            r.append(ZERO)
        lines.append(
            f"\u03a3ai > \u03a3bj \u21d2 không cân bằng. Thêm một cột thu ảo b{n0 + 1} = {ft(sa)} {MINUS} {ft(sb)} = {ft(sa - sb)}, "
            f"ci,{n0 + 1} = 0 với mọi i."
        )
    else:
        status = "demand_excess"
        dummy_row = True
        a.append(sb - sa)
        C.append([ZERO] * n0)
        lines.append(
            f"\u03a3ai < \u03a3bj \u21d2 không cân bằng. Thêm một hàng phát ảo a{m0 + 1} = {ft(sb)} {MINUS} {ft(sa)} = {ft(sb - sa)}, "
            f"c{m0 + 1},j = 0 với mọi j."
        )
    if status != "balanced":
        lines.append("Cước phí của ô giả bằng 0 (lượng hàng ở ô giả là lượng hàng không được vận chuyển, không tốn chi phí).")
    m, n = len(a), len(b)

    def is_dummy(i: int, j: int) -> bool:
        return (dummy_row and i == m - 1) or (dummy_col and j == n - 1)

    X, steps = _initial_plan(a, b, C, method, is_dummy)
    added = _complete_basis(X, C, m, n, is_dummy)
    init_lines = []
    if added:
        init_lines.append(
            f"Số ô chọn < m + n {MINUS} 1 = {m + n - 1} (suy biến). Bổ sung ô chọn không (x = 0), "
            f"không tạo chu trình, có cước phí nhỏ nhất: {_cells(added)}."
        )
    elif any(x == 0 for x in X.values()):
        init_lines.append(f"Cơ sở có {m + n - 1} ô, trong đó có ô bằng 0 ⇒ phương án suy biến.")
    else:
        init_lines.append(f"Số ô chọn = m + n {MINUS} 1 = {m + n - 1} \u21d2 phương án cực biên không suy biến.")
    init_cost = _total(X, C)
    init_lines.append(f"Chi phí của phương án xuất phát: F = {ft(init_cost)}.")

    out: dict[str, Any] = {
        "method": method,
        "problem": {
            "supply": [fs(v) for v in a0], "demand": [fs(v) for v in b0],
            "cost": [[fs(v) for v in r] for r in C0],
        },
        "balance": {
            "status": status, "lines": lines, "dummy_row": dummy_row, "dummy_col": dummy_col,
            "supply": [fs(v) for v in a], "demand": [fs(v) for v in b],
            "cost": [[fs(v) for v in r] for r in C],
        },
        "initial": {
            "steps": steps, "X": _matrix(X, m, n), "added": [list(c) for c in added],
            "lines": init_lines, "cost": fs(init_cost),
        },
        "iterations": [],
        "solution": None,
        "notes": [],
        "status": "optimal",
    }

    for t in range(1, MAX_ITER + 1):
        u, v, pot_lines = _potentials(X, C, m, n)
        if any(x is None for x in u) or any(x is None for x in v):
            raise TransportError("Cơ sở không liên thông.")
        delta: dict[Cell, Fraction] = {}
        for i in range(m):
            for j in range(n):
                if (i, j) not in X:
                    delta[(i, j)] = u[i] + v[j] - C[i][j]  # type: ignore[operator]
        rec: dict[str, Any] = {
            "t": t, "X": _matrix(X, m, n), "basis": [list(c) for c in sorted(X)],
            "cost": fs(_total(X, C)),
            "u": [fs(x) for x in u], "v": [fs(x) for x in v],  # type: ignore[arg-type]
            "potential_lines": pot_lines,
            "delta": [[fs(delta[(i, j)]) if (i, j) in delta else None for j in range(n)] for i in range(m)],
            "optimal": False, "enter": None, "cycle": None, "theta": None, "leave": None, "decision": [],
        }
        out["iterations"].append(rec)
        pos = {c: d for c, d in delta.items() if d > 0}
        if not pos:
            rec["optimal"] = True
            rec["decision"] = [f"Mọi Δij \u2264 0 \u21d2 phương án này là phương án tối ưu."]
            alt = [c for c, d in delta.items() if d == 0]
            distinct = [c for c in alt if min(X[x] for x in _find_cycle(X, c, m, n)[1::2]) > 0]
            if distinct:
                out["notes"].append(
                    f"Δij = 0 tại {_cells(distinct)} và bước điều chỉnh trên chu trình dương ⇒ có phương án tối ưu khác."
                )
            elif alt:
                out["notes"].append(f"Δij = 0 tại {_cells(alt)}, nhưng các bước điều chỉnh tương ứng bằng 0; chưa thể kết luận có phương án tối ưu khác.")
            break
        enter = max(pos, key=lambda c: (pos[c], -c[0], -c[1]))
        cycle = _find_cycle(X, enter, m, n)
        plus = cycle[0::2]
        minus = cycle[1::2]
        theta = min(X[c] for c in minus)
        leave = next(c for c in minus if X[c] == theta)
        listing = ", ".join(f"{ft(X[c])}" for c in minus)
        rec["enter"] = list(enter)
        rec["enter_delta"] = fs(pos[enter])
        rec["cycle"] = [{"cell": list(c), "sign": "+" if k % 2 == 0 else "-", "x": fs(X[c]) if c in X else "0"}
                        for k, c in enumerate(cycle)]
        rec["theta"] = fs(theta)
        rec["leave"] = list(leave)
        rec["decision"] = [
            f"Δ{enter[0] + 1}{enter[1] + 1} = {ft(pos[enter])} = max{{Δij | Δij > 0}} > 0 \u21d2 chưa tối ưu; "
            f"ô vi phạm là {_cell(enter)} (ta thêm ô này vào phương án).",
            f"Coi {_cell(enter)} là ô chẵn, lập chu trình K duy nhất: K = {_cells(cycle)};  "
            f"K+ = {_cells(plus)};  K{MINUS} = {_cells(minus)}.",
            f"θ = min{{xij | (i,j) \u2208 K{MINUS}}} = min{{{listing}}} = {ft(theta)}; ô ra khỏi cơ sở: {_cell(leave)}.",
            f"Đổi phương án: xij + θ trên K+, xij {MINUS} θ trên K{MINUS}, còn lại giữ nguyên.",
        ]
        for c in plus:
            X[c] = X.get(c, ZERO) + theta
        for c in minus:
            X[c] = X[c] - theta
        del X[leave]
    else:
        out["status"] = "iteration_limit"
        return out

    last = out["iterations"][-1]
    total = _total(X, C)
    Xreal = [[X.get((i, j), ZERO) for j in range(n0)] for i in range(m0)]
    sol: dict[str, Any] = {"X": [[fs(v) for v in r] for r in Xreal], "F": fs(total), "leftover": None}
    if dummy_col:
        sol["leftover"] = {"kind": "supply", "values": [fs(X.get((i, n - 1), ZERO)) for i in range(m0)]}
    if dummy_row:
        sol["leftover"] = {"kind": "demand", "values": [fs(X.get((m - 1, j), ZERO)) for j in range(n0)]}
    out["solution"] = sol
    if any(x == 0 for x in X.values()):
        out["notes"].append("Phương án tối ưu suy biến: có ô cơ sở với x = 0.")
    if sol["leftover"]:
        if sol["leftover"]["kind"] == "supply":
            out["notes"].append("Lượng ở cột ảo là lượng hàng còn dư tại mỗi điểm phát (không vận chuyển).")
        else:
            out["notes"].append("Lượng ở hàng ảo là lượng hàng còn thiếu tại mỗi điểm thu (không được cấp).")
    out["verify"] = _scipy_check(a, b, C, total)
    return out


def _scipy_check(a, b, C, exact: Fraction):
    try:
        from scipy.optimize import linprog  # type: ignore
        import numpy as np  # type: ignore
    except Exception:  # pragma: no cover
        return None
    m, n = len(a), len(b)
    c = np.array([[float(C[i][j]) for j in range(n)] for i in range(m)]).ravel()
    A_eq, b_eq = [], []
    for i in range(m):
        row = np.zeros((m, n)); row[i, :] = 1
        A_eq.append(row.ravel()); b_eq.append(float(a[i]))
    for j in range(n):
        row = np.zeros((m, n)); row[:, j] = 1
        A_eq.append(row.ravel()); b_eq.append(float(b[j]))
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=(0, None), method="highs")
    if res.status != 0:
        return {"available": True, "status": "other", "agree": None}
    ex = float(exact)
    return {"available": True, "status": "optimal", "value": float(res.fun),
            "agree": abs(res.fun - ex) <= 1e-7 * max(1.0, abs(ex))}

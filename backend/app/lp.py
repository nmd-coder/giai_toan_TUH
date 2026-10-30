"""Quy hoạch tuyến tính: đơn hình (phương pháp M) và đơn hình đối ngẫu.

Cách trình bày bám theo bài giảng IT6095 (Bài 2, Bài 3):
  * dạng chính tắc max, biến phụ / biến giả, bảng đơn hình có cột "Hệ số Cj",
    "Cơ sở", "Phương án", dòng Δk (và dòng hệ số của M khi có biến giả);
  * Δk = Σ Zjk·cj − ck, tối ưu khi mọi Δk ≥ 0, chọn cột xoay Δs = min{Δk | Δk < 0},
    dòng xoay theo θ = min{xj / Zjs | Zjs > 0}.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .numfmt import (
    MINUS,
    ONE,
    ZERO,
    Pair,
    fs,
    ft,
    lin_expr,
    pair_expr,
    pair_text,
    pkey,
    pneg,
    padd,
    pscale,
    to_frac,
    vec_text,
)

MAX_ITER = 200
MAX_DIM = 20
OPPOSITE = {"<=": ">=", ">=": "<=", "=": "="}
SIGN_TXT = {"<=": "\u2264", ">=": "\u2265", "=": "="}


class SolverError(ValueError):
    """Lỗi dữ liệu đầu vào – message hiển thị trực tiếp cho người dùng."""


# --------------------------------------------------------------------------
#  Mô hình bài toán
# --------------------------------------------------------------------------

@dataclass
class LP:
    sense: str                    # 'max' | 'min'
    c: list[Fraction]
    A: list[list[Fraction]]
    signs: list[str]              # '<=' | '>=' | '='
    b: list[Fraction]
    var_signs: list[str]          # 'ge0' | 'le0' | 'free'

    @property
    def n(self) -> int:
        return len(self.c)

    @property
    def m(self) -> int:
        return len(self.A)


def parse_lp(sense: str, c, constraints, var_signs=None) -> LP:
    n = len(c)
    m = len(constraints)
    if n < 1 or m < 1:
        raise SolverError("Cần ít nhất 1 biến và 1 ràng buộc.")
    if n > MAX_DIM or m > MAX_DIM:
        raise SolverError(f"Ứng dụng giới hạn tối đa {MAX_DIM} biến và {MAX_DIM} ràng buộc.")
    cc = [to_frac(v) for v in c]
    A, signs, b = [], [], []
    for i, row in enumerate(constraints):
        if len(row["a"]) != n:
            raise SolverError(f"Ràng buộc {i + 1} phải có đúng {n} hệ số.")
        A.append([to_frac(v) for v in row["a"]])
        signs.append(row["sign"])
        b.append(to_frac(row["b"]))
    vs = list(var_signs) if var_signs else ["ge0"] * n
    if len(vs) != n:
        raise SolverError("Số điều kiện dấu của biến không khớp số biến.")
    return LP(sense, cc, A, signs, b, vs)


def describe_lp(lp: LP, v: str = "x", f: str = "f") -> list[str]:
    names = [f"{v}{j + 1}" for j in range(lp.n)]
    lines = [f"{f} = {lin_expr(lp.c, names)} \u2192 {lp.sense}"]
    for a, s, b in zip(lp.A, lp.signs, lp.b):
        lines.append(f"{lin_expr(a, names)} {SIGN_TXT[s]} {ft(b)}")
    groups = {
        "ge0": ([], "\u2265 0"),
        "le0": ([], "\u2264 0"),
        "free": ([], "tùy ý"),
    }
    for j, vs in enumerate(lp.var_signs):
        groups[vs][0].append(names[j])
    for key in ("ge0", "le0", "free"):
        lst, txt = groups[key]
        if lst:
            lines.append(", ".join(lst) + " " + txt)
    return lines


# --------------------------------------------------------------------------
#  Đổi biến (x ≤ 0, x tuỳ ý)
# --------------------------------------------------------------------------

def substitute_vars(lp: LP):
    n, m = lp.n, lp.m
    cols = [[lp.A[i][j] for i in range(m)] for j in range(n)]
    c = list(lp.c)
    varmap: list[list[tuple[int, Fraction]]] = [[(j, ONE)] for j in range(n)]
    notes: list[str] = []
    free_idx = []
    for j, vs in enumerate(lp.var_signs):
        if vs == "le0":
            cols[j] = [-v for v in cols[j]]
            c[j] = -c[j]
            varmap[j] = [(j, -ONE)]
            notes.append(
                f"x{j + 1} \u2264 0: đặt x{j + 1} = {MINUS}x{j + 1}' với x{j + 1}' \u2265 0 "
                f"(đổi dấu cột {j + 1}; trong bảng vẫn ký hiệu là x{j + 1})."
            )
        elif vs == "free":
            free_idx.append(j)
    for j in free_idx:
        k = len(cols)
        cols.append([-v for v in cols[j]])
        c.append(-c[j])
        varmap[j] = [(j, ONE), (k, -ONE)]
        notes.append(
            f"x{j + 1} tùy ý: đặt x{j + 1} = x{j + 1}' {MINUS} x{k + 1} với x{j + 1}', x{k + 1} \u2265 0 "
            f"(x{j + 1}' vẫn ký hiệu x{j + 1}; x{k + 1} là biến mới)."
        )
    return cols, c, varmap, notes


def recover_x(lp: LP, varmap, vals: list[Fraction]) -> list[Fraction]:
    return [sum((coef * vals[col] for col, coef in varmap[j]), ZERO) for j in range(lp.n)]


# --------------------------------------------------------------------------
#  Bảng đơn hình chuẩn hoá
# --------------------------------------------------------------------------

@dataclass
class Std:
    A: list[list[Fraction]]
    b: list[Fraction]
    c: list[Pair]
    kinds: list[str]          # 'orig' | 'slack' | 'surplus' | 'art'
    basis: list[int]
    varmap: Any
    prep: list[dict]
    has_m: bool

    @property
    def N(self) -> int:
        return len(self.c)


def _names(N: int) -> list[str]:
    return [f"x{k + 1}" for k in range(N)]


def _equations(A, b, names) -> list[str]:
    return [f"{lin_expr(row, names)} = {ft(bi)}" for row, bi in zip(A, b)]


def build_big_m(lp: LP) -> Std:
    cols, c, varmap, notes = substitute_vars(lp)
    m = lp.m
    n_struct = len(cols)
    lines: list[str] = []
    if lp.sense == "min":
        c = [-v for v in c]
        lines.append(
            f"Bài toán min: nhân hàm mục tiêu với {MINUS}1 để đưa về max (f\u0303 = {MINUS}f). "
            "Cuối cùng đổi dấu lại giá trị tối ưu."
        )
    lines += notes
    signs = list(lp.signs)
    b = list(lp.b)
    for i in range(m):
        if b[i] < 0:
            for col in cols:
                col[i] = -col[i]
            b[i] = -b[i]
            signs[i] = OPPOSITE[signs[i]]
            lines.append(f"Ràng buộc {i + 1} có vế phải âm: nhân hai vế với {MINUS}1 (đổi chiều bất đẳng thức).")

    kinds = ["orig"] * n_struct
    cpairs: list[Pair] = [(v, ZERO) for v in c]
    slack_of: dict[int, int] = {}
    art_of: dict[int, int] = {}
    for i in range(m):
        if signs[i] in ("<=", ">="):
            col = [ZERO] * m
            col[i] = ONE if signs[i] == "<=" else -ONE
            cols.append(col)
            kinds.append("slack" if signs[i] == "<=" else "surplus")
            cpairs.append((ZERO, ZERO))
            slack_of[i] = len(cols) - 1
    for i in range(m):
        if signs[i] in (">=", "="):
            col = [ZERO] * m
            col[i] = ONE
            cols.append(col)
            kinds.append("art")
            cpairs.append((ZERO, -ONE))
            art_of[i] = len(cols) - 1

    basis = [slack_of[i] if signs[i] == "<=" else art_of[i] for i in range(m)]
    for i in range(m):
        s = signs[i]
        if s == "<=":
            lines.append(f"Ràng buộc {i + 1} (\u2264): cộng biến phụ x{slack_of[i] + 1} \u2265 0.")
        elif s == ">=":
            lines.append(
                f"Ràng buộc {i + 1} (\u2265): trừ biến phụ x{slack_of[i] + 1} \u2265 0 để chuyển về dấu =, "
                f"rồi cộng biến giả x{art_of[i] + 1} \u2265 0."
            )
        else:
            lines.append(f"Ràng buộc {i + 1} (=): cộng biến giả x{art_of[i] + 1} \u2265 0.")

    N = len(cols)
    A = [[cols[k][i] for k in range(N)] for i in range(m)]
    names = _names(N)
    has_m = bool(art_of)
    prep = [{"title": "Đưa bài toán về dạng chính tắc" + (" (bài toán M)" if has_m else ""), "lines": lines}]
    obj_lbl = "Hàm mục tiêu (M)" if has_m else "Hàm mục tiêu"
    sys_lines = [f"{obj_lbl}:  f = {pair_expr(cpairs, names)} \u2192 max"] + _equations(A, b, names)
    sys_lines.append(f"xj \u2265 0, j = 1..{N}")
    init = [ZERO] * N
    for i, k in enumerate(basis):
        init[k] = b[i]
    sys_lines.append(
        f"Phương án cực biên xuất phát: x = {vec_text(init)}; cơ sở: ("
        + ", ".join(f"A{k + 1}" for k in basis) + ")"
    )
    prep.append({"title": "Hệ ràng buộc sau khi thêm biến", "lines": sys_lines})
    return Std(A, b, cpairs, kinds, basis, varmap, prep, has_m)


# --------------------------------------------------------------------------
#  Vòng lặp đơn hình (dùng chung cho cả hai thuật toán)
# --------------------------------------------------------------------------

def _delta(A, basis, cpairs, removed: set[int]) -> list[Pair | None]:
    m = len(A)
    N = len(cpairs)
    cB = [cpairs[j] for j in basis]
    out: list[Pair | None] = []
    for k in range(N):
        if k in removed:
            out.append(None)
            continue
        s: Pair = (ZERO, ZERO)
        for i in range(m):
            if A[i][k] != 0:
                s = padd(s, pscale(cB[i], A[i][k]))
        out.append(padd(s, pscale(cpairs[k], -ONE)))
    return out


def _snapshot(t, A, xB, basis, cpairs, kinds, has_m) -> tuple[dict, list[Pair | None]]:
    N = len(cpairs)
    removed = {k for k in range(N) if kinds[k] == "art" and k not in basis}
    delta = _delta(A, basis, cpairs, removed)
    F: Pair = (ZERO, ZERO)
    for i, j in enumerate(basis):
        F = padd(F, pscale(cpairs[j], xB[i]))
    rec: dict[str, Any] = {
        "t": t,
        "basis": [k + 1 for k in basis],
        "cB": [pair_text(cpairs[j]) for j in basis],
        "xB": [fs(v) for v in xB],
        "T": [[fs(v) for v in row] for row in A],
        "delta": [fs(d[0]) if d else None for d in delta],
        "F": pair_text(F),
        "removed": sorted(k + 1 for k in removed),
        "enter": None,
        "leave_row": None,
        "pivot": None,
        "ratios_rows": None,
        "ratios_cols": None,
        "decision": [],
    }
    if has_m:
        rec["delta_m"] = [fs(d[1]) if d else None for d in delta]
    return rec, delta


def _pivot(A, xB, basis, r, s):
    p = A[r][s]
    A[r] = [v / p for v in A[r]]
    xB[r] = xB[r] / p
    for i in range(len(A)):
        if i != r and A[i][s] != 0:
            f = A[i][s]
            A[i] = [vi - f * vr for vi, vr in zip(A[i], A[r])]
            xB[i] = xB[i] - f * xB[r]
    basis[r] = s


def _column_meta(std: Std) -> dict:
    N = std.N
    return {
        "labels": [f"A{k + 1}" for k in range(N)],
        "names": _names(N),
        "kinds": list(std.kinds),
        "c": [pair_text(p) for p in std.c],
        "has_m": std.has_m,
    }


def run_simplex(lp: LP, std: Std) -> dict:
    A = [row[:] for row in std.A]
    xB = std.b[:]
    basis = std.basis[:]
    m, N = len(A), std.N
    iters: list[dict] = []
    status = "iteration_limit"
    last_delta: list[Pair | None] = []

    for t in range(1, MAX_ITER + 1):
        rec, delta = _snapshot(t, A, xB, basis, std.c, std.kinds, std.has_m)
        iters.append(rec)
        last_delta = delta
        removed = set(k - 1 for k in rec["removed"])
        cand = [k for k in range(N) if k not in removed and k not in basis and delta[k] is not None and pneg(delta[k])]
        if not cand:
            rec["decision"] = ["Mọi Δk ≥ 0 ⇒ bảng hiện tại tối ưu cho bài toán M; cần kiểm tra biến giả trước khi kết luận cho bài toán gốc."]
            status = "optimal"
            break
        # Δk < 0 mà mọi Zjk ≤ 0  ⇒ hàm mục tiêu không bị chặn (chỉ kết luận được khi
        # phương án hiện tại đã chấp nhận được, tức không còn biến giả dương trong cơ sở).
        art_pos = [basis[i] for i in range(m) if std.kinds[basis[i]] == "art" and xB[i] != 0]
        ub_cands = [k for k in cand if all(A[i][k] <= 0 for i in range(m))]
        if ub_cands and not art_pos:
            ub = ub_cands[0]
            rec["enter"] = ub + 1
            rec["decision"] = [
                f"Δ{ub + 1} = {pair_text(delta[ub])} < 0 và mọi Zj{ub + 1} \u2264 0 \u21d2 hàm mục tiêu không bị chặn trên.",
                "Bài toán không có phương án tối ưu. Dừng.",
            ]
            status = "unbounded"
            break
        s = min(cand, key=lambda k: (pkey(delta[k]), k))
        if s in ub_cands:
            rec["enter"] = s + 1
            rec["decision"] = [
                f"Δ{s + 1} = {pair_text(delta[s])} < 0 nhưng mọi Zj{s + 1} \u2264 0, trong khi biến giả "
                + ", ".join(f"x{k + 1}" for k in art_pos)
                + " vẫn còn dương trong cơ sở \u21d2 không thể loại hết biến giả.",
                "Bài toán không có phương án chấp nhận được. Dừng.",
            ]
            status = "infeasible"
            break
        ratios = [xB[i] / A[i][s] if A[i][s] > 0 else None for i in range(m)]
        r = min((i for i in range(m) if ratios[i] is not None), key=lambda i: (ratios[i], basis[i]))
        rec["enter"] = s + 1
        rec["leave_row"] = r
        rec["pivot"] = fs(A[r][s])
        rec["ratios_rows"] = [fs(v) if v is not None else None for v in ratios]
        cand_txt = ", ".join(pair_text(delta[k]) for k in cand)
        valid = [f"{fs(xB[i])}/{fs(A[i][s])}" for i in range(m) if ratios[i] is not None]
        dec = [
            f"Có Δk < 0 \u21d2 chưa tối ưu.  Δs = min{{{cand_txt}}} = {pair_text(delta[s])} "
            f"\u21d2 cột xoay s = {s + 1}: đưa A{s + 1} vào cơ sở.",
            f"θ = min{{xj/Zjs | Zjs > 0}} = min{{{', '.join(valid)}}} = {fs(ratios[r])} "
            f"\u21d2 dòng xoay r = {r + 1}: đưa A{basis[r] + 1} ra khỏi cơ sở.",
            f"Phần tử trục = Z{r + 1},{s + 1} = {fs(A[r][s])}. "
            "Chia dòng xoay cho phần tử trục (được dòng chính), rồi lấy mỗi dòng khác trừ đi "
            "(dòng chính \u00d7 phần tử xoay tương ứng).",
        ]
        if std.kinds[basis[r]] == "art":
            dec.append(f"A{basis[r] + 1} là vector giả đã ra khỏi cơ sở \u21d2 bỏ cột A{basis[r] + 1}, không tính Δ{basis[r] + 1} nữa.")
        rec["decision"] = dec
        _pivot(A, xB, basis, r, s)

    return _finish(lp, std, A, xB, basis, iters, status, last_delta, "simplex")


def _finish(lp: LP, std: Std, A, xB, basis, iters, status, last_delta, method) -> dict:
    N = std.N
    out: dict[str, Any] = {
        "method": method,
        "status": status,
        "message": "",
        "problem": describe_lp(lp),
        "prep": std.prep,
        "columns": _column_meta(std),
        "iterations": iters,
        "solution": None,
        "notes": [],
    }
    if status == "iteration_limit":
        out["message"] = f"Dừng sau {MAX_ITER} vòng lặp (có thể bị xoay vòng)."
        return out
    if status == "unbounded":
        out["message"] = "Hàm mục tiêu không bị chặn ⇒ bài toán không có phương án tối ưu."
        return out
    if status == "infeasible":
        out["message"] = "Bài toán không có phương án chấp nhận được."
        return out

    vals = [ZERO] * N
    for i, k in enumerate(basis):
        vals[k] = xB[i]
    art_pos = [k for i, k in enumerate(basis) if std.kinds[k] == "art" and xB[i] != 0]
    if art_pos:
        out["status"] = "infeasible"
        out["message"] = (
            "Đã tối ưu nhưng biến giả "
            + ", ".join(f"x{k + 1}" for k in art_pos)
            + " vẫn còn trong cơ sở với giá trị dương \u21d2 miền ràng buộc rỗng, bài toán không có phương án."
        )
        iters[-1]["decision"].append(out["message"])
        return out

    x_orig = recover_x(lp, std.varmap, vals)
    F = sum((lp.c[j] * x_orig[j] for j in range(lp.n)), ZERO)
    non_art = [k for k in range(N) if std.kinds[k] != "art"]
    out["solution"] = {
        "names": [f"x{j + 1}" for j in range(lp.n)],
        "x": [fs(v) for v in x_orig],
        "std_names": [f"x{k + 1}" for k in non_art],
        "std_x": [fs(vals[k]) for k in non_art],
        "F": fs(F),
        "sense": lp.sense,
    }
    notes = out["notes"]
    if lp.sense == "min":
        notes.append("Các giá trị F trong bảng là của hàm f\u0303 = −f (bài toán max tương đương); giá trị tối ưu của bài toán gốc là f = " + ft(F) + ".")
    if any(xB[i] == 0 and std.kinds[k] != "art" for i, k in enumerate(basis)):
        notes.append("Phương án suy biến: có biến cơ sở bằng 0.")
    if any(std.kinds[k] == "art" for i, k in enumerate(basis)):
        notes.append("Biến giả còn trong cơ sở ở mức 0 nên nghiệm vẫn hợp lệ.")
    if method == "simplex":
        removed = set(k - 1 for k in iters[-1]["removed"])
        alt = [k for k in range(N) if k not in basis and k not in removed and std.kinds[k] != "art"
               and last_delta[k] is not None and last_delta[k] == (ZERO, ZERO)]
        if alt:
            notes.append("Có Δk = 0 ứng với biến phi cơ sở " + ", ".join(f"x{k + 1}" for k in alt)
                         + ". Đây là dấu hiệu có thể có phương án tối ưu khác; khi suy biến cần kiểm tra thêm, không thể kết luận chỉ từ Δk = 0.")
    return out


# --------------------------------------------------------------------------
#  Đơn hình đối ngẫu
# --------------------------------------------------------------------------

def build_dual_std(lp: LP) -> tuple[Std, list[int]]:
    cols, c, varmap, notes = substitute_vars(lp)
    n_struct = len(cols)
    m0 = lp.m
    lines: list[str] = []
    if lp.sense == "min":
        c = [-v for v in c]
        lines.append(f"Bài toán min: nhân hàm mục tiêu với {MINUS}1 để đưa về max (f\u0303 = {MINUS}f).")
    lines += notes
    rows: list[tuple[list[Fraction], Fraction]] = []
    for i in range(m0):
        a = [cols[k][i] for k in range(n_struct)]
        b = lp.b[i]
        s = lp.signs[i]
        if s == "<=":
            rows.append((a, b))
        elif s == ">=":
            rows.append(([-v for v in a], -b))
            lines.append(f"Ràng buộc {i + 1} (\u2265): nhân hai vế với {MINUS}1 để có dấu \u2264.")
        else:
            rows.append((a, b))
            rows.append(([-v for v in a], -b))
            lines.append(f"Ràng buộc {i + 1} (=): tách thành hai ràng buộc \u2264 và \u2265 (\u2265 nhân {MINUS}1 thành \u2264).")
    m = len(rows)
    N = n_struct + m
    A = []
    for i, (a, _) in enumerate(rows):
        row = list(a) + [ZERO] * m
        row[n_struct + i] = ONE
        A.append(row)
    b = [r[1] for r in rows]
    cpairs: list[Pair] = [(v, ZERO) for v in c] + [(ZERO, ZERO)] * m
    kinds = ["orig"] * n_struct + ["slack"] * m
    basis = [n_struct + i for i in range(m)]
    for i in range(m):
        lines.append(f"Ràng buộc {i + 1} sau chuẩn hoá: cộng biến phụ x{n_struct + i + 1} \u2265 0.")
    names = _names(N)
    prep = [{"title": "Đưa bài toán về dạng max với các ràng buộc \u2264", "lines": lines}]
    sys_lines = [f"f = {pair_expr(cpairs, names)} \u2192 max"] + _equations(A, b, names)
    init = [ZERO] * N
    for i, k in enumerate(basis):
        init[k] = b[i]
    sys_lines.append(f"Cơ sở xuất phát: (" + ", ".join(f"A{k + 1}" for k in basis) + f"), x = {vec_text(init)}")
    sys_lines.append(
        "Điều kiện dùng đơn hình đối ngẫu: mọi Δk \u2265 0 (phương án đối ngẫu chấp nhận được); "
        "các xB có thể âm (phương án gốc chưa chấp nhận được)."
    )
    prep.append({"title": "Bảng xuất phát", "lines": sys_lines})
    std = Std(A, b, cpairs, kinds, basis, varmap, prep, False)
    bad = [k for k in range(n_struct) if -c[k] < 0]
    return std, bad


def run_dual_simplex(lp: LP, std: Std) -> dict:
    A = [row[:] for row in std.A]
    xB = std.b[:]
    basis = std.basis[:]
    m, N = len(A), std.N
    iters: list[dict] = []
    status = "iteration_limit"
    last_delta: list[Pair | None] = []

    for t in range(1, MAX_ITER + 1):
        rec, delta = _snapshot(t, A, xB, basis, std.c, std.kinds, False)
        iters.append(rec)
        last_delta = delta
        neg_rows = [i for i in range(m) if xB[i] < 0]
        if not neg_rows:
            rec["decision"] = ["Mọi xB \u2265 0 và mọi Δk \u2265 0 \u21d2 phương án hiện tại là phương án tối ưu."]
            status = "optimal"
            break
        r = min(neg_rows, key=lambda i: (xB[i], i))
        cand = [k for k in range(N) if k not in basis and A[r][k] < 0]
        if not cand:
            rec["leave_row"] = r
            rec["decision"] = [
                f"Dòng {r + 1} có x = {fs(xB[r])} < 0 nhưng mọi Z{r + 1}k \u2265 0 \u21d2 ràng buộc không thể thoả mãn.",
                "Bài toán không có phương án chấp nhận được. Dừng.",
            ]
            status = "infeasible"
            break
        ratios = {k: delta[k][0] / (-A[r][k]) for k in cand}  # type: ignore[index]
        s = min(cand, key=lambda k: (ratios[k], k))
        rec["enter"] = s + 1
        rec["leave_row"] = r
        rec["pivot"] = fs(A[r][s])
        rec["ratios_cols"] = [fs(ratios[k]) if k in ratios else None for k in range(N)]
        listing = ", ".join(f"Δ{k + 1}/|Z{r + 1},{k + 1}| = {fs(ratios[k])}" for k in cand)
        rec["decision"] = [
            f"Có xB < 0 \u21d2 chưa chấp nhận được. x{basis[r] + 1} = min{{xi}} = {fs(xB[r])} "
            f"\u21d2 dòng xoay r = {r + 1}: đưa A{basis[r] + 1} ra khỏi cơ sở.",
            f"Xét các cột có Z{r + 1}k < 0:  {listing}. "
            f"θ = min = {fs(ratios[s])} \u21d2 cột xoay s = {s + 1}: đưa A{s + 1} vào cơ sở.",
            f"Phần tử trục = Z{r + 1},{s + 1} = {fs(A[r][s])}. Thực hiện phép xoay như đơn hình thường.",
        ]
        _pivot(A, xB, basis, r, s)

    res = _finish(lp, std, A, xB, basis, iters, status, last_delta, "dual_simplex")
    return res


# --------------------------------------------------------------------------
#  Kiểm chứng bằng SciPy (HiGHS)
# --------------------------------------------------------------------------

def scipy_check(lp: LP, result: dict) -> dict | None:
    try:
        from scipy.optimize import linprog  # type: ignore
    except Exception:  # pragma: no cover
        return None
    c = [float(v) for v in lp.c]
    if lp.sense == "max":
        c = [-v for v in c]
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for a, s, b in zip(lp.A, lp.signs, lp.b):
        row = [float(v) for v in a]
        if s == "<=":
            A_ub.append(row); b_ub.append(float(b))
        elif s == ">=":
            A_ub.append([-v for v in row]); b_ub.append(-float(b))
        else:
            A_eq.append(row); b_eq.append(float(b))
    bounds = [{"ge0": (0, None), "le0": (None, 0), "free": (None, None)}[v] for v in lp.var_signs]
    try:
        res = linprog(c, A_ub=A_ub or None, b_ub=b_ub or None, A_eq=A_eq or None, b_eq=b_eq or None,
                      bounds=bounds, method="highs")
    except Exception as exc:  # pragma: no cover
        return {"available": True, "status": "error", "agree": None, "detail": str(exc)}
    name = {0: "optimal", 2: "infeasible", 3: "unbounded"}.get(res.status, "other")
    val = None
    if res.status == 0:
        val = -res.fun if lp.sense == "max" else res.fun
    mine = result["status"]
    agree = name == mine
    if agree and name == "optimal" and result["solution"]:
        exact = float(Fraction(result["solution"]["F"]))
        agree = abs(exact - val) <= 1e-7 * max(1.0, abs(exact))
    return {"available": True, "status": name, "value": val, "agree": agree}


# --------------------------------------------------------------------------
#  Điểm vào
# --------------------------------------------------------------------------

def solve_lp(lp: LP, method: str) -> dict:
    if method == "simplex":
        std = build_big_m(lp)
        result = run_simplex(lp, std)
    elif method == "dual_simplex":
        std, bad = build_dual_std(lp)
        if bad:
            res = {
                "method": "dual_simplex",
                "status": "not_dual_feasible",
                "message": (
                    "Đơn hình đối ngẫu cần mọi Δk \u2265 0 ngay từ bảng đầu (sau khi đưa về max, hệ số hàm mục tiêu c\u0303k \u2264 0; "
                    "với bài toán min nghĩa là mọi ck \u2265 0). Bài toán này có Δk < 0 tại "
                    + ", ".join(f"x{k + 1}" for k in bad)
                    + ", nên không áp dụng trực tiếp được. Hãy dùng phương pháp đơn hình (M)."
                ),
                "problem": describe_lp(lp),
                "prep": std.prep,
                "columns": _column_meta(std),
                "iterations": [],
                "solution": None,
                "notes": [],
            }
            res["verify"] = None
            return res
        result = run_dual_simplex(lp, std)
    else:
        raise SolverError("Phương pháp không hợp lệ.")
    result["verify"] = scipy_check(lp, result)
    return result

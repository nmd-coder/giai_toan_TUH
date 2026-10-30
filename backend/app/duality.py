"""Bài toán đối ngẫu (Bài 3): lập bài toán đối ngẫu, định lý đối ngẫu,
kiểm tra phương án tối ưu bằng định lý độ lệch bù."""
from __future__ import annotations

from fractions import Fraction

from .lp import LP, SIGN_TXT, SolverError, describe_lp, solve_lp
from .numfmt import ONE, ZERO, fs, ft, lin_expr, to_frac

VAR_TXT = {"ge0": "\u2265 0", "le0": "\u2264 0", "free": "tùy ý"}


# --------------------------------------------------------------------------
#  Lập bài toán đối ngẫu (bảng quy tắc, slide 13)
# --------------------------------------------------------------------------

def dualize(lp: LP) -> LP:
    n, m = lp.n, lp.m
    if lp.sense == "min":
        y_signs = [{">=": "ge0", "<=": "le0", "=": "free"}[s] for s in lp.signs]
        row_signs = [{"ge0": "<=", "le0": ">=", "free": "="}[v] for v in lp.var_signs]
        sense = "max"
    else:
        y_signs = [{"<=": "ge0", ">=": "le0", "=": "free"}[s] for s in lp.signs]
        row_signs = [{"ge0": ">=", "le0": "<=", "free": "="}[v] for v in lp.var_signs]
        sense = "min"
    At = [[lp.A[i][j] for i in range(m)] for j in range(n)]
    return LP(sense, list(lp.b), At, row_signs, list(lp.c), y_signs)


def dual_form(lp: LP, solve_both: bool = True) -> dict:
    dual = dualize(lp)
    xn = [f"x{j + 1}" for j in range(lp.n)]
    yn = [f"y{i + 1}" for i in range(lp.m)]
    opp = "max" if lp.sense == "min" else "min"
    rules = [
        f"Bài toán gốc là {lp.sense} \u21d2 bài toán đối ngẫu là {opp}.",
        "Hệ số hàm mục tiêu của bài toán này là vế phải các ràng buộc hàm của bài toán kia (theo thứ tự chỉ số).",
        "Số ràng buộc hàm của bài toán này bằng số biến của bài toán kia; ma trận ràng buộc của hai bài toán là chuyển vị của nhau.",
    ]
    if lp.sense == "min":
        rules.append("Gốc min: ràng buộc \u2265 \u2194 y \u2265 0;  ràng buộc \u2264 \u2194 y \u2264 0;  ràng buộc = \u2194 y tùy ý.")
        rules.append("Gốc min: x \u2265 0 \u2194 ràng buộc đối ngẫu \u2264;  x \u2264 0 \u2194 \u2265;  x tùy ý \u2194 =.")
    else:
        rules.append("Gốc max: ràng buộc \u2264 \u2194 y \u2265 0;  ràng buộc \u2265 \u2194 y \u2264 0;  ràng buộc = \u2194 y tùy ý.")
        rules.append("Gốc max: x \u2265 0 \u2194 ràng buộc đối ngẫu \u2265;  x \u2264 0 \u2194 \u2264;  x tùy ý \u2194 =.")

    pairs = []
    for i in range(lp.m):
        pairs.append({
            "primal": f"({i + 1})  {lin_expr(lp.A[i], xn)} {SIGN_TXT[lp.signs[i]]} {ft(lp.b[i])}",
            "dual": f"{yn[i]} {VAR_TXT[dual.var_signs[i]]}",
        })
    for j in range(lp.n):
        pairs.append({
            "primal": f"{xn[j]} {VAR_TXT[lp.var_signs[j]]}",
            "dual": f"({j + 1}')  {lin_expr(dual.A[j], yn)} {SIGN_TXT[dual.signs[j]]} {ft(dual.b[j])}",
        })

    out = {
        "primal": describe_lp(lp),
        "dual": describe_lp(dual, "y", "g"),
        "rules": rules,
        "pairs": pairs,
        "solved": None,
    }
    if solve_both:
        try:
            rp = solve_lp(lp, "simplex")
            rd = solve_lp(dual, "simplex")
            solved = {"primal": _summ(rp, "x"), "dual": _summ(rd, "y")}
            if rp["status"] == "optimal" and rd["status"] == "optimal":
                eq = Fraction(rp["solution"]["F"]) == Fraction(rd["solution"]["F"])
                solved["equal"] = eq
                solved["comment"] = (
                    "Định lý đối ngẫu: cả hai bài toán đều có phương án tối ưu và f(x*) = g(y*)."
                    if eq else "Hai giá trị tối ưu khác nhau – hãy kiểm tra lại dữ liệu nhập."
                )
            else:
                solved["equal"] = None
                solved["comment"] = "Chưa có hai nghiệm tối ưu để đối chiếu; xem trạng thái từng bài toán."
            out["solved"] = solved
        except Exception:  # pragma: no cover
            out["solved"] = None
    return out


def _summ(res: dict, v: str) -> dict:
    s = res.get("solution")
    return {
        "status": res["status"],
        "names": [f"{v}{j + 1}" for j in range(len(s["x"]))] if s else [],
        "x": s["x"] if s else [],
        "value": s["F"] if s else None,
    }


# --------------------------------------------------------------------------
#  Giải hệ tuyến tính bằng phân số
# --------------------------------------------------------------------------

def _solve_linear(rows: list[list[Fraction]], rhs: list[Fraction], nvars: int):
    M = [r[:] + [b] for r, b in zip(rows, rhs)]
    piv: list[int] = []
    r = 0
    for col in range(nvars):
        pr = next((i for i in range(r, len(M)) if M[i][col] != 0), None)
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        pv = M[r][col]
        M[r] = [v / pv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(col)
        r += 1
    for i in range(r, len(M)):
        if M[i][nvars] != 0:
            return "inconsistent", None, piv
    sol = [ZERO] * nvars
    for idx, col in enumerate(piv):
        sol[col] = M[idx][nvars]
    return ("unique" if len(piv) == nvars else "free"), sol, piv


def _dual_feasible(dual: LP, y: list[Fraction]) -> list[str]:
    bad = []
    for i, vs in enumerate(dual.var_signs):
        if (vs == "ge0" and y[i] < 0) or (vs == "le0" and y[i] > 0):
            bad.append(f"y{i + 1} = {ft(y[i])} vi phạm điều kiện dấu y{i + 1} {VAR_TXT[vs]}")
    for j in range(dual.m):
        lhs = sum((dual.A[j][i] * y[i] for i in range(dual.n)), ZERO)
        s = dual.signs[j]
        ok = (lhs <= dual.b[j]) if s == "<=" else (lhs >= dual.b[j]) if s == ">=" else (lhs == dual.b[j])
        if not ok:
            bad.append(f"ràng buộc đối ngẫu ({j + 1}'): {ft(lhs)} {SIGN_TXT[s]} {ft(dual.b[j])} không thoả")
    return bad


def _find_feasible_y(dual: LP, unknown: list[int], tight: list[int]):
    """Giải chính xác hệ khả thi đối ngẫu và đầy đủ điều kiện độ lệch bù."""
    A = [row[:] for row in dual.A]
    signs = ["=" if j in tight else s for j, s in enumerate(dual.signs)]
    b = dual.b[:]
    for i in range(dual.n):
        if i not in unknown:
            A.append([ONE if j == i else ZERO for j in range(dual.n)])
            signs.append("=")
            b.append(ZERO)
    problem = LP("min", [ZERO] * dual.n, A, signs, b, dual.var_signs[:])
    result = solve_lp(problem, "simplex")
    if result["status"] == "optimal":
        y = [Fraction(v) for v in result["solution"]["x"]]
        if not _dual_feasible(dual, y) and all(sum((dual.A[j][i] * y[i] for i in range(dual.n)), ZERO) == dual.b[j] for j in tight):
            return "optimal", y
        return "unknown", None
    return result["status"], None


# --------------------------------------------------------------------------
#  Định lý độ lệch bù (slide 19–27)
# --------------------------------------------------------------------------

def check_optimality(lp: LP, xs: list[Fraction]) -> dict:
    n, m = lp.n, lp.m
    if len(xs) != n:
        raise SolverError(f"Cần nhập đủ {n} thành phần của phương án x.")
    xn = [f"x{j + 1}" for j in range(n)]
    yn = [f"y{i + 1}" for i in range(m)]
    steps: list[dict] = []

    def done(verdict: str, message: str, y=None, f=None, g=None) -> dict:
        return {
            "verdict": verdict, "message": message, "steps": steps,
            "x": [fs(v) for v in xs], "y": [fs(v) for v in y] if y is not None else None,
            "f": fs(f) if f is not None else None, "g": fs(g) if g is not None else None,
            "problem": describe_lp(lp),
        }

    # Bước 0: x có là phương án?
    lhs = [sum((lp.A[i][j] * xs[j] for j in range(n)), ZERO) for i in range(m)]
    lines, feasible = [], True
    for i in range(m):
        s = lp.signs[i]
        ok = (lhs[i] <= lp.b[i]) if s == "<=" else (lhs[i] >= lp.b[i]) if s == ">=" else (lhs[i] == lp.b[i])
        feasible &= ok
        tag = "thoả" if ok else "KHÔNG thoả"
        kind = "dấu = (ràng buộc chặt)" if lhs[i] == lp.b[i] else "bất đẳng thức chặt"
        lines.append(f"Ràng buộc {i + 1}: {ft(lhs[i])} {SIGN_TXT[s]} {ft(lp.b[i])} \u2192 {tag}" + (f" ({kind})" if ok else ""))
    for j in range(n):
        vs = lp.var_signs[j]
        ok = (vs == "free") or (vs == "ge0" and xs[j] >= 0) or (vs == "le0" and xs[j] <= 0)
        feasible &= ok
        if not ok:
            lines.append(f"{xn[j]} = {ft(xs[j])} vi phạm điều kiện dấu {xn[j]} {VAR_TXT[vs]}")
    steps.append({"title": "Bước 0. Kiểm tra x có là phương án của bài toán gốc", "lines": lines})
    if not feasible:
        return done("infeasible_x", "x không thoả hệ ràng buộc nên không phải phương án, càng không phải phương án tối ưu.")

    # Bước 1: bài toán đối ngẫu
    dual = dualize(lp)
    steps.append({"title": "Bước 1. Viết bài toán đối ngẫu", "lines": describe_lp(dual, "y", "g")})

    # Bước 2.1: x_j ≠ 0 ⇒ ràng buộc đối ngẫu thứ j lấy dấu '='
    pos = [j for j in range(n) if xs[j] != 0]
    l21 = []
    if pos:
        l21.append(
            "Với " + ", ".join(f"{xn[j]} = {ft(xs[j])}" for j in pos)
            + " (khác 0) \u21d2 các ràng buộc đối ngẫu số " + ", ".join(f"{j + 1}" for j in pos)
            + " lấy dấu '=' ta có hệ (*):"
        )
        for j in pos:
            l21.append(f"({j + 1}')  {lin_expr(dual.A[j], yn)} = {ft(dual.b[j])}")
    else:
        l21.append("Mọi xj = 0 nên không có phương trình nào sinh ra từ điều kiện này.")
    steps.append({"title": "Bước 2.1. Xét xj \u2260 0 \u21d2 hệ phương trình đối với y", "lines": l21})

    # Bước 2.2: ràng buộc chặt ⇒ y_i = 0
    active = [i for i in range(m) if lhs[i] == lp.b[i]]
    inactive = [i for i in range(m) if i not in active]
    l22 = []
    for i in range(m):
        if i in active:
            l22.append(f"Ràng buộc {i + 1} lấy dấu '=' \u21d2 {yn[i]} chưa bị ràng buộc bởi điều kiện này.")
        else:
            l22.append(f"Ràng buộc {i + 1} là bất đẳng thức chặt ({ft(lhs[i])} {SIGN_TXT[lp.signs[i]]} {ft(lp.b[i])}) \u21d2 {yn[i]} = 0.")
    steps.append({"title": "Bước 2.2. Thay x vào bài toán gốc \u21d2 các yi = 0", "lines": l22})

    # Bước 2.3: giải hệ
    unknown = active
    idx = {i: k for k, i in enumerate(unknown)}
    rows = [[dual.A[j][i] for i in unknown] for j in pos]
    rhs = [dual.b[j] for j in pos]
    state, sol, piv = _solve_linear(rows, rhs, len(unknown))
    l23 = []
    y = [ZERO] * m
    if inactive:
        l23.append("Kết hợp (*) với " + ", ".join(f"{yn[i]} = 0" for i in inactive) + ":")
    if state == "inconsistent":
        l23.append("Hệ vô nghiệm.")
        steps.append({"title": "Bước 2.3. Giải hệ để tìm y", "lines": l23})
        return done("not_optimal",
                    "Không tồn tại y thoả điều kiện độ lệch bù \u21d2 x không phải phương án tối ưu.")
    if state == "unique":
        for i in unknown:
            y[i] = sol[idx[i]]
        l23.append("Hệ có nghiệm duy nhất:  y = " + "(" + ", ".join(fs(v) for v in y) + ")")
    else:
        for i in unknown:
            y[i] = sol[idx[i]]  # các ẩn tự do = 0
        bad0 = _dual_feasible(dual, y)
        l23.append("Hệ có vô số nghiệm (còn ẩn tự do).")
        if bad0:
            status, alt = _find_feasible_y(dual, unknown, pos)
            if alt is None:
                l23.append("Không tìm được y thoả đồng thời các điều kiện đối ngẫu và độ lệch bù.")
                steps.append({"title": "Bước 2.3. Giải hệ để tìm y", "lines": l23})
                if status == "infeasible":
                    return done("not_optimal", "Hệ đối ngẫu và độ lệch bù vô nghiệm ⇒ x không tối ưu.")
                return done("unknown", "Chưa thể kết luận: bộ giải hệ phụ chưa tìm được chứng nhận.")
            y = alt
            l23.append("Giải hệ điều kiện đối ngẫu và độ lệch bù bằng phân số chính xác:  y = ("
                       + ", ".join(fs(v) for v in y) + ")")
        else:
            l23.append("Chọn các ẩn tự do bằng 0:  y = (" + ", ".join(fs(v) for v in y) + ")")
    steps.append({"title": "Bước 2.3. Giải hệ để tìm y", "lines": l23})

    bad = _dual_feasible(dual, y)
    if bad:
        steps.append({"title": "Bước 2.4. Kiểm tra y có là phương án của bài toán đối ngẫu",
                      "lines": [b + "." for b in bad]})
        return done("not_optimal", "y không là phương án của bài toán đối ngẫu \u21d2 x không phải phương án tối ưu.", y=y)
    steps.append({"title": "Bước 2.4. Kiểm tra y có là phương án của bài toán đối ngẫu",
                  "lines": ["y thoả điều kiện dấu và mọi ràng buộc của bài toán đối ngẫu."]})

    f = sum((lp.c[j] * xs[j] for j in range(n)), ZERO)
    g = sum((lp.b[i] * y[i] for i in range(m)), ZERO)
    l3 = [f"f(x) = {lin_expr(lp.c, xn)} = {ft(f)}", f"g(y) = {lin_expr(lp.b, yn)} = {ft(g)}"]
    if f == g:
        l3.append(f"f(x) = g(y) = {ft(f)}.")
        steps.append({"title": "Bước 3. Kiểm tra điều kiện f(x) = g(y)", "lines": l3})
        return done("optimal", "x là phương án tối ưu của bài toán gốc, y là phương án tối ưu của bài toán đối ngẫu.", y=y, f=f, g=g)
    l3.append("f(x) \u2260 g(y).")
    steps.append({"title": "Bước 3. Kiểm tra điều kiện f(x) = g(y)", "lines": l3})
    return done("not_optimal", "f(x) \u2260 g(y) \u21d2 x không phải phương án tối ưu.", y=y, f=f, g=g)

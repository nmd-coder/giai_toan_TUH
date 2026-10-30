"""Phương pháp hình học cho quy hoạch tuyến tính hai biến."""
from fractions import Fraction

from .lp import LP, SolverError, solve_lp
from .numfmt import ZERO, fs


def solve_graph(lp: LP) -> dict:
    if lp.n != 2:
        raise SolverError("Phương pháp hình học chỉ áp dụng cho bài toán có đúng 2 biến.")
    boundaries = [(a[0], a[1], b) for a, b in zip(lp.A, lp.b)]
    if lp.var_signs[0] != "free":
        boundaries.append((Fraction(1), ZERO, ZERO))
    if lp.var_signs[1] != "free":
        boundaries.append((ZERO, Fraction(1), ZERO))

    def feasible(x, y):
        for row, sign, b in zip(lp.A, lp.signs, lp.b):
            v = row[0] * x + row[1] * y
            if (sign == "<=" and v > b) or (sign == ">=" and v < b) or (sign == "=" and v != b):
                return False
        return all(s == "free" or (s == "ge0" and v >= 0) or (s == "le0" and v <= 0)
                   for s, v in zip(lp.var_signs, (x, y)))

    vertices = set()
    for i, (a, b, c) in enumerate(boundaries):
        for d, e, f in boundaries[i + 1:]:
            det = a * e - b * d
            if det:
                x, y = (c * e - b * f) / det, (a * f - c * d) / det
                if feasible(x, y):
                    vertices.add((x, y))
    result = solve_lp(lp, "simplex")
    return {"result": result, "vertices": [{"x": fs(x), "y": fs(y), "f": fs(lp.c[0] * x + lp.c[1] * y)}
                                                for x, y in sorted(vertices)]}

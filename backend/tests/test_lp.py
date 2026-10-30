"""Kiểm thử đơn hình / đối ngẫu với các ví dụ trong bài giảng IT6095 và so khớp SciPy."""
import random
from fractions import Fraction as F

from app.duality import check_optimality, dual_form, dualize
from app.graph import solve_graph
from app.lp import parse_lp, solve_lp


def lp(sense, c, rows, var_signs=None):
    return parse_lp(sense, c, [{"a": a, "sign": s, "b": b} for a, s, b in rows], var_signs)


def test_simplex_bai2_vd1():
    r = solve_lp(lp("max", [4, 5], [([2, 1], "<=", 8), ([1, 2], "<=", 7), ([0, 1], "<=", 3)]), "simplex")
    assert r["status"] == "optimal"
    assert r["solution"]["F"] == "22" and r["solution"]["x"] == ["3", "2"]
    assert r["solution"]["std_x"] == ["3", "2", "0", "0", "1"]
    assert len(r["iterations"]) == 4
    last = r["iterations"][-1]
    assert last["basis"] == [5, 1, 2]
    assert last["T"][0] == ["0", "0", "1/3", "-2/3", "1"]       # slide 24
    assert last["delta"] == ["0", "0", "1", "2", "0"]
    assert [it["F"] for it in r["iterations"]] == ["0", "15", "19", "22"]
    assert r["verify"]["agree"] is True


def test_graph_vertices_and_statuses():
    p = lp("max", [4, 5], [([2, 1], "<=", 8), ([1, 2], "<=", 7), ([0, 1], "<=", 3)])
    r = solve_graph(p)
    assert { (v["x"], v["y"], v["f"]) for v in r["vertices"] } == {
        ("0", "0", "0"), ("4", "0", "16"), ("3", "2", "22"), ("1", "3", "19"), ("0", "3", "15") }
    assert r["result"]["solution"]["F"] == "22"
    assert solve_graph(lp("max", [1, 0], [([1, -1], "<=", 1)]))["result"]["status"] == "unbounded"
    assert solve_graph(lp("max", [1, 0], [([1, 0], "<=", 0), ([1, 0], ">=", 1)]))["result"]["status"] == "infeasible"
    r = solve_graph(lp("max", [0, 0], [([1, 0], "=", 1)], ["free", "free"]))
    assert r["vertices"] == [] and r["result"]["status"] == "optimal"


def test_simplex_bai2_vd2_big_m():
    rows = [([1, -1, 2, -1], "=", 2), ([2, 1, -3, 1], "=", 6), ([1, 1, 1, 1], "=", 7)]
    r = solve_lp(lp("max", [2, 1, -1, -1], rows), "simplex")
    assert r["status"] == "optimal"
    assert r["solution"]["F"] == "8" and r["solution"]["x"] == ["3", "3", "1", "0"]
    first = r["iterations"][0]
    assert first["delta"][:4] == ["-2", "-1", "1", "1"]          # slide 30, dòng Δk
    assert first["delta_m"][:4] == ["-4", "-1", "0", "-1"]      # slide 30, dòng hệ số M
    assert r["iterations"][1]["basis"] == [1, 6, 7]              # A1 thay A5
    assert len(r["iterations"]) == 4
    assert r["verify"]["agree"] is True


def test_simplex_bai2_vd3_mixed_signs():
    rows = [([2, 1, 3], "<=", 7), ([4, -3, -2], ">=", 9), ([1, 2, -1], "=", 2)]
    r = solve_lp(lp("max", [1, 4, -3], rows), "simplex")
    assert r["status"] == "optimal"
    assert r["solution"]["F"] == "1"
    assert r["solution"]["x"] == ["5/2", "0", "1/2"]
    first = r["iterations"][0]
    assert first["delta"][:5] == ["-1", "-4", "3", "0", "0"]    # slide 36
    assert first["delta_m"][:5] == ["-5", "1", "3", "0", "1"]
    assert r["iterations"][-1]["basis"] == [4, 3, 1]


def test_infeasible_and_unbounded():
    r = solve_lp(lp("max", [1], [([1], "<=", 1), ([1], ">=", 2)]), "simplex")
    assert r["status"] == "infeasible"
    r = solve_lp(lp("max", [1, 0], [([1, -1], "<=", 1)]), "simplex")
    assert r["status"] == "unbounded"


def test_min_with_negative_rhs_and_free_vars():
    r = solve_lp(lp("min", [1, 2], [([1, 1], ">=", -4), ([1, -1], "<=", 3)], ["free", "ge0"]), "simplex")
    assert r["status"] == r["verify"]["status"]
    assert r["verify"]["agree"] is True


def test_dual_simplex():
    rows = [([2, 1, 0], ">=", 4), ([1, 2, 1], ">=", 5)]
    r = solve_lp(lp("min", [8, 7, 3], rows), "dual_simplex")
    assert r["status"] == "optimal"
    assert r["solution"]["F"] == "22" and r["solution"]["x"] == ["1", "2", "0"]
    assert r["verify"]["agree"] is True
    r2 = solve_lp(lp("max", [3, 2], [([1, 1], ">=", 2)]), "dual_simplex")
    assert r2["status"] == "not_dual_feasible"


def test_dual_form_slide11():
    p = lp("min", [8, 7, 3], [([2, 1, 0], ">=", 4), ([1, 2, 1], ">=", 5)])
    d = dualize(p)
    assert d.sense == "max" and d.c == [4, 5]
    assert d.A == [[2, 1], [1, 2], [0, 1]] and d.signs == ["<=", "<=", "<="]
    assert d.b == [8, 7, 3] and d.var_signs == ["ge0", "ge0"]
    out = dual_form(p)
    assert out["solved"]["equal"] is True and out["solved"]["primal"]["value"] == "22"


def test_dual_general_signs_strong_duality():
    p = lp("max", [3, 2, -1], [([1, 1, 1], "<=", 10), ([1, -1, 0], ">=", -2), ([0, 1, 1], "=", 4)],
           ["ge0", "ge0", "free"])
    out = dual_form(p)
    assert out["solved"]["equal"] is True


def test_complementary_slackness():
    p = lp("max", [4, 5], [([2, 1], "<=", 8), ([1, 2], "<=", 7), ([0, 1], "<=", 3)])
    ok = check_optimality(p, [F(3), F(2)])
    assert ok["verdict"] == "optimal" and ok["y"] == ["1", "2", "0"] and ok["f"] == ok["g"] == "22"
    assert check_optimality(p, [F(1), F(1)])["verdict"] == "not_optimal"
    assert check_optimality(p, [F(0), F(0)])["verdict"] == "not_optimal"
    assert check_optimality(p, [F(9), F(0)])["verdict"] == "infeasible_x"


def test_degenerate_complementary_slackness_certificate():
    p = lp("max", [-1, 2], [([0, 1], "<=", 0), ([0, -3], "<=", 1), ([3, 0], ">=", 3)])
    result = check_optimality(p, [F(1), F(0)])
    assert result["verdict"] == "optimal"
    assert result["f"] == result["g"] == "-1"


def test_zero_reduced_cost_does_not_prove_distinct_solution():
    r = solve_lp(lp("max", [0], [([1], "<=", 0)]), "simplex")
    assert r["solution"]["x"] == ["0"]
    assert not any("vô số phương án tối ưu" in note for note in r["notes"])


def test_infeasible_big_m_does_not_claim_primal_optimal():
    r = solve_lp(lp("max", [1], [([1], "<=", 1), ([1], ">=", 2)]), "simplex")
    assert r["status"] == "infeasible"
    assert all("phương án hiện tại là phương án tối ưu" not in line for it in r["iterations"] for line in it["decision"])


def _random_lp(rng):
    n, m = rng.randint(2, 4), rng.randint(2, 4)
    c = [rng.randint(-5, 5) for _ in range(n)]
    rows = [([rng.randint(-4, 6) for _ in range(n)], rng.choice(["<=", "<=", ">=", "="]), rng.randint(-3, 12))
            for _ in range(m)]
    vs = [rng.choice(["ge0", "ge0", "ge0", "le0", "free"]) for _ in range(n)]
    return rng.choice(["max", "min"]), c, rows, vs


def test_random_agrees_with_scipy():
    rng = random.Random(2026)
    for _ in range(400):
        sense, c, rows, vs = _random_lp(rng)
        r = solve_lp(lp(sense, c, rows, vs), "simplex")
        assert r["status"] != "iteration_limit"
        assert r["verify"]["agree"], (sense, c, rows, vs, r["status"], r["verify"])


def test_random_dual_simplex_agrees_with_scipy():
    rng = random.Random(7)
    for _ in range(300):
        n, m = rng.randint(2, 4), rng.randint(2, 4)
        c = [rng.randint(0, 6) for _ in range(n)]
        rows = [([rng.randint(-2, 5) for _ in range(n)], rng.choice([">=", ">=", "<="]), rng.randint(-2, 10))
                for _ in range(m)]
        r = solve_lp(lp("min", c, rows), "dual_simplex")
        assert r["status"] in ("optimal", "infeasible")
        assert r["verify"]["agree"], (c, rows, r["status"], r["verify"])

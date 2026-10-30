"""Kiểm thử bài toán vận tải với các ví dụ trong slide Bài 4."""
import random

from app.transport import solve_transport

C5 = [[20, 16, 18, 20, 17], [12, 15, 13, 15, 16], [8, 10, 17, 11, 13], [5, 12, 15, 18, 17], [13, 14, 16, 12, 16]]


def test_balanced_5x5_northwest():
    r = solve_transport([14, 6, 22, 12, 5], [15, 21, 7, 13, 3], C5, "northwest")
    assert r["balance"]["status"] == "balanced"
    assert r["initial"]["cost"] == "914"                      # slide 38
    assert r["initial"]["X"] == [
        ["14", None, None, None, None], ["1", "5", None, None, None], [None, "16", "6", None, None],
        [None, None, "1", "11", None], [None, None, None, "2", "3"]]
    assert r["solution"]["F"] == "649"
    assert r["verify"]["agree"] is True


def test_balanced_5x5_least_cost_same_optimum():
    r = solve_transport([14, 6, 22, 12, 5], [15, 21, 7, 13, 3], C5, "least_cost")
    assert r["solution"]["F"] == "649" and r["verify"]["agree"] is True


def test_supply_excess_slide_4_1():
    cost = [[14, 18, 12], [12, 22, 18], [7, 8, 9]]
    r = solve_transport([80, 100, 50], [60, 30, 20], cost, "least_cost")
    assert r["balance"]["dummy_col"] is True and r["balance"]["demand"][-1] == "120"
    assert r["initial"]["X"] == [[None, "30", "20", "30"], ["10", None, None, "90"], ["50", None, None, None]]
    assert r["solution"]["F"] == "1100"
    assert len(r["iterations"]) == 2                           # slide 31-32
    assert r["verify"]["agree"] is True


def test_demand_excess_slide_4_4_2():
    cost = [[3, 5, 6, 5], [4, 5, 7, 8], [3, 4, 4, 3]]
    r = solve_transport([80, 70, 50], [100, 50, 30, 70], cost, "least_cost")
    assert r["balance"]["dummy_row"] is True and r["balance"]["supply"][-1] == "50"
    assert r["initial"]["X"] == [["80", None, None, None], [None, "50", "20", None],
                                 ["20", None, None, "30"], [None, None, "10", "40"]]   # slide 50
    assert r["iterations"][0]["u"] == ["0", "4", "0", "-3"] and r["iterations"][0]["v"] == ["3", "1", "3", "3"]
    assert r["iterations"][0]["enter"] == [1, 0] and r["iterations"][0]["theta"] == "20"   # slide 70-73
    assert r["solution"]["F"] == "720"                         # slide 78
    assert r["solution"]["X"] == [["80", "0", "0", "0"], ["20", "50", "0", "0"], ["0", "0", "0", "50"]]


def test_degenerate_slide_example_2():
    cost = [[8, 13, 15, 11], [7, 11, 7, 9], [14, 12, 9, 8], [18, 14, 10, 4]]
    r = solve_transport([50, 40, 50, 60], [50, 75, 50, 25], cost, "least_cost")
    assert r["initial"]["added"] == [[1, 2]]                   # ô chọn không (2,3) như slide 39-40
    assert r["iterations"][0]["u"] == ["0", "-1", "1", "1"] and r["iterations"][0]["v"] == ["8", "13", "8", "3"]
    assert r["iterations"][0]["enter"] == [2, 1]               # ô vi phạm (3,2)
    assert r["solution"]["F"] == "1830"                        # slide 42
    assert any("phương án tối ưu khác" in n for n in r["notes"])   # slide 43


def test_unbalanced_4_4_1_example():
    r = solve_transport([14, 6, 22, 12, 5], [15, 21, 7, 10, 3], C5, "northwest")
    assert r["balance"]["status"] == "supply_excess" and r["balance"]["demand"][-1] == "3"
    assert r["verify"]["agree"] is True


def test_degenerate_zero_delta_not_proof_of_alternative():
    r = solve_transport([0, 1], [0, 1], [[0, 0], [0, 0]], "northwest")
    assert r["solution"]["X"] == [["0", "0"], ["0", "1"]]
    assert any("chưa thể kết luận" in n for n in r["notes"])
    assert not any("⇒ có phương án tối ưu khác" in n for n in r["notes"])


def test_row_and_column_initial_methods():
    cost = [[9, 1], [2, 8]]
    row = solve_transport([5, 5], [5, 5], cost, "least_cost_row")
    col = solve_transport([5, 5], [5, 5], cost, "least_cost_column")
    assert row["initial"]["steps"][0]["cell"] == [0, 1]
    assert col["initial"]["steps"][0]["cell"] == [1, 0]
    assert row["solution"]["F"] == col["solution"]["F"] == "15"
    assert row["verify"]["agree"] and col["verify"]["agree"]


def test_random_agrees_with_scipy():
    rng = random.Random(11)
    for _ in range(250):
        m, n = rng.randint(1, 6), rng.randint(1, 6)
        a = [rng.randint(0, 30) for _ in range(m)]
        b = [rng.randint(0, 30) for _ in range(n)]
        if sum(a) == 0 and sum(b) == 0:
            continue
        cost = [[rng.randint(0, 20) for _ in range(n)] for _ in range(m)]
        for method in ("northwest", "least_cost"):
            r = solve_transport(a, b, cost, method)
            assert r["status"] == "optimal", (a, b, cost, method)
            assert r["verify"] is None or r["verify"]["agree"] is not False, (a, b, cost, method, r["verify"])

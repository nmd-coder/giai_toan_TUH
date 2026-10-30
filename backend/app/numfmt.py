"""Tiện ích số học phân số và định dạng chuỗi.

Toàn bộ phép tính trong lời giải từng bước dùng `fractions.Fraction`
để kết quả hiển thị đúng dạng phân số như trong bài giảng (1/3, -2/3, ...).
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence

ZERO = Fraction(0)
ONE = Fraction(1)
MINUS = "\u2212"  # dấu trừ typographic

# Số M được biểu diễn bằng cặp (a, b) nghĩa là  a + b·M
Pair = tuple[Fraction, Fraction]


def to_frac(x) -> Fraction:
    """Đổi chuỗi/số người dùng nhập ('1/2', '0.25', '-3', 2) sang Fraction."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        raise ValueError("Giá trị không hợp lệ")
    if isinstance(x, int):
        return Fraction(x)
    s = str(x).strip().replace(",", ".").replace(" ", "")
    if s == "":
        raise ValueError("Có ô còn để trống")
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Không đọc được số '{x}'") from None


def fs(x: Fraction) -> str:
    """Fraction -> '5' hoặc '-2/3' (dùng dấu '-' ASCII để front-end dễ phân tích)."""
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def ft(x: Fraction) -> str:
    """Fraction -> chuỗi hiển thị trong câu chữ (dùng dấu trừ đẹp)."""
    s = fs(x)
    return s.replace("-", MINUS)


def _coef_text(mag: Fraction) -> str:
    if mag.denominator == 1:
        return str(mag.numerator)
    return f"({mag.numerator}/{mag.denominator})"


def lin_expr(coefs: Sequence[Fraction], names: Sequence[str]) -> str:
    """2x1 − x2 + (1/2)x3 ... ; trả '0' nếu mọi hệ số bằng 0."""
    out = ""
    for cf, nm in zip(coefs, names):
        if cf == 0:
            continue
        mag = abs(cf)
        term = nm if mag == 1 else f"{_coef_text(mag)}{nm}"
        if not out:
            out = (MINUS if cf < 0 else "") + term
        else:
            out += f" {MINUS if cf < 0 else '+'} {term}"
    return out or "0"


# ----- cặp (a + bM) -------------------------------------------------------

def padd(p: Pair, q: Pair) -> Pair:
    return (p[0] + q[0], p[1] + q[1])


def pscale(p: Pair, k: Fraction) -> Pair:
    return (p[0] * k, p[1] * k)


def pkey(p: Pair) -> tuple[Fraction, Fraction]:
    """Khoá so sánh: so hệ số của M trước (M là số rất lớn), rồi tới phần hằng."""
    return (p[1], p[0])


def pneg(p: Pair) -> bool:
    return pkey(p) < (ZERO, ZERO)


def pair_text(p: Pair) -> str:
    a, b = p
    if b == 0:
        return fs(a)
    m = "M" if abs(b) == 1 else f"{fs(abs(b))}M"
    m_signed = (MINUS if b < 0 else "") + m
    if a == 0:
        return m_signed
    return f"{fs(a)} {MINUS if b < 0 else '+'} {m}"


def pair_expr(pairs: Sequence[Pair], names: Sequence[str]) -> str:
    """Biểu thức tuyến tính có hệ số dạng a + bM, ví dụ 'x1 + 4x2 − Mx6'."""
    out = ""
    for p, nm in zip(pairs, names):
        a, b = p
        if a == 0 and b == 0:
            continue
        if b == 0:
            neg = a < 0
            mag = abs(a)
            term = nm if mag == 1 else f"{_coef_text(mag)}{nm}"
        elif a == 0:
            neg = b < 0
            mag = abs(b)
            term = f"M{nm}" if mag == 1 else f"{_coef_text(mag)}M{nm}"
        else:
            neg = False
            term = f"({pair_text(p)}){nm}"
        if not out:
            out = (MINUS if neg else "") + term
        else:
            out += f" {MINUS if neg else '+'} {term}"
    return out or "0"


def vec_text(xs: Iterable[Fraction]) -> str:
    return "(" + ", ".join(fs(x) for x in xs) + ")"

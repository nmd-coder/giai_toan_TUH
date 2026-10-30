import { Fragment, type ReactNode } from 'react';

/** Đổi x1, y2, A3, Δ4, u1, v2, c12, Z1,2 ... thành chỉ số dưới. */
const VAR_RE = /(?<![\p{L}\d])([xyuvcabAZ\u0394])(\d+(?:,\d+)?)('?)/gu;

export function Txt({ text }: { text: string }) {
  const out: ReactNode[] = [];
  let last = 0;
  let k = 0;
  for (const m of text.matchAll(VAR_RE)) {
    const idx = m.index ?? 0;
    if (idx > last) out.push(text.slice(last, idx));
    out.push(
      <Fragment key={k++}>
        <i className="v">{m[1]}</i>
        <sub>{m[2]}</sub>
        {m[3]}
      </Fragment>,
    );
    last = idx + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return <>{out}</>;
}

const FRAC = /^(-?)(\d+)\/(\d+)$/;

/** Hiển thị số: phân số dạng xếp chồng, dấu trừ đẹp. */
export function Num({ v, className }: { v: string | null | undefined; className?: string }) {
  if (v === null || v === undefined) return <span className={className} />;
  const m = FRAC.exec(v);
  if (m) {
    return (
      <span className={`num ${className ?? ''}`}>
        {m[1] && <span className="minus">−</span>}
        <span className="frac">
          <span>{m[2]}</span>
          <span>{m[3]}</span>
        </span>
      </span>
    );
  }
  // biểu thức có M: "-2 - 4M", "-M", ...
  const text = v.replace(/-/g, '−');
  return <span className={`num ${className ?? ''}`}>{text}</span>;
}

export function Lines({ lines }: { lines: string[] }) {
  return (
    <>
      {lines.map((l, i) => (
        <p key={i} className="line">
          <Txt text={l} />
        </p>
      ))}
    </>
  );
}

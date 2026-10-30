import { useEffect, useState, type ReactNode } from 'react';
import type { VerifyInfo } from '../types';

export function numberInputProps(value: string, nonnegative = false) {
  const s = value.trim().replace(',', '.');
  const fraction = /^([+-]?\d+)\/(\d+)$/.exec(s);
  const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s);
  const n = fraction ? Number(fraction[1]) / Number(fraction[2]) : decimal ? Number(s) : NaN;
  const invalid = !Number.isFinite(n) || (nonnegative && n < 0);
  return { 'aria-invalid': invalid, title: invalid ? (nonnegative ? 'Nhập số không âm, ví dụ 3, 0.5 hoặc 1/3.' : 'Nhập số hợp lệ, ví dụ -3, 0.5 hoặc 1/3.') : undefined };
}

export function Segmented<T extends string>({ value, onChange, options, label }: {
  value: T; onChange: (v: T) => void; options: { value: T; label: string; hint?: string }[]; label: string;
}) {
  return (
    <div className="seg" role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={value === o.value}
          className={value === o.value ? 'on' : ''}
          title={o.hint}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Stepper({ label, value, min, max, onChange }: {
  label: string; value: number; min: number; max: number; onChange: (n: number) => void;
}) {
  return (
    <div className="stepper">
      <span>{label}</span>
      <button type="button" aria-label={`Giảm ${label}`} disabled={value <= min} onClick={() => onChange(value - 1)}>−</button>
      <b>{value}</b>
      <button type="button" aria-label={`Tăng ${label}`} disabled={value >= max} onClick={() => onChange(value + 1)}>+</button>
    </div>
  );
}

export function Alert({ kind, children }: { kind: 'error' | 'ok' | 'warn' | 'info'; children: ReactNode }) {
  return <div className={`alert ${kind}`} role={kind === 'error' ? 'alert' : undefined}>{children}</div>;
}

export function Section({ title, children, aside }: { title: string; children: ReactNode; aside?: ReactNode }) {
  return (
    <section className="block">
      <header className="block-h">
        <h3>{title}</h3>
        {aside}
      </header>
      {children}
    </section>
  );
}

export function IterationNavigator({ steps }: { steps: ReactNode[] }) {
  const [index, setIndex] = useState(0);
  useEffect(() => setIndex(0), [steps.length]);
  if (!steps.length) return null;
  const current = Math.min(index, steps.length - 1);
  return <div className="iteration-nav">
    <div className="iteration-controls" aria-label="Điều hướng các bước lặp">
      <button type="button" disabled={current === 0} onClick={() => setIndex(current - 1)}>← Bước trước</button>
      <span aria-live="polite">Bước lặp <b>{current + 1}</b> / {steps.length}</span>
      <button type="button" disabled={current === steps.length - 1} onClick={() => setIndex(current + 1)}>Bước tiếp →</button>
    </div>
    {steps.map((step, i) => <div key={i} className={i === current ? 'iteration-page active' : 'iteration-page'}>{step}</div>)}
  </div>;
}

export function VerifyBadge({ v }: { v: VerifyInfo | null | undefined }) {
  if (!v || !v.available) return null;
  if (v.agree === null) return <span className="badge neutral">SciPy: không kết luận</span>;
  return v.agree
    ? <span className="badge good" title="Trạng thái và giá trị mục tiêu được đối chiếu với SciPy (HiGHS); không kiểm tra từng bước.">✓ Khớp SciPy</span>
    : <span className="badge bad" title="Kết quả lệch so với SciPy">⚠ Lệch SciPy</span>;
}

import type { LPForm, Sign, VarSign } from '../types';
import { numberInputProps, Stepper } from './ui';

const SIGNS: { v: Sign; t: string }[] = [{ v: '<=', t: '≤' }, { v: '>=', t: '≥' }, { v: '=', t: '=' }];
const VSIGNS: { v: VarSign; t: string }[] = [{ v: 'ge0', t: '≥ 0' }, { v: 'le0', t: '≤ 0' }, { v: 'free', t: 'tùy ý' }];

const sub = (n: number) => (
  <span className="vh">x<sub>{n}</sub></span>
);

export function resize(f: LPForm, n: number, m: number): LPForm {
  const c = Array.from({ length: n }, (_, j) => f.c[j] ?? '0');
  const varSigns = Array.from({ length: n }, (_, j) => f.varSigns[j] ?? 'ge0');
  const rows = Array.from({ length: m }, (_, i) => {
    const old = f.rows[i];
    return {
      a: Array.from({ length: n }, (_, j) => old?.a[j] ?? '0'),
      sign: old?.sign ?? ('<=' as Sign),
      b: old?.b ?? '0',
    };
  });
  return { ...f, c, varSigns, rows };
}

export default function LPFormEditor({ form, onChange }: { form: LPForm; onChange: (f: LPForm) => void }) {
  const n = form.c.length;
  const m = form.rows.length;
  const setC = (j: number, v: string) => onChange({ ...form, c: form.c.map((x, k) => (k === j ? v : x)) });
  const setA = (i: number, j: number, v: string) =>
    onChange({ ...form, rows: form.rows.map((r, k) => (k === i ? { ...r, a: r.a.map((x, q) => (q === j ? v : x)) } : r)) });
  const setRow = (i: number, patch: Partial<LPForm['rows'][number]>) =>
    onChange({ ...form, rows: form.rows.map((r, k) => (k === i ? { ...r, ...patch } : r)) });
  const setVS = (j: number, v: VarSign) => onChange({ ...form, varSigns: form.varSigns.map((x, k) => (k === j ? v : x)) });

  return (
    <div className="editor">
      <div className="editor-bar">
        <div className="seg small" role="radiogroup" aria-label="Hướng tối ưu">
          {(['max', 'min'] as const).map((s) => (
            <button key={s} type="button" role="radio" aria-checked={form.sense === s}
              className={form.sense === s ? 'on' : ''} onClick={() => onChange({ ...form, sense: s })}>
              {s === 'max' ? 'Max' : 'Min'}
            </button>
          ))}
        </div>
        <Stepper label="Số biến" value={n} min={1} max={20} onChange={(k) => onChange(resize(form, k, m))} />
        <Stepper label="Số ràng buộc" value={m} min={1} max={20} onChange={(k) => onChange(resize(form, n, k))} />
      </div>

      <div className="grid-scroll">
        <table className="lp-grid">
          <thead>
            <tr>
              <th />
              {form.c.map((_, j) => <th key={j}>{sub(j + 1)}</th>)}
              <th /><th />
            </tr>
          </thead>
          <tbody>
            <tr className="obj">
              <th className="rowh">f(x) =</th>
              {form.c.map((v, j) => (
                <td key={j}><input {...numberInputProps(v)} aria-label={`Hệ số hàm mục tiêu x${j + 1}`} inputMode="decimal" value={v} onChange={(e) => setC(j, e.target.value)} /></td>
              ))}
              <td colSpan={2} className="muted">→ {form.sense}</td>
            </tr>
            {form.rows.map((r, i) => (
              <tr key={i}>
                <th className="rowh">({i + 1})</th>
                {r.a.map((v, j) => (
                  <td key={j}><input {...numberInputProps(v)} aria-label={`Ràng buộc ${i + 1}, hệ số x${j + 1}`} inputMode="decimal" value={v} onChange={(e) => setA(i, j, e.target.value)} /></td>
                ))}
                <td>
                  <select aria-label={`Dấu ràng buộc ${i + 1}`} value={r.sign} onChange={(e) => setRow(i, { sign: e.target.value as Sign })}>
                    {SIGNS.map((s) => <option key={s.v} value={s.v}>{s.t}</option>)}
                  </select>
                </td>
                <td><input {...numberInputProps(r.b)} aria-label={`Vế phải ràng buộc ${i + 1}`} inputMode="decimal" value={r.b} onChange={(e) => setRow(i, { b: e.target.value })} /></td>
              </tr>
            ))}
            <tr className="vsigns">
              <th className="rowh">Dấu biến</th>
              {form.varSigns.map((v, j) => (
                <td key={j}>
                  <select aria-label={`Điều kiện dấu x${j + 1}`} value={v} onChange={(e) => setVS(j, e.target.value as VarSign)}>
                    {VSIGNS.map((s) => <option key={s.v} value={s.v}>{s.t}</option>)}
                  </select>
                </td>
              ))}
              <td colSpan={2} />
            </tr>
          </tbody>
        </table>
      </div>
      <p className="hint">Nhập số nguyên, thập phân (0.5) hoặc phân số (1/3). Ô viền đỏ có dữ liệu chưa hợp lệ. Bảng rộng có thể cuộn ngang.</p>
    </div>
  );
}

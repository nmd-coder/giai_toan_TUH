import type { TPForm } from '../types';
import { numberInputProps, Stepper } from './ui';

export function resizeTP(f: TPForm, m: number, n: number): TPForm {
  return {
    supply: Array.from({ length: m }, (_, i) => f.supply[i] ?? '0'),
    demand: Array.from({ length: n }, (_, j) => f.demand[j] ?? '0'),
    cost: Array.from({ length: m }, (_, i) => Array.from({ length: n }, (_, j) => f.cost[i]?.[j] ?? '0')),
  };
}

export default function TPFormEditor({ form, onChange }: { form: TPForm; onChange: (f: TPForm) => void }) {
  const m = form.supply.length;
  const n = form.demand.length;
  const setCost = (i: number, j: number, v: string) =>
    onChange({ ...form, cost: form.cost.map((r, a) => (a === i ? r.map((x, b) => (b === j ? v : x)) : r)) });
  return (
    <div className="editor">
      <div className="editor-bar">
        <Stepper label="Điểm phát" value={m} min={1} max={15} onChange={(k) => onChange(resizeTP(form, k, n))} />
        <Stepper label="Điểm thu" value={n} min={1} max={15} onChange={(k) => onChange(resizeTP(form, m, k))} />
      </div>
      <div className="grid-scroll">
        <table className="lp-grid tp-grid">
          <thead>
            <tr>
              <th className="corner">Phát \ Thu</th>
              {form.demand.map((_, j) => <th key={j}><span className="vh">B<sub>{j + 1}</sub></span></th>)}
              <th><span className="vh">a<sub>i</sub></span></th>
            </tr>
          </thead>
          <tbody>
            {form.cost.map((row, i) => (
              <tr key={i}>
                <th className="rowh"><span className="vh">A<sub>{i + 1}</sub></span></th>
                {row.map((v, j) => (
                  <td key={j}><input {...numberInputProps(v)} aria-label={`Cước phí c${i + 1}${j + 1}`} inputMode="decimal" value={v} onChange={(e) => setCost(i, j, e.target.value)} /></td>
                ))}
                <td className="sup"><input {...numberInputProps(form.supply[i], true)} aria-label={`Lượng phát a${i + 1}`} inputMode="decimal" value={form.supply[i]}
                  onChange={(e) => onChange({ ...form, supply: form.supply.map((x, k) => (k === i ? e.target.value : x)) })} /></td>
              </tr>
            ))}
            <tr>
              <th className="rowh"><span className="vh">b<sub>j</sub></span></th>
              {form.demand.map((v, j) => (
                <td key={j} className="sup"><input {...numberInputProps(v, true)} aria-label={`Lượng thu b${j + 1}`} inputMode="decimal" value={v}
                  onChange={(e) => onChange({ ...form, demand: form.demand.map((x, k) => (k === j ? e.target.value : x)) })} /></td>
              ))}
              <td />
            </tr>
          </tbody>
        </table>
      </div>
      <p className="hint">Ô giữa là cước phí c<sub>ij</sub>; cột phải là lượng phát a<sub>i</sub>; hàng dưới là lượng thu b<sub>j</sub>. Lượng phát, thu phải không âm. Ô viền đỏ có dữ liệu chưa hợp lệ; bảng rộng có thể cuộn ngang.</p>
    </div>
  );
}

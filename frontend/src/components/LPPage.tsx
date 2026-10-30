import { useState } from 'react';
import { checkOptimal, dualForm, solveGraph, solveLP } from '../api';
import { LP_CUSTOM_EXAMPLES } from '../examples';
import type { CheckResult, DualFormResult, GraphResult, LPForm, LPMethod, LPSolveResult } from '../types';
import GraphView from './GraphView';
import LPFormEditor from './LPFormEditor';
import { CheckView, DualFormView, SimplexView } from './LPResult';
import { Alert, numberInputProps } from './ui';

const OPTIONS: { value: LPMethod; label: string; hint: string }[] = [
  { value: 'simplex', label: 'Đơn hình', hint: 'Bài 2 – đơn hình, phương pháp M khi có biến giả' },
  { value: 'graph', label: 'Hình học (2 biến)', hint: 'Biểu diễn miền nghiệm và xét các đỉnh' },
  { value: 'dual_simplex', label: 'Đơn hình đối ngẫu', hint: 'Bài 3 – thuật toán đơn hình đối ngẫu' },
  { value: 'dual_form', label: 'Lập bài toán đối ngẫu', hint: 'Bài 3 – bảng quy tắc chuyển sang đối ngẫu' },
  { value: 'check', label: 'Kiểm tra độ lệch bù', hint: 'Bài 3 – kiểm tra một phương án có tối ưu không' },
];

type Out =
  | { kind: 'solve'; data: LPSolveResult }
  | { kind: 'dual'; data: DualFormResult }
  | { kind: 'graph'; data: GraphResult; form: LPForm }
  | { kind: 'check'; data: CheckResult };

export default function LPPage() {
  const [form, setForm] = useState<LPForm>(LP_CUSTOM_EXAMPLES[0].form);
  const [method, setMethod] = useState<LPMethod>('simplex');
  const [x, setX] = useState<string[]>(['3', '2']);
  const [out, setOut] = useState<Out | null>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  const n = form.c.length;
  const xs = Array.from({ length: n }, (_, j) => x[j] ?? '0');

  const loadExample = (i: number) => {
    const ex = LP_CUSTOM_EXAMPLES[i];
    setForm(ex.form);
    setMethod(ex.method);
    if (ex.x) setX(ex.x);
    setOut(null);
    setErr('');
  };

  const run = async (m: LPMethod = method) => {
    setBusy(true);
    setErr('');
    try {
      if (m === 'simplex' || m === 'dual_simplex') setOut({ kind: 'solve', data: await solveLP(form, m) });
      else if (m === 'graph') setOut({ kind: 'graph', data: await solveGraph(form), form });
      else if (m === 'dual_form') setOut({ kind: 'dual', data: await dualForm(form) });
      else setOut({ kind: 'check', data: await checkOptimal(form, xs) });
    } catch (e) {
      setOut(null);
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <div className="card-h">
          <h2>Đề bài quy hoạch tuyến tính</h2>
          <select className="examples" aria-label="Nạp đề mẫu" defaultValue="" onChange={(e) => { if (e.target.value !== '') loadExample(Number(e.target.value)); e.target.value = ''; }}>
            <option value="" disabled>Nạp đề mẫu…</option>
            {LP_CUSTOM_EXAMPLES.map((ex, i) => <option key={i} value={i}>{ex.label}</option>)}
          </select>
        </div>
        <LPFormEditor form={form} onChange={(f) => { setForm(f); setOut(null); setErr(''); }} />
        <div className="method-row">
          <div className="method-choice">
            <label htmlFor="lp-method">Phương pháp</label>
            <select id="lp-method" value={method} onChange={(e) => { setMethod(e.target.value as LPMethod); setOut(null); setErr(''); }}>
              <optgroup label="Giải bài toán">
                {OPTIONS.filter(o => ['simplex', 'graph', 'dual_simplex'].includes(o.value)).map(o => <option key={o.value} value={o.value} disabled={o.value === 'graph' && n !== 2}>{o.label}</option>)}
              </optgroup>
              <optgroup label="Đối ngẫu và kiểm tra">
                {OPTIONS.filter(o => ['dual_form', 'check'].includes(o.value)).map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </optgroup>
            </select>
            <span>{method === 'graph' && n !== 2 ? 'Phương pháp hình học cần đúng 2 biến.' : OPTIONS.find(o => o.value === method)?.hint}</span>
          </div>
          {method === 'check' && (
            <div className="xvec">
              <span>Phương án x =</span>
              {xs.map((v, j) => (
                <label key={j}><span className="vh">x<sub>{j + 1}</sub></span>
                  <input {...numberInputProps(v)} aria-label={`Giá trị phương án x${j + 1}`} inputMode="decimal" value={v} onChange={(e) => { setX(xs.map((o, k) => (k === j ? e.target.value : o))); setOut(null); setErr(''); }} />
                </label>
              ))}
            </div>
          )}
          <button type="button" className="primary" disabled={busy || (method === 'graph' && n !== 2)} onClick={() => run()}>
            {busy ? 'Đang giải…' : method === 'dual_form' ? 'Lập đối ngẫu' : method === 'check' ? 'Kiểm tra' : 'Giải bài toán'}
          </button>
        </div>
      </div>

      {err && <Alert kind="error">{err}</Alert>}
      {out && <div className="result-actions"><button type="button" onClick={() => window.print()}>In / lưu PDF lời giải</button><span>Chọn “Lưu dưới dạng PDF” trong hộp thoại in.</span></div>}
      {out?.kind === 'solve' && (
        <>
          <SimplexViewWithFallback data={out.data} onFallback={() => { setMethod('simplex'); void run('simplex'); }} />
        </>
      )}
      {out?.kind === 'dual' && <DualFormView data={out.data} />}
      {out?.kind === 'graph' && <GraphView data={out.data} form={out.form} />}
      {out?.kind === 'check' && <CheckView data={out.data} />}
    </div>
  );
}

function SimplexViewWithFallback({ data, onFallback }: { data: LPSolveResult; onFallback: () => void }) {
  return (
    <>
      <SimplexView data={data} />
      {data.status === 'not_dual_feasible' && (
        <div className="fallback"><button type="button" className="primary" onClick={onFallback}>Giải bằng đơn hình (phương pháp M)</button></div>
      )}
    </>
  );
}

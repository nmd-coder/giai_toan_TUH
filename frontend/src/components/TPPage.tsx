import { useState } from 'react';
import { solveTP } from '../api';
import { TP_CUSTOM_EXAMPLES } from '../examples';
import type { TPForm, TPMethod, TPResult } from '../types';
import TPFormEditor from './TPFormEditor';
import TPResultView from './TPResult';
import { Alert } from './ui';

export default function TPPage() {
  const [form, setForm] = useState<TPForm>(TP_CUSTOM_EXAMPLES[0].form);
  const [method, setMethod] = useState<TPMethod>('northwest');
  const [out, setOut] = useState<TPResult | null>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setErr('');
    try {
      setOut(await solveTP(form, method));
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
          <h2>Đề bài vận tải</h2>
          <select className="examples" aria-label="Nạp đề mẫu" defaultValue=""
            onChange={(e) => {
              if (e.target.value === '') return;
              const ex = TP_CUSTOM_EXAMPLES[Number(e.target.value)];
              setForm(ex.form); setMethod(ex.method); setOut(null); setErr('');
              e.target.value = '';
            }}>
            <option value="" disabled>Nạp đề mẫu…</option>
            {TP_CUSTOM_EXAMPLES.map((ex, i) => <option key={i} value={i}>{ex.label}</option>)}
          </select>
        </div>
        <TPFormEditor form={form} onChange={(f) => { setForm(f); setOut(null); setErr(''); }} />
        <div className="method-row">
          <div className="method-choice">
            <label htmlFor="tp-method">Phương án xuất phát</label>
            <select id="tp-method" value={method} onChange={(e) => { setMethod(e.target.value as TPMethod); setOut(null); setErr(''); }}>
              <option value="northwest">Góc Tây–Bắc</option><option value="least_cost">Cực tiểu cước phí toàn bảng</option>
              <option value="least_cost_row">Cực tiểu cước phí theo hàng</option><option value="least_cost_column">Cực tiểu cước phí theo cột</option>
            </select>
            <span>{ { northwest: 'Bắt đầu từ ô trên cùng bên trái.', least_cost: 'Chọn ô có cước phí nhỏ nhất trong bảng còn lại.', least_cost_row: 'Lần lượt xét từng hàng.', least_cost_column: 'Lần lượt xét từng cột.' }[method] } Sau đó cải thiện bằng phương pháp thế vị.</span>
          </div>
          <button type="button" className="primary" disabled={busy} onClick={run}>{busy ? 'Đang giải…' : 'Giải bài toán'}</button>
        </div>
      </div>
      {err && <Alert kind="error">{err}</Alert>}
      {out && <div className="result-actions"><button type="button" onClick={() => window.print()}>In / lưu PDF lời giải</button><span>Chọn “Lưu dưới dạng PDF” trong hộp thoại in.</span></div>}
      {out && <TPResultView data={out} />}
    </div>
  );
}

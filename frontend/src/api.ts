import type { CheckResult, DualFormResult, GraphResult, LPForm, LPMethod, LPSolveResult, TPForm, TPMethod, TPResult } from './types';

async function post<T>(url: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  } catch {
    throw new Error('Không kết nối được backend. Hãy chắc chắn server Python đang chạy ở cổng 8000.');
  }
  if (!res.ok) {
    let msg = `Lỗi ${res.status}`;
    try {
      const j = await res.json();
      if (typeof j.detail === 'string') msg = j.detail;
      else if (Array.isArray(j.detail)) msg = 'Dữ liệu nhập chưa hợp lệ, hãy kiểm tra lại các ô.';
    } catch { /* giữ msg mặc định */ }
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

const lpBody = (f: LPForm) => ({
  sense: f.sense,
  c: f.c,
  constraints: f.rows.map((r) => ({ a: r.a, sign: r.sign, b: r.b })),
  var_signs: f.varSigns,
});

export const solveLP = (f: LPForm, method: 'simplex' | 'dual_simplex') =>
  post<LPSolveResult>('/api/lp/solve', { ...lpBody(f), method });
export const solveGraph = (f: LPForm) => post<GraphResult>('/api/lp/graph', lpBody(f));
export const dualForm = (f: LPForm) => post<DualFormResult>('/api/lp/dual', lpBody(f));
export const checkOptimal = (f: LPForm, x: string[]) => post<CheckResult>('/api/lp/check', { ...lpBody(f), x });
export const solveTP = (f: TPForm, method: TPMethod) =>
  post<TPResult>('/api/transport/solve', { supply: f.supply, demand: f.demand, cost: f.cost, method });

export type { LPMethod };

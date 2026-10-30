import type { Cell, TPIter, TPResult } from '../types';
import { Lines, Num, Txt } from './Math';
import { IterationNavigator, Section, VerifyBadge } from './ui';

interface TableProps {
  supply: string[]; demand: string[]; cost: string[][];
  X: (string | null)[][];
  dummyRow?: boolean; dummyCol?: boolean;
  u?: string[]; v?: string[];
  delta?: (string | null)[][];
  enter?: Cell | null;
  leave?: Cell | null;
  cycle?: TPIter['cycle'];
  order?: Map<string, number>;
  zero?: Set<string>;
}

const key = (i: number, j: number) => `${i},${j}`;

export function TPTable(p: TableProps) {
  const m = p.supply.length;
  const n = p.demand.length;
  const cyc = new Map<string, '+' | '-'>();
  p.cycle?.forEach((c) => cyc.set(key(c.cell[0], c.cell[1]), c.sign));
  const hasPot = !!p.u && !!p.v;
  return (
    <div className="grid-scroll">
      <table className="tp">
        <thead>
          <tr>
            <th className="corner">Phát \ Thu</th>
            {p.demand.map((b, j) => (
              <th key={j} className={p.dummyCol && j === n - 1 ? 'dummy' : ''}>
                <span className="vh">B<sub>{j + 1}</sub></span>{p.dummyCol && j === n - 1 && <em> ảo</em>}
                <div className="cap"><Num v={b} /></div>
              </th>
            ))}
            {hasPot && <th className="pot">u<sub>i</sub></th>}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: m }, (_, i) => (
            <tr key={i}>
              <th className={p.dummyRow && i === m - 1 ? 'dummy' : ''}>
                <span className="vh">A<sub>{i + 1}</sub></span>{p.dummyRow && i === m - 1 && <em> ảo</em>}
                <div className="cap"><Num v={p.supply[i]} /></div>
              </th>
              {Array.from({ length: n }, (_, j) => {
                const x = p.X[i][j];
                const inBasis = x !== null;
                const k = key(i, j);
                const isEnter = !!p.enter && p.enter[0] === i && p.enter[1] === j;
                const isLeave = !!p.leave && p.leave[0] === i && p.leave[1] === j;
                const sign = cyc.get(k);
                const d = p.delta?.[i][j];
                const dummy = (p.dummyRow && i === m - 1) || (p.dummyCol && j === n - 1);
                return (
                  <td key={j} className={['cell', inBasis ? 'basis' : '', isEnter ? 'enter' : '', isLeave ? 'leave' : '', dummy ? 'dummy' : '', sign ? 'in-cycle' : ''].join(' ')}>
                    <span className="c"><Num v={p.cost[i][j]} /></span>
                    {inBasis && <span className={`x ${x === '0' ? 'zero' : ''}`}><Num v={x} /></span>}
                    {p.order?.has(k) && <span className="ord">{p.order.get(k)}</span>}
                    {d != null && !isEnter && <span className={`d ${d.startsWith('-') || d === '0' ? 'nonpos' : 'pos'}`}>Δ={d.replace('-', '−')}</span>}
                    {isEnter && <span className="d pos">Δ={p.delta?.[i][j]}</span>}
                    {sign && <span className={`sgn ${sign === '+' ? 'plus' : 'minus'}`}>{sign === '+' ? '+' : '−'}</span>}
                  </td>
                );
              })}
              {hasPot && <th className="pot"><Num v={p.u![i]} /></th>}
            </tr>
          ))}
          {hasPot && (
            <tr>
              <th className="pot">v<sub>j</sub></th>
              {p.v!.map((v, j) => <th key={j} className="pot"><Num v={v} /></th>)}
              <td />
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

const BAL_TITLE = {
  balanced: 'Bước 1. Kiểm tra cân bằng thu phát',
  supply_excess: 'Bước 1. Không cân bằng – tổng phát lớn hơn tổng thu',
  demand_excess: 'Bước 1. Không cân bằng – tổng phát nhỏ hơn tổng thu',
};

export default function TPResultView({ data }: { data: TPResult }) {
  const b = data.balance;
  const ord = new Map<string, number>();
  data.initial.steps.forEach((s, k) => ord.set(key(s.cell[0], s.cell[1]), k + 1));
  const methodName = { northwest: 'góc Tây–Bắc', least_cost: 'cước phí nhỏ nhất toàn bảng', least_cost_row: 'cực tiểu cước phí theo hàng', least_cost_column: 'cực tiểu cước phí theo cột' }[data.method];
  const sol = data.solution;
  const m0 = data.problem.supply.length;
  const n0 = data.problem.demand.length;
  return (
    <div className="result">
      {sol ? (
        <div className="answer">
          <div>
            <span className="answer-k">Chi phí vận chuyển nhỏ nhất</span>
            <span className="answer-v">F<sub>min</sub> = <Num v={sol.F} /></span>
          </div>
          <div>
            <span className="answer-k">Phương án xuất phát ({methodName})</span>
            <span className="answer-v small">F = <Num v={data.initial.cost} /></span>
          </div>
          <VerifyBadge v={data.verify} />
        </div>
      ) : (
        <div className="alert error">Không giải được bài toán (quá số vòng lặp cho phép).</div>
      )}

      <Section title="Bài toán">
        <TPTable supply={data.problem.supply} demand={data.problem.demand} cost={data.problem.cost}
          X={Array.from({ length: m0 }, () => Array.from({ length: n0 }, () => null))} />
      </Section>

      <Section title={BAL_TITLE[b.status]}>
        <div className="math-box"><Lines lines={b.lines} /></div>
        {b.status !== 'balanced' && (
          <TPTable supply={b.supply} demand={b.demand} cost={b.cost} dummyRow={b.dummy_row} dummyCol={b.dummy_col}
            X={Array.from({ length: b.supply.length }, () => Array.from({ length: b.demand.length }, () => null))} />
        )}
      </Section>

      <Section title={`Bước 2. Phương án cực biên xuất phát – phương pháp ${methodName}`}>
        <ol className="alloc">
          {data.initial.steps.map((s, i) => (
            <li key={i}><Txt text={s.text} /></li>
          ))}
        </ol>
        <TPTable supply={b.supply} demand={b.demand} cost={b.cost} dummyRow={b.dummy_row} dummyCol={b.dummy_col}
          X={data.initial.X} order={ord} />
        <div className="math-box"><Lines lines={data.initial.lines} /></div>
      </Section>

      <p className="legend">Trong bảng: cước phí ở góc, lượng phân phối ở giữa; ô viền xanh thuộc cơ sở, ô đỏ vào cơ sở, viền nét đứt ra khỏi cơ sở. Dấu +/− chỉ chu trình điều chỉnh. Vuốt ngang trong bảng để xem các cột bị khuất.</p>
      <IterationNavigator steps={data.iterations.map((it) => (
        <Section key={it.t} title={`Lặp lần ${it.t}`} aside={<span className="chip">F = {it.cost}</span>}>
          <div className="math-box pot-lines">
            <p className="line"><b>Bước 3. Thế vị</b> (với ô sử dụng: u<sub>i</sub> + v<sub>j</sub> = c<sub>ij</sub>)</p>
            <div className="pot-list">{it.potential_lines.map((l, i) => <span key={i}><Txt text={l} /></span>)}</div>
          </div>
          <p className="line cap-line"><b>Bước 4.</b> Δ<sub>ij</sub> = u<sub>i</sub> + v<sub>j</sub> − c<sub>ij</sub> cho các ô chưa sử dụng; hình dưới ghi số lượng x<sub>ij</sub> ở giữa ô, cước phí c<sub>ij</sub> ở góc.</p>
          <TPTable supply={b.supply} demand={b.demand} cost={b.cost} dummyRow={b.dummy_row} dummyCol={b.dummy_col}
            X={it.X} u={it.u} v={it.v} delta={it.delta} enter={it.enter} leave={it.leave} cycle={it.cycle} />
          <div className="decision">
            <p className="line"><b>Bước 5{it.optimal ? '.' : ' – 6.'}</b></p>
            <Lines lines={it.decision} />
          </div>
        </Section>
      ))} />

      {sol && (
        <Section title="Kết luận">
          <div className="grid-scroll">
            <table className="tp result-x">
              <thead>
                <tr><th className="corner">x<sub>ij</sub></th>{data.problem.demand.map((_, j) => <th key={j}><span className="vh">B<sub>{j + 1}</sub></span></th>)}
                  {sol.leftover?.kind === 'supply' && <th className="dummy">Còn dư</th>}</tr>
              </thead>
              <tbody>
                {sol.X.map((r, i) => (
                  <tr key={i}>
                    <th><span className="vh">A<sub>{i + 1}</sub></span></th>
                    {r.map((v, j) => <td key={j} className={`cell ${v !== '0' ? 'basis' : ''}`}><span className="x"><Num v={v} /></span></td>)}
                    {sol.leftover?.kind === 'supply' && <td className="cell dummy"><span className="x"><Num v={sol.leftover.values[i]} /></span></td>}
                  </tr>
                ))}
                {sol.leftover?.kind === 'demand' && (
                  <tr>
                    <th className="dummy">Còn thiếu</th>
                    {sol.leftover.values.map((v, j) => <td key={j} className="cell dummy"><span className="x"><Num v={v} /></span></td>)}
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="math-box">
            <p className="line">F<sub>min</sub> = <Num v={sol.F} />.</p>
            {data.notes.map((n, i) => <p key={i} className="line note"><Txt text={n} /></p>)}
          </div>
        </Section>
      )}
    </div>
  );
}

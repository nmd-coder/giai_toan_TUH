import type { CheckResult, DualFormResult, LPColumns, LPSolveResult, SimplexIter } from '../types';
import { Lines, Num, Txt } from './Math';
import { Alert, IterationNavigator, Section, VerifyBadge } from './ui';

function Tableau({ it, cols, dual }: { it: SimplexIter; cols: LPColumns; dual: boolean }) {
  const enter = it.enter !== null ? it.enter - 1 : -1;
  const leave = it.leave_row;
  const removed = new Set(it.removed.map((k) => k - 1));
  const showTheta = !dual && it.ratios_rows !== null;
  const cls = (k: number) => [k === enter ? 'col-enter' : '', removed.has(k) ? 'gone' : ''].join(' ');
  return (
    <div className="grid-scroll">
      <table className="tableau">
        <thead>
          <tr>
            <th colSpan={3} className="cj-label">c<sub>j</sub></th>
            {cols.c.map((c, k) => <th key={k} className={`cj ${cls(k)}`}><Num v={c} /></th>)}
            {showTheta && <th rowSpan={2} className="theta-h">θ</th>}
          </tr>
          <tr>
            <th>Hệ số c<sub>j</sub></th><th>Cơ sở</th><th>Phương án</th>
            {cols.labels.map((l, k) => <th key={k} className={cls(k)}><Txt text={l} /></th>)}
          </tr>
        </thead>
        <tbody>
          {it.basis.map((b, i) => (
            <tr key={i} className={i === leave ? 'row-leave' : ''}>
              <td className="cb"><Num v={it.cB[i]} /></td>
              <th className="basis"><Txt text={`A${b}`} /></th>
              <td className="xb"><Num v={it.xB[i]} /></td>
              {it.T[i].map((v, k) => (
                <td key={k} className={`${cls(k)} ${k === enter && i === leave ? 'pivot' : ''}`}>
                  {removed.has(k) ? <span className="x">×</span> : <Num v={v} />}
                </td>
              ))}
              {showTheta && <td className="theta"><Num v={it.ratios_rows?.[i] ?? null} />{it.ratios_rows?.[i] == null && <span className="x">—</span>}</td>}
            </tr>
          ))}
          <tr className="delta">
            <th colSpan={2} className="lbl">Δ<sub>k</sub></th>
            <td className="F">F = <Num v={it.F} /></td>
            {it.delta.map((d, k) => (
              <td key={k} className={`${cls(k)} ${d !== null && (d.startsWith('-')) ? 'neg' : ''}`}>
                {d === null ? <span className="x">×</span> : <Num v={d} />}
              </td>
            ))}
            {showTheta && <td />}
          </tr>
          {it.delta_m && (
            <tr className="delta">
              <th colSpan={2} className="lbl">Δ<sub>k</sub> (hệ số của M)</th>
              <td />
              {it.delta_m.map((d, k) => (
                <td key={k} className={`${cls(k)} ${d !== null && d.startsWith('-') ? 'neg' : ''}`}>
                  {d === null ? <span className="x">×</span> : <Num v={d} />}
                </td>
              ))}
              {showTheta && <td />}
            </tr>
          )}
          {dual && it.ratios_cols && (
            <tr className="delta">
              <th colSpan={2} className="lbl">θ<sub>k</sub> = Δ<sub>k</sub> / |Z<sub>rk</sub>|</th>
              <td />
              {it.ratios_cols.map((d, k) => (
                <td key={k} className={cls(k)}>{d === null ? <span className="x">—</span> : <Num v={d} />}</td>
              ))}
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

const STATUS_TEXT: Record<string, string> = {
  infeasible: 'Bài toán không có phương án chấp nhận được',
  unbounded: 'Hàm mục tiêu không bị chặn – không có phương án tối ưu',
  not_dual_feasible: 'Không áp dụng trực tiếp được đơn hình đối ngẫu',
  iteration_limit: 'Quá số vòng lặp cho phép',
};

export function SimplexView({ data }: { data: LPSolveResult }) {
  const dual = data.method === 'dual_simplex';
  const sol = data.solution;
  return (
    <div className="result">
      {sol ? (
        <div className="answer">
          <div>
            <span className="answer-k">{sol.sense === 'max' ? 'Giá trị lớn nhất' : 'Giá trị nhỏ nhất'}</span>
            <span className="answer-v">f* = <Num v={sol.F} /></span>
          </div>
          <div>
            <span className="answer-k">Phương án tối ưu</span>
            <span className="answer-v small">x* = (
              {sol.x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)})
            </span>
          </div>
          <VerifyBadge v={data.verify} />
        </div>
      ) : (
        <Alert kind={data.status === 'not_dual_feasible' ? 'warn' : 'error'}>
          <b>{STATUS_TEXT[data.status] ?? data.status}.</b> {data.message}
        </Alert>
      )}

      <Section title="Bài toán">
        <div className="math-box"><Lines lines={data.problem} /></div>
      </Section>

      {data.prep.map((p, i) => (
        <Section key={i} title={p.title}>
          <div className="math-box"><Lines lines={p.lines} /></div>
        </Section>
      ))}

      {data.iterations.length > 0 && <p className="legend">Trong bảng: vùng tô màu đánh dấu cột vào và dòng ra; ô viền đậm là phần tử trục. Dấu × chỉ cột biến giả đã loại. Vuốt ngang trong bảng để xem các cột bị khuất.</p>}
      <IterationNavigator steps={data.iterations.map((it) => (
        <Section key={it.t} title={`Bước ${it.t}`} aside={<span className="chip">{it.basis.map((b) => `A${b}`).join(', ')}</span>}>
          <Tableau it={it} cols={data.columns} dual={dual} />
          <div className="decision"><Lines lines={it.decision} /></div>
        </Section>
      ))} />

      {sol && (
        <Section title="Kết luận">
          <div className="math-box">
            <p className="line">Phương án tối ưu (đủ biến phụ): x* = (
              {sol.std_x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)})
            </p>
            <p className="line">Nghiệm của bài toán gốc: x* = (
              {sol.x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)}), f(x*) = <Num v={sol.F} />
            </p>
            {data.notes.map((n, i) => <p key={i} className="line note"><Txt text={n} /></p>)}
          </div>
        </Section>
      )}
    </div>
  );
}

export function DualFormView({ data }: { data: DualFormResult }) {
  return (
    <div className="result">
      <div className="two-col">
        <Section title="Bài toán gốc (P)"><div className="math-box"><Lines lines={data.primal} /></div></Section>
        <Section title="Bài toán đối ngẫu (P′)"><div className="math-box"><Lines lines={data.dual} /></div></Section>
      </div>
      <Section title="Quy tắc đã áp dụng">
        <div className="math-box">{data.rules.map((r, i) => <p key={i} className="line"><Txt text={r} /></p>)}</div>
      </Section>
      <Section title="Các cặp ràng buộc đối ngẫu">
        <div className="grid-scroll">
          <table className="pairs">
            <thead><tr><th>Bài toán gốc</th><th /><th>Bài toán đối ngẫu</th></tr></thead>
            <tbody>
              {data.pairs.map((p, i) => (
                <tr key={i}><td><Txt text={p.primal} /></td><td className="arrow">⟷</td><td><Txt text={p.dual} /></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>
      {data.solved && (
        <Section title="Kiểm chứng định lý đối ngẫu">
          <div className="math-box">
            <p className="line">
              (P): {data.solved.primal.status === 'optimal'
                ? <>f(x*) = <Num v={data.solved.primal.value} />, x* = ({data.solved.primal.x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)})</>
                : data.solved.primal.status}
            </p>
            <p className="line">
              (P′): {data.solved.dual.status === 'optimal'
                ? <>g(y*) = <Num v={data.solved.dual.value} />, y* = ({data.solved.dual.x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)})</>
                : data.solved.dual.status}
            </p>
            <p className="line note">{data.solved.comment}</p>
          </div>
        </Section>
      )}
    </div>
  );
}

export function CheckView({ data }: { data: CheckResult }) {
  const kind = data.verdict === 'optimal' ? 'ok' : 'warn';
  return (
    <div className="result">
      <Alert kind={kind}><b>{data.verdict === 'optimal' ? 'x là phương án tối ưu.' : data.verdict === 'unknown' ? 'Chưa thể kết luận.' : 'Kết luận: x không phải phương án tối ưu.'}</b> {data.message}</Alert>
      <Section title="Bài toán"><div className="math-box"><Lines lines={data.problem} /></div></Section>
      <p className="line" style={{ margin: '0 0 8px' }}>Phương án cần kiểm tra: x = ({data.x.map((v, i) => <span key={i}>{i > 0 && ', '}<Num v={v} /></span>)})</p>
      {data.steps.map((s, i) => (
        <Section key={i} title={s.title}><div className="math-box"><Lines lines={s.lines} /></div></Section>
      ))}
    </div>
  );
}

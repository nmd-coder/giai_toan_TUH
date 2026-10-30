import { useState } from 'react';
import type { GraphResult, LPForm } from '../types';
import { Num } from './Math';
import { Alert, Section, VerifyBadge } from './ui';

type Point = [number, number];
type HalfPlane = { a: number; b: number; c: number };
const number = (value: string) => {
  const parts = value.trim().replace(',', '.').split('/').map(Number);
  return parts.length === 1 ? parts[0] : parts[0] / parts[1];
};

function clip(poly: Point[], h: HalfPlane): Point[] {
  if (!poly.length) return [];
  const value = (p: Point) => h.a * p[0] + h.b * p[1] - h.c;
  const out: Point[] = [];
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i], q = poly[(i + 1) % poly.length];
    const vp = value(p), vq = value(q);
    const insideP = vp <= 1e-9, insideQ = vq <= 1e-9;
    if (insideP) out.push(p);
    if (insideP !== insideQ) {
      const t = vp / (vp - vq);
      out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
    }
  }
  return out;
}

export default function GraphView({ data, form }: { data: GraphResult; form: LPForm }) {
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState<number | null>(null);
  const result = data.result;
  const boundaries = form.rows.map(r => ({ a: number(r.a[0]), b: number(r.a[1]), c: number(r.b), sign: r.sign }));
  const points: Point[] = data.vertices.map(v => [number(v.x), number(v.y)]);
  if (result.solution) points.push([number(result.solution.x[0]), number(result.solution.x[1])]);
  for (const h of boundaries) {
    if (h.a) points.push([h.c / h.a, 0]);
    if (h.b) points.push([0, h.c / h.b]);
  }
  points.push([0, 0]);
  const valid = points.every(p => p.every(Number.isFinite)) && boundaries.every(h => [h.a, h.b, h.c].every(Number.isFinite));
  const scale = Math.max(2, ...points.flat().map(Math.abs)) * 1.2 / zoom;
  const min = -scale, max = scale;
  const mapX = (x: number) => 300 + 270 * x / scale;
  const mapY = (y: number) => 300 - 270 * y / scale;
  let poly: Point[] = [[min, min], [max, min], [max, max], [min, max]];
  for (const h of boundaries) {
    if (h.sign !== '>=') poly = clip(poly, h);
    if (h.sign !== '<=') poly = clip(poly, { a: -h.a, b: -h.b, c: -h.c });
  }
  form.varSigns.forEach((s, i) => {
    if (s !== 'free') {
      const d = s === 'ge0' ? -1 : 1;
      poly = clip(poly, { a: i === 0 ? d : 0, b: i === 1 ? d : 0, c: 0 });
    }
  });
  const line = (h: HalfPlane): Point[] => {
    const ps: Point[] = [];
    if (h.b) for (const x of [min, max]) { const y = (h.c - h.a * x) / h.b; if (y >= min && y <= max) ps.push([x, y]); }
    if (h.a) for (const y of [min, max]) { const x = (h.c - h.b * y) / h.a; if (x >= min && x <= max) ps.push([x, y]); }
    return ps.slice(0, 2);
  };
  const colors = ['#c44c45', '#265fa6', '#a56d13', '#7b4aad', '#087d73', '#b04b87'];
  const objective = result.solution ? line({ a: number(form.c[0]), b: number(form.c[1]), c: number(result.solution.F) }) : [];
  const ticks = [-1, -0.5, 0.5, 1];
  return <div className="result">
    <Section title="Bước 1. Biểu diễn các ràng buộc">
      <p className="line">Vẽ các đường biên và lấy giao các nửa mặt phẳng thỏa ràng buộc và điều kiện dấu. Miền màu xanh là phần miền nghiệm trong khung hình.</p>
      <div className="graph-controls" aria-label="Điều chỉnh đồ thị">
        <button type="button" onClick={() => setZoom(z => Math.max(0.25, z / 2))} disabled={zoom <= 0.25}>− Thu nhỏ</button>
        <button type="button" onClick={() => setZoom(1)}>Khung ban đầu</button>
        <button type="button" onClick={() => setZoom(z => Math.min(8, z * 2))} disabled={zoom >= 8}>+ Phóng to</button>
        <span>{zoom}×</span>
      </div>
      {valid && Number.isFinite(scale) ? <svg className="graph" viewBox="0 0 600 600" role="img" aria-label="Đồ thị miền nghiệm của bài toán hai biến">
        <rect x="30" y="30" width="540" height="540" fill="var(--card)" stroke="var(--line-strong)" />
        <defs><clipPath id="graph-area"><rect x="30" y="30" width="540" height="540" /></clipPath></defs>
        <g clipPath="url(#graph-area)">
        {poly.length > 0 && <polygon points={poly.map(p => `${mapX(p[0])},${mapY(p[1])}`).join(' ')} fill="#46a48e" fillOpacity="0.28" stroke="#187e68" strokeWidth="3" />}
        <line x1="30" y1="300" x2="570" y2="300" stroke="currentColor" /><line x1="300" y1="30" x2="300" y2="570" stroke="currentColor" />
        {boundaries.map((h, i) => { const p = line(h); return p.length === 2 ? <line key={i} x1={mapX(p[0][0])} y1={mapY(p[0][1])} x2={mapX(p[1][0])} y2={mapY(p[1][1])} stroke={colors[i % colors.length]} strokeWidth="2" /> : null; })}
        {objective.length === 2 && <line x1={mapX(objective[0][0])} y1={mapY(objective[0][1])} x2={mapX(objective[1][0])} y2={mapY(objective[1][1])} stroke="#e05a3f" strokeWidth="2" strokeDasharray="7 5" />}
        {data.vertices.map((v, i) => <g key={i}><circle cx={mapX(number(v.x))} cy={mapY(number(v.y))} r={selected === i ? 8 : 4} fill={selected === i ? '#e05a3f' : '#172b47'} stroke="white" strokeWidth="1" /><text x={mapX(number(v.x)) + 8} y={mapY(number(v.y)) - 8} fill="currentColor">{i + 1}</text></g>)}
        {result.solution && <circle cx={mapX(number(result.solution.x[0]))} cy={mapY(number(result.solution.x[1]))} r="7" fill="#e05a3f" stroke="white" strokeWidth="2" />}
        </g>
        {ticks.map(t => <g key={t}><line x1={mapX(t * scale)} y1="296" x2={mapX(t * scale)} y2="304" stroke="currentColor" /><text x={mapX(t * scale)} y="320" textAnchor="middle" fill="currentColor">{(t * scale).toPrecision(3)}</text><line x1="296" y1={mapY(t * scale)} x2="304" y2={mapY(t * scale)} stroke="currentColor" /><text x="291" y={mapY(t * scale) - 5} textAnchor="end" fill="currentColor">{(t * scale).toPrecision(3)}</text></g>)}
        <text x="557" y="290" fill="currentColor">x₁</text><text x="308" y="45" fill="currentColor">x₂</text><text x="305" y="316" fill="currentColor">0</text>
      </svg> : <Alert kind="warn">Không thể vẽ đồ thị với các hệ số quá lớn; hãy xem kết quả chính xác bên dưới.</Alert>}
      <p className="line">Khung vẽ từ {(-scale).toPrecision(4)} đến {scale.toPrecision(4)} trên mỗi trục; khung chỉ minh họa, không chứng minh miền bị chặn. Chấm đỏ là một nghiệm tối ưu khi có.</p>
      <div className="graph-legend">{boundaries.map((_, i) => <span key={i} style={{ color: colors[i % colors.length] }}>● Đường biên ràng buộc {i + 1}</span>)}{objective.length === 2 && <span>┄ Đường mục tiêu tại f*</span>}</div>
    </Section>
    <Section title="Bước 2. Xét các đỉnh khả thi">
      <p className="line">Các giao điểm thỏa mọi điều kiện được tính chính xác bằng phân số; thay từng đỉnh vào hàm mục tiêu:</p>
      {data.vertices.length ? <div className="grid-scroll"><table className="pairs"><thead><tr><th>Đỉnh</th><th>x₁</th><th>x₂</th><th>f(x)</th></tr></thead><tbody>{data.vertices.map((v, i) => <tr key={i} className={selected === i ? 'selected-vertex' : ''}><td><button type="button" className="vertex-button" aria-pressed={selected === i} onClick={() => setSelected(i)}>Đỉnh {i + 1}</button></td><td><Num v={v.x} /></td><td><Num v={v.y} /></td><td><Num v={v.f} /></td></tr>)}</tbody></table></div> : <p className="line">Không tìm thấy đỉnh khả thi; miền có thể rỗng hoặc không có đỉnh. Xem kết luận dưới đây.</p>}
    </Section>
    <Section title="Bước 3. Kết luận">
      {result.solution ? <><p className="line">Một phương án tối ưu: x* = (<Num v={result.solution.x[0]} />, <Num v={result.solution.x[1]} />), f* = <Num v={result.solution.F} />.</p><VerifyBadge v={result.verify} /></> : <Alert kind="warn">{result.message}</Alert>}
      <p className="line">Trạng thái và giá trị tối ưu được kiểm tra bằng thuật toán đơn hình với số hữu tỉ; đồ thị dùng số gần đúng để minh họa.</p>
      {result.notes.map((n, i) => <p className="line note" key={i}>{n}</p>)}
    </Section>
  </div>;
}

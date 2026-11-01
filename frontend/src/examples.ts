import type { LPForm, LPMethod, TPForm, TPMethod } from './types';

export interface LPExample { label: string; form: LPForm; method: LPMethod; x?: string[] }

const rows = (r: [number[], '<=' | '>=' | '=', number][]) =>
  r.map(([a, sign, b]) => ({ a: a.map(String), sign, b: String(b) }));

export const LP_CUSTOM_EXAMPLES: LPExample[] = [
  {
    label: 'Ví dụ 1 – Phương pháp hình học', method: 'graph',
    form: { sense: 'max', c: ['5', '4'], varSigns: ['ge0', 'ge0'],
      rows: rows([[[2, 1], '<=', 10], [[1, 2], '<=', 8], [[1, 0], '<=', 4]]) },
  },
  {
    label: 'Ví dụ 2 – Đơn hình đối ngẫu', method: 'dual_simplex',
    form: { sense: 'min', c: ['3', '2'], varSigns: ['ge0', 'ge0'],
      rows: rows([[[1, 1], '>=', 6], [[2, 1], '>=', 8]]) },
  },
  {
    label: 'Ví dụ 3 – Đơn hình, phương pháp M', method: 'simplex',
    form: { sense: 'max', c: ['3', '2', '1'], varSigns: ['ge0', 'ge0', 'ge0'],
      rows: rows([[[1, 1, 1], '=', 6], [[1, 2, 0], '<=', 8], [[1, 0, 1], '>=', 2]]) },
  },
  {
    label: 'Ví dụ 4 – Lập bài toán đối ngẫu', method: 'dual_form',
    form: { sense: 'max', c: ['2', '1'], varSigns: ['ge0', 'free'],
      rows: rows([[[1, 1], '<=', 6], [[1, -1], '<=', 4], [[1, 0], '>=', 1]]) },
  },
  {
    label: 'Ví dụ 5 – Kiểm tra độ lệch bù', method: 'check', x: ['2', '2'],
    form: { sense: 'max', c: ['5', '4'], varSigns: ['ge0', 'ge0'],
      rows: rows([[[2, 1], '<=', 10], [[1, 2], '<=', 8], [[1, 0], '<=', 4]]) },
  },
  {
    label: 'Ví dụ 6 – Kiểm tra độ lệch bù: x tối ưu', method: 'check', x: ['2', '2'],
    form: { sense: 'max', c: ['3', '2'], varSigns: ['ge0', 'ge0'],
      rows: rows([[[1, 1], '<=', 4], [[1, 0], '<=', 2], [[0, 1], '<=', 3]]) },
  },
];

export interface TPExample { label: string; form: TPForm; method: TPMethod }

export const TP_CUSTOM_EXAMPLES: TPExample[] = [
  { label: 'Ví dụ 1 – Góc Tây–Bắc', method: 'northwest',
    form: { supply: ['20', '30', '25'], demand: ['25', '20', '30'],
      cost: [['4', '7', '6'], ['5', '3', '8'], ['9', '4', '2']] } },
  { label: 'Ví dụ 2 – Cực tiểu cước phí theo hàng', method: 'least_cost_row',
    form: { supply: ['40', '35'], demand: ['20', '25', '20'],
      cost: [['6', '3', '5'], ['4', '7', '2']] } },
  { label: 'Ví dụ 3 – Cực tiểu cước phí theo cột', method: 'least_cost_column',
    form: { supply: ['15', '25', '20'], demand: ['30', '40'],
      cost: [['4', '8'], ['6', '3'], ['5', '2']] } },
  { label: 'Ví dụ 4 – Cực tiểu cước phí toàn bảng', method: 'least_cost',
    form: { supply: ['12', '18'], demand: ['10', '20'], cost: [['8', '2'], ['3', '7']] } },
];

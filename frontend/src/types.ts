export type Sense = 'max' | 'min';
export type Sign = '<=' | '>=' | '=';
export type VarSign = 'ge0' | 'le0' | 'free';
export type LPMethod = 'simplex' | 'dual_simplex' | 'dual_form' | 'check' | 'graph';
export type TPMethod = 'northwest' | 'least_cost' | 'least_cost_row' | 'least_cost_column';

export interface LPForm {
  sense: Sense;
  c: string[];
  rows: { a: string[]; sign: Sign; b: string }[];
  varSigns: VarSign[];
}

export interface TPForm {
  supply: string[];
  demand: string[];
  cost: string[][];
}

export interface PrepBlock { title: string; lines: string[] }
export interface VerifyInfo { available: boolean; status: string; value?: number | null; agree: boolean | null }

export interface LPColumns {
  labels: string[]; names: string[]; kinds: string[]; c: string[]; has_m: boolean;
}

export interface SimplexIter {
  t: number;
  basis: number[];
  cB: string[];
  xB: string[];
  T: string[][];
  delta: (string | null)[];
  delta_m?: (string | null)[];
  F: string;
  removed: number[];
  enter: number | null;
  leave_row: number | null;
  pivot: string | null;
  ratios_rows: (string | null)[] | null;
  ratios_cols: (string | null)[] | null;
  decision: string[];
}

export interface LPSolution {
  names: string[]; x: string[]; std_names: string[]; std_x: string[]; F: string; sense: Sense;
}

export interface LPSolveResult {
  method: 'simplex' | 'dual_simplex';
  status: 'optimal' | 'infeasible' | 'unbounded' | 'not_dual_feasible' | 'iteration_limit';
  message: string;
  problem: string[];
  prep: PrepBlock[];
  columns: LPColumns;
  iterations: SimplexIter[];
  solution: LPSolution | null;
  notes: string[];
  verify: VerifyInfo | null;
}

export interface GraphResult { result: LPSolveResult; vertices: { x: string; y: string; f: string }[] }

export interface DualFormResult {
  primal: string[];
  dual: string[];
  rules: string[];
  pairs: { primal: string; dual: string }[];
  solved: null | {
    primal: { status: string; names: string[]; x: string[]; value: string | null };
    dual: { status: string; names: string[]; x: string[]; value: string | null };
    equal: boolean | null;
    comment: string;
  };
}

export interface CheckResult {
  verdict: 'optimal' | 'not_optimal' | 'infeasible_x' | 'unknown';
  message: string;
  steps: PrepBlock[];
  x: string[]; y: string[] | null; f: string | null; g: string | null;
  problem: string[];
}

export type Cell = [number, number];
export interface TPIter {
  t: number;
  X: (string | null)[][];
  basis: Cell[];
  cost: string;
  u: string[]; v: string[];
  potential_lines: string[];
  delta: (string | null)[][];
  optimal: boolean;
  enter: Cell | null;
  enter_delta?: string;
  cycle: { cell: Cell; sign: '+' | '-'; x: string }[] | null;
  theta: string | null;
  leave: Cell | null;
  decision: string[];
}
export interface TPResult {
  method: TPMethod;
  status: string;
  problem: { supply: string[]; demand: string[]; cost: string[][] };
  balance: {
    status: 'balanced' | 'supply_excess' | 'demand_excess'; lines: string[];
    dummy_row: boolean; dummy_col: boolean; supply: string[]; demand: string[]; cost: string[][];
  };
  initial: {
    steps: { cell: Cell; amount: string; text: string; ra: string[]; rb: string[] }[];
    X: (string | null)[][]; added: Cell[]; lines: string[]; cost: string;
  };
  iterations: TPIter[];
  solution: null | { X: string[][]; F: string; leftover: null | { kind: 'supply' | 'demand'; values: string[] } };
  notes: string[];
  verify?: VerifyInfo | null;
}

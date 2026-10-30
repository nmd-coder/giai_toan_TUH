import { useEffect, useState } from 'react';
import LPPage from './components/LPPage';
import TPPage from './components/TPPage';

type Tab = 'lp' | 'tp';
type Theme = 'light' | 'dark';

export default function App() {
  const [tab, setTab] = useState<Tab>('lp');
  const [theme, setTheme] = useState<Theme>(() =>
    window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return (
    <>
      <header className="top">
        <div className="top-in">
          <div className="brand">
            <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true">
              <rect width="32" height="32" rx="7" fill="var(--ink)" />
              <path d="M7 24 L16 7 L25 24 Z" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinejoin="round" />
              <circle cx="16" cy="7" r="2.6" fill="var(--pen)" />
            </svg>
            <div>
              <h1>Giải tối ưu hoá</h1>
              <p>Quy hoạch tuyến tính · Bài toán vận tải</p>
            </div>
          </div>
          <nav className="tabs" aria-label="Chọn loại bài toán">
            <button type="button" className={tab === 'lp' ? 'on' : ''} aria-current={tab === 'lp'} onClick={() => setTab('lp')}>Quy hoạch tuyến tính</button>
            <button type="button" className={tab === 'tp' ? 'on' : ''} aria-current={tab === 'tp'} onClick={() => setTab('tp')}>Bài toán vận tải</button>
          </nav>
          <button type="button" className="theme" aria-label="Đổi giao diện sáng/tối" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? 'Sáng' : 'Tối'}
          </button>
        </div>
      </header>
      <main className="main">
        <div hidden={tab !== 'lp'}><LPPage /></div>
        <div hidden={tab !== 'tp'}><TPPage /></div>
      </main>
      <footer className="foot">Lời giải trình bày theo bài giảng IT6095 – Tối ưu hoá (HaUI). Tính toán bằng phân số chính xác, đối chiếu với SciPy.</footer>
    </>
  );
}

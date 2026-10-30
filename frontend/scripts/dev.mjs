import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const frontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const backend = path.resolve(frontend, '..', 'backend');
const python = path.join(backend, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const vite = path.join(frontend, 'node_modules', 'vite', 'bin', 'vite.js');
let backendProcess;
let viteProcess;
let shuttingDown = false;

function checkBackend() {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:8000/api/health', { timeout: 1500 }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { body += chunk; if (body.length > 4096) req.destroy(); });
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(res.statusCode === 200 && data.status === 'ok' && data.service === 'optimization-solver' ? 'ready' : 'other');
        } catch { resolve('other'); }
      });
    });
    req.on('timeout', () => req.destroy());
    req.on('error', () => resolve('unavailable'));
  });
}

function stop(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;
  if (process.platform === 'win32' && child.pid) {
    spawnSync('taskkill', ['/pid', String(child.pid), '/t', '/f'], { stdio: 'ignore', windowsHide: true });
  } else child.kill('SIGTERM');
}

function shutdown(code = 0) {
  if (shuttingDown) return;
  shuttingDown = true;
  stop(viteProcess);
  stop(backendProcess);
  process.exit(code);
}
process.on('SIGINT', () => shutdown());
process.on('SIGTERM', () => shutdown());

if (!existsSync(vite)) {
  console.error('Chưa cài frontend. Chạy npm install trong thư mục frontend.');
  process.exit(1);
}

let state = await checkBackend();
if (state === 'other') {
  console.error('Cổng 8000 đang có dịch vụ khác hoặc backend phiên bản cũ. Hãy kiểm tra tiến trình trên cổng 8000 và khởi động lại backend của dự án.');
  process.exit(1);
}
if (state !== 'ready') {
  if (!existsSync(python)) {
    console.error('Chưa có môi trường Python backend/.venv. Hãy tạo môi trường và cài requirements.txt theo README.');
    process.exit(1);
  }
  console.log('Đang khởi động backend tại http://127.0.0.1:8000...');
  backendProcess = spawn(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: backend, stdio: 'inherit' });
  backendProcess.on('error', (error) => { console.error('Không khởi động được backend:', error.message); shutdown(1); });
  backendProcess.on('exit', (code) => { if (!shuttingDown) { console.error('Backend đã dừng; xem thông báo phía trên.'); shutdown(code || 1); } });
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline && state !== 'ready' && !shuttingDown) {
    await new Promise(resolve => setTimeout(resolve, 500));
    state = await checkBackend();
    if (state === 'other') break;
  }
  if (state !== 'ready') {
    console.error('Backend chưa sẵn sàng. Kiểm tra lỗi phía trên, dependencies hoặc cổng 8000.');
    shutdown(1);
  }
} else console.log('Đang sử dụng backend của dự án đã chạy ở cổng 8000.');

console.log('Backend đã sẵn sàng. Đang khởi động giao diện...');
viteProcess = spawn(process.execPath, [vite, ...process.argv.slice(2)], { cwd: frontend, stdio: 'inherit' });
viteProcess.on('error', (error) => { console.error('Không khởi động được giao diện:', error.message); shutdown(1); });
viteProcess.on('exit', (code) => { if (!shuttingDown) shutdown(code || 0); });

# Phần mềm giải bài toán tối ưu hóa

Ứng dụng web hỗ trợ học môn **Tối ưu hóa IT6095**. Phần mềm giải bài toán quy hoạch tuyến tính và bài toán vận tải, đồng thời trình bày các bước để người học theo dõi và đối chiếu với bài giảng.

## Chức năng

| Nội dung | Phương pháp và cách trình bày |
| --- | --- |
| Quy hoạch tuyến tính | Giải bằng đơn hình; tự thêm biến phụ hoặc biến giả và dùng phương pháp M khi cần. Hiển thị bảng, cột xoay, dòng xoay và phần tử trục. |
| Phương pháp hình học | Với bài toán **đúng hai biến**, vẽ các đường biên, phần miền nghiệm trong khung hình và liệt kê các đỉnh khả thi cùng giá trị hàm mục tiêu. |
| Đối ngẫu | Lập bài toán đối ngẫu, giải bài toán gốc và đối ngẫu để so sánh; kiểm tra phương án bằng điều kiện độ lệch bù. |
| Đơn hình đối ngẫu | Trình bày các bảng và tỷ số chọn cột xoay khi bảng ban đầu thỏa điều kiện áp dụng. |
| Bài toán vận tải | Tìm phương án xuất phát bằng góc Tây–Bắc hoặc cực tiểu cước phí toàn bảng, theo hàng, theo cột; cải thiện bằng phương pháp thế vị. |
| Vận tải không cân bằng | Tự thêm điểm phát hoặc điểm thu ảo với cước phí bằng 0; chỉ ra lượng hàng còn thiếu hoặc còn dư. |

Phần mềm nhận bài toán **max** hoặc **min**, các ràng buộc `≤`, `≥`, `=` và biến không âm, không dương hoặc tùy ý. Kết quả có thể là nghiệm tối ưu, bài toán vô nghiệm, hàm mục tiêu không bị chặn, hoặc thông báo chưa thể kết luận khi thuật toán đạt giới hạn.

## Cài đặt và chạy

### Yêu cầu

- Python 3.10 trở lên và `pip`.
- Node.js 18 trở lên và `npm`.
- Terminal, PowerShell hoặc VS Code. Mở terminal tại thư mục dự án `project_tuh_nhom3` trước khi chạy các lệnh dưới đây.

### Cài đặt lần đầu

Trên Windows, mở PowerShell tại thư mục dự án:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Trên macOS hoặc Linux:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Sau đó mở terminal tại thư mục dự án và cài frontend:

```bash
cd frontend
npm install
```

### Chạy frontend và backend cùng lúc

Sau khi cài đặt lần đầu, mở terminal tại thư mục dự án:

```bash
cd frontend
npm run dev
```

Lệnh này tự khởi động backend nếu chưa chạy, sau đó khởi động frontend. Mở địa chỉ Vite ghi trong terminal (thường là <http://localhost:5173>) và giữ terminal mở. Nhấn `Ctrl + C` để dừng. Nếu backend của dự án đã chạy trước đó, lệnh dùng lại và không dừng tiến trình này. Để chỉnh sửa mã Python, khởi động lại lệnh sau khi sửa.

Có thể kiểm tra backend tại <http://127.0.0.1:8000/api/health>; kết quả có `"status":"ok"` và `"service":"optimization-solver"`. Tài liệu API nằm tại <http://127.0.0.1:8000/docs>.

Nếu muốn chạy từng phần riêng trên Windows, mở PowerShell tại thư mục `backend` và chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Sau đó mở terminal khác tại thư mục `frontend` và chạy `npm run dev:ui`. Trên macOS/Linux, thay đường dẫn Python bằng `.venv/bin/python`.

Nếu không khởi động được, kiểm tra thông báo trong terminal. Nếu cổng 8000 đã được chương trình khác sử dụng, dừng chương trình đó hoặc backend phiên bản cũ rồi chạy lại `npm run dev`.

### Chạy bằng bản giao diện đã biên dịch

Nếu thư mục `frontend/dist` có sẵn, có thể chỉ chạy backend bằng lệnh ở trên và mở <http://127.0.0.1:8000>. Sau khi sửa mã giao diện, tạo lại bản này bằng:

```bash
cd frontend
npm install
npm run build
```

## Cách sử dụng

1. Chọn **Quy hoạch tuyến tính** hoặc **Bài toán vận tải**.
2. Nhập số biến và ràng buộc, hoặc số điểm phát và điểm thu; điền các hệ số. Chọn **Nạp đề mẫu** để thử nhanh một bài toán theo phương pháp mong muốn.
3. Nhập số nguyên, số thập phân như `0.5` hoặc phân số như `1/3`. Với vận tải, lượng phát và thu phải không âm.
4. Chọn phương pháp và bấm **Giải bài toán**, **Lập đối ngẫu** hoặc **Kiểm tra**. Với kiểm tra độ lệch bù, nhập thêm phương án `x` cần kiểm tra.
5. Đọc kết quả và các bước bên dưới. Khi thay dữ liệu hoặc phương pháp, hãy giải lại để nhận lời giải tương ứng.

Ở phần kết quả, dùng **Bước trước / Bước tiếp** để xem từng bảng lặp. Nút **In / lưu PDF lời giải** mở hộp thoại in của trình duyệt và đưa tất cả bảng lặp vào bản in. Với đồ thị, dùng các nút thu phóng và chọn một đỉnh trong bảng để làm nổi bật trên hình.

Ví dụ: trong phần quy hoạch tuyến tính, chọn **Ví dụ 1 – Phương pháp hình học**. Bài toán `max f = 5x₁ + 4x₂` có một nghiệm tối ưu `x = (4, 2)` và giá trị `f = 28`.

## Đọc và hiểu kết quả

- **Đơn hình:** bảng thể hiện cơ sở, phương án, hệ số và dòng ước lượng `Δ`. Với phương pháp M, các hệ số chứa `M` được tách để theo dõi. Bài toán min được đổi sang max tương đương trong bảng; kết luận dùng hàm mục tiêu ban đầu.
- **Hình học:** bảng đỉnh dùng phân số chính xác; đồ thị dùng số gần đúng và chỉ hiển thị trong khung được chọn tự động. Không thể kết luận miền bị chặn chỉ vì hình vẽ có giới hạn. Trạng thái và giá trị tối ưu được kiểm tra bằng đơn hình.
- **Vận tải:** trong mỗi ô, số ở góc là cước phí, số giữa ô là lượng phân phối; các ô cơ sở bằng 0 dùng để xử lý suy biến. Lời giải thể hiện thế vị, `Δ`, chu trình điều chỉnh và lượng điều chỉnh `θ`.
- **Điểm ảo:** lượng ở cột thu ảo là hàng dư; lượng ở hàng phát ảo là nhu cầu chưa được đáp ứng. Mô hình dùng cước phí ảo bằng 0.
- **Đối chiếu SciPy:** huy hiệu **Khớp SciPy** cho biết trạng thái và, khi có nghiệm tối ưu, giá trị mục tiêu khớp với SciPy/HiGHS trong sai số số học. Huy hiệu không kiểm chứng từng bước trình bày hoặc mọi nghiệm tối ưu.

Các phép biến đổi trong bộ giải dùng phân số chính xác. Khi có nhiều lựa chọn hợp lệ, trình tự bảng hoặc phương án thu được có thể khác bài giảng. Một ước lượng bằng 0 ở phương án suy biến chưa đủ để khẳng định có phương án tối ưu khác.

## Phạm vi và giới hạn

- Quy hoạch tuyến tính: tối đa **20 biến và 20 ràng buộc**. Hình học chỉ hỗ trợ hai biến.
- Vận tải: tối đa **15 điểm phát và 15 điểm thu** theo dữ liệu đầu vào.
- Đơn hình đối ngẫu cần bảng xuất phát thỏa điều kiện đối ngẫu. Nếu không áp dụng trực tiếp được, giao diện gợi ý chuyển sang đơn hình M.
- Đơn hình dừng sau tối đa 200 vòng lặp; vận tải dừng sau 500 vòng. Khi đạt giới hạn, kết quả không được coi là nghiệm tối ưu đã chứng minh.
- Trong bài toán vận tải không cân bằng, điểm ảo có cước phí bằng 0; các phương pháp cực tiểu ưu tiên ô thực khi lập phương án xuất phát. Nếu thực tế có chi phí lưu kho, thiếu hàng hoặc phạt khác 0, cần mô hình hóa phù hợp trước khi sử dụng.

## Kiểm thử

Từ thư mục `backend`, cài phụ thuộc kiểm thử và chạy:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Trên Windows, có thể thay `python` bằng `.\.venv\Scripts\python.exe`; trên macOS/Linux dùng `.venv/bin/python`. Bộ kiểm thử gồm các ví dụ bài giảng, trường hợp suy biến, vô nghiệm, không bị chặn và các bài ngẫu nhiên đối chiếu với SciPy.

## Cấu trúc dự án

```text
project_tuh_nhom3/
├── backend/
│   ├── app/           API, các bộ giải và định dạng số
│   ├── tests/         Kiểm thử bộ giải
│   ├── requirements.txt
│   └── requirements-dev.txt
└── frontend/
    ├── src/           Giao diện React và TypeScript
    ├── dist/          Giao diện đã biên dịch, nếu có
    └── package.json
```

Backend sử dụng **Python/FastAPI**; frontend sử dụng **React/TypeScript/Vite**. Nội dung và ký hiệu lời giải được xây dựng dựa trên đề cương Bài 2, Bài 3 và Bài 4 của môn IT6095. Các đề cương PDF được lưu bên ngoài thư mục dự án trong bộ tài liệu hiện tại.

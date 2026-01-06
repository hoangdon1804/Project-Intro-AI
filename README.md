# 🚀 AI Pathfinding Trainer – Genetic Algorithm

Dự án sử dụng **Giải thuật Di truyền (Genetic Algorithm)** để huấn luyện các cá thể AI tự học cách vượt qua các màn chơi phức tạp.  
AI phải học cách **di chuyển**, **tránh né kẻ địch**, **thu thập vật phẩm (coins) theo đúng thứ tự** và **tìm đường về đích**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)
![Genetic Algorithm](https://img.shields.io/badge/Logic-Genetic%20Algorithm-orange.svg)

---

## ✨ Tính năng nổi bật

- 🧬 **Hệ thống DNA động**  
  Độ dài DNA tự động tăng dần theo số thế hệ (`DNA_INCREASE_RATE`), giúp AI học từ các bước ngắn đến lộ trình dài và phức tạp hơn.

- 🪙 **Logic thu thập tuần tự**  
  AI không chỉ tìm đích mà phải học cách thu thập các đồng xu **theo đúng thứ tự** trước khi về đích.

- 👑 **Cơ chế tinh anh (Elitism)**  
  Giữ lại các cá thể xuất sắc nhất của mỗi thế hệ để đảm bảo quá trình tiến hóa không bị thụt lùi.

- 🔄 **Đột biến có kế thừa**  
  Khi cá thể va chạm, các gene trước thời điểm chết được giữ lại, chỉ đột biến các bước cuối → tối ưu hành vi tại các điểm “thắt nút”.

- 🎮 **Trực quan hóa thời gian thực**  
  Hiển thị toàn bộ quá trình huấn luyện với màu sắc phân biệt giữa cá thể thường, tinh anh và cá thể đã chết.

---

## 🛠️ Cấu trúc dự án

├── train.py # Khởi tạo game cho người chơi

├── train.py # Vòng lặp huấn luyện & logic Genetic Algorithm

├── sprites.py # Định nghĩa Player, Enemy

├── level_manager.py # Quản lý bản đồ, tường, coins, điểm xuất phát

├── settings.py # Các hằng số cấu hình (tốc độ, màu sắc, kích thước)

└── archivement.txt # Lưu DNA cá thể xuất sắc nhất

## 🧬 Cơ chế Giải thuật Di truyền

### 1️⃣ Khởi tạo
- Tạo quần thể **1000 cá thể**
- DNA ngẫu nhiên có **quán tính** giúp chuyển động mượt hơn

### 2️⃣ Đánh giá (Fitness)
- ➕ Điểm lớn cho mỗi đồng xu thu thập được  
- ➕ Điểm theo khoảng cách đến mục tiêu hiện tại (coin tiếp theo hoặc đích)  
- ⏱️ Thưởng điểm thời gian (hoàn thành càng nhanh càng tốt)  
- ❌ Phạt điểm khi va chạm với kẻ địch

### 3️⃣ Chọn lọc
- Chọn các cá thể có **Fitness cao nhất**

### 4️⃣ Lai ghép (Crossover)
- Kết hợp DNA của hai cá thể bố mẹ để tạo ra thế hệ con

### 5️⃣ Đột biến (Mutation)
- Thay đổi ngẫu nhiên một số gene
- Tránh việc AI bị mắc kẹt vào các lối mòn cục bộ

---

## 🚀 Hướng dẫn cài đặt

### Yêu cầu
- Python **3.8+**

### Cài đặt Pygame
```bash
pip install pygame
```
### Chạy chương trình huấn luyện
Chọn level muốn train: trainer = TrainVisualizer(level=3)
```bash
python train.py
```
⚙️ Cấu hình huấn luyện
Bạn có thể điều chỉnh các tham số trong main_train.py để tối ưu tốc độ và chất lượng học:

POPULATION_SIZE = 1000       # Số cá thể mỗi thế hệ
MUTATION_RATE = 0.05         # Tỉ lệ đột biến (5%)
GENES_PER_STEP = 200         # Số bước di chuyển ban đầu
DNA_INCREASE_RATE = 50       # Gene tăng thêm mỗi chu kỳ
GENERATION_INCEASE_DNA = 15  # Sau 15 thế hệ thì tăng DNA

📺 Trực quan hóa
🔴 Đỏ: Cá thể đang học

🟡 Vàng (Elite): Cá thể tinh anh

⚪ Xám: Cá thể đã va chạm (Dead)

🔢 Vòng tròn số: Coins cần thu thập theo thứ tự 1 → 2 → 3 → ...

📝 Lưu ý

Khi AI hoàn thành màn chơi, DNA tốt nhất sẽ được lưu vào archivement.txt

Việc khởi tạo các thông  số hợp lý rất quan trọng, ví dụ : nếu như tạo chuỗi ADN ban đầu quá dài, thế hệ tăng độ dài ADN quá ngắn dẫn đến việc kẹt cục bộ ban đầu (các cá thể luôn chết).

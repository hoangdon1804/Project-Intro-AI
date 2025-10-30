import os

def clear_file(path):
    """Xóa nội dung của một file."""
    try:
        file_dir = os.path.dirname(path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        open(path, 'w', encoding='utf-8').close()
        print(f"Đã xóa dữ liệu cũ từ: {path}")
    except Exception as e:
        print(f"Không thể xóa file {path}: {e}")
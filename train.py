from AITrainer import AITrainer
from functions import clear_file
from settings import *

if __name__ == "__main__":
    LEVEL_TO_TRAIN = 1
    POPULATION_SIZE = 1000
    INITIAL_MAX_MOVES = 200
    MAX_GENERATIONS = 1500
    
    random.seed(12345)

    clear_file(moves_path)
    clear_file(archive_path)

    trainer = AITrainer(
        level=LEVEL_TO_TRAIN,
        population_size=POPULATION_SIZE,
        max_move_limit=INITIAL_MAX_MOVES,
        visualize_mode=VISUALIZATION_MODE
    )
    
    print(f"Bắt đầu huấn luyện AI cho Màn {LEVEL_TO_TRAIN}...")
    print(f"Chế độ hiển thị: {VISUALIZATION_MODE} ('0': None, '1': Best, '3': Parallel)")
    if VISUALIZATION_MODE == 3:
        print("CẢNH BÁO: Chế độ hiển thị đồng thời RẤT NẶNG và sẽ làm quá trình huấn luyện rất chậm!")

    trainer.run_training(max_generations=MAX_GENERATIONS)
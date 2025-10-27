from settings import *
import os

def python_sort(start, end):
    """
    Sorts the moves file from lowest to highest score with python's built in sort.
    """
    start_time = time.time()
    with open(moves_path, 'r') as file:
        data = file.readlines()
    cluster_lines = data[start : end + 1]

    def get_score_from_line(line):
        try:
            start_index = line.find("Score: ") + 7
            end_index = line.find(" Moves:")
            score_str = line[start_index:end_index].strip()
            return float(score_str)
        except (ValueError, IndexError):
            return -float('inf')

    cluster_lines.sort(key=get_score_from_line)

    data[start : end + 1] = cluster_lines
    with open(moves_path, 'w') as file:
        file.writelines(data)

def calculate_final_score(game, player, cause_of_death):
    """
    Tính điểm cuối cùng cho một player dựa trên công thức mới.
    Score = (1/distance) - penalties
    """
    # 1. Tính khoảng cách đến mục tiêu
    player_center_x = player.rect.x + player.size / 2
    player_center_y = player.rect.y + player.size / 2
    
    distance_to_target = math.hypot(game.target_x - player_center_x, game.target_y - player_center_y)

    # 2. Tính phần thưởng chính (1 / khoảng cách)
    # Thêm 1.0 vào mẫu số để tránh lỗi chia cho 0 và giữ cho điểm không quá lớn
    reward = 150000.0 / (distance_to_target + 1.0)
    
    # 3. Tính toán các hình phạt
    safe_zone_penalty = player.safe_zone_frames * SAFE_ZONE_PENALTY_WEIGHT
    move_penalty = len(player.moves) * MOVE_PENALTY_WEIGHT
    
    # 4. Áp dụng hình phạt dựa trên nguyên nhân chết
    final_score = reward - safe_zone_penalty - move_penalty
    
    if cause_of_death == 'enemy_hit':
        final_score -= ENEMY_HIT_PENALTY
    elif cause_of_death == 'wander_death':
        final_score -= WANDER_DEATH_PENALTY
    elif cause_of_death == 'win':
        final_score += WIN_REWARD

    # In thông tin debug để kiểm tra
    print(f"--- Score Calculation (Gen {game.generation}) ---")
    print(f"  Cause of Death: {cause_of_death}")
    print(f"  Distance to Target: {distance_to_target:.2f}")
    print(f"  Base Reward (1/dist): {reward:.4f}")
    print(f"  Safe Zone Penalty: -{safe_zone_penalty:.2f} ({player.safe_zone_frames} frames)")
    print(f"  Move Penalty: -{move_penalty:.2f} ({len(player.moves)} moves)")
    print(f"  Final Score: {final_score:.4f}")
    print(f"-------------------------")

    return format(final_score, '.5f')

def clear_moves():
    """
    Clears all contents from the moves file
    """
    moves_dir = os.path.dirname(moves_path)
    if not os.path.exists(moves_dir):
        os.makedirs(moves_dir)

    open(moves_path, 'w').close()
    print(f"Cleared previous moves data from: {moves_path}")
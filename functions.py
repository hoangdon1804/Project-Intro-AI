from settings import *
import os

def bubble_sort(start, end):
    """
    Sorts the moves file from lowest to highest score with bubble sorting

    Parameters
    ----------
    start: int
        Starting line index of the lines that will be sorted
    end: int
        End line index of the lines that will be sorted

    Return
    ------
    None

    """

    start_time = time.time()
    with open(moves_path, 'r') as file:
        data = file.readlines()
    # Cluster that is going to be sorted
    cluster = data[start : end + 1]

    for i in range (0, len(cluster) - 1):
        for j in range (0, len(cluster) - 1):
            # Swap if value is greater than the next value
            current = cluster[j]
            next = cluster[j + 1]
            # Extract score for comparison (e.g., "Score: 1.2345 Moves: 12345...")
            current_score = float(current[current.find("Score: ") + 7 : current.find(" Moves:")])
            next_score = float(next[next.find("Score: ") + 7 : next.find(" Moves:")])

            if current_score > next_score:
                cluster[j], cluster[j + 1] = next, current

    # Write back to moves file
    data[start : end + 1] = cluster
    with open(moves_path, 'w') as file:
        file.writelines(data)
    # print("Bubble sort execution time:  %s seconds" % (time.time() - start_time)) # Commented out for cleaner output

def insertion_sort(start, end):
    """
    Sorts the moves file from lowest to highest score with insertion sorting

    Parameters
    ----------
    start: int
        Starting line index of the lines that will be sorted
    end: int
        End line index of the lines that will be sorted

    Return
    ------
    None

    """

    start_time = time.time()
    with open(moves_path, 'r') as file:
        data = file.readlines()
    # Cluster that is going to be sorted
    cluster = data[start : end + 1]

    for i in range(0, len(cluster)):
        current = cluster[i]
        position = i
        
        current_score = float(current[current.find("Score: ") + 7 : current.find(" Moves:")])

        while position > 0:
            prev_item = cluster[position - 1]
            prev_score = float(prev_item[prev_item.find("Score: ") + 7 : prev_item.find(" Moves:")])

            if prev_score > current_score:
                cluster[position] = cluster[position - 1]
                position -= 1
            else:
                break # Correct placement found

        cluster[position] = current
    # [4, 4 , 6, 5, 8, 12]
    # Write back to moves file
    data[start : end + 1] = cluster
    with open(moves_path, 'w') as file:
        file.writelines(data)
    # print("Insertion sort execution time:  %s seconds" % (time.time() - start_time)) # Commented out for cleaner output

def python_sort(start, end):
    """
    Sorts the moves file from lowest to highest score with python's built in sort.
    This version correctly handles string parsing for scores.

    Parameters
    ----------
    start: int
        Starting line index of the lines that will be sorted
    end: int
        End line index of the lines that will be sorted

    Return
    ------
    None

    """

    start_time = time.time()
    with open(moves_path, 'r') as file:
        data = file.readlines()
    # Cluster that is going to be sorted
    cluster_lines = data[start : end + 1]

    # Custom sort key to parse the score from each line
    def get_score_from_line(line):
        try:
            # Find "Score: " and " Moves:" to extract the float value
            start_index = line.find("Score: ") + 7
            end_index = line.find(" Moves:")
            score_str = line[start_index:end_index].strip()
            return float(score_str)
        except (ValueError, IndexError):
            # Handle malformed lines by returning a very low score
            return -float('inf')

    # Sort the cluster using the custom key
    cluster_lines.sort(key=get_score_from_line)

    # Write back to moves file
    data[start : end + 1] = cluster_lines
    with open(moves_path, 'w') as file:
        file.writelines(data)
    # print("Python built in sort execution time:  %s seconds" % (time.time() - start_time)) # Commented out for cleaner output


def checkpoint_score(game, player):
    """
    Assigns a score to a set of moves based on the map's checkpoints.
    A higher score is better.

    Parameters
    ----------
    game : Game
        The game instance.
    player : Player
        The player object whose score is being calculated.

    Return
    ------
    str
        Returns the score as a formatted string (e.g., '.5f' for 5 decimal places).

    """

    # Check if the player has reached or exceeded the final checkpoint
    if player.current_target_checkpoint_index >= len(game.checkpoints_list):
        # Assign a very high score for completing the level
        score = 1000.0 + len(player.moves) / 1000.0 # Reward for shorter path to completion
        return format(score, '.5f')


    # Get coordinates for the currently targeted checkpoint
    # Use player.current_target_checkpoint_index here!
    coordinates = game.checkpoints_list[player.current_target_checkpoint_index]


    # Calculate distance to the center of the current target checkpoint tile
    target_center_x = float(coordinates[0] + tile_size / 2)
    target_center_y = float(coordinates[1] + tile_size / 2)
    player_center_x = float(player.rect.x + player.size / 2)
    player_center_y = float(player.rect.y + player.size / 2)

    dist_to_target = math.hypot(target_center_x - player_center_x,
                                target_center_y - player_center_y)

    # Calculate total distance from the previous checkpoint to the current target checkpoint
    total_segment_dist = 0.0
    if player.current_target_checkpoint_index == 0:
        # If targeting the first checkpoint, distance is from start_x, start_y
        start_center_x = float(game.startx + tile_size / 2)
        start_center_y = float(game.starty + tile_size / 2)
        total_segment_dist = math.hypot(target_center_x - start_center_x,
                                        target_center_y - start_center_y)
    else:
        # Distance from the previous checkpoint to the current target checkpoint
        prev_coords = game.checkpoints_list[player.current_target_checkpoint_index - 1]
        prev_center_x = float(prev_coords[0] + tile_size / 2)
        prev_center_y = float(prev_coords[1] + tile_size / 2)
        total_segment_dist = math.hypot(target_center_x - prev_center_x,
                                        target_center_y - prev_center_y)

    # Prevent division by zero if target/prev checkpoints are at the exact same spot
    if total_segment_dist == 0:
        dist_ratio = 0 # No progress to be made on this segment
    else:
        dist_ratio = dist_to_target / total_segment_dist


    # Base score: number of checkpoints reached + (1 - normalized distance to next checkpoint)
    # The (1 - dist_ratio) term gives more score as player gets closer to target.
    # Add a small penalty for each move to encourage shorter paths.
    # Add a larger bonus for each checkpoint reached.
    score = (player.current_target_checkpoint_index * 100.0) + (100.0 * (1.0 - dist_ratio)) - (len(player.moves) * 0.01)

    if player.hit:
        score -= 50 # Significant penalty for hitting an enemy

    # Ensure score is not extremely negative if player dies very early
    if score < -100: # Cap minimum score for better sorting
        score = -100.0

    if score < 0:
        return format(score, '.4f')
    else:
        return format(score, '.5f')

def clear_moves():
    """
    Clears all contents from the moves file

    Parameters
    ----------
    None

    Return
    ------
    None

    """

    # Ensure the directory exists before trying to open the file
    moves_dir = os.path.dirname(moves_path)
    if not os.path.exists(moves_dir):
        os.makedirs(moves_dir) # Create the directory if it doesn't exist

    open(moves_path, 'w').close()
    print(f"Cleared previous moves data from: {moves_path}")
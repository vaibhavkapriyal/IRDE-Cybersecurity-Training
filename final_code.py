import cv2
import numpy as np
import random

def create_puzzle_grid(frame, grid_size):
    height, width = frame.shape[:2]
    piece_width = width // grid_size
    piece_height = height // grid_size
    puzzle_grid = []

    for i in range(grid_size):
        for j in range(grid_size):
            left = j * piece_width
            upper = i * piece_height
            right = left + piece_width
            lower = upper + piece_height
            piece = frame[upper:lower, left:right]
            puzzle_grid.append(piece)

    return puzzle_grid, piece_width, piece_height

def shuffle_puzzle_grid(puzzle_grid):
    indices = list(range(len(puzzle_grid)))
    random.shuffle(indices)
    shuffled = [puzzle_grid[i] for i in indices]
    return shuffled, indices

def reverse_shuffle_puzzle_grid(shuffled_grid, permutation):
    original_grid = [None] * len(shuffled_grid)
    for i, idx in enumerate(permutation):
        original_grid[idx] = shuffled_grid[i]
    return original_grid

def assemble_frame(puzzle_grid, grid_size, piece_width, piece_height, frame_shape):
    frame = np.zeros(frame_shape, dtype=np.uint8)
    for i in range(grid_size):
        for j in range(grid_size):
            index = i * grid_size + j
            piece = puzzle_grid[index]
            left = j * piece_width
            upper = i * piece_height
            frame[upper:upper+piece_height, left:left+piece_width] = piece
    return frame

def main():
    grid_size = 4  # Adjust based on your processing speed and webcam resolution
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encryption
        puzzle_grid, pw, ph = create_puzzle_grid(frame, grid_size)
        shuffled_grid, permutation = shuffle_puzzle_grid(puzzle_grid)
        encrypted_frame = assemble_frame(shuffled_grid, grid_size, pw, ph, frame.shape)

        # Decryption (immediate)
        original_grid = reverse_shuffle_puzzle_grid(shuffled_grid, permutation)
        decrypted_frame = assemble_frame(original_grid, grid_size, pw, ph, frame.shape)

        # Show both frames
        cv2.imshow('Encrypted', encrypted_frame)
        cv2.imshow('Decrypted', decrypted_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

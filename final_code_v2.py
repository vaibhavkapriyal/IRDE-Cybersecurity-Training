import cv2
import numpy as np
import random
import tkinter as tk
from threading import Thread

# --- Real-time Webcam Encryption/Decryption ---

def start_webcam_stream(grid_size):
    cap = cv2.VideoCapture(0)
    encryption_enabled = False
    decryption_enabled = False
    permutation = []

    print("Press 'e' to toggle encryption, 'd' to toggle decryption, 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_copy = frame.copy()
        piece_width = frame.shape[1] // grid_size
        piece_height = frame.shape[0] // grid_size

        if encryption_enabled:
            puzzle_grid = create_puzzle_grid(frame_copy, grid_size)
            shuffled_grid, permutation = shuffle_puzzle_grid(puzzle_grid)
            encrypted_frame = np.zeros_like(frame_copy)

            for i in range(grid_size):
                for j in range(grid_size):
                    piece = shuffled_grid[i * grid_size + j]
                    left = j * piece_width
                    upper = i * piece_height
                    encrypted_frame[upper:upper + piece_height, left:left + piece_width] = piece
            display_frame = encrypted_frame

        elif decryption_enabled and permutation:
            puzzle_grid = create_puzzle_grid(frame_copy, grid_size)
            reordered_grid = [puzzle_grid[permutation[i]] for i in range(len(permutation))]
            decrypted_frame = np.zeros_like(frame_copy)

            for i in range(grid_size):
                for j in range(grid_size):
                    piece = reordered_grid[i * grid_size + j]
                    left = j * piece_width
                    upper = i * piece_height
                    decrypted_frame[upper:upper + piece_height, left:left + piece_width] = piece
            display_frame = decrypted_frame

        else:
            display_frame = frame_copy

        cv2.imshow('Real-time Puzzle Encryptor/Decryptor', display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('e'):
            encryption_enabled = not encryption_enabled
            decryption_enabled = False
            print("Encryption:", encryption_enabled)
        elif key == ord('d'):
            if permutation:
                decryption_enabled = not decryption_enabled
                encryption_enabled = False
                print("Decryption:", decryption_enabled)
            else:
                print("No permutation found. Encrypt something first.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# --- Puzzle Grid Functions ---

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

    return puzzle_grid

def shuffle_puzzle_grid(puzzle_grid):
    shuffled_grid = puzzle_grid.copy()
    indices = list(range(len(puzzle_grid)))
    random.shuffle(indices)
    permutation = [0] * len(puzzle_grid)

    for i, idx in enumerate(indices):
        shuffled_grid[i] = puzzle_grid[idx]
        permutation[idx] = i

    return shuffled_grid, permutation

def reverse_shuffle_puzzle_grid(shuffled_grid, permutation):
    original_grid = [None] * len(shuffled_grid)
    for i, idx in enumerate(permutation):
        original_grid[idx] = shuffled_grid[i]
    return original_grid

# --- GUI for Grid Size ---

def get_grid_size_and_start():
    try:
        grid_size = int(entry.get())
        if grid_size < 2 or grid_size > 64:
            raise ValueError
        root.destroy()
        Thread(target=start_webcam_stream, args=(grid_size,)).start()
    except ValueError:
        entry.delete(0, tk.END)
        entry.insert(0, "Enter 2–64")

root = tk.Tk()
root.title("Grid Size Input")
root.geometry("300x150")
tk.Label(root, text="Enter Grid Size (e.g., 4, 8, 16)").pack(pady=10)
entry = tk.Entry(root)
entry.pack(pady=5)
entry.focus()
tk.Button(root, text="Start", command=get_grid_size_and_start).pack(pady=10)
root.mainloop()

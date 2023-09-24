import cv2
import numpy as np
import random
import threading
import os

def create_puzzle_grid(frame, grid_size):
    height, width = frame.shape[:2]

    # Calculate the size of each puzzle piece
    piece_width = width // grid_size
    piece_height = height // grid_size

    puzzle_grid = []

    # Split the frame into puzzle pieces and store them in the puzzle_grid list
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
    # Shuffle the puzzle pieces and store their original positions in a dictionary
    shuffled_grid = puzzle_grid.copy()
    indices = list(range(len(puzzle_grid)))
    random.shuffle(indices)

    permutation = [0] * len(puzzle_grid)
    for i, idx in enumerate(indices):
        shuffled_grid[i] = puzzle_grid[idx]
        permutation[idx] = i

    return shuffled_grid, permutation

def encrypt_video(grid_size):
    cap = cv2.VideoCapture(0)  # 0 for default webcam, change to the appropriate device ID if needed

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = 30.0  # Assuming a constant 30 frames per second

    out = cv2.VideoWriter('encrypted_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Create an empty list to store the permutation
    permutation = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        puzzle_grid = create_puzzle_grid(frame, grid_size)
        shuffled_grid, piece_permutation = shuffle_puzzle_grid(puzzle_grid)

        # Add the piece permutation to the overall permutation list
        permutation.extend(piece_permutation)
        
        # Calculate the size of each puzzle piece in the frame
        piece_width = frame_width // grid_size
        piece_height = frame_height // grid_size

        # Create a new frame to store the shuffled puzzle pieces
        encrypted_frame = np.zeros_like(frame)

        # Assemble the shuffled puzzle pieces back into the encrypted frame
        for i in range(grid_size):
            for j in range(grid_size):
                piece = shuffled_grid[i * grid_size + j]
                left = j * piece_width
                upper = i * piece_height
                encrypted_frame[upper:upper + piece_height, left:left + piece_width] = piece

        out.write(encrypted_frame)

        # Show the encrypted frame in a window (optional)
        cv2.imshow('Encrypted Video', encrypted_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save the permutation to a file
    with open('encrypted_video.mp4.permutation', 'w') as perm_file:
        perm_file.write(','.join(str(index) for index in permutation))
        print(permutation)
        print("wwwwwwwwwwwwwwwwwwwwwwwww")
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def read_permutation_file(filename, frame_size):
    try:
        with open(filename, 'r') as perm_file:
            permutation_str = perm_file.read()
            permutation_list = [int(index) for index in permutation_str.split(',')]
            num_frames = len(permutation_list) // frame_size
            permutation_chunks = [permutation_list[i * frame_size: (i + 1) * frame_size] for i in range(num_frames)]
            print("Permutation Chunks:", permutation_chunks)
            return permutation_chunks
    except Exception as e:
        print("Error reading permutation:", e)
        return None

def reverse_shuffle_puzzle_grid(shuffled_grid, permutation):
    grid_size = int(np.sqrt(len(shuffled_grid)))
    original_grid = [None] * len(shuffled_grid)

    for i, idx in enumerate(permutation):
        original_grid[idx] = shuffled_grid[i]
        

    # Reshape the original_grid back to the original puzzle_grid
    puzzle_grid = np.array(original_grid).reshape((grid_size, grid_size, *original_grid[0].shape))
    

    return puzzle_grid

def decrypt_video(grid_size):
    frame_size = grid_size * grid_size
    cap = cv2.VideoCapture('encrypted_video.mp4')  # Read the encrypted video

    if not cap.isOpened():
        print("Error: Video file not found or could not be opened.")
        return

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = 30.0  # Assuming a constant 30 frames per second

    out = cv2.VideoWriter('decrypted_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Read the permutation chunks from the file
    permutation_chunks = read_permutation_file('encrypted_video.mp4.permutation', frame_size)

    if permutation_chunks is None:
        print("Error: Invalid permutation data.")
        return

    frame_number = 0  # Track the frame number for debugging

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the size of each puzzle piece in the frame
        piece_width = frame.shape[1] // grid_size
        piece_height = frame.shape[0] // grid_size



        # Split the frame into puzzle pieces
        puzzle_grid = []
        # Split the encrypted image into puzzle pieces and store them in the encrypted_grid list
        for i in range(grid_size):
            for j in range(grid_size):
                left = j * piece_width
                upper = i * piece_height
                right = left + piece_width
                lower = upper + piece_height
                piece = frame[upper:lower, left:right]
                puzzle_grid.append(piece)
        # Create an empty frame to store the decrypted frame
        decrypted_frame = np.zeros_like(frame)


        # Get the permutation for the current frame
        permutation = permutation_chunks.pop(0)

        # Assemble the puzzle pieces back into the decrypted image using the original ordering
        for i in range(grid_size):
            for j in range(grid_size):
                piece = puzzle_grid[permutation[i * grid_size + j]]
                left = j * piece_width
                upper = i * piece_height
                decrypted_frame[upper:upper + piece_height, left:left + piece_width] = piece


        # For debugging, print the frame number and permutation
        print("Frame Number:", frame_number)
        print("Permutation for Frame:", permutation)

        frame_number += 1

        out.write(decrypted_frame)

        # Show the decrypted frame in a window (optional)
        cv2.imshow('Decrypted Video', decrypted_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    grid_size = 16  # Adjust the grid size as desired

    # Start the encryption process in a separate thread
    encryption_thread = threading.Thread(target=encrypt_video, args=(grid_size,))
    encryption_thread.start()

    # Start the decryption process in the main thread
    

    # Wait for the encryption thread to complete
    encryption_thread.join()

    decrypt_video(grid_size)

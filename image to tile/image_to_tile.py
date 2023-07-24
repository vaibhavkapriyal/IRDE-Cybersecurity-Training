from PIL import Image
import os

def convert_to_tiles(input_image_path, output_directory, num_tiles):
    # Open the input image
    img = Image.open(input_image_path)

    # Get the size of the input image
    img_width, img_height = img.size

    # Calculate the dimensions of each tile
    tile_width = img_width // num_tiles
    tile_height = img_height // num_tiles

    # Extract and save each tile
    for i in range(num_tiles):
        for j in range(num_tiles):
            left = j * tile_width
            upper = i * tile_height
            right = left + tile_width
            lower = upper + tile_height
            tile = img.crop((left, upper, right, lower))
            tile_path = os.path.join(output_directory, f"tile_{i}_{j}.png")
            tile.save(tile_path)

if __name__ == "__main__":
    input_image_path = "E:\Intership Training IRDE\luffy.jpg"
    output_directory = "E:\Intership Training IRDE\tiles"
    num_tiles = num_tiles = int(input("Enter Number of tiles : ")) #Enter Number of tiles-----> creates tiles as n*n

    convert_to_tiles(input_image_path, output_directory, num_tiles)

# Decompress a file compressed with Deflate algorithm
import zlib

with open("input.bmp", "rb") as binary_file:
    # Read the whole file at once
    data = binary_file.read()
    decoded_data = zlib.decompress( data , -15)
    with open("output.bmp", "wb") as binary_file2:
        binary_file2.write(decoded_data)

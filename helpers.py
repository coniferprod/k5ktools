import sys

def read_file_data(filename: str) -> bytes:
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            #print('Read {} bytes from file {}'.format(len(data), filename))
            return data
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(-1)

def write_file_data(filename: str, data: bytes) -> None:
    try:
        with open(filename, 'wb') as f:
            f.write(data)
    except FileExistsError:
        print(f'File exists: {filename}')
        sys.exit(-1)

def hexdump(data: bytes) -> str:
    result = ''
    for b in data:
        result += f'{b:02X} '
    return result

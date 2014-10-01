import os

def write_to_file(fileName, contents, mode = 'w'):
    ensure_dir(fileName)
    file = open(fileName, mode)
    file.write(contents)
    file.close()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

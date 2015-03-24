import os
import codecs

def write_to_file(fileName, contents, mode='w', encoding='utf-8', **kwargs):
    ensure_dir(fileName)
    file = codecs.open(fileName, mode=mode, encoding=encoding, **kwargs)
    file.write(contents)
    file.close()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

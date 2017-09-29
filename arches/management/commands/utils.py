import os
import codecs

def get_yn_input(msg="are you sure you want to continue?"):
    '''function can be passed a custom message and will use that prompt to get
    a y/n response. will return True ONLY if the user input (forced to lower())
    begins with 'y'. all other responses return False.'''
    o = raw_input(msg +" y/n ")
    if o.lower().startswith("y"):
        return True
    else:
        print "operation cancelled."
        return False

def write_to_file(fileName, contents, mode='w', encoding='utf-8', **kwargs):
    ensure_dir(fileName)
    file = codecs.open(fileName, mode=mode, encoding=encoding, **kwargs)
    file.write(contents)
    file.close()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

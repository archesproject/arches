import os
import codecs

def get_yn_input(msg="are you sure you want to continue?",default="Y"):
    '''function can be passed a custom message and will use that prompt to get
    a y/n response. default defines what will happen if enter is hit with no
    input.'''
    
    if not default in ["Y", "N"]:
        raise Exception("function must be called with default = 'Y' or 'N'")
        
    if default == "Y":
        o = raw_input(msg+" [Y/n] ")
        if o.lower().startswith("y") or o == "":
            ret = True
        else:
            print "operation cancelled."
            ret = False

    if default == "N":
        o = raw_input(msg+" [y/N] ")
        if o.lower().startswith("n") or o == "":
            print "operation cancelled."
            ret = False
        else:
            ret = True
            
    return ret

def write_to_file(fileName, contents, mode='w', encoding='utf-8', **kwargs):
    ensure_dir(fileName)
    file = codecs.open(fileName, mode=mode, encoding=encoding, **kwargs)
    file.write(contents)
    file.close()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

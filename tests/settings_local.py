LOCAL_BROWSERS = ['Chrome'] #['Firefox']

NOSE_ARGS = [
    '--with-coverage',
    '--nocapture',
    '--cover-package=arches',
    '--verbosity=1',
    '--cover-erase',
]

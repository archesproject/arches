from PIL import Image, ImageOps
import io
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.conf import settings

def generate_thumbnail(file):
    if 'image' in file.content_type:
        im = Image.open(file)
        try:
            thumb = ImageOps.fit(im, (128,128), Image.ANTIALIAS)
        except IOError as e:
            print "I/O error({0}): {1}".format(e, e.strerror)
        f = io.BytesIO()
        try:
          thumb.save(f, 'JPEG')
        except KeyError as e:
            print "I/O error({0}): {1}".format(e, e.strerror)
            
        return SimpleUploadedFile('%s_%s.%s' % ('thumb', os.path.splitext(file.name)[0], 'jpg'), f.getvalue(), content_type='image/jpeg')
    else:
        return None

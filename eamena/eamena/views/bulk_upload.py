'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import os
import json
import time
from StringIO import StringIO
from django import forms
from django.conf import settings
from django.core.management import call_command
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def handle_uploaded_file(f):
    '''the actual file upload happens here, and returns a path to the file
    where it exists on the server'''
    dest_path = os.path.join(settings.BULK_UPLOAD_DIR,str(f))
    with open(dest_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return dest_path

def get_archesfile_path(filepath):
    '''takes the input spreadsheet path and outputs a path for a new .arches
    file inside of the BULK_UPLOAD_DIR.'''

    basename = os.path.splitext(os.path.basename(filepath))[0].replace(" ","_")
    name = time.strftime("{}_%H%M%d%m%Y.arches".format(basename))
    destpath = os.path.join(settings.BULK_UPLOAD_DIR,name)

    return destpath

def new_upload(request):
    ''' nothing special here, everything is handled with ajax'''

    return render_to_response('bulk-upload/new.htm',
        {'active_page': 'Bulk Upload'}, # not sure if this is necessary
        context_instance=RequestContext(request) # or this
    )
    
def main(request):
    ''' nothing special here, everything is handled with ajax'''

    with open(os.path.join(settings.BULK_UPLOAD_DIR,"_loadlog.txt"),'rb') as loadlog:
        loads = loadlog.readlines()
    return render_to_response('bulk-upload/main.htm',
        {'active_page': 'Bulk Upload',
        'load_log':loads}, # not sure if this is necessary
        context_instance=RequestContext(request) # or this
    )

def validate(request):
    '''this view is designed to be hit with an ajax call that includes the path
    to the spreadsheet on the server, and the resource type for the spreadsheet
    '''

    fpath = request.POST.get('filepath', '')
    restype = request.POST.get('restype','')

    convert = {'false':False,'true':True}
    append = convert[request.POST.get('append', 'false')]

    fullpath = os.path.join(settings.BULK_UPLOAD_DIR,str(fpath))
    destpath = get_archesfile_path(fullpath)
    call_command('Excelreader',
        operation='site_dataset',
        source=fullpath,
        dest_dir=destpath,
        resource_type=restype,
        append_data=append,
    )
    errorlog = os.path.join(settings.BULK_UPLOAD_DIR,'_validation_errors.json')

    with open(errorlog,'r') as readjson:
        data = readjson.read()
        result = json.loads(data)
    if 'success' not in result:
        os.remove(fullpath)

    else:
        result['filepath'] = os.path.basename(destpath)

    return HttpResponse(json.dumps(result), content_type="application/json")
    
def upload_spreadsheet(request):
    '''this is the view that handles the file upload ajax call. it includes a
    very simple test for the file format, which should be XLSX, and returns the
    file path, name, and validity, all of which are used on the front-end.'''
    
    if request.method == 'POST':
        f = request._files['files[]']
        fname = os.path.basename(str(f))
        response_data = {
            'filevalid':True,
            'filename':fname,
            'filepath':'',
        }
        ## simple test for file type; don't upload non-excel files
        if not fname.endswith('.xlsx'):
            response_data['filevalid'] = False
        else:
            fpath = handle_uploaded_file(f)
            response_data['filepath'] = os.path.basename(fpath)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

def import_archesfile(request):
    '''just a wrapper to the load_resources command. expects the name of a file
    that is in the BULK_UPLOAD_DIR directory. returns nothing because the load
    results are written to a log file.'''

    fpath = request.POST.get('filepath','')
    fullpath = os.path.join(settings.BULK_UPLOAD_DIR,fpath)
    append = request.POST.get('append', 'false')

    call_command('packages',
        operation='load_resources',
        source=fullpath,
        appending=append,
    )
    
    return HttpResponse(json.dumps({}), content_type="application/json")
    

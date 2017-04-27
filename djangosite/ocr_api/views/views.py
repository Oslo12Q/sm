#encoding: utf-8
import json
import logging
import os
import random
import time
import traceback

from django.shortcuts import render
from django.http import HttpResponse


def get_json_response(request, json_rsp):
    return HttpResponse(json.dumps(json_rsp), content_type='application/json')

def exhibition_index(request):
    
    return render(request,'ocr_api/index.html')

def get_exhibition_index(request):
    
    return render(request,'ocr_api/settlement.html')

def list_exhibition_index(request):
    
    return render(request,'ocr_api/health.html')

def case_report(request):
    
    return render(request,'ocr_api/casebook.html')

def index(request):
    context = dict(status='ok', description='')
    return render(request, 'ocr_api/upload.html', context=context)

import base64
from datetime import datetime   
def async_analysis(request):
    try:
        if request.method != 'POST':
            return get_json_response(request, dict(status='error', message='only POST method supported.', data=None))
    
        file_obj_base = request.POST.get('fileData', None)
        if not file_obj_base:
            return get_json_response(request, dict(status='error', message='file object not found.', data=None))
        file_obj = base64.b64decode(file_obj_base)  
    
        file_name = 'assay_{}_{}.jpg'.format(datetime.now().strftime("%Y%m%d%H%M%S"),random.randint(1000, 9999))
        file_dest = 'C:/input/{}'.format(file_name)

        writer = open(file_dest, 'wb+')
        writer.write(file_obj)
        writer.close()

        return get_json_response(request, dict(status='ok', message='success', data=dict(fid=file_name)))
    except Exception, err:
        logging.error(err)
        logging.error(traceback.format_exc())
        return get_json_response(request, dict(suc_id=0, ret_cd=500, ret_ts=long(time.time()), pic_id=0, data=None))


def async_analysis_result(request):
    file_id = request.GET.get('fid') or ''

    if not file_id:
        return get_json_response(request, dict(status='error', message='fid not found.', data=None))

    file_dest = _get_analysis_result_path(fid=file_id)

    file_name = file_dest.replace('C:/output/', '')
    if not file_dest:
        return get_json_response(request, dict(status='running', message='analysis is running.', data=None))

    from sm.data_cleaning.data_clear import data_clear
    try:
        rsp_data = data_clear(file_dest)
        
        indicators, extra_info, unknown_indicators = rsp_data.get('indicators', []), rsp_data.get('extra_info', {}), rsp_data.get('unknown_indicators', [])
        result = dict(indicators=indicators, extra_info=extra_info)
        re = json.dumps(result,ensure_ascii=False)
        print re
        return get_json_response(request, dict(status='ok', message='success.', data=result))
    except Exception, err:
        logging.error(err)
        logging.error(traceback.format_exc())
        return get_json_response(request, dict(status='500', message='data_clear is 500.', data=None))

def _get_analysis_result_path(fid):
    for extension in ['.doc', '.pdf', '.xls', '.xlsx']:
        file_dest = 'C:/output/{}{}'.format(fid, extension)
        if os.path.exists(file_dest):
            return file_dest
    return ''

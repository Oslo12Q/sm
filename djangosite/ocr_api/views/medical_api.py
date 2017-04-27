# encoding: utf-8

import datetime
import json
import logging
import os
import random
import time
import traceback

from django.conf import settings
from django.http import HttpResponse


def get_json_response(request, json_rsp):
    return HttpResponse(json.dumps(json_rsp), content_type='application/json')


def check_access(request):
    user_code = request.REQUEST.get('user_code', '')
    user_key = request.REQUEST.get('user_key', '')
    if user_code == 'picc' and user_key == 'bquQBFx4Wswu1Xjh5Y5Dva125UYjsDJH':
        return True, user_code, user_key
    if user_code == 'ciming' and user_key == '7GogiBHZRb2wq3YSRY1Jvmk8JlwmOqiY':
        return True, user_code, user_key
    return False, user_code, user_key


def analysis(request):
    try:
        has_access, user_code, user_key = check_access(request)
        if not has_access:
            return get_json_response(request, dict(suc_id=0, ret_cd=1, ret_ts=long(time.time()), pic_id=0, data=None))
        if request.method != 'POST':
            return get_json_response(request, dict(suc_id=0, ret_cd=405, ret_ts=long(time.time()), pic_id=0, data=None))
        file_obj = request.FILES.get('pic_data', None)
        if not file_obj:
            return get_json_response(request, dict(suc_id=0, ret_cd=104, ret_ts=long(time.time()), pic_id=0, data=None))

        file_name = '{}_{}_{}.jpg'.format(user_code, long(time.time()), random.randint(1000, 9999))
        file_abs_path = os.path.join(settings.OCR_IMG_INPUT_DIR, file_name)

        writer = open(file_abs_path, 'wb+')
        writer.write(file_obj.read())
        writer.close()

        def wait_ready(fid):
            for i in xrange(15):
                ret = detect_ready(fid=fid)
                if ret:
                    return ret
                time.sleep(1)
            return ''
        ret_abs_path = wait_ready(fid=file_name)

        if not ret_abs_path:
            return get_json_response(request, dict(suc_id=0, ret_cd=404, ret_ts=long(time.time()), pic_id=0, data=None))

        from sm.data_cleaning.data_clear import data_clear
        rsp_data = data_clear(file_dest)
        indicators, extra_info, unknown_indicators = rsp_data.get('indicators', []), rsp_data.get('extra_info', {}), rsp_data.get('unknown_indicators', [])
        result = dict(indicators=indicators, extra_info=extra_info)

        return get_json_response(request, dict(
            suc_id=1,
            ret_cd=200,
            ret_ts=long(time.time()),
            pic_id=file_name,
            data=result,
        ))
    except Exception, err:
        logging.error(err)
        logging.error(traceback.format_exc())
        return get_json_response(request, dict(suc_id=0, ret_cd=500, ret_ts=long(time.time()), pic_id=0, data=None))


def async_analysis(request):
    try:
        has_access, user_code, user_key = check_access(request)
        if not has_access:
            return get_json_response(request, dict(suc_id=0, ret_cd=1, ret_ts=long(time.time()), pic_id=0, data=None))
        if request.method != 'POST':
            return get_json_response(request, dict(suc_id=0, ret_cd=405, ret_ts=long(time.time()), pic_id=0, data=None))
        file_obj = request.FILES.get('pic_data', None)
        if not file_obj:
            return get_json_response(request, dict(suc_id=0, ret_cd=104, ret_ts=long(time.time()), pic_id=0, data=None))

        file_name = '{}_{}_{}.jpg'.format(user_code, long(time.time()), random.randint(1000, 9999))
        file_abs_path = os.path.join(settings.OCR_IMG_INPUT_DIR, file_name)

        writer = open(file_abs_path, 'wb+')
        writer.write(file_obj.read())
        writer.close()

        return get_json_response(request, dict(
            suc_id=1,
            ret_cd=200,
            ret_ts=long(time.time()),
            pic_id=file_name,
            data=None,
        ))
    except Exception, err:
        logging.error(err)
        logging.error(traceback.format_exc())
        return get_json_response(request, dict(suc_id=0, ret_cd=500, ret_ts=long(time.time()), pic_id=0, data=None))


def async_analysis_result(request):
    pic_id = request.REQUEST.get('pic_id')
    if not pic_id:
        return get_json_response(request, dict(suc_id=0, ret_cd=104, ret_ts=long(time.time()), pic_id=0, data=None))

    file_path = detect_ready(fid=pic_id)
    if not file_path:
        return get_json_response(request, dict(
            suc_id=1,
            ret_cd=201,
            ret_ts=long(time.time()),
            pic_id=pic_id,
            data=None,
        ))

    from sm.data_cleaning.data_clear import data_clear
    rsp_data = data_clear(file_path)
    indicators, extra_info, unknown_indicators = rsp_data.get('indicators', []), rsp_data.get('extra_info', {}), rsp_data.get('unknown_indicators', [])
    result = dict(indicators=indicators, extra_info=extra_info)
    return get_json_response(request, dict(
        suc_id=1,
        ret_cd=200,
        ret_ts=long(time.time()),
        pic_id=pic_id,
        data=result,
    ))


def detect_ready(fid):
    for extension in settings.OCR_IMG_OUTPUT_EXTENSIONS:
        path = os.path.join(settings.OCR_IMG_OUTPUT_DIR, '{}{}'.format(fid, extension))
        if os.path.exists(path):
            return path
    return ''

import json
from django.http import HttpResponse
from django.utils.datetime_safe import datetime


def restful(body, error_code=0, error_msg='success'):
    """
    """
    result = {'error_code': error_code, 'error_msg': error_msg}
    result.update(body)
    # print result
    return HttpResponse(json.dumps(result), content_type="application/json")


def dt2str(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def str2dt(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def str2d(s):
    return datetime.strptime(s, '%Y-%m-%d')


def _generate_req_seq(aux_id=''):
    return datetime.now().strftime('%Y%m%d%H%M%S') + str(aux_id)

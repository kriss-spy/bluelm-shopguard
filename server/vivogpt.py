# vivogpt.py
import uuid
import time
import requests
from auth_util import gen_sign_headers

APP_ID = '2025863341'
APP_KEY = 'ShRBDpAqGvISQKOb'
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

def ask_vivogpt(messages, extra, model='vivo-BlueLM-TB-Pro', session_id=None):
    """
    向大模型发起同步请求并返回 (content, time_cost)。
    出错时返回 (None, 错误信息)。
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    if extra is None:
        extra = {}

    request_id = str(uuid.uuid4())
    params = {'requestId': request_id}
    payload = {
        'messages': messages,
        'model': model,
        'sessionId': session_id,
        'extra': extra
    }

    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'
    url = f'https://{DOMAIN}{URI}'

    start_time = time.time()
    try:
        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=15)
    except requests.RequestException as e:
        return None, str(e)

    time_cost = time.time() - start_time
    if resp.status_code != 200:
        return None, f'HTTP {resp.status_code}: {resp.text}'

    res_obj = resp.json()
    code = res_obj.get('code')
    if code != 0 or 'data' not in res_obj:
        return None, f'API error, code: {code}, msg: {res_obj.get("msg")}'

    content = res_obj['data'].get('content', '')
    return content, time_cost
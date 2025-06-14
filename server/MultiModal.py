# MultiModal.py
# 多模态图片理解与OCR文本提取工具
import uuid
import requests
from auth_util import gen_sign_headers

# vivo AI 平台分配的 APP_ID 和 APP_KEY
APP_ID = '2025863341'
APP_KEY = 'ShRBDpAqGvISQKOb'

# 接口路径和域名
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

def extract_text(image_base64, temperature=0.1, max_tokens=1024, timeout=15):
    """
    使用多模态大模型对图片进行OCR文字提取，仅返回原始文本内容。

    参数:
        image_base64 (str): 图片的Base64字符串（可带或不带data:image前缀）
        temperature (float): 控制输出的随机性，默认0.1
        max_tokens (int): 最大生成token数，默认1024
        timeout (int): 请求超时时间（秒），默认15

    返回:
        (文本内容, 错误信息) 元组。成功时错误信息为None，失败时文本内容为None。
    """
    prompt_text = "请提取图片中的所有文字内容，按原格式返回。忽略图片描述，只返回原始文本。"
    request_id = str(uuid.uuid4())
    params = {'requestId': request_id}
    payload = {
        'requestId': request_id,
        'sessionId': str(uuid.uuid4()),
        'model': 'vivo-BlueLM-V-2.0',
        'messages': [
            {
                "role": "user",
                "content": image_base64,
                "contentType": "image"
            },
            {
                "role": "user",
                "content": prompt_text,
                "contentType": "text"
            }
        ],
        'extra': {
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'
    url = f'https://{DOMAIN}{URI}'
    try:
        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return None, f'HTTP error: {resp.status_code} - {resp.text}'
        res_obj = resp.json()
        if res_obj.get('code') != 0:
            return None, f'API error: {res_obj.get("msg")}'
        return res_obj['data'].get('content', ''), None
    except Exception as e:
        return None, f'Request exception: {str(e)}'

def interpret_image(
    image_base64,
    prompt_text=None,
    temperature=0.9,
    top_p=0.7,
    top_k=50,
    max_tokens=1024,
    repetition_penalty=1.02,
    stop=None,
    ignore_eos=False,
    skip_special_tokens=True,
    timeout=15
):
    """
    使用多模态大模型对图片进行内容理解，返回详细描述。

    参数:
        image_base64 (str): 图片的Base64字符串（可带或不带data:image前缀）
        prompt_text (str): 图片理解的自定义提示词，默认详细描述图片内容
        temperature (float): 控制输出的随机性，默认0.9
        top_p (float): 核采样保留的概率质量，默认0.7
        top_k (int): 从前k个token中采样，默认50
        max_tokens (int): 最大生成token数，默认1024
        repetition_penalty (float): 重复惩罚，默认1.02
        stop (list): 生成时遇到这些词强制停止，默认["</end>"]
        ignore_eos (bool): 是否忽略模型的EOS标志，默认False
        skip_special_tokens (bool): 解码时跳过特殊token，默认True
        timeout (int): 请求超时时间（秒），默认15

    返回:
        (描述文本, 错误信息) 元组。成功时错误信息为None，失败时描述文本为None。
    """
    if prompt_text is None:
        prompt_text = (
            "请详细描述这张图片的全部内容，要求覆盖以下方面：\n"
            "1. 主要物体/人物：列出图片中出现的主要物体或人物，并简要说明其特征、动作、姿态、表情等；\n"
            "2. 场景和环境：描述图片的背景、地点、时间、氛围、色彩等环境信息；\n"
            "3. 文字内容：如图片中包含文字，请完整提取并说明其位置和字体风格；\n"
            "4. 关系与互动：如有多个元素，说明它们之间的关系或互动情况；\n"
            "5. 其他显著特征：如特殊标志、符号、颜色、光影效果等；\n"
            "6. 图片整体风格或用途：如是插画、照片、截图、广告等，请说明类型和可能用途。\n"
            "请按照上述结构分条详细描述，内容尽量全面、具体。"
        )
    if stop is None:
        stop = ["</end>"]

    request_id = str(uuid.uuid4())
    params = {'requestId': request_id}
    payload = {
        'requestId': request_id,
        'sessionId': str(uuid.uuid4()),
        'model': 'vivo-BlueLM-V-2.0',
        'messages': [
            {
                "role": "user",
                "content": image_base64,
                "contentType": "image"
            },
            {
                "role": "user",
                "content": prompt_text,
                "contentType": "text"
            }
        ],
        'extra': {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_tokens": max_tokens,
            "repetition_penalty": repetition_penalty,
            "stop": stop,
            "ignore_eos": ignore_eos,
            "skip_special_tokens": skip_special_tokens
        }
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'
    url = f'https://{DOMAIN}{URI}'
    try:
        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return None, f'HTTP error: {resp.status_code} - {resp.text}'
        res_obj = resp.json()
        if res_obj.get('code') != 0:
            return None, f'API error: {res_obj.get("msg")}'
        return res_obj['data'].get('content', ''), None
    except Exception as e:
        return None, f'Request exception: {str(e)}'
# encoding: utf-8
import uuid           # 用于生成 requestId 和 sessionId，保证全局唯一性
import time           # 用于计算请求耗时
import requests       # HTTP 请求库
from auth_util import gen_sign_headers  # 自定义模块，用于生成签名相关 Header 参数

# ===================== 接口配置信息 =====================

# 请根据 vivo AI 平台分配的值替换为你自己团队的 APP_ID 和 APP_KEY
APP_ID = '2025863341'
APP_KEY = 'ShRBDpAqGvISQKOb'

# 接口路径（固定）,这个 URI 是蓝心大模型的 API 接口地址
URI = '/vivogpt/completions'
# 接口域名（固定）
DOMAIN = 'api-ai.vivo.com.cn'
# 请求方法（POST 是同步请求方式）
METHOD = 'POST'

# ===================== 同步请求函数 =====================
def sync_vivogpt():
    # ========== URL 参数 ==========
    # requestId 是唯一请求标识，必须 URL 编码，保证请求可追踪
    params = {
        'requestId': str(uuid.uuid4())#uuid是一个全球唯一的标识符，通常用于生成唯一的 requestId
    }
    print('requestId:', params['requestId'])

    # ========== 请求体参数 ==========
    # prompt 与 messages 二选一：本次只使用 prompt 简单测试
    data = {
        'prompt': '你是谁',           # 单轮对话输入内容，若使用 messages 可支持多轮上下文
        'model': 'vivo-BlueLM-TB-Pro',        # 模型名称，目前支持 vivo-BlueLM-TB-Pro（输入+输出总长度8K）
        'sessionId': str(uuid.uuid4()),       # 会话 ID，使用 UUID 标识一次会话
        # systemPrompt 是可选的人设提示词（本次未使用）
        # 'systemPrompt': '你的中文名字叫小蓝，你是vivo的AI助手。',
        'extra': {
            'temperature': 0.9,               # 控制回答的随机性（创造性）；值越高越随机，越低越稳定
            # 'top_p': 0.7,                   # 可选参数：控制生成答案的核采样范围（未使用）
            # 'top_k': 50,                    # 可选参数：在概率最高的前K个tokens中采样（未使用）
            # 'max_new_tokens': 2048,         # 可选参数：控制生成内容最大长度（未使用）
            # 'repetition_penalty': 1.02      # 可选参数：对重复内容进行惩罚（未使用）
        }
    }

    # ========== Header 参数 ==========
    # 以下 header 参数由 gen_sign_headers() 生成，包含：
    # - Content-Type: 固定为 application/json
    # - X-AI-GATEWAY-APP-ID: vivo 分配的 app_id
    # - X-AI-GATEWAY-TIMESTAMP: 当前时间戳，单位秒
    # - X-AI-GATEWAY-NONCE: 8位随机字符串
    # - X-AI-GATEWAY-SIGNED-HEADERS: 标识签名中使用的 header 名称
    # - X-AI-GATEWAY-SIGNATURE: 根据上述信息计算出的签名
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    # ========== 发起请求 ==========
    start_time = time.time()
    url = 'https://{}{}'.format(DOMAIN, URI)

    try:
        # 向蓝心大模型发送 POST 请求
        response = requests.post(url, json=data, headers=headers, params=params)
    except Exception as e:
        print('请求异常:', e)
        return

    # ========== 响应处理 ==========
    if response.status_code == 200:
        # 成功接收响应，解析为 JSON
        res_obj = response.json()
        print(f'response:{res_obj}')

        # 判断业务状态码（0 表示成功；1007 表示内容命中审核）
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']  # 获取大模型生成的文本
            print(f'final content:\n{content}')
        else:
            print(f"请求失败，code: {res_obj.get('code')}, msg: {res_obj.get('msg')}")
    else:
        # HTTP 层返回错误（如 401、403、500 等）
        print(response.status_code, response.text)

    end_time = time.time()
    timecost = end_time - start_time
    print('请求耗时: %.2f秒' % timecost)


# ===================== 入口函数 =====================
if __name__ == '__main__':
    sync_vivogpt()

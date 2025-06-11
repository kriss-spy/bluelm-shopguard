# encoding: utf-8

#testoutput:是一张曼德宝猴（也称“蓝脸猴”）的特写照片。图片展示了它的面部特征，包括蓝色的面部条纹、红色的鼻子和黄色的眼睛。曼德宝猴以其独特的面部条纹和鲜艳的颜色而闻名，这些特征是其 物种身份的重要识别标志。

import base64
import uuid
import time
import requests
from auth_util import gen_sign_headers  # 签名工具函数，生成鉴权头部

# 请替换为你自己的 APP_ID 和 APP_KEY
APP_ID = '2025863341'
APP_KEY = 'ShRBDpAqGvISQKOb'

# 接口路径和域名
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

# 图片文件路径，可替换为任意图片,放在当前目录下
PIC_FILE = 'baboon.jpeg'


def stream_vivogpt():
    # URL参数
    params = {
        'requestId': str(uuid.uuid4())  # 请求ID，全局唯一，用于追踪请求
    }
    print('requestId:', params['requestId'])

    # 读取图片并进行Base64编码
    with open(PIC_FILE, "rb") as f:
        b_image = f.read()
    image = base64.b64encode(b_image).decode('utf-8')

    # 请求体（Body）
    data = {
        'prompt': '你好',  # 单轮问答文本，可选字段，prompt 和 messages 二选一
        'sessionId': str(uuid.uuid4()),  # 会话ID，每次请求唯一；prompt 使用时用于多轮上下文追踪
        'requestId': params['requestId'],  # 再次携带 requestId 作为 Body 里的字段
        'model': 'vivo-BlueLM-V-2.0',  # 多模态模型名称

        # 多轮消息体：必须为奇数个，role 目前只支持 "user"，最后一条为当前请求
        "messages": [
            {
                "role": "user",  # 用户角色
                "content": "data:image/JPEG;base64," + image,  # 图片内容Base64格式（带前缀）
                "contentType": "image"  # 声明内容类型为图片
            },
            {
                "role": "user",  # 紧跟的文字说明
                "content": "描述图片的内容",  # 要求模型描述上面图片
                "contentType": "text"  # 声明内容类型为文本
            }
        ],

        # 模型推理控制参数（可选）
        "extra": {
            "temperature": 0.9,  # 控制输出的随机性，越高越发散
            "top_p": 0.7,        # 核采样保留的概率质量
            "top_k": 50,         # 从前k个token中采样
            "max_tokens": 1024,  # 生成内容的最大token数（注意不是输入+输出之和）
            "repetition_penalty": 1.02,  # 重复惩罚，降低重复生成的概率
            "stop": ["</end>"],  # 模型生成时遇到这些词强制停止
            "ignore_eos": False,  # 是否忽略模型的EOS标志
            "skip_special_tokens": True  # 解码时跳过特殊token，如[CLS]等
        }
    }

    # 生成签名后的头部字段（含 APP_ID、签名等）
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    # 构造最终请求URL
    url = f'http://{DOMAIN}{URI}'

    # 发起POST请求
    start_time = time.time()
    response = requests.post(url, json=data, headers=headers, params=params)

    # 打印响应
    if response.status_code == 200:
        print(response.json())
    else:
        print("错误状态码:", response.status_code)
        print("错误信息:", response.text)

    # 输出请求耗时
    end_time = time.time()
    print("请求耗时: %.2f秒" % (end_time - start_time))


if __name__ == "__main__":
    stream_vivogpt()

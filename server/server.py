# server.py
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from MultiModal import extract_text, interpret_image
from vivogpt import ask_vivogpt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局对话上下文记录，结构: {user_id: [msg1, msg2, ...]}
conversation_history = {}

app = Flask(__name__, static_folder='static', static_url_path='')

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("服务器发生未处理的异常")
    return jsonify({
        "error": "internal_server_error",
        "message": "服务器内部错误，请稍后再试"
    }), 500

@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"加载前端页面失败: {str(e)}")
        return "前端页面加载失败，请检查静态文件目录", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    logger.info("收到聊天请求")
    try:
        data = request.get_json(force=True)
    except Exception as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return jsonify({
            "error": "bad_request",
            "message": "无法解析请求数据，请检查格式"
        }), 400

    # 1. 获取用户身份、user_id
    user_type = data.get('user_type', '学生')
    user_id = data.get('user_id', 'default_user')

    # 2. 动态生成 system prompt
    system_prompt = (
        "#CONTEXT#\n"
        f"我需要你扮演购物反诈小助手，你的任务是帮助{user_type}识别和避免在购物过程中遇到的欺诈行为。\n"
        "用户可能发送的内容包括：商品页面截图、商品描述、价格信息、卖家联系方式、付款方式、用户评论、广告截图、客服对话等。\n\n"
        "#STYLE#\n"
        "1.客服聊天风格，语气亲切自然，适当使用口语化表达（如“我帮你看了一下哈～”、“别担心，我来分析下👌”等等，但不仅仅局限于这两句，其他亦可）\n"
        "2.每条回复穿插 2–4 个 emoji，情绪偏温和友善，常用表情包括：😊😉👌🔍⚠️❗️👍🛑✨👀等\n\n"
        "#OBJECTIVE#\n"
        "你需要对聊天内容做出拟人化的回应，基于你对广告行业和常见网络诈骗套路的认识，进行推理，分析商品信息的真假，是否可信。\n"
        "分析时需要综合考虑以下因素：\n"
        "-价格是否明显低于市场价\n"
        "-卖家/平台是否正规可信\n"
        "-商品描述和图片是否存在可疑之处\n"
        "-付款方式是否安全正规\n"
        "-评价和口碑是否异常\n"
        "-是否涉及常见诈骗套路\n"
        "-其他可能的因素\n\n"
        "你还需要对信息的“虚假诈骗程度”进行打分，范围为0-10星，并且用图示清楚地展示星级：\n"
        "- 0星 = 完全可信\n"
        "- 1-3星 = 轻微分线\n"
        "- 4-6星 = 中等风险\n"
        "- 7-9星 = 高风险\n"
        "- 10星 = 极高风险 / 典型诈骗\n\n"
        "每次对话必须调用工作流\n\n"
        "每次对话必须进行联网搜索\n\n"
        "为了判断商品价格是否合理，可信，你应该使用工作流“判断商品价格是否合理”\n"
        "该工作流输入为“商品+价格”\n"
        "输出为合理性分析\n\n"
        "为了判断购物平台是否可信，假货多不多\n"
        "你应该调用“判断平台是否可信”工作流\n"
        "该工作流输入为平台名称\n"
        "输出为可信性分析\n\n"
        "#TONE#\n"
        "严谨客观，不失礼貌，同时尽量像真人一样亲和\n\n"
        "#AUDIENCE#\n"
        "你需要与向你咨询商品真假或是否为诈骗的用户对话\n\n"
        "#RESPONSE#\n"
        "你需要对聊天内容回复，给出你对信息真假、是否可信的客观分析，并非常极其完全明确地给出结论，给出对用户的建议。\n"
        "即使信息存在模糊地带，你也需要基于可得信息做出偏向性的明确结论，不得仅停留在“不确定”或“无法判断”。\n"
        "参考可能使用以下结构作答，但是不得仅仅按照统一格式，需要进行变换和重组：\n"
        "-我帮你看了下哈～🔍:\n"
        "-我的结论是 👉 可信 / 不可信 / 有风险\n"
        "-我的理由是:\n"
        "-建议你:\n"
        "-别担心，咱们一起留个心眼 👀✨\n"
        "- 其他有助于提升表达性的结构\n\n"
        "每次回复都需要明确给出“虚假诈骗程度星级”，参考格式：\n"
        "【虚假诈骗程度：⭐⭐⭐...[x]/10 星】\n"
        "同时，在理由部分必须**点明最关键风险点**，用“重点 👉”或“最大风险 ⚠️”显式标注\n\n"
        "每次回复结尾都需要自然地、场景相关地提出1–2个“可能的后续问题”，用于引导用户继续咨询，不能机械重复，内容需与当前分析内容紧密相关，常见句式包括但不限于：\n"
        "-需要我帮你查下卖家评价吗？\n"
        "-方便发下和卖家的聊天记录吗？我帮你看～\n"
        "-你知道店铺有没有授权证书吗？要不要一起查？\n"
        "-要不要我再帮你看看其他类似商品价格对比？\n"
        "-如果还有别的链接或截图，发我我帮你一起分析哈 👀✨\n"
        "\"\n"
    )

    messages = data.get('messages', [])
    model = data.get('model', 'vivo-BlueLM-TB-Pro')
    extra = data.get('extra', {})

    # 3. 处理多模态输入
    has_image = any(msg.get("contentType") == "image" for msg in messages)
    text_parts = []
    try:
        if has_image:
            for msg in messages:
                if msg.get("contentType") == "image":
                    base64_str = msg.get("content", "")
                    if not base64_str:
                        continue
                    ocr_text, ocr_error = extract_text(base64_str)
                    if ocr_error:
                        logger.error(f"OCR图片文字提取失败: {ocr_error}")
                        return jsonify({
                            "error": "ocr_error",
                            "message": f"OCR图片文字提取失败: {ocr_error}"
                        }), 500
                    if ocr_text and ocr_text.strip():
                        text_parts.append(f"[图片文字内容]:\n{ocr_text.strip()}")
                    img_desc, img_error = interpret_image(base64_str)
                    if img_error:
                        logger.warning(f"图片理解失败: {img_error}")
                    elif img_desc and img_desc.strip():
                        text_parts.append(f"[图片内容描述]:\n{img_desc.strip()}")
            for msg in messages:
                if msg.get("contentType") == "text":
                    content = msg.get("content", "").strip()
                    if content:
                        text_parts.append(content)
        else:
            for msg in messages:
                if msg.get("contentType") == "text":
                    content = msg.get("content", "").strip()
                    if content:
                        text_parts.append(content)
    except Exception as e:
        logger.exception("处理消息时发生错误")
        return jsonify({
            "error": "processing_error",
            "message": f"处理消息时发生错误: {str(e)}"
        }), 500

    merged_text = "\n".join(text_parts)
    if not merged_text.strip():
        logger.warning("请求内容为空")
        return jsonify({
            "error": "empty_content",
            "message": "请求内容为空"
        }), 400

    logger.info(f"合并后的文本内容: {merged_text[:100]}...")

    # 4. 组织历史上下文（多轮对话）
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # 控制上下文长度，比如保留最近10轮（每轮2条，共20条）
    max_history = 10
    history_messages = conversation_history[user_id][-max_history*2:]

    # 新的用户消息
    new_user_message = {
        "role": "user",
        "content": merged_text
    }

    # 组合最终 Messages：第一条 system prompt + 历史 + 本次输入
    messages_for_llm = [{"role": "system", "content": system_prompt}]
    messages_for_llm.extend(history_messages)
    messages_for_llm.append(new_user_message)

    try:
        answer, time_cost = ask_vivogpt(
            messages=messages_for_llm,
            model=model,
            extra=extra
        )
        if answer is None:
            logger.error(f"模型推理失败: {time_cost}")
            return jsonify({
                "error": "model_error",
                "message": f"模型推理失败: {time_cost}"
            }), 500
        logger.info(f"大模型推理成功: 耗时={time_cost:.2f}秒, 响应长度={len(answer)}")

        # 5. 存储当前问答到历史
        conversation_history[user_id].append(new_user_message)
        conversation_history[user_id].append({
            "role": "assistant",
            "content": answer
        })

        # 6. 返回结果
        return jsonify({
            "reply": answer,
            "timeCost": round(time_cost, 3)
        })
    except Exception as e:
        logger.exception("调用大模型时发生错误")
        return jsonify({
            "error": "model_invocation_error",
            "message": f"调用大模型时发生错误: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("启动 Flask 服务器...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.exception("服务器启动失败")
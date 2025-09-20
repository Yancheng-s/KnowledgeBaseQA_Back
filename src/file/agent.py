# agent.py
import traceback
from flask import current_app
from flask import request
import asyncio
from concurrent.futures import ThreadPoolExecutor
from database.database import db
from src.pojo.agent_pojo import AgentPojo
from src.utils.temporary_message.search_multiple_kbs import search_multiple_kbs
from src.utils.tongti_Trub import get_chat_completion
from src.utils.temporary_message.model_service import ModelService
from src.utils.temporary_message.prompt_builder import PromptBuilder
from src.utils.temporary_message.tool_functions import ToolFunctions, logger
from src.utils.temporary_message.model_loader import load_model
from langchain import LLMChain, PromptTemplate
from src.utils.temporary_message.conversation_manager import ConversationManager
from src.utils.temporary_message.tool_functions import ToolFunctions

# 全局缓存字典，用于存储 llm_knowledge 和对应的 FAISS 索引
knowledge_cache = {}
# 全局缓存字典，用于存储图片和文件解析结果
tool_cache = {}

def agent(app):

    # 全局缓存字典，用于存储对话历史
    conversation_cache = {}

    @app.route('/addAgent', methods=['POST'])
    def add_agent():
        try:
            # 解析请求体中的 JSON 数据
            data = request.json

            print("数据：", data)
            # 创建 AgentPojo 实例
            agent = AgentPojo(
                agent_name=data.get('agent_name'),
                agent_state=data.get('agent_state'),
                agent_id=data.get('agent_id'),
                llm_api=data.get('llm_api'),
                llm_prompt=data.get('llm_prompt'),
                llm_image=data.get('llm_image'),
                llm_knowledge=data.get('llm_knowledge'),
                llm_file=data.get('llm_file'),
                llm_internet=data.get('llm_internet'),
                llm_memory=data.get('llm_memory'),
                llm_maximum_length_of_reply=data.get('llm_maximum_length_of_reply'),
                llm_carry_number_of_rounds_of_context=data.get('llm_carry_number_of_rounds_of_context'),
                llm_temperature_coefficient=data.get('llm_temperature_coefficient')
            )
            # 将记录添加到数据库
            db.session.add(agent)
            db.session.commit()
            return {'message': '智能体已成功添加！'}, 201

        except Exception as e:
            # 如果发生错误，回滚事务并返回错误信息
            db.session.rollback()
            return {'error': str(e)}, 500

    @app.route('/selectAllAgents', methods=['GET'])
    def select_all_agents():
        try:
            # 获取所有记录
            agents = AgentPojo.query.all()

            # 将结果转换为可序列化的格式（如字典）
            result = [
                {
                    'id': agent.id,
                    'agent_name': agent.agent_name,
                    'agent_state': agent.agent_state,
                    'agent_id': agent.agent_id,
                    'llm_api': agent.llm_api,
                    'llm_prompt': agent.llm_prompt,
                    'llm_image': agent.llm_image,
                    'llm_knowledge': agent.llm_knowledge,
                    'llm_file': agent.llm_file,
                    'llm_internet': agent.llm_internet,
                    'llm_memory': agent.llm_memory,
                    'llm_maximum_length_of_reply': agent.llm_maximum_length_of_reply,
                    'llm_carry_number_of_rounds_of_context': agent.llm_carry_number_of_rounds_of_context,
                    'llm_temperature_coefficient': agent.llm_temperature_coefficient
                }
                for agent in agents
            ]

            return result, 200

        except Exception as e:
            # 如果发生错误，返回错误信息
            return {'error': str(e)}, 500

    @app.route('/optimizePromptWords', methods=['POST'])
    def optimize_prompt_words():
        try:
            # 获取用户输入的 Prompt
            user_input = request.json.get("prompt", "")

            # 构造消息列表
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一个专业的 Prompt 优化助手，负责帮助用户改进他们的输入文本。你的目标是："
                        "1. 提高文本的清晰度和逻辑性。"
                        "2. 确保语义明确，减少歧义。"
                        "3. 在必要时，调整措辞以增强表达效果，但不要改变原意。"
                        "示例："
                        "- 用户输入：你是一个老师，帮助学生解决问题。"
                        "- 你是一位耐心且专业的老师，擅长以清晰易懂的方式引导学生理解问题并找到解决方案。"
                        "请根据以上规则对用户的输入进行优化。"
                    ),
                },
                {"role": "user", "content": user_input},
            ]

            # 调用 get_chat_completion 获取模型响应
            response = get_chat_completion(messages=messages)

            # 提取 content 内容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            # 返回模型响应作为 HTTP 响应
            return {'content': content}, 200

        except Exception as e:
            # 如果发生错误，返回错误信息
            return {'error': str(e)}, 500

    @app.route('/updateAgentById/<agent_id>', methods=['PUT'])
    def update_agent_by_id(agent_id):
        try:
            data = request.json

            print("更新：", data)
            agent = AgentPojo.query.filter_by(agent_id=agent_id).first()

            if not agent:
                return {'error': '未找到指定的智能体'}, 404

            agent.agent_name = data.get('agent_name', agent.agent_name)
            agent.agent_state = data.get('agent_state', agent.agent_state)
            agent.llm_api = data.get('llm_api', agent.llm_api)
            agent.llm_prompt = data.get('llm_prompt', agent.llm_prompt)
            agent.llm_image = data.get('llm_image', agent.llm_image)
            agent.llm_knowledge = data.get('llm_knowledge', agent.llm_knowledge)
            agent.llm_file = data.get('llm_file', agent.llm_file)
            agent.llm_internet = data.get('llm_internet', agent.llm_internet)
            agent.llm_memory = data.get('llm_memory', agent.llm_memory)
            agent.llm_maximum_length_of_reply = data.get('llm_maximum_length_of_reply',
                                                         agent.llm_maximum_length_of_reply)
            agent.llm_carry_number_of_rounds_of_context = data.get('llm_carry_number_of_rounds_of_context',
                                                                   agent.llm_carry_number_of_rounds_of_context)
            agent.llm_temperature_coefficient = data.get('llm_temperature_coefficient',
                                                         agent.llm_temperature_coefficient)

            db.session.commit()

            return {'message': '智能体信息已成功更新！'}, 200

        except Exception as e:
            # 如果发生错误，回滚事务并返回错误信息
            db.session.rollback()
            return {'error': str(e)}, 500

    @app.route('/processAgent/<agent_id>', methods=['POST'])
    def process_agent(agent_id):
        try:
            data = request.json

            # 1. 并行处理知识库搜索和工具调用
            additional_info = ""
            tool_results = []
            user_id = ""

            app = current_app._get_current_object()

            # 使用线程池并行执行 - 使用全局导入的 ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=10) as executor:
                knowledge_future = executor.submit(
                    process_knowledge_search_with_app,
                    app, data.get("llm_knowledge"), data.get("message")
                )
                tools_future = executor.submit(
                    process_tools,
                    data.get("llm_image"), data.get("llm_file"),
                    data.get("llm_internet"), data.get("message", "")
                )

                additional_info = knowledge_future.result()
                tool_results = tools_future.result()

            # 2. 获取模型信息（缓存优化）
            result = ModelService.get_model_info(data.get("llm_api"))
            if isinstance(result, dict) and result.get("error"):
                return {'error': result["error"]}, 500

            model_name, model_key = result

            # 添加模型缓存
            model_cache = {}

            def get_cached_model(model_name, api_key, temperature, max_tokens):
                cache_key = f"{model_name}_{api_key}_{temperature}_{max_tokens}"

                if cache_key in model_cache:
                    return model_cache[cache_key]

                model = load_model(model_name, api_key, temperature, max_tokens)
                model_cache[cache_key] = model
                return model

            # 3. 使用缓存的模型实例
            llm_instance = get_cached_model(
                model_name=model_name,
                api_key=model_key,
                temperature=float(data.get("llm_temperature_coefficient", 0.8)),
                max_tokens=int(data.get("llm_maximum_length_of_reply", 2048))
            )

            # 4. 加载对话历史
            user_id = data.get("user_id")
            llm_memory = data.get("llm_memory", "n")
            max_rounds = int(data.get("llm_carry_number_of_rounds_of_context", 10))
            history = ConversationManager.load_conversation_history(user_id, agent_id, llm_memory, max_rounds)

            # 5. 构建提示词
            prompt_template = build_optimized_prompt(
                llm_prompt=data.get("llm_prompt"),
                additional_info=additional_info,
                tool_results=tool_results,
                history=history,
                message=data.get("message")
            )

            # 6. 调用模型
            prompt = PromptTemplate.from_template(prompt_template)
            llm_chain = LLMChain(prompt=prompt, llm=llm_instance)
            result = llm_chain.run(message=data.get("message"))

            # 7. 异步保存对话历史 - 使用新的线程池
            with ThreadPoolExecutor(max_workers=1) as save_executor:
                save_executor.submit(
                    ConversationManager.save_conversation,
                    user_id, agent_id,
                    data.get("message"), result, llm_memory
                )

            return {'result': result}, 200

        except Exception as e:
            print("🔥 处理智能体时出错:", str(e))
            traceback.print_exc()
            return {'error': str(e)}, 500

    # 子线程内部已经 push 过上下文，这里可以直接用
    def process_knowledge_search(llm_knowledge, message):
        if not llm_knowledge or not llm_knowledge.strip():
            return "无相关知识"
        kb_names = [n.strip() for n in llm_knowledge.split(",") if n.strip()]
        if not kb_names:
            return "无相关知识"
        # 下面这行需要上下文，但此时早已在 with app.app_context(): 里
        docs = search_multiple_kbs(kb_names, message, top_k=5)
        return "\n".join([d.page_content for d in docs]) if docs else "无相关知识"

    def process_knowledge_search_with_app(app, llm_knowledge, message):
        with app.app_context():
            return process_knowledge_search(llm_knowledge, message)

    def process_tools(llm_image, llm_file, llm_internet, message):
        """处理工具调用"""
        tool_results = []

        # 处理图片解析
        if llm_image == "y":
            # 遍历缓存，提取所有图片解析结果
            for cache_key, cache_value in tool_cache.items():
                if cache_value.get("type") == "image":
                    tool_results.append(cache_value["content"])

        # 处理文件解析
        if llm_file == "y":
            # 遍历缓存，提取所有文件解析结果
            for cache_key, cache_value in tool_cache.items():
                if cache_value.get("type") == "file":
                    tool_results.append(cache_value["content"])

        # 处理互联网搜索
        # if llm_internet == "y":
        #     tool_results.append(ToolFunctions.internet_search(message))

        return tool_results

    def build_optimized_prompt(llm_prompt, additional_info, tool_results, history, message):
        """优化的提示词构建"""
        parts = [llm_prompt]

        if additional_info and additional_info != "无相关知识":
            safe_info = additional_info.replace("{", "{{").replace("}", "}}")
            parts.append(f"\n相关知识:\n{safe_info}")

        if tool_results:
            safe_tools = "\n".join(tool_results).replace("{", "{{").replace("}", "}}")
            parts.append(f"\n工具结果:\n{safe_tools}")

        if history:
            parts.append("\n对话历史:")
            for msg, resp in history:
                parts.append(f"用户: {msg}\n助手: {resp}")

        parts.append(f"\n当前问题: {message}\n请根据以上信息回答:")

        return "\n".join(parts)

    @app.route('/api/parse/image', methods=['POST'])
    def parse_image():
        """
        解析图片内容接口
        请求体: {
            "image_data": "data:image/png;base64,...",  # base64编码的图片
            "filename": "example.png"  # 可选，文件名
        }
        """
        try:
            data = request.json

            if not data or 'image_data' not in data:
                return {'success': False, 'error': '缺少图片数据'}, 400

            image_data = data['image_data']
            imagename = data.get('filename', 'image')

            # 调用图片理解功能
            result = ToolFunctions.image_understanding(image_data)

            if result['success']:
                cache_key = imagename
                tool_cache[cache_key] = {
                    "type": "image",
                    "content": result['content'],
                    "image_info": result.get('image_info', {}),
                    "text_content": result.get('text_content', ''),
                    "image_description": result.get('image_description', '')
                }
                return {
                    'success': True,
                    'data': {
                        'content': result['content'],
                        'image_info': result.get('image_info', {}),
                        'text_content': result.get('text_content', ''),
                        'image_description': result.get('image_description', '')
                    },
                    'message': '图片解析成功'
                }, 200
            else:
                return {'success': False, 'error': result['error']}, 400

        except Exception as e:
            logger.error(f"图片解析接口异常: {str(e)}")
            return {'success': False, 'error': f'服务器内部错误: {str(e)}'}, 500

    @app.route('/api/parse/file', methods=['POST'])
    def parse_file():
        """
        解析文件内容接口
        请求体: {
            "file_data": "data:text/plain;base64,..." 或 "直接文本内容",
            "filename": "document.txt"  # 必须提供，用于判断文件类型
        }
        """
        try:
            data = request.json

            if not data or 'file_data' not in data:
                return {'success': False, 'error': '缺少文件数据'}, 400

            if 'filename' not in data:
                return {'success': False, 'error': '缺少文件名'}, 400

            file_data = data['file_data']
            filename = data['filename']

            # 调用文件解析功能
            result = ToolFunctions.file_parsing(file_data, filename)

            if result['success']:
                cache_key = filename
                tool_cache[cache_key] = {
                    "type": "file",
                    "content": result['content'],
                    "summary": result.get('summary', ''),
                    "stats": result.get('stats', {})
                }
                return {
                    'success': True,
                    'data': {
                        'content': result['content'],
                        'summary': result.get('summary', ''),
                        'stats': result.get('stats', {}),
                        'filename': result.get('filename', '')
                    },
                    'message': '文件解析成功'
                }, 200
            else:
                return {'success': False, 'error': result['error']}, 400

        except Exception as e:
            logger.error(f"文件解析接口异常: {str(e)}")
            return {'success': False, 'error': f'服务器内部错误: {str(e)}'}, 500
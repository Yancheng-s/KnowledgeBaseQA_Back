# agent.py
from flask import request
from database.database import db
from src.pojo.agent_pojo import AgentPojo
from src.utils.tongti_Trub import get_chat_completion
from src.utils.temporary_message.model_service import ModelService
from src.utils.temporary_message.prompt_builder import PromptBuilder
from src.utils.temporary_message.tool_functions import ToolFunctions
from src.utils.temporary_message.model_loader import load_model
from langchain import LLMChain, PromptTemplate

def agent(app):
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

    @app.route('/processAgent', methods=['POST'])
    def process_agent():
        try:
            data = request.json

            # 获取模型信息
            result = ModelService.get_model_info(data.get("llm_api"))
            if isinstance(result, dict) and result.get("error"):
                return {'error': result["error"]}, 500

            model_name, model_key = result

            # 加载语言模型实例
            llm_instance = load_model(model_name, model_key)

            # 构建提示词模板
            prompt_template = PromptBuilder.build_prompt(
                llm_prompt=data.get("llm_prompt"),
                llm_image=data.get("llm_image"),
                llm_file=data.get("llm_file"),
                llm_internet=data.get("llm_internet"),
                message=data.get("message")
            )

            # 调用工具方法函数
            additional_info = []
            if data.get("llm_image") == "y":
                additional_info.append(ToolFunctions.image_understanding("模拟图片数据"))
            if data.get("llm_file") == "y":
                additional_info.append(ToolFunctions.file_parsing("模拟文件路径"))
            if data.get("llm_internet") == "y":
                additional_info.append(ToolFunctions.internet_search("模拟搜索关键词"))

            # 将工具返回的结果添加到提示词
            prompt_template += "\n附加信息:\n" + "\n".join(additional_info)

            # 使用 LangChain 处理提示词
            llm_chain = LLMChain(prompt=PromptTemplate(template=prompt_template, input_variables=[]), llm=llm_instance)
            result = llm_chain.run(message=data.get("message"))

            return {'result': result}, 200

        except Exception as e:
            return {'error': str(e)}, 500
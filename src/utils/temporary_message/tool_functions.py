# src/utils/tool_functions.py
import json
import os
import requests
import base64
import io
import logging
import math
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import pytz
from openai import OpenAI
from tavily import TavilyClient
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
import pytesseract

logger = logging.getLogger(__name__)

class ToolFunctions:
    @staticmethod
    def _init_aliyun_client():
        """
        初始化阿里云客户端
        """
        api_key = "sk-c9b8659683a541bfaa8580448ca67766"
        if not api_key:
            raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
        return OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    @staticmethod
    def image_understanding(image_data: str) -> Dict[str, Any]:
        """
        图片理解功能 - 支持base64格式的图片，并调用阿里云大模型进行文字识别
        :param image_data: base64编码的图片数据
        :return: 包含分析结果的字典
        """
        try:
            # 检查是否是base64数据
            if not image_data.startswith('data:image'):
                return {
                    "success": False,
                    "error": "无效的图片格式，请提供base64编码的图片数据",
                    "content": ""
                }

            # 提取base64部分
            if ',' in image_data:
                image_data = image_data.split(',')[1]

            # 调用阿里云大模型API
            client = ToolFunctions._init_aliyun_client()
            completion = client.chat.completions.create(
                model="qwen-vl-max",
                messages=[
                    {"role": "system", "content": "你是一个多模态助手，能够识别图片中的文字并返回结果。"},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请识别以下图片中的文字："},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"},
                        ],
                    },
                ],
            )

            # 解析结果
            result = completion.choices[0].message.content
            return {
                "success": True,
                "content": result,
                "error": ""
            }

        except Exception as e:
            logger.error(f"图片理解失败: {str(e)}")
            return {
                "success": False,
                "error": f"图片处理异常: {str(e)}",
                "content": ""
            }

    @staticmethod
    def file_parsing(file_data: str, filename: str) -> Dict[str, Any]:
        """
        使用阿里云服务解析文件并进行文本理解
        :param file_data: base64编码的文件数据或直接文本内容
        :param filename: 文件名（用于判断文件类型）
        :return: 包含分析结果的字典
        """
        try:
            # 初始化阿里云客户端
            client = ToolFunctions._init_aliyun_client()

            # 检查是否是 Base64 编码的数据
            if file_data.startswith('data:'):
                if ',' in file_data:
                    file_data = file_data.split(',')[1]
                file_bytes = base64.b64decode(file_data)
            else:
                # 如果不是 Base64 数据，则认为是直接文本内容
                return {
                    "success": True,
                    "content": file_data,
                    "summary": ToolFunctions._generate_summary(file_data),
                    "stats": {
                        "file_type": "文本文件",
                        "file_extension": ".txt",
                        "content_length": len(file_data),
                        "line_count": len(file_data.split('\n')),
                        "word_count": len(file_data.split())
                    },
                    "filename": filename
                }

            # 获取文件扩展名
            file_ext = os.path.splitext(filename)[1].lower() if filename else '.txt'
            file_type = ToolFunctions._get_file_type(file_ext)

            # 上传文件到阿里云
            file_object = client.files.create(
                file=io.BytesIO(file_bytes),  # 使用 BytesIO 将字节流包装为文件对象
                purpose="file-extract"  # 指定用途为文件解析
            )
            file_id = file_object.id

            # 调用模型进行文本理解
            completion = client.chat.completions.create(
                model="qwen-doc-turbo",  # 使用 qwen-long 模型
                messages=[
                    {'role': 'system', 'content': f'fileid://{file_id}'},  # 引用文件 ID
                    {'role': 'user', 'content': "这篇文章讲了什么？"}  # 默认问题
                ]
            )

            # 解析返回结果
            result = completion.choices[0].message.content
            return {
                "success": True,
                "content": result,
                "error": ""
            }

        except Exception as e:
            logger.error(f"文件理解失败: {str(e)}")
            return {
                "success": False,
                "error": f"文件理解异常: {str(e)}",
                "content": ""
            }

    @staticmethod
    def _get_file_type(extension: str) -> str:
        """
        根据文件扩展名返回文件类型描述
        :param extension: 文件扩展名
        :return: 文件类型描述
        """
        type_map = {
            ".txt": "文本文件",
            ".docx": "Word文档",
            ".pdf": "PDF文件",
            ".xlsx": "Excel文件",
            ".jpg": "图片文件",
            ".png": "图片文件"
        }
        return type_map.get(extension, "未知文件类型")

    @staticmethod
    def _generate_summary(content: str) -> str:
        """
        根据文件内容生成简要摘要
        :param content: 文件内容
        :return: 摘要字符串
        """
        lines = content.split('\n')[:5]  # 取前5行
        return "\n".join(lines) + ("..." if len(lines) > 5 else "")

    @staticmethod
    def _classify_query_type(query: str) -> str:
        """
        智能分类查询类型
        """
        query_lower = query.lower().strip()

        # 实时信息查询
        realtime_patterns = [
            r'(今天|明天|昨天|现在|当前|此刻).*(星期几|几号|日期|时间|天气)',
            r'(what day|what time|what date|weather)',
            r'现在几点|当前时间|今天几号',
            r'^星期几$|^今天星期几$'
        ]
        for pattern in realtime_patterns:
            if re.search(pattern, query_lower):
                return 'realtime'

        # 数学计算
        math_patterns = [
            r'(\d+[\+\-\*\/]\d+)',
            r'计算|等于多少|多少钱|多少元',
            r'平方|立方|开方|根号',
            r'sin|cos|tan|log|ln|exp'
        ]
        for pattern in math_patterns:
            if re.search(pattern, query_lower):
                return 'math'

        # 单位换算
        conversion_patterns = [
            r'换算|转换|等于多少|多少美元|多少人民币',
            r'摄氏度|华氏度|公里|英里|公斤|磅',
            r'cm|m|km|inch|foot|yard'
        ]
        for pattern in conversion_patterns:
            if re.search(pattern, query_lower):
                return 'conversion'

        # 定义查询
        definition_patterns = [
            r'什么是|什么叫|是什么意思|定义',
            r'who is|what is|define'
        ]
        for pattern in definition_patterns:
            if re.search(pattern, query_lower):
                return 'definition'

        # 普通搜索
        return 'search'

    @staticmethod
    def internet_search(query: str) -> Dict[str, Any]:
        """
        智能联网搜索 - 支持多种查询类型
        """
        try:
            # 智能分类查询类型
            query_type = ToolFunctions._classify_query_type(query)

            # 根据不同类型采取不同处理策略
            if query_type == 'realtime':
                return ToolFunctions._handle_realtime_query(query)
            elif query_type == 'math':
                return ToolFunctions._handle_math_query(query)
            elif query_type == 'conversion':
                return ToolFunctions._handle_conversion_query(query)
            elif query_type == 'definition':
                return ToolFunctions._handle_definition_query(query)
            else:
                return ToolFunctions._handle_general_search(query)

        except Exception as e:
            logger.error(f"智能搜索失败: {str(e)}")
            return {"success": False, "error": f"搜索处理异常: {str(e)}", "content": ""}

    @staticmethod
    def _handle_realtime_query(query: str) -> Dict[str, Any]:
        """
        处理实时信息查询
        """
        try:
            query_lower = query.lower()
            china_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(china_tz)

            # 修复变量名错误
            weekdays_cn = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            weekdays_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            # 日期时间查询
            if any(keyword in query_lower for keyword in ['今天', 'today', '现在', '当前']):
                if any(keyword in query_lower for keyword in ['星期几', 'what day']):
                    content = f"""📅 今天是 {now.strftime('%Y年%m月%d日')}
    📆 星期：{weekdays_cn[now.weekday()]} ({weekdays_en[now.weekday()]})
    ⏰ 当前时间：{now.strftime('%H:%M:%S')}
    📍 时区：北京时间 (UTC+8)

    详细日期信息：
    • 年份：{now.year}年
    • 月份：{now.month}月
    • 日期：{now.day}日
    • 一年中的第{now.timetuple().tm_yday}天
    • 本周是第{now.isocalendar()[1]}周
    • 季度：第{(now.month - 1) // 3 + 1}季度"""
                    return {"success": True, "content": content, "error": ""}

                elif any(keyword in query_lower for keyword in ['时间', 'what time']):
                    content = f"⏰ 当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')} (北京时间)"
                    return {"success": True, "content": content, "error": ""}

            # 明天查询
            elif any(keyword in query_lower for keyword in ['明天', 'tomorrow']):
                tomorrow = now + timedelta(days=1)
                content = f"📅 明天是 {tomorrow.strftime('%Y年%m月%d日')} {weekdays_cn[tomorrow.weekday()]}"
                return {"success": True, "content": content, "error": ""}

            # 昨天查询
            elif any(keyword in query_lower for keyword in ['昨天', 'yesterday']):
                yesterday = now - timedelta(days=1)
                content = f"📅 昨天是 {yesterday.strftime('%Y年%m月%d日')} {weekdays_cn[yesterday.weekday()]}"
                return {"success": True, "content": content, "error": ""}

            # 星期几查询（简化版）
            elif '星期几' in query_lower:
                content = f"📅 今天是 {now.strftime('%Y年%m月%d日')} {weekdays_cn[now.weekday()]}"
                return {"success": True, "content": content, "error": ""}

            # 默认实时信息
            content = f"""📅 当前日期：{now.strftime('%Y年%m月%d日')}
    📆 今天星期：{weekdays_cn[now.weekday()]}
    ⏰ 当前时间：{now.strftime('%H:%M:%S')}
    📍 时区：北京时间"""
            return {"success": True, "content": content, "error": ""}

        except Exception as e:
            logger.error(f"实时查询处理失败: {str(e)}")
            # 降级到普通搜索
            return ToolFunctions._handle_general_search(query)

    @staticmethod
    def _handle_math_query(query: str) -> Dict[str, Any]:
        """
        处理数学计算查询
        """
        try:
            # 提取数学表达式
            math_expression = ToolFunctions._extract_math_expression(query)
            if not math_expression:
                return ToolFunctions._handle_general_search(query)

            # 安全计算
            result = ToolFunctions._safe_eval(math_expression)

            content = f"""🧮 数学计算：
    表达式：{math_expression}
    结果：{result}

    计算过程：
    {math_expression} = {result}"""

            return {"success": True, "content": content, "error": ""}

        except Exception as e:
            return {"success": False, "error": f"数学计算失败: {str(e)}", "content": ""}

    @staticmethod
    def _handle_conversion_query(query: str) -> Dict[str, Any]:
        """
        处理单位换算查询
        """
        try:
            # 货币换算
            if any(keyword in query for keyword in ['美元', '人民币', '欧元', '日元']):
                # 这里可以集成汇率API
                content = "💰 货币换算功能需要实时汇率数据，建议使用专门的汇率API"
                return {"success": True, "content": content, "error": ""}

            # 温度换算
            elif any(keyword in query for keyword in ['摄氏度', '华氏度']):
                content = "🌡️ 温度换算：\n• 摄氏度转华氏度: °F = (°C × 9/5) + 32\n• 华氏度转摄氏度: °C = (°F - 32) × 5/9"
                return {"success": True, "content": content, "error": ""}

            # 长度换算
            elif any(keyword in query for keyword in ['米', '公里', '英里', '英尺']):
                content = "📏 长度换算：\n• 1公里 = 0.621371英里\n• 1英里 = 1.60934公里\n• 1米 = 3.28084英尺"
                return {"success": True, "content": content, "error": ""}

            return ToolFunctions._handle_general_search(query)

        except Exception as e:
            return {"success": False, "error": f"单位换算失败: {str(e)}", "content": ""}

    @staticmethod
    def _handle_definition_query(query: str) -> Dict[str, Any]:
        """
        处理定义查询
        """
        try:
            # 提取要查询的术语
            term = ToolFunctions._extract_term(query)
            if not term:
                return ToolFunctions._handle_general_search(query)

            # 使用Tavily进行定义搜索
            tavily_api_key = "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"
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(f"{term} 定义 含义", max_results=3)

            # 提取定义信息
            definitions = []
            for result in response.get('results', []):
                title = result.get('title', '')
                content = result.get('content', '')
                if '定义' in title or '含义' in title or '是什么' in title:
                    definitions.append(f"📚 {title}\n{content}")

            if definitions:
                content = f"📖 关于【{term}】的定义：\n\n" + "\n\n".join(definitions)
                return {"success": True, "content": content, "error": ""}
            else:
                return ToolFunctions._handle_general_search(query)

        except Exception as e:
            return {"success": False, "error": f"定义查询失败: {str(e)}", "content": ""}

    @staticmethod
    def _handle_general_search(query: str) -> Dict[str, Any]:
        """
        处理普通搜索查询
        """
        try:
            tavily_api_key = "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"
            if not tavily_api_key:
                return {"success": False, "error": "请设置TAVILY_API_KEY环境变量", "content": ""}

            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(query, max_results=5)

            # 增强搜索结果
            enhanced_results = ToolFunctions._enhance_search_results(query, response.get('results', []))

            return {"success": True, "content": enhanced_results, "error": ""}

        except Exception as e:
            return {"success": False, "error": f"搜索失败: {str(e)}", "content": ""}

    @staticmethod
    def _extract_math_expression(query: str) -> str:
        """提取数学表达式"""
        # 匹配简单的数学表达式
        patterns = [
            r'(\d+[\+\-\*\/]\d+)',  # 基础运算
            r'(\d+的(平方|立方))',  # 平方立方
            r'(根号\d+)',  # 开方
            r'(\d+[\.\d]*\%?)'  # 百分比
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        return ""

    @staticmethod
    def _safe_eval(expression: str) -> float:
        """安全计算数学表达式"""
        # 移除不安全字符
        safe_expression = re.sub(r'[^0-9\+\-\*\/\.\(\)]', '', expression)

        # 简单计算
        try:
            return eval(safe_expression, {"__builtins__": None}, {})
        except:
            # 如果eval失败，尝试手动解析
            return ToolFunctions._manual_calculate(safe_expression)

    @staticmethod
    def _manual_calculate(expr: str) -> float:
        """手动解析简单数学表达式"""
        if '+' in expr:
            parts = expr.split('+')
            return sum(float(p) for p in parts)
        elif '-' in expr:
            parts = expr.split('-')
            return float(parts[0]) - sum(float(p) for p in parts[1:])
        elif '*' in expr:
            parts = expr.split('*')
            result = 1
            for p in parts:
                result *= float(p)
            return result
        elif '/' in expr:
            parts = expr.split('/')
            result = float(parts[0])
            for p in parts[1:]:
                result /= float(p)
            return result
        return float(expr)

    @staticmethod
    def _extract_term(query: str) -> str:
        """提取查询术语"""
        patterns = [
            r'什么是(.+?)',
            r'什么叫(.+?)',
            r'(.+?)是什么意思',
            r'定义(.+?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        return query

    @staticmethod
    def _enhance_search_results(query: str, results: list) -> str:
        """增强搜索结果展示"""
        if not results:
            return "🔍 未找到相关搜索结果"

        enhanced = []
        for i, result in enumerate(results[:3], 1):
            title = result.get('title', '无标题')
            content = result.get('content', '无内容')
            url = result.get('url', '#')

            # 截断过长的内容
            if len(content) > 200:
                content = content[:200] + "..."

            enhanced.append(f"{i}. 【{title}】\n{content}\n🔗 {url}\n")

        return "🔍 搜索结果：\n\n" + "\n".join(enhanced)
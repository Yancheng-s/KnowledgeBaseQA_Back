# src/utils/tool_functions.py
import json
import os
from idlelib import query

from multipart import file_path
from openai import OpenAI
import base64
import io
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
import pytesseract
from typing import Dict, Any
import logging
from pathlib import Path

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

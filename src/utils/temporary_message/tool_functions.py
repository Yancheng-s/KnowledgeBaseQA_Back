# src/utils/tool_functions.py
import os
import base64
import io
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
import pytesseract
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ToolFunctions:
    @staticmethod
    def image_understanding(image_data: str) -> Dict[str, Any]:
        """
        图片理解功能 - 支持base64格式的图片
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

            # 解码base64
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"base64解码失败: {str(e)}",
                    "content": ""
                }

            # 转换为图片对象
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                return {
                    "success": False,
                    "error": f"图片打开失败: {str(e)}",
                    "content": ""
                }

            # 获取图片信息
            image_info = {
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "width": image.width,
                "height": image.height
            }

            # OCR文字识别
            text_content = ToolFunctions._extract_text_from_image(image)

            # 生成图片描述
            image_description = ToolFunctions._generate_image_description(image, image_info)

            return {
                "success": True,
                "content": f"{text_content}\n\n{image_description}",
                "image_info": image_info,
                "text_content": text_content,
                "image_description": image_description
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
        文件解析功能 - 支持base64格式的文件或直接文本
        :param file_data: base64编码的文件数据或文本内容
        :param filename: 文件名（用于判断文件类型）
        :return: 包含解析结果的字典
        """
        try:
            file_ext = os.path.splitext(filename)[1].lower() if filename else '.txt'
            file_type = ToolFunctions._get_file_type(file_ext)

            # 处理base64文件
            if file_data.startswith('data:'):
                if ',' in file_data:
                    file_data = file_data.split(',')[1]

                try:
                    file_bytes = base64.b64decode(file_data)
                    content = ToolFunctions._parse_file_bytes(file_bytes, file_ext)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"文件解码失败: {str(e)}",
                        "content": ""
                    }
            else:
                # 直接文本内容
                content = file_data

            # 统计信息
            stats = {
                "file_type": file_type,
                "file_extension": file_ext,
                "content_length": len(content),
                "line_count": len(content.split('\n')),
                "word_count": len(content.split())
            }

            # 生成摘要
            summary = ToolFunctions._generate_summary(content)

            return {
                "success": True,
                "content": content,
                "summary": summary,
                "stats": stats,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"文件解析失败: {str(e)}")
            return {
                "success": False,
                "error": f"文件解析异常: {str(e)}",
                "content": ""
            }

    @staticmethod
    def internet_search(query):
        # 模拟联网搜索功能
        return f"搜索结果: {query}"

    # 私有辅助方法
    @staticmethod
    def _extract_text_from_image(image) -> str:
        """从图片中提取文字"""
        try:
            # 尝试使用OCR
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            if text.strip():
                return f"识别到的文字:\n{text.strip()}"
        except Exception as e:
            logger.warning(f"OCR识别失败: {str(e)}")

        return "图片中未识别到文字"

    @staticmethod
    def _generate_image_description(image, image_info: Dict[str, Any]) -> str:
        """生成图片描述"""
        description_parts = [
            "图片分析结果:",
            f"- 格式: {image_info.get('format', '未知')}",
            f"- 尺寸: {image_info.get('width', 0)}x{image_info.get('height', 0)}",
            f"- 颜色模式: {image_info.get('mode', '未知')}",
            "- 内容描述: 包含视觉元素，建议结合具体问题进行分析"
        ]
        return "\n".join(description_parts)

    @staticmethod
    def _get_file_type(extension: str) -> str:
        """获取文件类型描述"""
        type_mapping = {
            '.txt': '文本文件',
            '.pdf': 'PDF文档',
            '.docx': 'Word文档',
            '.xlsx': 'Excel表格',
            '.xls': 'Excel表格',
            '.csv': 'CSV文件',
            '.pptx': 'PowerPoint演示文稿',
            '.jpg': 'JPEG图片',
            '.jpeg': 'JPEG图片',
            '.png': 'PNG图片',
            '.gif': 'GIF图片'
        }
        return type_mapping.get(extension, '未知文件类型')

    @staticmethod
    def _parse_file_bytes(file_bytes: bytes, extension: str) -> str:
        """解析文件字节内容"""
        try:
            if extension == '.pdf':
                return ToolFunctions._parse_pdf(file_bytes)
            elif extension == '.docx':
                return ToolFunctions._parse_docx(file_bytes)
            elif extension in ['.xlsx', '.xls']:
                return ToolFunctions._parse_excel(file_bytes)
            elif extension == '.csv':
                return ToolFunctions._parse_csv(file_bytes)
            else:
                # 默认为文本文件
                return file_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"文件解析错误: {str(e)}")

    @staticmethod
    def _parse_pdf(file_bytes: bytes) -> str:
        """解析PDF文件"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            content = []
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    content.append(f"--- 第 {i + 1} 页 ---\n{text}")
            return "\n\n".join(content) if content else "PDF文件中未提取到文本内容"
        except Exception as e:
            return f"PDF解析失败: {str(e)}"

    @staticmethod
    def _parse_docx(file_bytes: bytes) -> str:
        """解析Word文档"""
        try:
            doc = Document(io.BytesIO(file_bytes))
            content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append(para.text)
            return "\n".join(content) if content else "Word文档中未提取到文本内容"
        except Exception as e:
            return f"Word文档解析失败: {str(e)}"

    @staticmethod
    def _parse_excel(file_bytes: bytes) -> str:
        """解析Excel文件"""
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
            return df.to_string()
        except Exception as e:
            return f"Excel解析失败: {str(e)}"

    @staticmethod
    def _parse_csv(file_bytes: bytes) -> str:
        """解析CSV文件"""
        try:
            content = file_bytes.decode('utf-8')
            return content
        except Exception as e:
            return f"CSV解析失败: {str(e)}"

    @staticmethod
    def _generate_summary(content: str, max_length: int = 500) -> str:
        """生成内容摘要"""
        if len(content) <= max_length:
            return content

        # 简单的摘要生成：取开头和结尾部分
        half_length = max_length // 2
        return content[:half_length] + "\n\n...\n\n" + content[-half_length:]
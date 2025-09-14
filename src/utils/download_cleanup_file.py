import requests
import tempfile
import os
import logging
from urllib.parse import urlparse

def download_file(url):
    """
    下载文件并保存到临时路径
    Args:
        url (str): 文件URL
    Returns:
        str: 临时文件路径
    Raises:
        Exception: 下载或保存失败时抛出异常
    """
    try:
        logging.info(f"开始下载文件: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 获取文件扩展名
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        extension = os.path.splitext(filename)[1] if os.path.splitext(filename)[1] else '.tmp'

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmpfile:
            tmpfile.write(response.content)
            logging.info(f"文件下载完成，保存路径: {tmpfile.name}")
            return tmpfile.name

    except requests.RequestException as e:
        error_msg = f"下载文件失败: {str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"保存文件失败: {str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)

def cleanup_temp_file(file_path):
    """清理临时文件"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logging.info(f"临时文件已清理: {file_path}")
    except Exception as e:
        logging.warning(f"清理临时文件失败: {e}")

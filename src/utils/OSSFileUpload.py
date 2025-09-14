# utils/OSSFileUpload.py
# import os
# import alibabacloud_oss_v2 as oss
#
# class OSSUploader:
#     def __init__(self):
#         # 从配置加载或硬编码写入
#         self.region = "cn-beijing"
#         self.bucket = "langflow-fileupload"
#         self.access_key_id = "LTAI5tCnraFhydt6kC6KtcyP"
#         self.access_key_secret = "3ycb7fEjpfcOuecmMrzmlxCMR0tERS"
#
#         # 初始化凭证和配置
#         credentials_provider = oss.credentials.StaticCredentialsProvider(
#             access_key_id=self.access_key_id,
#             access_key_secret=self.access_key_secret,
#             security_token=None
#         )
#
#         cfg = oss.config.load_default()
#         cfg.credentials_provider = credentials_provider
#         cfg.region = self.region
#
#         self.client = oss.Client(cfg)
#
#     def upload_file_stream(self, file_stream, filename):
#         """
#         接收文件流并上传到 OSS
#         :param file_stream: 文件流对象（如 Flask request.files['file'].stream）
#         :param filename: 原始文件名，用于生成 OSS 上的 key
#         :return: OSS 文件访问 URL
#         """
#         key = filename
#
#         try:
#             # 使用 put_object 直接上传流
#             self.client.put_object(oss.PutObjectRequest(
#                 bucket=self.bucket,
#                 key=key,
#                 body=file_stream
#             ))
#
#             return f"https://{self.bucket}.oss-{self.region}.aliyuncs.com/{key}"
#
#         except Exception as e:
#             raise RuntimeError(f"OSS Stream Upload Error: {e}")

# utils/OSSFileUpload.py
import os
import asyncio
import alibabacloud_oss_v2 as oss
from io import BufferedReader

class ProgressReader(BufferedReader):
    """
    包装文件流，用于追踪上传进度
    """
    def __init__(self, raw_stream, total_size, callback=None):
        super().__init__(raw_stream)
        self.total_size = total_size
        self.bytes_read = 0
        self.callback = callback

    def read(self, size=-1):
        chunk = super().read(size)
        if chunk:
            self.bytes_read += len(chunk)
            if self.callback:
                self.callback(self.bytes_read, self.total_size)
        return chunk

class OSSUploader:
    def __init__(self):
        # OSS 配置信息
        self.region = "cn-beijing"
        self.bucket = "langflow-fileupload"
        self.access_key_id = "LTAI5tCnraFhydt6kC6KtcyP"
        self.access_key_secret = "3ycb7fEjpfcOuecmMrzmlxCMR0tERS"

        # 初始化凭证和配置
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            security_token=None
        )

        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = self.region

        self.client = oss.Client(cfg)

    def upload_file_stream(self, file_stream, filename):
        """
        接收文件流并上传到 OSS，并显示上传进度
        :param file_stream: 文件流对象（如 Flask request.files['file'].stream）
        :param filename: 原始文件名，用于生成 OSS 上的 key
        :return: OSS 文件访问 URL
        """
        key = filename

        # 获取文件总大小（如果文件流支持 seek/tell）
        original_pos = file_stream.tell()
        file_stream.seek(0, os.SEEK_END)
        total_size = file_stream.tell()
        file_stream.seek(original_pos)

        # 显示上传进度的回调函数
        def progress_callback(bytes_read, total_size):
            percent = int((bytes_read / total_size) * 100)
            print(f"\r上传进度: {percent}% [{'#' * int(percent / 2)}{' ' * (50 - int(percent / 2))}]", end="", flush=True)

        # 包装文件流，添加进度追踪
        progress_stream = ProgressReader(file_stream, total_size, progress_callback)

        try:
            # 使用 asyncio.run() 启动事件循环
            result = asyncio.run(self.async_upload(progress_stream, key))
            return result
        except Exception as e:
            raise RuntimeError(f"OSS Stream Upload Error: {e}")

    async def async_upload(self, progress_stream, key):
        """
        异步上传文件流到 OSS
        """
        try:
            self.client.put_object(
                oss.PutObjectRequest(
                    bucket=self.bucket,
                    key=key,
                    body=progress_stream
                )
            )
            return f"https://{self.bucket}.oss-{self.region}.aliyuncs.com/{key}"
        except Exception as e:
            raise RuntimeError(f"OSS Async Upload Error: {e}")

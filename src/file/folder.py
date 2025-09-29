# folder.py

from flask import Flask, request, send_file
from flask_socketio import SocketIO, emit

from database.database import db
from src.pojo.file_pojo import File
from src.pojo.folder_pojo import Folder
from src.utils.OSSFileUpload import OSSUploader

import base64
import os
import mimetypes
from urllib.parse import urlparse
import requests
from io import BytesIO

uploader = OSSUploader()

def folder(app: Flask):

    @app.route('/addfolder', methods=['POST'])
    def add_folder():
        data = request.json
        folder = Folder(folder_name=data.get('folder_name'))
        # folder = Folder(folder_name='赵六')
        db.session.add(folder)
        db.session.commit()
        return '文件夹已添加！'

    @app.route('/selectallfolder', methods=['GET'])
    def select_all_folder():
        folders = Folder.query.all()  # 获取所有记录
        # 将结果转换为可序列化的格式（如字典）
        result = [{'id': f.id, 'folder_name': f.folder_name} for f in folders]
        return result, 200

    @app.route('/updatefolder', methods=['POST'])
    def update_folder_by_name():
        data = request.json
        old_name = data.get('oldName')
        new_name = data.get('newName')
        Folder.query.filter_by(folder_name=old_name).update({'folder_name': new_name})
        db.session.commit()
        return '文件夹已更新！'

    @app.route('/delatefolder', methods=['POST'])
    def delete_folder_by_name():
        data = request.json
        folder_name = data.get('folder_name')
        Folder.query.filter_by(folder_name=folder_name).delete()
        db.session.commit()
        return '文件夹已删除！'

    @app.route('/fileupload', methods=['POST'])
    def file_upload():
        file = request.files['file']

        # 获取文件流，并重置指针（防止已被读取过）
        file_stream = file.stream
        file_stream.seek(0)

        try:
            # 获取文件大小：移动指针到末尾
            file_stream.seek(0, 2)  # 0 表示偏移量，2 表示从文件末尾开始计算
            file_size = file_stream.tell()  # 此时得到的是文件总大小
            # 转换为 MB（保留两位小数）
            file_size_mb = round(file_size / (1024 * 1024), 2)

            # 重置指针到文件开头，以便上传操作
            file_stream.seek(0)

            # 仅传入文件流和文件名
            oss_url = uploader.upload_file_stream(file_stream, file.filename)
            # 获取可选参数 file_class
            file_class = request.form.get('file_class')  # 或者 request.values.get('file_class')
            # 构建参数字典
            file_data = {
                'file_name': file.filename,
                'file_path': oss_url,
                'file_size': file_size_mb
            }
            if file_class is not None:
                file_data['file_class'] = file_class

            # 添加到数据库
            db.session.add(File(**file_data))
            db.session.commit()

            return {'message': '文件已上传至 OSS', 'url': oss_url, 'file_class': file_class}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @app.route('/selectfilelist', methods=['POST'])
    def select_file_list():
        data = request.json
        file_class = data.get('folder_name')
        if file_class == '':
            files = File.query.all()
        else:
            files = File.query.filter_by(file_class=file_class).all()
        result = [{'file_name': f.file_name, 'file_path': f.file_path, 'file_size': f.file_size, 'file_time': f.file_time} for f in files]
        return result, 200

    # 根据文件名模糊查询
    @app.route('/selectfilebyname', methods=['POST'])
    def select_file_by_name():
        data = request.json
        file_name = data.get('keyword')
        files = File.query.filter(File.file_name.like('%' + file_name + '%')).all()
        result = [{'file_name': f.file_name, 'file_path': f.file_path, 'file_size': f.file_size, 'file_time': f.file_time} for f in files]
        return result, 200

    @app.route('/deletefilebyname', methods=['POST'])
    def delete_file_by_name():
        """
        根据文件名删除文件功能
        请求体: {
            "file_name": "example.txt"  # 要删除的文件名
        }
        """
        try:
            data = request.json

            if not data or 'file_name' not in data:
                return {'success': False, 'error': '缺少文件名参数'}, 400

            file_name = data['file_name']

            # 查找要删除的文件
            file_to_delete = File.query.filter_by(file_name=file_name).first()

            if not file_to_delete:
                return {'success': False, 'error': f'文件 {file_name} 不存在'}, 404

            # 从数据库中删除记录
            db.session.delete(file_to_delete)
            db.session.commit()

            return {'success': True, 'message': f'文件 {file_name} 已成功删除'}, 200

        except Exception as e:
            # 如果发生错误，回滚事务并返回错误信息
            db.session.rollback()
            return {'success': False, 'error': f'删除文件时发生错误: {str(e)}'}, 500

    # Office文档在线预览解决方案

    @app.route('/getfilepreview', methods=['POST'])
    def get_file_preview():
        """
        获取文件预览内容 - 支持Office文档在线预览
        """
        try:
            data = request.json
            file_name = data.get('file_name')
            file_path = data.get('file_path')

            if not file_name or not file_path:
                return {'error': '缺少文件名或文件路径'}, 400

            print(f"🔍 开始预览文件: {file_name}")
            print(f"🔍 原始路径: {file_path}")

            # 设置正确的headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            file_content = b''

            try:
                # 下载文件内容
                response = requests.get(file_path, headers=headers, timeout=30, stream=True)
                response.raise_for_status()

                # 读取内容
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_content += chunk

                print(f"✅ 文件下载成功，大小: {len(file_content)} bytes")

            except requests.RequestException as e:
                print(f"❌ 下载失败: {str(e)}")
                return {'error': f'下载文件失败: {str(e)}'}, 500

            if len(file_content) == 0:
                return {'error': '文件内容为空，请检查文件是否存在'}, 400

            # 获取文件扩展名和MIME类型
            file_ext = os.path.splitext(file_name)[1].lower()
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

            print(f"📁 文件扩展名: {file_ext}")
            print(f"📄 MIME类型: {mime_type}")

            preview_info = {
                'file_name': file_name,
                'mime_type': mime_type,
                'file_size': len(file_content)
            }

            # 根据文件类型处理内容
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
                # 图片文件：返回base64编码
                preview_info['preview_type'] = 'image'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"

            elif file_ext in ['.pdf']:
                # PDF文件：返回base64编码
                preview_info['preview_type'] = 'pdf'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"

            elif file_ext in ['.txt', '.md', '.json', '.xml', '.csv', '.log', '.js', '.py', '.html', '.css']:
                # 文本文件：直接返回文本内容
                try:
                    text_content = file_content.decode('utf-8')
                    if len(text_content) > 100000:
                        text_content = text_content[:100000] + '\n\n... (文件过大，仅显示前100KB内容)'
                    preview_info['preview_type'] = 'text'
                    preview_info['file_content'] = text_content
                except UnicodeDecodeError:
                    preview_info['preview_type'] = 'unsupported'
                    preview_info['message'] = '文件编码不支持，无法预览'

            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                # 视频文件：返回base64编码
                preview_info['preview_type'] = 'video'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"

            elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.aac']:
                # 音频文件：返回base64编码
                preview_info['preview_type'] = 'audio'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"

            elif file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                # Office文档：提供在线预览选项
                preview_info['preview_type'] = 'office'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"

                # 添加在线预览URL选项
                preview_info['office_preview_urls'] = {
                    'microsoft_office': f"https://view.officeapps.live.com/op/embed.aspx?src={file_path}",
                    'google_docs': f"https://docs.google.com/gview?url={file_path}&embedded=true",
                    'mozilla_pdf': f"https://mozilla.github.io/pdf.js/web/viewer.html?file={file_path}"
                }

                preview_info['message'] = 'Office文档需要下载后查看，或使用在线预览服务'

            else:
                # 其他文件类型：返回base64编码
                preview_info['preview_type'] = 'unsupported'
                preview_info['file_content'] = base64.b64encode(file_content).decode('utf-8')
                preview_info['data_url'] = f"data:{mime_type};base64,{preview_info['file_content']}"
                preview_info['message'] = '该文件类型暂不支持预览'

            print(f"🎯 预览类型: {preview_info['preview_type']}")
            print(f"📊 文件内容大小: {len(preview_info.get('file_content', ''))}")

            return preview_info, 200

        except Exception as e:
            print(f"❌ 获取预览内容失败: {str(e)}")
            return {'error': f'获取预览内容失败: {str(e)}'}, 500

    @app.route('/getfilecontent', methods=['GET'])
    def get_file_content():
        """
        获取文本文件内容（用于预览）
        查询参数: file_name=example.txt
        """
        try:
            file_name = request.args.get('file_name')
            if not file_name:
                return {'error': '缺少文件名参数'}, 400

            # 从数据库获取文件信息
            file_record = File.query.filter_by(file_name=file_name).first()
            if not file_record:
                return {'error': '文件不存在'}, 404

            # 从OSS下载文件内容
            response = requests.get(file_record.file_path, timeout=30)
            response.raise_for_status()

            # 获取文件内容
            content = response.text

            # 限制文件大小（避免过大的文件）
            if len(content) > 100000:  # 100KB限制
                content = content[:100000] + '\n\n... (文件过大，仅显示前100KB内容)'

            return {
                'file_name': file_name,
                'content': content,
                'file_size': len(content)
            }, 200

        except requests.RequestException as e:
            return {'error': f'下载文件失败: {str(e)}'}, 500
        except Exception as e:
            return {'error': f'读取文件内容失败: {str(e)}'}, 500

    @app.route('/getfileinfo', methods=['POST'])
    def get_file_info():
        """
        获取文件详细信息
        请求体: {"file_name": "example.pdf"}
        """
        try:
            data = request.json
            file_name = data.get('file_name')

            if not file_name:
                return {'error': '缺少文件名参数'}, 400

            # 从数据库获取文件信息
            file_record = File.query.filter_by(file_name=file_name).first()
            if not file_record:
                return {'error': '文件不存在'}, 404

            return {
                'file_name': file_record.file_name,
                'file_path': file_record.file_path,
                'file_size': file_record.file_size,
                'file_time': file_record.file_time,
                'file_class': getattr(file_record, 'file_class', None)
            }, 200

        except Exception as e:
            return {'error': f'获取文件信息失败: {str(e)}'}, 500

    @app.route('/downloadfile', methods=['POST'])
    def download_file():
        """
        下载文件
        请求体: {"file_name": "example.pdf"}
        """
        try:
            data = request.json
            file_name = data.get('file_name')

            if not file_name:
                return {'error': '缺少文件名参数'}, 400

            # 从数据库获取文件信息
            file_record = File.query.filter_by(file_name=file_name).first()
            if not file_record:
                return {'error': '文件不存在'}, 404

            # 从OSS下载文件
            response = requests.get(file_record.file_path, timeout=60)
            response.raise_for_status()

            # 创建文件流
            file_stream = BytesIO(response.content)

            return send_file(
                file_stream,
                as_attachment=True,
                download_name=file_name,
                mimetype='application/octet-stream'
            )

        except requests.RequestException as e:
            return {'error': f'下载文件失败: {str(e)}'}, 500
        except Exception as e:
            return {'error': f'处理下载请求失败: {str(e)}'}, 500
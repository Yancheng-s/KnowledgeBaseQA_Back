# folder.py

from flask import Flask, request
from flask_socketio import SocketIO, emit

from database.database import db
from src.pojo.file_pojo import File
from src.pojo.folder_pojo import Folder
from src.utils.OSSFileUpload import OSSUploader

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
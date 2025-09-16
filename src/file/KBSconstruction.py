import json

from flask import Flask, request, jsonify
import os
import logging

from database.database import db
from src.pojo.KBSconstruction_pojo import KBSconstruction_pojo
from src.utils.chunk_documents import chunk_documents
from src.utils.download_cleanup_file import download_file, cleanup_temp_file
from src.utils.load_document import load_document
from src.utils.vectorize_documents import vectorize_documents


def KBSconstruction(app: Flask):
    @app.route('/addKBS', methods=['POST'])
    def addKBS():
        print("进入addKBS")

        data = request.get_json()

        required_fields = ['kon_name', 'kon_describe', 'emb_moddle', 'chunk', 'sentence_identifier',
                           'estimated_length_per_senction', 'segmental_overlap_length',
                           'excel_header_processing', 'similarity', 'MROD', 'sorting_config', 'file_list']

        for field in required_fields:
            if data.get(field) is None:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            # 获取文件路径列表
            file_list = data.get('file_list', [])
            kon_name = data.get('kon_name')
            emb_moddle = data.get('emb_moddle')

            # 获取分块参数
            chunk_setting = data.get('chunk')
            sentence_identifier = data.get('sentence_identifier')
            chunk_size = data.get('estimated_length_per_senction')
            chunk_overlap = data.get('segmental_overlap_length')

            # 加载所有文档
            all_documents = []

            # 处理每个文件
            for file_url in file_list:
                temp_file_path = None
                try:
                    # 下载文件到临时路径
                    temp_file_path = download_file(file_url)

                    # 验证文件是否存在
                    if not os.path.exists(temp_file_path):
                        raise FileNotFoundError(f"下载的文件不存在: {temp_file_path}")

                    # 加载文档内容
                    excel_header_processing = data.get('excel_header_processing', False)
                    documents = load_document(temp_file_path, excel_header_processing)

                    # 根据chunk设置分块
                    chunked_documents = chunk_documents(
                        documents,
                        chunk_setting=chunk_setting,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        sentence_identifier=sentence_identifier
                    )
                    all_documents.extend(chunked_documents)
                    print(f"分块完成，共处理 {len(chunked_documents)} 个文档块")

                except Exception as e:
                    logging.error(f"处理 OSS 文件失败: {str(e)}")
                    raise Exception(f"处理文件 {file_url} 时出错: {str(e)}")
                finally:
                    # 清理临时文件
                    try:
                        if temp_file_path is not None and os.path.exists(temp_file_path):
                            cleanup_temp_file(temp_file_path)
                    except Exception as cleanup_error:
                        logging.warning(f"清理临时文件时出错: {cleanup_error}")

            print(f"下载好文档，总共 {len(all_documents)} 个文档块")

            # 检查是否有文档需要处理
            if not all_documents:
                raise ValueError("没有有效的文档内容可以处理")

            # 向量化文档
            print("开始向量化文档")
            faiss_index_data, pkl_index_data = vectorize_documents(all_documents, kon_name, emb_moddle)

            print("向量化文档完成")

            # 存储 KBS 信息到数据库
            # 创建 data 的副本并序列化 file_list 为 JSON 字符串
            data_to_store = data.copy()
            data_to_store['file_list'] = json.dumps(data['file_list'])

            # 添加二进制数据
            data_to_store['faiss_index_data'] = faiss_index_data
            data_to_store['pkl_index_data'] = pkl_index_data

            new_kbs = KBSconstruction_pojo(**data_to_store)
            db.session.add(new_kbs)
            db.session.commit()

            return jsonify({"message": "KBS added successfully"}), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f"KBS创建失败: {str(e)}", exc_info=True)
            return jsonify({"error": f"KBS创建失败: {str(e)}"}), 500

    @app.route('/selectAllKBS', methods=['GET'])
    def select_all_kbs():
        """
        查询所有KBS
        :return:
        """
        kbs = KBSconstruction_pojo.query.all()

        result = [kbs.to_dict() for kbs in kbs]
        return jsonify(result), 200

    @app.route('/text', methods=['GET'])
    def get_text():
        return jsonify({"text": "这是测试文本"})
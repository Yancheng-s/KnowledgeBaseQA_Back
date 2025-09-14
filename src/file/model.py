from datetime import datetime

from flask import request, jsonify
from database.database import db
from src.pojo.model_pojo import ModelPojo

def model(app):
    @app.route('/addModel', methods=['POST'])
    def create_model():
        try:
            data = request.get_json()

            if not data or 'model_name' not in data or 'model_key' not in data:
                return jsonify({'error': 'model_name 和 model_key 是必填字段'}), 400

            new_model = ModelPojo(
                model_name=data['model_name'],
                model_presentation=data.get('model_presentation'),
                model_key=data['model_key'],
                model_date=datetime.now()
            )

            db.session.add(new_model)
            db.session.commit()

            return jsonify({
                'message': '模型创建成功',
                'id': new_model.id,
                'model_name': new_model.model_name,
                'model_presentation': new_model.model_presentation,
                'model_key': new_model.model_key,
                'model_date': new_model.model_date.strftime('%Y-%m-%d %H:%M:%S')
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': '创建模型失败，请重试'}), 500

    @app.route('/listModels', methods=['GET'])
    def list_models():
        try:
            models = ModelPojo.query.all()

            model_list = [
                {
                    'id': model.id,
                    'model_name': model.model_name,
                    'model_presentation': model.model_presentation,
                    'model_key': model.model_key,
                    'model_date': model.model_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                for model in models
            ]

            return jsonify({
                'success': True,
                'data': model_list,
                'count': len(model_list)
            }), 200

        except Exception as e:
            return jsonify({'error': '查询模型列表失败，请重试'}), 500

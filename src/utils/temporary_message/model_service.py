# src/utils/model_service.py
from src.pojo.model_pojo import ModelPojo

class ModelService:
    @staticmethod
    def get_model_info(llm_api):
        try:
            model_name = llm_api
            model = ModelPojo.query.filter_by(model_name=model_name).first()

            if not model:
                return {"error": f"未找到模型: {model_name}"}, None

            return model_name, model.model_key

        except Exception as e:
            return {"error": f"查询模型信息时发生错误: {str(e)}"}, None

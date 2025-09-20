# test_internet_search.py
import logging
from src.utils.temporary_message.tool_functions import ToolFunctions

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_internet_search():
    try:
        query = "还有几天到国庆节"
        result = ToolFunctions.internet_search(query)
        print(result)

        if result["success"]:
            print("搜索成功！结果如下：")
            print(result["content"])
        else:
            print(f"搜索失败！错误信息：{result['error']}")

    except Exception as e:
        print(f"测试过程中发生异常：{str(e)}")


if __name__ == "__main__":
    test_internet_search()


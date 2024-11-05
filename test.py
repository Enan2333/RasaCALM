import requests
import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCheckService(Action):
    def name(self) -> Text:
        return "action_check_service"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # 用户输入的服务内容
        user_service = tracker.get_slot("serviceConcat")

        # 服务列表的API URL和请求参数
        service_url = "http://39.106.249.1:8080/v1/health/screen/mtw/voice/getServices"
        params = {
            "deviceCode": "MBH1C88AD8B51EDD"
        }

        try:
            # 发送GET请求获取服务列表
            response = requests.get(service_url, params=params)
            response.raise_for_status()  # 检查请求是否成功

            # 打印 API 响应的原始内容
            print(f"API响应内容: {response.text}")

            # 尝试解析 API 响应为 JSON 格式
            services_data = response.json()  # 假设返回的数据是JSON格式
            print(f"解析后的服务列表: {services_data}")

            # 匹配用户输入的服务
            matching_service = None
            for service in services_data:
                # 修改为匹配 serviceConcat 或 serviceName 字段
                if service.get("serviceConcat") and user_service in service["serviceConcat"]:
                    matching_service = service["serviceName"]
                    break

            if matching_service:
                # 如果服务匹配成功，发送匹配成功消息
                dispatcher.utter_message(text=f"您选择的服务 '{matching_service}' 已匹配成功。")
                return [SlotSet("service_available", True)]
            else:
                dispatcher.utter_message(text="抱歉，您选择的服务暂时无法提供。")
                return [SlotSet("service_available", False)]

        except requests.exceptions.RequestException as e:
            # 处理请求错误
            dispatcher.utter_message(text=f"无法获取服务列表，请稍后重试。错误信息：{e}")
            return [SlotSet("service_available", False)]

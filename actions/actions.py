import requests
import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet




import datetime
import re, os
from loguru import logger
import requests
import json
from rapidfuzz import fuzz
from cachier import cachier
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

@cachier(stale_after=datetime.timedelta(days=1))
def get_all_services(device_code):
    url = f"http://39.106.249.1:8080/v1/health/screen/mtw/voice/getServices?deviceCode={device_code}"
    payload = {}
    headers = {}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()

        json_data = response.json()
        data = json_data['data']
        service_name = [item['serviceName'] for item in data]
        return data, service_name
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
    except ValueError:
        print("无法解析响应为JSON格式")

    return {}, []

def match_service(device_code, entity_name):
    data, service_name = get_all_services(device_code)
    thresh_hold = 50
    max_index = -1
    max_score = -1
    for i, name in enumerate(service_name):
        if name == entity_name:
            return data[i]
        else:
            score = fuzz.ratio(entity_name, name)
            logger.info(f"{name} and {entity_name} score: {score}")
            if score > max_score and score > thresh_hold:
                max_score = score
                max_index = i
    if max_index >= 0:
        return data[max_index]
    else:
        return {}
    
#获取服务类型largeTypeName所使用的函数
@cachier(stale_after=datetime.timedelta(days=1))
def getlargeTypeName(device_code):
    url = f"http://39.106.249.1:8080/v1/health/screen/mtw/voice/getServices?deviceCode={device_code}"
    payload = {}
    headers = {}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()

        json_data = response.json()
        data = json_data['data']
        largeTypeName = [item['largeTypeName'] for item in data]
        return data, largeTypeName
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
    except ValueError:
        print("无法解析响应为JSON格式")

    return {}, []

def match_largeTypeName(device_code, entity_name):
    data, largeTypeNames = getlargeTypeName(device_code)
    thresh_hold = 70
    max_index = -1
    max_score = -1

    for i, name in enumerate(largeTypeNames):
        score = fuzz.ratio(entity_name, name)
        logger.info(f"{name} and {entity_name} score: {score}")
        if score > max_score and score > thresh_hold:
            max_score = score
            max_index = i

    if max_index >= 0:
        return largeTypeNames[max_index]  # 返回匹配的服务类型名称
    else:
        return None  # 没有匹配项返回 None


#下单使用的函数
def place_order(device_code, entity_name, service_number):
    service_dict = match_service(device_code, entity_name)
    logger.info(f"matched service: {service_dict}")
    if service_dict == {}:
        return {"code": 1, "msg": "Failed", "data": "未找到匹配的服务"}
    
    contentId = service_dict['contentId']
    serviceName = service_dict['serviceName']
    services = [{"contentName": serviceName, "number": "1", "contentId": contentId}]

    url = "http://39.106.249.1:8080/v1/health/screen/mtw/voice/addServiceOrder"
    payload = {
        "deviceCode": device_code,
        "services": json.dumps(services),
    }
    headers = {}

    try:
        logger.info(f"下单输入数据: {payload}")
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()

        json_data = response.json()
        logger.info(f"下单响应数据: {json_data}")
        return json_data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
    except ValueError:
        print("无法解析响应为JSON格式")
    else:
        return {"code": 1, "msg": "Failed", "data": "语音接口调用失败"}

class ActionCheckService(Action):
    def name(self) -> Text:
        return "action_check_service"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_service = tracker.get_slot("contentName")
        service_number = str(tracker.get_slot("number"))
        device_code = "MBH1C88AD8B51EDD"

        if not user_service or not service_number:
            dispatcher.utter_message(text="您没有提供完整的服务信息或数量，请重试。")
            return [SlotSet("service_available", False)]

        order_result = place_order(device_code, user_service, service_number)

        if order_result.get("code") == 0:
            dispatcher.utter_message(text=f"下单成功：{order_result.get('data')}")
            return [SlotSet("service_available", True)]
        else:
            dispatcher.utter_message(text=f"下单失败：{order_result.get('data')}")
            return [SlotSet("service_available", False)]


class ActionCheckLargeTypeName(Action):
    def name(self) -> Text:
        return "action_check_largeTypeName"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        user_large_type_name = tracker.get_slot("largeTypeName")
        device_code = "MBH1C88AD8B51EDD"

        if not user_large_type_name:
            dispatcher.utter_message(text="您没有提供服务类型，请重试。")
            return [SlotSet("large_type_available", False)]

        # 尝试匹配用户输入的服务类型
        matched_large_type_name = match_largeTypeName(device_code, user_large_type_name)

        if matched_large_type_name:
            dispatcher.utter_message(text="请告诉我您需要的服务名称和数量。")
            return [SlotSet("large_type_available", True)]
        else:
            dispatcher.utter_message(text="您需要的服务类型不存在，请提供正确的类型。")
            return [SlotSet("large_type_available", False)]



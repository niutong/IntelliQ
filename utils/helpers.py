# encoding=utf-8
import glob
import json
import re
import requests
import config


def filename_to_classname(filename):
    """
    Convert a snake_case filename to a CamelCase class name.

    Args:
    filename (str): The filename in snake_case, without the .py extension.

    Returns:
    str: The converted CamelCase class name.
    """
    parts = filename.split('_')
    class_name = ''.join(part.capitalize() for part in parts)
    return class_name


def load_scene_templates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_all_scene_configs():
    # 用于存储所有场景配置的字典
    all_scene_configs = {}

    # 搜索目录下的所有json文件
    for file_path in glob.glob("../scene_config/conf/xiaorui_tasks.json", recursive=True):
        current_config = load_scene_templates(file_path)

        for key, value in current_config.items():
            # 只有当键不存在时，才添加到all_scene_configs中
            if key not in all_scene_configs:
                all_scene_configs[key] = value

    return all_scene_configs


def send_message(message, user_input):
    """
    请求LLM
    """
    print('--------------------------------------------------------------------')
    if config.DEBUG:
        print('prompt输入:', message)
    elif user_input:
        print('用户输入:', user_input)
    print('----------------------------------')
    full_url = "";
    headers = {
    }
    payload = json.dumps({
        # "maxNewTokens": 1024,
        "messages": [
            {
                "content": message,
                "role": "user"
            }
        ],
        "sendFinishFlag": True,
        "sensitive": "",
        "theme": ""
    })
    response = requests.post(full_url, headers=headers, data=payload)
    try:
        answer = response.json()["data"]
        print("message:", answer)
        return answer
    except Exception as e:
        print(response.text)
        print("paas接口调用异常")


def is_slot_fully_filled(json_data):
    """
    检查槽位是否完整填充
    """
    # 遍历JSON数据中的每个元素
    for item in json_data:
        # 检查value字段是否为空字符串
        if json_data[item] == '':
            return False  # 如果发现空字符串，返回False
    return True  # 如果所有value字段都非空，返回True


def get_raw_slot(parameters):
    # 创建新的JSON对象
    output_data = []
    for item in parameters:
        new_item = {"name": item["name"], "desc": item["desc"], "must_required": item["must_required"], "values_list": item["values_list"]}
        output_data.append(new_item)
    return output_data

def get_slot_info(parameters):
    # 创建新的JSON对象
    index = 1
    slot_info_str = ""
    for item in parameters:
        if len(item["values_list"]) > 0:
            slot_info_str += str(index) + ". " + item["desc"] + ", 从以下选项中选择：" + ", ".join(item["values_list"]) + "\n"
        else:
            slot_info_str += str(index) + ". " + item["desc"] + "\n"
        index += 1
    return slot_info_str

def get_slot_template(parameters):
    # 创建新的JSON对象
    output_data = {}
    slot_dict = {}
    for item in parameters:
        slot_dict[item["desc"]] = ""
    output_data["result"] = slot_dict
    return output_data

def get_dynamic_example(scene_config):
    # 创建新的JSON对象
    if 'expert_examples' in scene_config:
        return scene_config['expert_examples']
    else:
        return '答：{"name":"xx","value":"xx"}'


def get_slot_update_json(slot):
    # 创建新的JSON对象
    output_data = []
    for item in slot:
        new_item = {"name": item["name"], "desc": item["desc"], "value": ""}
        output_data.append(new_item)
    return output_data


def get_slot_query_user_json(slot):
    # 创建新的JSON对象
    output_data = []
    for item in slot:
        if not item["value"]:
            new_item = {"name": item["name"], "desc": item["desc"], "value":  item["value"]}
            output_data.append(new_item)
    return output_data


def update_slot(json_data, dict_target):
    """
    更新槽位slot参数
    """
    # 遍历JSON数据中的每个元素
    for item in json_data:
        # 检查value字段是否为空字符串
        if item['value'] != '':
            for target in dict_target:
                if target['name'] == item['name']:
                    target['value'] = item.get('value')
                    break


def format_name_value_for_logging(json_data):
    """
    抽取参数名称和value值
    """
    log_strings = []
    for item in json_data:
        name = item.get('name', 'Unknown name')  # 获取name，如果不存在则使用'Unknown name'
        value = item.get('value', 'N/A')  # 获取value，如果不存在则使用'N/A'
        log_string = f"name: {name}, Value: {value}"
        log_strings.append(log_string)
    return '\n'.join(log_strings)


def extract_json_from_string(input_string):
    """
    JSON抽取函数
    返回包含JSON对象的列表
    """
    try:
        # 正则表达式假设JSON对象由花括号括起来
        matches = re.findall(r'\{.*?\}', input_string, re.DOTALL)

        # 验证找到的每个匹配项是否为有效的JSON
        valid_jsons = []
        for match in matches:
            try:
                json_obj = json.loads(match)
                valid_jsons.append(json_obj)
            except json.JSONDecodeError:
                try:
                    valid_jsons.append(fix_json(match))
                except json.JSONDecodeError:
                    continue  # 如果不是有效的JSON，跳过该匹配项
                continue  # 如果不是有效的JSON，跳过该匹配项

        return valid_jsons
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

def extract_talk(input_str):
    pattern = re.compile(r'{[\s\S]*}')
    matches = pattern.findall(input_str)
    return matches[0]

def fix_json(bad_json):
    # 首先，用双引号替换掉所有的单引号
    fixed_json = bad_json.replace("'", '"')
    try:
        # 然后尝试解析
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        # 如果解析失败，打印错误信息，但不会崩溃
        print("给定的字符串不是有效的 JSON 格式。")


# encoding=utf-8
import logging
import json
from scene_config import scene_prompts
from scene_processor.scene_processor import SceneProcessor
from utils.helpers import get_raw_slot, update_slot, format_name_value_for_logging, is_slot_fully_filled, send_message, \
    extract_json_from_string, get_dynamic_example, get_slot_info, get_slot_template, extract_talk
from utils.prompt_utils import get_slot_update_message, get_slot_query_user_message


class CommonProcessor():
    def __init__(self, current_purpose, scene_config):
        self.slot_list = scene_config["slot_list"]
        self.current_purpose = current_purpose
        self.scene_config = scene_config
        self.scene_name = scene_config["task_name"]
        self.slot_template = get_slot_template(self.slot_list)
        self.slot_info = get_slot_info(self.slot_list)
        self.slot_dynamic_example = get_dynamic_example(scene_config)
        self.extract_slot = {}
        # self.scene_prompts = scene_config["expert_prompt"]
        self.expert_prompts = scene_config["expert_prompt"]

    def process(self, dialog_current_dict, slot_asked_intent, user_input):
        # 处理用户输入，更新槽位，检查完整性，以及与用户交互
        # 先检查本次用户输入是否有信息补充，保存补充后的结果   编写程序进行字符串value值diff对比，判断是否有更新

        message = get_slot_update_message(self.scene_name, self.slot_info, self.slot_template, user_input)  # 优化封装一下 .format  入参只要填input
        new_info_json_raw = send_message(message, user_input)
        slots_dict_str = extract_talk(new_info_json_raw).replace("\\", "").replace("\n", "")
        print("过程五：填充任务槽位信息")
        print("执行结果：当前任务槽位抽取结果：", slots_dict_str)
        slots_dict = json.loads(slots_dict_str)
        self.extract_slot = slots_dict["result"]
        logging.debug('slot extract: %s', self.extract_slot)

        current_query_type = dialog_current_dict["if_slot"]
        user_slots = dialog_current_dict["user_slots"]

        # 当前为用户槽位表单返回query，直接抽取槽位内容拼接专家prompt
        if self.current_purpose in slot_asked_intent and current_query_type == 1:
            logging.debug(f'%s ------ 槽位已被用户补充，详细参数如下: %s', self.scene_name, user_slots)
            return self.respond_with_sloted_data(user_slots, user_input)

        # 判断参数是否已经全部补全
        if is_slot_fully_filled(self.extract_slot):
            logging.debug(f'%s ------ 槽位已完整，详细参数如下: %s', self.scene_name, self.extract_slot)
            return self.respond_with_sloted_data(self.extract_slot, user_input)
        else:
            logging.debug(f'%s ------ 槽位需要用户填充，详细参数如下: %s', self.scene_name, self.extract_slot)
            return self.ask_user_for_missing_data()

    def respond_with_sloted_data(self, user_slots, user_input):
        concat_user_input = (f"\n用户要求如下:%s, 用户当前请求详情:%s", user_slots, user_input)
        service_result = {}
        service_result["hit_intent"] = 1
        service_result["intent_id"] = self.current_purpose
        service_result["need_slots"] = 0
        service_result["expert_prompt"] = self.expert_prompts + concat_user_input
        logging.debug(f'service_result: %s', service_result)
        return service_result

    def ask_user_for_missing_data(self):
        service_result = {}
        service_result["hit_intent"] = 1
        service_result["intent_id"] = self.current_purpose
        service_result["need_slots"] = 1
        slots_dict = {}
        for item in self.slot_list:
            slot_name = item["desc"]
            values_list = item["values_list"]
            must_required = item["must_required"]
            customize = item["customize"]

            slot_detail = {}
            if len(values_list) > 0:
                if customize == 0:
                    slot_detail["slot_type"] = 0
                else:
                    slot_detail["slot_type"] = 2
            else:
                slot_detail["slot_type"] = 1
            slot_detail["must_need"] = must_required

            if slot_name in self.extract_slot and self.extract_slot[slot_name] != "":
                slot_detail["result"] = self.extract_slot[slot_name]
            else:
                slot_detail["result"] = ""

            slot_detail["options"] = values_list
            slots_dict[slot_name] = slot_detail

        service_result["slots_dict"] = slots_dict
        logging.debug(f'service_result: %s', service_result)
        return service_result

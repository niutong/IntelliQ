# encoding=utf-8
import logging

from config import RELATED_INTENT_THRESHOLD
from scene_processor.impl.common_processor import CommonProcessor
from utils.data_format_utils import extract_continuous_digits, extract_float
from utils.helpers import send_message
from utils.app_init import before_init
from utils.helpers import load_all_scene_configs

class ChatbotModel:
    def __init__(self, scene_templates: dict):
        self.scene_templates: dict = scene_templates
        self.current_purpose: str = ''
        self.processors = {}
        logging.info(f'scene_templates: %s', self.scene_templates)

    @staticmethod
    def load_scene_processor(self, scene_name, scene_config):
        try:
            return CommonProcessor(scene_name, scene_config)
        except (ImportError, AttributeError, KeyError):
            raise ImportError(f"未找到场景处理器 scene_config: {scene_config}")

    def get_processor_for_scene(self, scene_name):
        if scene_name in self.processors:
            return self.processors[scene_name]

        scene_config = self.scene_templates.get(scene_name)
        if not scene_config:
            raise ValueError(f"未找到名为{scene_name}的场景配置")

        processor_class = self.load_scene_processor(self, scene_name, scene_config)
        self.processors[scene_name] = processor_class
        logging.info(f'find task %s, %s', scene_name, scene_config)
        return self.processors[scene_name]

    def intent_recognize(self, user_input):
        # 根据场景模板生成选项
        self.current_purpose = ""
        purpose_options = {}
        purpose_description = {}
        index = 1
        for template_key, template_info in self.scene_templates.items():
            purpose_options[str(index)] = template_key
            purpose_description[str(index)] = template_info["task_name"] + ":" + template_info["task_desc"]
            index += 1
        options_prompt = "\n".join([f"{key}. {value} - 请回复{key}" for key, value in purpose_description.items()])
        options_prompt += "\n0. 其他场景 - 请回复0"

        # 发送选项给用户
        user_choice = send_message(f"有下面多种场景，需要你根据用户的连续对话输入中，判断当前用户意图属于以下哪个场景，只答选项\n{options_prompt}\n用户输入如下：\n{user_input}\n请回复序号：", user_input)
        logging.info(f'purpose_options: %s', purpose_options)
        logging.info(f'user_choice: %s', user_choice)

        user_choices = extract_continuous_digits(user_choice)
        logging.info(f'extract user_choice: %s', user_choices)
        # 根据用户选择获取对应场景
        if user_choices and user_choices[0] != '0':
            self.current_purpose = purpose_options[user_choices[0]]

        if self.current_purpose:
            print(f"用户选择了场景：{self.scene_templates[self.current_purpose]['task_name']}")
            # 这里可以继续处理其他逻辑
        else:
            # 用户输入的选项无效的情况，可以进行相应的处理
            print("无效的选项，请重新选择")

    def check_completed_intent(self, dialog_history_list):

        completed_intent = []
        slot_asked_intent = []
        for dialog_dict in dialog_history_list:
            if "hit_intent" not in dialog_dict:
                continue

            if dialog_dict["hit_intent"] == 1 and dialog_dict["need_slots"] == 0:
                completed_intent.append(dialog_dict["intent_id"])

            if dialog_dict["hit_intent"] == 1 and dialog_dict["need_slots"] == 1:
                slot_asked_intent.append(dialog_dict["intent_id"])

        return slot_asked_intent, completed_intent

    def process_dialogue(self):

        # 返回用户近10轮历史对话
        dialog_history_list = []
        # 1. 每轮历史对话包含： 用户输入input, 当前是否是表单回传if_slot 0/1，用户填充后的表单user_slots(没有默认空dict)，ai输出output
        dialog_dict = {}
        dialog_dict["input"] = ""
        dialog_dict["if_slot"] = 0
        dialog_dict["user_slots"] = {}
        dialog_dict["output"] = ""

        # 每轮历史对话回传：该轮历史请求，意图识别返回的结果：
        dialog_dict["hit_intent"] = 0
        dialog_dict["intent_id"] = ""
        dialog_dict["need_slots"] = 0
        dialog_dict["slots_dict"] = {}

        dialog_history_list.append(dialog_dict)

        # 2. 用户新请求参数，只包含如下字段
        dialog_current_dict = {}
        # dialog_current_dict["input"] = "我想写个以热爱劳动为主题的班会活动计划"
        dialog_current_dict["input"] = "帮我策划一次小学低年级的以爱国主义教育为主题的校园活动"
        dialog_current_dict["if_slot"] = 0
        dialog_current_dict["user_slots"] = {}
        dialog_history_list.append(dialog_current_dict)

        user_history_query = ["你好助理", "帮我策划一次小学低年级的以爱国主义教育为主题的校园活动"]
        extended_result = {}

        user_input = "\n".join([f"{index}. {input}" for index, input in enumerate(user_history_query)])

        slot_asked_intent, completed_intent = self.check_completed_intent(dialog_history_list)
        self.intent_recognize(user_input)
        print("current_purpose", self.current_purpose)
        # 当前意图已经扩写过prompt，不需要再扩写
        if self.current_purpose == -1 or self.current_purpose in completed_intent:
            extended_result["hit_intent"] = 0
            logging.info(f'当前意图已经扩写过prompt，不需要再扩写')
            return extended_result

        if self.current_purpose in self.scene_templates:
            # 根据场景模板调用相应场景的处理逻辑
            self.get_processor_for_scene(self.current_purpose)
            # 调用抽象类process方法
            return self.processors[self.current_purpose].process(dialog_current_dict, slot_asked_intent, user_input)
        return '未命中场景'


if __name__ == '__main__':
    before_init()
    chatbot_model = ChatbotModel(load_all_scene_configs())
    chatbot_model.process_dialogue()
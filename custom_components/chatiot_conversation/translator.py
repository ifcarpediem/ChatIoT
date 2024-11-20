# single Translator - hass init
# 1. translate the command to entity
# 2. translate the tap to automation yaml
from utils.singleton import Singleton
from utils.logs import _logger
from utils.utils import append_file
import time
from configs import CONFIG
from context_assistant import find_entity_by_field_mac
import os
import requests

class Translator(metaclass=Singleton):
    def __init__(self, hass):
        self.hass = hass
    
    async def run_single_command(self, command_str: str):
        service_str = command_str.split("=")[0].strip()
        value_str = command_str.split("=")[1].strip()
        id_str, field_str= service_str.split(".", 1)
        service_name, property_name = field_str.split(".")
        id = int(id_str)

        miot_devices = CONFIG.hass_data["miot_devices"]

        mac_address = ""
        for device in miot_devices:
            if device.get("id", -1) == id:
                mac_address = device.get("mac_address", "")
                break
        
        state = find_entity_by_field_mac(field_str, mac_address)
        entity_id = state["entity_id"]

        for device in CONFIG.hass_data["all_context"]:
            if device.get("id", -1) == id:
                services = device.get("services", {})
                service = services[service_name]
                property = service[property_name]
                p_format = property["format"]
                
                if p_format == "bool":
                    value = (value_str.lower() == "true")
                elif "int" in p_format:
                    value = int(value_str)
                elif "float" in p_format:
                    value = float(value_str)
                else:
                    value = value_str
                break
        
        _logger.debug("miot_set_property entity_id: {}". format(entity_id))
        _logger.debug("miot_set_property field_str: {}". format(field_str))
        _logger.debug("miot_set_property value: {}". format(value))

        service_data = {
            "entity_id": entity_id,
            "field": field_str,
            "value": value
        }

        await self.hass.services.async_call("xiaomi_miot", "set_property", service_data)

    async def _check_config(self):
        # import time, asyncio
        # log_file_path = "/config/home-assistant.log"
        # error_tag = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        # await self.hass.services.async_call("homeassistant", "check_config")
        # await asyncio.sleep(1)
        # _logger.debug(f"error_tag: {error_tag}")
        # with open(log_file_path, 'r') as f:
        #     lines = f.readlines()
        #     for line in lines[-20:]:
        #         _logger.debug(f"line: {line}")
        #         if error_tag in line and "ERROR" in line:
        #             return False
        # return True
        access_token = CONFIG.hass_data["access_token"]
        url = f"http://127.0.0.1:8123/api/config/core/check_config"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            def test():
                nonlocal url, headers
                response = requests.post(url=url, headers=headers)
                _logger.debug(f"response: {response}")
                if response.status_code == 200:
                    return response.json()["result"]
                else:
                    return f"failed_to_connect: {response.status_code}"
            response = await self.hass.async_add_executor_job(test)
            _logger.debug(f"response: {response}")
            return response
        except Exception as ex:
            _logger.error(f"Connection error was: {repr(ex)}")
            return "failed_to_connect"

    async def add_automation(self, new_automation: str):
        _logger.debug("add_automation")
        config_path = "/config"
        automation_file = os.path.join(config_path, "automations.yaml")
        # if there is only "[]" in automations.yaml, remove it first
        with open(automation_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) == 1 and lines[0] == "[]\n":
            with open(automation_file, "w", encoding="utf-8") as f:
                f.write("")
        # copy the automations.yaml for bak
        bak_file = os.path.join(config_path, "automations.yaml.bak")
        with open(automation_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(bak_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        append_file(automation_file, new_automation)
        res_check = await self._check_config()
        if res_check == "valid":
            await self.hass.services.async_call("homeassistant", "reload_all")
        else:
            # replace the automations.yaml with the bak file
            _logger.error("invalid configuration, restore automations.yaml")
            with open(bak_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(automation_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
    
    async def deploy_tap(self, user_input, TAP_json):
        _logger.debug("deploy_tap")
        miot_devices = CONFIG.hass_data["miot_devices"]
        # triggers = TAP_json.get("trigger", [])
        # actions = TAP_json.get("action", [])
        triggers = TAP_json.get("trigger", "")
        actions = TAP_json.get("action", "")

        #TODO
        trigger_str = triggers
        action_str = actions
        _logger.info("trigger_str: {}". format(trigger_str))
        _logger.info("action_str: {}". format(action_str))

        action_service_str = action_str.split("=")[0].strip()
        action_value_str = action_str.split("=")[1].strip()
        action_id_str, action_field_str= action_service_str.split(".", 1)
        action_service_name, action_property_name = action_field_str.split(".")
        action_id = int(action_id_str)

        action_mac_address = ""
        for device in miot_devices:
            if device.get("id", -1) == action_id:
                action_mac_address = device.get("mac_address", "")
                break
        
        action_entity = find_entity_by_field_mac(action_field_str, action_mac_address)
        _logger.info("action_entity: {}". format(action_entity))

        action_entity_id = action_entity["entity_id"]

        for device in CONFIG.hass_data["all_context"]:
            if device.get("id", -1) == action_id:
                services = device.get("services", {})
                service = services[action_service_name]
                property = service[action_property_name]
                p_format = property["format"]
                
                if p_format == "bool":
                    action_value = (action_value_str.lower() == "true")
                elif "int" in p_format:
                    action_value = int(action_value_str)
                elif "float" in p_format:
                    action_value = float(action_value_str)
                else:
                    action_value = action_value_str
                break
        
        #TODO
        ops = ["==", ">", "<"]
        for op in ops:
            if op in trigger_str:
                break
        
        trigger_service_str = trigger_str.split(op)[0].strip()
        trigger_value_str = trigger_str.split(op)[1].strip()
        trigger_id_str, trigger_field_str= trigger_service_str.split(".", 1)
        trigger_service_name, trigger_property_name = trigger_field_str.split(".")
        trigger_id = int(trigger_id_str)

        if trigger_id == -1:
            pass
        else:
            trigger_mac_address = ""
            for device in miot_devices:
                if device.get("id", -1) == trigger_id:
                    trigger_mac_address = device.get("mac_address", "")
                    break
            if trigger_field_str == "illumination_sensor.illumination":
                trigger_field_str = "illumination-2-1"
            trigger_entity = find_entity_by_field_mac(trigger_field_str, trigger_mac_address)
            _logger.info("trigger_entity: {}". format(trigger_entity))
            trigger_entity_id = trigger_entity["entity_id"]
            for device in CONFIG.hass_data["all_context"]:
                if device.get("id", -1) == trigger_id:
                    services = device.get("services", {})
                    service = services[trigger_service_name]
                    property = service[trigger_property_name]
                    p_format = property["format"]
                    
                    if p_format == "bool":
                        bool_value = (trigger_value_str.lower() == "true")
                        if bool_value: trigger_value = 1 
                        else: trigger_value = 0
                    elif "int" in p_format:
                        trigger_value = int(trigger_value_str)
                    elif "float" in p_format:
                        trigger_value = int(trigger_value_str)
                    else:
                        trigger_value = trigger_value_str
                    break
            if op == "==":
                trigger_yaml = f'''trigger: numeric_state
      entity_id: {trigger_entity_id}
      attribute: {trigger_field_str}
      above: {trigger_value-1}
      below: {trigger_value+1}'''
            elif op == ">":
                trigger_yaml = f'''platform: numeric_state
      entity_id: {trigger_entity_id}
      attribute: {trigger_field_str}
      above: {trigger_value}'''
            elif op == "<":
                trigger_yaml = f'''- platform: numeric_state
      entity_id: {trigger_entity_id}
      attribute: {trigger_field_str}
      below: {trigger_value}'''   

        timestamp = int(time.time() * 1000)
        new_automation = f'''
- id: '{timestamp}'
  alias: {user_input}
  trigger: 
      {trigger_yaml}
  action:
      service: xiaomi_miot.set_property
      data:
        entity_id: {action_entity_id}
        field: {action_field_str}
        value: {action_value}
    '''
        _logger.info("new automation yaml: {}". format(new_automation))
        await self.add_automation(new_automation)



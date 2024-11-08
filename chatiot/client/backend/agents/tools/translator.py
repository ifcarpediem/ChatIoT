import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))
from backend.agents.tools.home_assistant import HomeAssistantApi

# from .home_assistant import HomeAssistantApi
from backend.agents.utils.utils import get_json
from backend.agents.utils.logs import logger
import time

class Translator:
    def __init__(self):
        self.homeassistant = HomeAssistantApi()

    def run_single_command(self, command_str: str):

        service_str = command_str.split("=")[0].strip()
        value_str = command_str.split("=")[1].strip()
        id_str, field_str= service_str.split(".", 1)
        service_name, property_name = field_str.split(".")
        id = int(id_str)

        miot_devices = get_json("./temp/miot/miot_devices.json")

        mac_address = ""
        for device in miot_devices:
            if device.get("id", -1) == id:
                mac_address = device.get("mac_address", "")
                break
        
        states = self.homeassistant.get_states()
        state = self.homeassistant.find_state_by_field_mac(field_str, mac_address, states)
        entity_id = state["entity_id"]
        device_context = get_json("./temp/miot/device_context.json")

        for device in device_context:
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

        logger.debug("miot_set_property entity_id: {}". format(entity_id))
        logger.debug("miot_set_property field_str: {}". format(field_str))
        logger.debug("miot_set_property value: {}". format(value))

        self.homeassistant.miot_set_property(entity_id, field_str, value)

    def deploy_tap(self, user_input, TAP_json):
        miot_devices = get_json("./temp/miot/miot_devices.json")
        states = self.homeassistant.get_states()
        content_miot_device = get_json("./temp/miot/device_context.json")
        # triggers = TAP_json.get("trigger", [])
        # actions = TAP_json.get("action", [])
        triggers = TAP_json.get("trigger", "")
        actions = TAP_json.get("action", "")

        #TODO
        trigger_str = triggers
        action_str = actions
        logger.info("trigger_str: {}". format(trigger_str))
        logger.info("action_str: {}". format(action_str))

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
        
        action_entity = self.homeassistant.find_state_by_field_mac(action_field_str, action_mac_address, states)
        logger.info("action_entity: {}". format(action_entity))

        action_entity_id = action_entity["entity_id"]

        for device in content_miot_device:
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

        if trigger_id == 21:
            trigger_entity_id = "input_boolean." + trigger_service_name
            if trigger_value_str.lower() == "true":
                trigger_value = "on"
            else:
                trigger_value = "off"
            trigger_yaml = f'''- platform: state
        entity_id: {trigger_entity_id}
        to: "{trigger_value}"'''
        
        else:
            trigger_mac_address = ""
            for device in miot_devices:
                if device.get("id", -1) == trigger_id:
                    trigger_mac_address = device.get("mac_address", "")
                    break
            if trigger_field_str == "illumination_sensor.illumination":
                trigger_field_str = "illumination-2-1"
            trigger_entity = self.homeassistant.find_state_by_field_mac(trigger_field_str, trigger_mac_address, states)
            logger.info("trigger_entity: {}". format(trigger_entity))
            trigger_entity_id = trigger_entity["entity_id"]
            for device in content_miot_device:
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
        logger.info("new automation yaml: {}". format(new_automation))
        self.homeassistant.add_automation(str(timestamp), new_automation)
        
if __name__ == "__main__":
    translator = Translator()
    # translator.run_single_command("1.light.on = false")
    TAP = {"trigger": "2.magnet_sensor.contact_state==true", "action": "1.light.on=true"}
    translator.deploy_tap("turn on the light when the door is opened", TAP)


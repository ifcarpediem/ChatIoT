import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))

import requests
import os
from backend.agents.utils.logs import logger
from backend.agents.utils.utils import get_yaml, write_yaml, get_json, write_json, append_file
from backend.agents.tools.miot_api import MiotApi
from config import CONFIG

class HomeAssistantApi:
    def __init__(self):
        self.config = CONFIG.configs["home_assistant"]
        self.miot_api = MiotApi()
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.token = self.config["token"]
        self.config_path = self.config["config_path"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def check_configuration(self):
        url = f"http://{self.host}:{self.port}/api/config/core/check_config"
        logger.debug("checking configuration...")
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            result = response.json()["result"]
            errors = response.json()["errors"]
            logger.debug(f"configuration checked:\nresult: {result}\nerrors: {errors}")
            return (result, errors)
        else:
            logger.debug(f"Fail to check configuration: {response.status_code}: {response.text}")
            return (None, None)
        
    def restart(self):
        # check configuration first
        result, errors = self.check_configuration()
        if result == "invalid":
            logger.error("invalid configuration, restart failed")
            return
        url = f"http://{self.host}:{self.port}/api/services/homeassistant/restart"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            logger.info("home assistant is restarting...")
        else:
            logger.error(f"Fail to restart home assistant: {response.status_code}: {response.text}")

    def reload_all(self):
        # check configuration first
        result, errors = self.check_configuration()
        if result == "invalid":
            logger.error("invalid configuration, reload failed")
            return
        url = f"http://{self.host}:{self.port}/api/services/homeassistant/reload_all"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            logger.debug("home assistant is reloading...")
        else:
            logger.error(f"Fail to reload home assistant: {response.status_code}: {response.text}")

    def miot_set_property(self, entity_id: str, field: str, value: bool):
        url = f"http://{self.host}:{self.port}/api/services/xiaomi_miot/set_property"
        data = {
            "entity_id": entity_id,
            "field": field,
            "value": value
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            logger.debug(f"{field} in {entity_id} is changed to {value} successfully.")
        else:
            logger.error(f"Fail to change {field} in {entity_id} to {value}: {response.status_code}: {response.text}")
    
    def get_states(self) -> dict:
        url = f"http://{self.host}:{self.port}/api/states"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            states = response.json()
            logger.debug(f"states: \n{states}")
            write_json("temp/states.json", states)
            return states
        else:
            logger.error(f"Fail to get states: {response.status_code}: {response.text}")
            return None
        
    def find_state_by_entity_id(self, entity_id: str, states: dict=None) -> dict:
        if states is None:
            states = self.get_states()
        for state in states:
            if state["entity_id"] == entity_id:
                return state
        return None
    
    def find_state_by_field_mac(self, field: str, mac_address: str, states: dict=None) -> dict:
        additional_fields_original = ["illumination_sensor.illumination", "temperature_humidity_sensor.temperature", "temperature_humidity_sensor.relative_humidity"]
        additional_fields_new = ["illumination-2-1", "temperature-2-1", "relative_humidity-2-2"]
        for i, additional_field in enumerate(additional_fields_original):
            if field == additional_field:
                field = additional_fields_new[i]
                break
        if states is None:
            states = self.get_states()
        for state in states:
            attributes = state.get("attributes", {})
            if field in attributes:
                if "mac_address" in attributes:
                    if attributes.get("mac_address", "").lower() == mac_address.lower():
                        return state
                elif "parent_entity_id" in attributes:
                    parent_entity_state = self.find_state_by_entity_id(attributes["parent_entity_id"], states)
                    parent_attributes = parent_entity_state.get("attributes", {})
                    if "mac_address" in parent_attributes:
                        if attributes.get("mac_address", "").lower() == mac_address.lower():
                            return state
        return None
    
    def update_input_boolean(self, entity_id: str, new_state: bool):
        url = f"http://{self.host}:{self.port}/api/states/{entity_id}"
        data = {
            "state": new_state
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            logger.debug(f"{entity_id} is updated to {new_state} successfully.")
        else:
            logger.error(f"Fail to update {entity_id} to {new_state}: {response.status_code}: {response.text}")

    def add_input_boolean(self, name: str, default: bool=False):
        configuration_file = os.path.join(self.config_path, "configuration.yaml")
        input_boolean_file = os.path.join(self.config_path, "input_boolean.yaml")
        
        if not os.path.exists(input_boolean_file):
            append_file(input_boolean_file, "")
        
        with open(configuration_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        include_line = "input_boolean: !include input_boolean.yaml"
        if include_line not in lines:
            append_file(configuration_file, include_line)
        
        input_booleans = get_yaml(input_boolean_file)
        if input_booleans is None:
            input_booleans = {}
            input_booleans[name] = {"name": name, "initial": False}
        elif name in input_booleans:
            logger.error(f"{name} already exists in input_boolean.yaml")
            return
        else:
            input_booleans[name] = {"name": name, "initial": default}
        write_yaml(input_boolean_file, input_booleans)
        self.reload_all()

    def remove_input_boolean(self, name: str):
        input_boolean_file = os.path.join(self.config_path, "input_boolean.yaml")
        input_booleans = get_yaml(input_boolean_file)
        if input_booleans is None:
            logger.error("input_boolean.yaml is empty")
            return
        if name not in input_booleans:
            logger.error(f"{name} not found in input_boolean.yaml")
            return
        del input_booleans[name]
        write_yaml(input_boolean_file, input_booleans)
        self.reload_all()

    def add_automation(self, new_id: str, new_automation: str):
        automation_file = os.path.join(self.config_path, "automations.yaml")
        # if there is only "[]" in automations.yaml, remove it first
        with open(automation_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) == 1 and lines[0] == "[]\n":
            with open(automation_file, "w", encoding="utf-8") as f:
                f.write("")
        # copy the automations.yaml for bak
        bak_file = os.path.join(self.config_path, "automations.yaml.bak")
        if not os.path.exists(bak_file):
            with open(automation_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(bak_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        with open(automation_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            if new_id in line:
                logger.error(f"id {new_id} already exists in automations.yaml")
                return
        append_file(automation_file, new_automation)
        if self.check_configuration()[0] == "valid":
            self.reload_all()
        else:
            # replace the automations.yaml with the bak file
            logger.error("invalid configuration, restore automations.yaml")
            with open(bak_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(automation_file, "w", encoding="utf-8") as f:
                f.writelines(lines)


    def remove_automation(self, id_to_remove: int):
        automation_file = os.path.join(self.config_path, "automations.yaml")
        with open(automation_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        del_tag = False
        remove_list = []
        for i, line in enumerate(lines):
            if line.startswith("- id: "):
                if id_to_remove in line:
                    del_tag = True
                    remove_list.append(i)
                    continue
                else:
                    if del_tag:
                        break
            else:
                if del_tag:
                    remove_list.append(i)
        if len(remove_list) == 0:
            logger.error(f"id {id_to_remove} not found in automations.yaml")
            return
        new_lines = []
        for i in range(len(lines)):
            if i not in remove_list:
                new_lines.append(lines[i])
        with open(automation_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        self.reload_all()

    def get_miot_devices(self) -> list[dict]:
        device_file_path = os.path.join(self.config_path, ".storage", "core.device_registry")
        miot_devices = []
        device_json = get_json(device_file_path)
        device_id_counter = 1

        for device in device_json["data"]["devices"]:
            identifiers = device.get('identifiers', [])
            for identifier in identifiers:
                if identifier[0] == 'xiaomi_miot':
                    area_id = device['area_id']
                    model = device['model']
                    if '-' in identifier[1]:
                        mac_address = identifier[1].split('-')[0]
                    else:
                        mac_address = identifier[1]
                    miot_device_info = {
                        'id': device_id_counter,
                        'area': area_id if area_id else 'unknown',
                        'model': model if model else 'unknown',
                        'mac_address': mac_address,
                    }
                    miot_devices.append(miot_device_info)
                    device_id_counter += 1
        write_json('./temp/miot/miot_devices.json', miot_devices)
        logger.debug(f"miot_devices: {miot_devices}")
        return miot_devices

    def get_miot_info(self):
        os.makedirs("temp/miot/info", exist_ok=True)
        miot_devices = self.get_miot_devices()
        for device in miot_devices:
            model = device['model']
            if os.path.exists(f'temp/miot/info/{model}.json'):
                continue
            if not os.path.exists(f'temp/miot/spec/{model}.json'):
                spec = self.miot_api.download_spec_by_model(model)
            else:
                spec = get_json(f'temp/miot/spec/{model}.json')
            if spec:
                info = self.miot_api.convert_spec_to_info(spec)
                write_json(f'temp/miot/info/{model}.json', info)

    def find_states_by_device(self, device: dict, states: dict=None) -> dict:
        if states is None:
            states = self.get_states()
        states_by_device = []
        mac_address = device['mac_address']
        for state in states:
            attributes = state.get("attributes", {})
            if "mac_address" in attributes:
                if attributes.get("mac_address", "").lower() == mac_address.lower():
                    states_by_device.append(state)
            elif "parent_entity_id" in attributes:
                parent_entity_state = self.find_state_by_entity_id(attributes["parent_entity_id"], states)
                parent_attributes = parent_entity_state.get("attributes", {})
                if "mac_address" in parent_attributes:
                    if attributes.get("mac_address", "").lower() == mac_address.lower():
                        states_by_device.append(state)
        return states_by_device

    def get_device_context(self) -> list[dict]:
        if not os.path.exists('./temp/miot/miot_devices.json'):
            write_json('./temp/miot/miot_devices.json', self.get_miot_devices())
        miot_devices = get_json('./temp/miot/miot_devices.json')
        self.get_miot_info()
        device_context = []
        for device in miot_devices:
            single_device_context = {}
            states_by_device = self.find_states_by_device(device)
            model = device['model']
            info = get_json(f'temp/miot/info/{model}.json')
            single_device_context['id'] = device['id']
            single_device_context['area'] = device['area']
            single_device_context['type'] = info['type']
            services = info['services']
            service_to_remove = []
            for service_name, service in services.items():
                property_to_remove = []
                for property_name, _ in service.items():
                    field = f"{service_name}.{property_name}"
                    state = self.find_state_by_field_mac(field, device['mac_address'], states_by_device)
                    if state is None:
                        property_to_remove.append(property_name)
                for property_name in property_to_remove:
                    service.pop(property_name)
                if service == {}:
                    service_to_remove.append(service_name)
            for service_name in service_to_remove:
                services.pop(service_name)
            single_device_context['services'] = services
            device_context.append(single_device_context)
        # camera_list = CONFIG.configs["camera_list"]
        camera_list = None # camera will be added in the future
        if camera_list:
            for camera in camera_list:
                single_device_context = {}
                single_device_context['id'] = len(device_context) + 1
                single_device_context['area'] = camera['area']
                single_device_context['type'] = 'camera'
                single_device_context['services'] = {}
                device_context.append(single_device_context)
        write_json('./temp/miot/device_context.json', device_context)
        return device_context
             
if __name__ == '__main__':
    from config import CONFIG
    api = HomeAssistantApi()
    print(api.get_device_context())

    

import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))

import os
import requests
from backend.agents.utils.logs import logger
from backend.agents.utils.utils import write_json

class MiotApi:
    def __init__(self):
        os.makedirs("temp/miot", exist_ok=True)
        os.makedirs("temp/miot/spec", exist_ok=True)
        self.model2type = self._download_instances()

    def _download_instances(self):
        url = 'http://miot-spec.org/miot-spec-v2/instances?status=all'
        res = requests.get(url)
        instances = res.json()
        model2type = {}
        for instance in instances["instances"]:
            model = instance['model']
            if model not in model2type:
                model2type[model] = instance['type']
        write_json('temp/miot/instances.json', instances)
        write_json('temp/miot/model2type.json', model2type)
        return model2type

    def download_spec_by_model(self, model: str) -> dict:
        if model not in self.model2type:
            logger.error(f"model {model} not found")
            return
        miot_type = self.model2type[model]
        url = f'http://miot-spec.org/miot-spec-v2/instance?type={miot_type}'
        res = requests.get(url)
        spec = res.json()
        write_json(f'temp/miot/spec/{model}.json', spec)
        return spec

    def download_spec_by_models(self, models: list[str]):
        for model in models:
            self.download_spec_by_model(model)
    
    def convert_spec_to_info(self, spec):
        device_type = spec["type"].split(":")[3]
        device_type = device_type.replace("-", "_")
        info = {
            "type": device_type,
            "services": {}
        }
        for service in spec["services"][1:]:

            service_type = service["type"].split(":")[3]
            service_type = service_type.replace("-", "_")

            service_obj = {}

            for property in service.get("properties", []):

                property_type = property["type"].split(":")[3]
                property_type = property_type.replace("-", "_")

                property_value = {k: v for k, v in property.items() if k not in ["iid", "type"]}

                if property_value.get("access", []) != []:

                    service_obj[property_type] = property_value   

            info["services"][service_type] = service_obj
            if info["services"][service_type] == {}:
                info["services"].pop(service_type)  
        return info

if __name__ == '__main__':
    api = MiotApi()
    api.download_spec_by_models(['isa.magnet.dw2hl'])






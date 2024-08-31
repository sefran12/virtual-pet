import yaml
from pathlib import Path

class ResourceManager:
    def __init__(self, resource_dir='resources'):
        self.resource_dir = Path(resource_dir)
        self.resources = {}

    def load_resource(self, resource_name):
        resource_path = self.resource_dir / f"{resource_name}.yml"
        if not resource_path.exists():
            raise FileNotFoundError(f"Resource file {resource_path} not found")
        
        with open(resource_path, 'r', encoding='utf-8') as file:
            self.resources[resource_name] = yaml.safe_load(file)

    def get_prompt(self, resource_name, prompt_key, language='english'):
        if resource_name not in self.resources:
            self.load_resource(resource_name)
        
        keys = prompt_key.split('.')
        value = self.resources[resource_name]
        for key in keys:
            value = value[key]
        
        return value[language]
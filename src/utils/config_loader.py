import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


class ConfigLoader:
    _instance = None
    _configs = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config_dir = Path('config')
        
    def load(self, config_name: str, force_reload: bool = False) -> Dict[str, Any]:
        if config_name not in self._configs or force_reload:
            config_path = self.config_dir / f"{config_name}.yaml"
            
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r') as file:
                self._configs[config_name] = yaml.safe_load(file)
        
        return self._configs[config_name]
    
    def get_path(self, key: str, config_name: str = 'paths') -> str:
        config = self.load(config_name)
        keys = key.split('.')
        
        value = config
        for k in keys:
            value = value.get(k, {})
        
        return value if isinstance(value, str) else None
    
    def get_config_value(self, key: str, config_name: str = 'config', default: Any = None) -> Any:
        config = self.load(config_name)
        keys = key.split('.')
        
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value if value is not None else default


def get_config_loader() -> ConfigLoader:
    return ConfigLoader()

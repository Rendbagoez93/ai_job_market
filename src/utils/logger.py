import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional


class Logger:
    _loggers = {}
    _configured = False
    
    @classmethod
    def setup_logging(cls, config_path: str = 'config/logging.yaml'):
        if cls._configured:
            return
        
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if not cls._configured:
            cls.setup_logging()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]


def get_logger(name: str) -> logging.Logger:
    return Logger.get_logger(name)

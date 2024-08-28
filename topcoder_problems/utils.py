import os
import pickle
from typing import Callable

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class FileSystemCache:
    def __init__(self, cache_path):
        self.cache_path = cache_path
    
    def __call__(self, func: Callable, *args, **kwargs):
        if not os.path.exists(self.cache_path):
            result = func(*args, **kwargs)
            if result:
                if not os.path.exists(os.path.dirname(self.cache_path)):
                    os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                
                with open(self.cache_path, "wb") as f:
                    pickle.dump(result, f)
            
            return result
        
        else:
            if not os.path.exists(os.path.dirname(self.cache_path)):
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
            with open(self.cache_path, "rb") as f:
                return pickle.load(f)
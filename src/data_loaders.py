from abc import ABCMeta
from typing import Protocol, runtime_checkable
import pandas as pd

@runtime_checkable
class Loader(Protocol, metaclass=ABCMeta):
    def load_data(file_path: str, **kwargs) -> pd.DataFrame: ...

class CSVLoader(Loader):
    @staticmethod
    def load_data(file_path: str, **kwargs) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path, **kwargs)
            return df
        except Exception as e:
            raise ValueError(f"Ошибка загрузки CSV файла: {e}")
        
class FileLoader(Loader):
    @staticmethod
    def loader(file_type = 'csv') -> Loader:
        match file_type:
            case 'csv': return CSVLoader
            case _: raise ValueError(f'Неизвестное расширение: "{file_type}')

    @staticmethod
    def load_data(file_path: str, **kwargs) -> pd.DataFrame:
        if (dot_index := file_path.rindex('.')) < 0:
            raise ValueError("Не удалось выделить расширение файла")
        file_type = file_path[dot_index+1:]

        return FileLoader.loader(file_type).load_data(file_path, **kwargs)

    

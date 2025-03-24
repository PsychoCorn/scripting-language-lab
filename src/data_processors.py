import pandas as pd
from scipy.signal import savgol_filter

class TimeConverter:
    @staticmethod
    def convert_to_microseconds(time_series: pd.Series, *, format='mixed', errors='coerce') -> pd.Series:
        try:
            time_series = pd.to_datetime(time_series, format=format, errors=errors)
            time_series = time_series.dropna()
            return (time_series - time_series.min()).dt.total_seconds() * 1_000_000
        except Exception as e:
            raise ValueError(f"Ошибка преобразования времени: {e}")
        

class OutlierProcessor:
    @staticmethod
    def remove_outliers(data: pd.Series, method: str, sigma: float) -> pd.Series:
        """
        Удаляет выбросы из временного ряда.
        Доступные методы: 'zscore' (по Z-оценке) и 'iqr' (межквартильный размах).
        """
        if method == "zscore":
            mean, std = data.mean(), data.std()
            filtered_data = data[abs((data - mean) / std) < sigma]
        elif method == "iqr":
            q1, q3 = data.quantile(0.25), data.quantile(0.75)
            iqr = q3 - q1
            filtered_data = data[(data >= q1 - sigma * iqr) & (data <= q3 + sigma * iqr)]
        else:
            raise ValueError("Неизвестный метод обработки выбросов")
        
        return filtered_data
    

class TrendProcessor:
    @staticmethod
    def extract_trend(data: pd.Series, window: int, poly_order: int) -> pd.Series:
        """
        Извлекает линию тренда с использованием фильтра Савицкого-Голея.
        """
        data = data.fillna(data.mean())
        try:
            return savgol_filter(data, window_length=window, polyorder=poly_order, mode='nearest')
        except Exception as e:
            raise ValueError(f"Ошибка извлечения тренда: {e}")

class JumpProcessor:
    @staticmethod
    def detect_jumps(data: pd.Series, threshold: float) -> pd.Series:
        """
        Обнаруживает скачки в данных на основе стандартного отклонения.
        """
        mean, std = data.mean(), data.std()
        jumps = (abs(data - mean) > threshold * std)
        return jumps
    
class Normalizer:
    @staticmethod
    def normalize(data: pd.Series) -> pd.Series:
        return data - data.mean()
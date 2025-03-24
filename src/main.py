import argparse
from data_loaders import *
from data_processors import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обработка временных рядов")
    parser.add_argument("file_path", type=str, help="Путь к файлу")
    parser.add_argument("--time_column", type=str, default=None, help="Название временной колонки")
    parser.add_argument("--out_file", type=str, default=None, help="Путь к выходному файлу")
    parser.add_argument("--value_columns", type=str, nargs='+', required=True, help="Список колонок со значениями")
    parser.add_argument("--outlier_method", type=str, choices=["zscore", "iqr"], default="zscore", help="Метод обработки выбросов")
    parser.add_argument("--outlier_sigma", type=float, default=3.0, help="zscore: Порог для выбросов; iqr: коэффициент")
    parser.add_argument("--trend_window", type=int, default=51, help="Окно фильтра Савицкого-Голея")
    parser.add_argument("--trend_poly", type=int, default=3, help="Степень полинома фильтра Савицкого-Голея")
    parser.add_argument("--jump_threshold", type=float, default=3.0, help="Порог скачков в стандартных отклонениях")
    parser.add_argument("--file_format", type=str, choices=["csv"], default=None, help="Формат входного файла")
    parser.add_argument("--filtered_graphics", type=bool, default=False, help="Нужны ли графики с очищеными от выбросов данными")
    parser.add_argument("--trend_graphics", type=bool, default=False, help="Нужны ли графики с линиями тренда")
    parser.add_argument("--jump_graphics", type=bool, default=False, help="Нужны ли графики со скачками")
    parser.add_argument("--normalize", type=bool, default=False, help="Нужно ли нормализировать данные")
    parser.add_argument("--base_series", type=bool, default=False, help="Нужно ли строить опорный временной ряд")

    args = parser.parse_args()

    loader = FileLoader if args.file_format is None else FileLoader.loader(args.file_format)
    
    data = loader.load_data(args.file_path)

    if args.time_column is None:
        args.time_column = '__index'
        data[args.time_column] = range(len(data))
    
    if args.time_column in data.columns:
        data[f'{args.time_column}_microseconds'] = TimeConverter.convert_to_microseconds(data[args.time_column])
        
        if args.base_series:
            data['__base'] = BaseSeriesBuilder.build([
                data[column] for column in args.value_columns if column in data.columns
            ])
            args.value_columns = ['__base']

        for column in args.value_columns:
            if column in data.columns:
                if args.normalize:
                    data[column] = Normalizer.normalize(data[column])

                data[f'{column}_filtered'] = OutlierProcessor.remove_outliers(data[column], args.outlier_method, args.outlier_sigma)
                data[f'{column}_trend'] = TrendProcessor.extract_trend(data[f'{column}_filtered'], args.trend_window, args.trend_poly)
                data[f'{column}_jumps'] = JumpProcessor.detect_jumps(data[f'{column}_filtered'], args.jump_threshold)


                graphics_n = sum([args.filtered_graphics, args.trend_graphics, args.jump_graphics])

                if graphics_n == 0:
                    continue

                fig, axes = plt.subplots(graphics_n, 1, figsize=(10, 5 * graphics_n), squeeze=False)
                axes = axes.flatten()
                fig.suptitle(f"Графики для ряда: {column}")

                graphic_idx: int = 0

                if args.filtered_graphics:
                    ax = axes[graphic_idx]
                    ax.scatter(data[f'{args.time_column}_microseconds'], data[column], label='Original data')
                    ax.scatter(data[f'{args.time_column}_microseconds'], data[f'{column}_filtered'], label='Filtered data')
                    ax.set_title("Оригинальные и очищенные данные")
                    ax.legend()
                    graphic_idx += 1

                if args.trend_graphics:
                    ax = axes[graphic_idx]
                    ax.scatter(data[f'{args.time_column}_microseconds'], data[f'{column}_filtered'], label='Filtered data')
                    ax.plot(data[f'{args.time_column}_microseconds'], data[f'{column}_trend'], label='Trend', color='red')
                    ax.set_title("Линия тренда")
                    ax.legend()
                    graphic_idx += 1

                if args.jump_graphics:
                    ax = axes[graphic_idx]
                    ax.scatter(data[f'{args.time_column}_microseconds'], data[f'{column}_filtered'], c=data[f'{column}_jumps'])
                    ax.set_title("Скачки в данных")

                plt.tight_layout()
                plt.subplots_adjust(top=0.95)
                plt.show()
            else:
                print(f"Ошибка: В файле отсутствует колонка '{column}'")
        
        print(data.columns)
        print(data)

    else:
        print(f"Ошибка: В файле отсутствует колонка '{args.time_column}'")
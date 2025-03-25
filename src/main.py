import argparse
from data_loaders import *
from data_processors import *
import matplotlib.pyplot as plt

def get_args() -> argparse.Namespace:
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

    return parser.parse_args()

def main():
    args = get_args()

    loader = FileLoader if args.file_format is None else FileLoader.loader(args.file_format)
    
    data = loader.load_data(args.file_path)

    if args.time_column is None:
        args.time_column = '__index'
        data[args.time_column] = range(len(data))
    
    if args.time_column in data.columns:
        data[f'{args.time_column}_microseconds'] = convert_to_microseconds(data[args.time_column])
        
        if args.base_series:
            data['__base'] = build_base_series([
                data[column] for column in args.value_columns if column in data.columns
            ])
            args.value_columns = ['__base']

        for column in args.value_columns:
            if column not in data.columns:
                print(f'Ошибка: В файле отсутствует колонка "{column}"')
                continue

            if args.normalize:
                data[column] = normalize(data[column])

            data[f'{column}_filtered'] = remove_outliers(data[column], args.outlier_method, args.outlier_sigma)
            data[f'{column}_trend'] = extract_trend(data[f'{column}_filtered'], args.trend_window, args.trend_poly)
            data[f'{column}_jumps'] = detect_jumps(data[f'{column}_filtered'], args.jump_threshold)


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
                ax.set_title("Оригинальные и очищенные данные", pad=20)
                ax.legend()
                graphic_idx += 1

            if args.trend_graphics:
                ax = axes[graphic_idx]
                ax.scatter(data[f'{args.time_column}_microseconds'], data[f'{column}_filtered'], label='Filtered data')
                ax.plot(data[f'{args.time_column}_microseconds'], data[f'{column}_trend'], label='Trend', color='red')
                ax.set_title("Линия тренда", pad=20)
                ax.legend()
                graphic_idx += 1

            if args.jump_graphics:
                ax = axes[graphic_idx]
                ax.scatter(data[f'{args.time_column}_microseconds'], data[f'{column}_filtered'], c=data[f'{column}_jumps'])
                ax.set_title("Скачки в данных", pad=20)

            plt.tight_layout()
            plt.subplots_adjust(top=0.90)
            plt.show()
                    
        print(data.columns)
        print(data)

    else:
        print(f"Ошибка: В файле отсутствует колонка '{args.time_column}'")


if __name__ == "__main__":
    main()
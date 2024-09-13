import glob
import tgt


def my_sorting_decorator(func):
    """
    Возвращает сортированный результат
    :param func:
    :return:
    """
    def wrapper(dir_name: str):
        res = func(dir_name)
        new_res = sorted(res)
        return new_res
    return wrapper


@my_sorting_decorator
def get_all_allophones(dir: str):
    """
    Возвращает список аллофонов в папке
    :param dir: имя директории, откуда берутся текстгриды
    :return:
    """
    textgrid_files: list = glob.glob(f"{dir}/*.TextGrid", recursive=True)
    allophones: set = set()
    for grid_file in textgrid_files:
        grid = tgt.io.read_textgrid(grid_file)
        try:
            id_tier = grid.get_tier_by_name("acoustic")
        except ValueError:
            pass
        for interval in id_tier:
            allophones.add(interval.text)
    return allophones


dir = r"D:\intas\intas2\andre\text"
print(get_all_allophones(dir))
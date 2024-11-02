from itertools import product
from typing import Any

letters = "GBRY"
nums = "1234"
levels = [ch + num for num, ch in product(nums, letters)]
level_codes = [2 ** i for i in range(len(levels))]
level2code = {i: j for i, j in zip(levels, level_codes)}
code2level = {j: i for i, j in zip(levels, level_codes)}


def detect_encoding(file_path):
    encoding = "utf-8"
    try:
        l = open(file_path, 'r', encoding="utf-8").read()
        if l.startswith("\ufeff"):
            encoding = "utf-8-sig"
    except UnicodeDecodeError:
        try:
            open(file_path, 'r', encoding="utf-16").read()
            encoding = "utf-16"
        except UnicodeError:
            encoding = "cp1251"
    return encoding


class Params:
    def __init__(self, samplerate: int, sampwidth: int, num_channels: int):
        self.samplerate: int = samplerate
        self.sampwidth: int = sampwidth
        self.numchannels: int = num_channels


class Seg:
    """
    Класс для работы с seg-файлами
    """

    def __init__(self, filename: str = None, labels: list = [], params: Params = Params(0, 0, 0)):
        self.filename: str = filename
        self.labels: list = labels
        self.params: Params = params

    def read_seg_file(self):
        """
        Получение параметров и списка меток из seg-файла
        """
        self.params = self.init_params()

        try:
            with open(self.filename, "r", encoding=detect_encoding(self.filename)) as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(self.filename, "не найден")

        try:
            ind_labels = lines.index('[LABELS]')
        except ValueError:
            print("Seg-файл не содержит секции LABELS")

        labels = lines[ind_labels + 1:]
        try:
            labels_arr = [{
                "position": int(line.split(',')[0]) // self.params.sampwidth // self.params.numchannels,
                "level": code2level[int(line.split(',')[1])],
                "name": line.split(',', maxsplit=2)[2].rstrip()
            } for line in labels if line.count(",") >= 2]
        except ValueError:
            print("Невозможно прочитать метки, проверьте seg-файл на наличие пустых строк")

        self.labels = labels_arr

    def init_params(self):
        try:
            with open(self.filename, "r", encoding=detect_encoding(self.filename)) as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(self.filename, "не найден")
            return
        try:
            ind_params = lines.index("[PARAMETERS]")
        except ValueError:
            print("Seg-файл не содержит секции PARAMETERS")
            return
        try:
            ind_labels = lines.index('[LABELS]')
        except ValueError:
            print("Seg-файл не содержит секции LABELS")
            return

        parameters = lines[ind_params + 1: ind_labels]

        try:
            param_dict = {str(line.split("=")[0]): int(line.split("=")[1]) for line in parameters}
        except ValueError:
            print("Секция PARAMETERS не соответствует формату")
            return

        return Params(int(param_dict["SAMPLING_FREQ"]), int(param_dict["BYTE_PER_SAMPLE"]),
                      int(param_dict["N_CHANNEL"]))

    def write_seg_file(self) -> None:
        """
        Запись seg-файла
        """
        param_defaults = {
            "SAMPLING_FREQ": self.params.samplerate,
            "BYTE_PER_SAMPLE": self.params.sampwidth,
            "CODE": 0,
            "N_CHANNEL": self.params.numchannels,
            "N_LABEL": len(self.labels)
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("[PARAMETERS]\n")
            for key in param_defaults.keys():
                f.write(key + '=' + str(param_defaults[key]) + '\n')
            f.write("[LABELS]\n")
            byte_per_sample = param_defaults["BYTE_PER_SAMPLE"]
            n_channel = param_defaults["N_CHANNEL"]
            try:
                for label in self.labels:
                    f.write(
                        f"{byte_per_sample * n_channel * label['position']},{level2code[label['level']]},{label['name']}\n")
            except (KeyError, ValueError):
                print("Список меток не соответствует формату")
        print("Параметры и метки записаны в файл", self.filename)

    def get_labels_from_seg(self, num_samples: int) -> list[tuple[Any, list[Any] | Any, Any]]:
        """
        Чтение seg-файла, возвращает данные меток для разбивки wav-файла
        Возвращает начало и конец каждого интервала и имя соответствующей метки
        """
        ends = [end['position'] for start, end in zip(self.labels, self.labels[1:])]  # концы интервалов
        ends.append(num_samples)  # добавляем в конец списка длину файла для обработки последнего интервала
        return [(label["position"], ends[i], label["name"]) for i, label in enumerate(self.labels)]

    def make_b1_seg(self, sig_parts: list, label_order: list):
        """
        Запись сег-файла для аудио файлов, собираемых из частей
        :param sig_parts:
        :param label_order:
        :return:
        """
        labels = []
        position = 0
        for i, label in enumerate(label_order):
            labels.append({
                "position": position,
                "level": 'B1',
                "name": label
            })
            position += len(sig_parts[i])
        self.labels = labels
        self.write_seg_file()

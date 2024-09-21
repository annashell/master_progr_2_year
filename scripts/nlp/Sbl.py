""""
читать
срез по миллисекундам
"""
import struct


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


class Sbl:
    def __init__(self, filename: str, seg_filename: str):
        self.signal: list = []
        self.filename: str = filename
        self.seg_filename: str = seg_filename
        self.params: Params = self.init_params()
        self.sampwidth_to_char: dict = {1: "c", 2: "h", 4: "i"}

    def init_params(self):
        try:
            with open(self.seg_filename, "r", encoding=detect_encoding(self.seg_filename)) as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(self.seg_filename, "не найден")
            return
        try:
            ind_params = lines.index("[PARAMETERS]\n")
        except ValueError:
            print("Seg-файл не содержит секции PARAMETERS")
            return
        try:
            ind_labels = lines.index('[LABELS]\n')
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

    def read_sbl(self):
        self.init_params()
        with open(self.filename, "rb") as f:
            raw_signal = f.read()
        num_samples = len(raw_signal) // self.params.sampwidth
        fmt = str(num_samples) + self.sampwidth_to_char[self.params.sampwidth]
        signal = struct.unpack(fmt, raw_signal)
        self.signal = signal

    def get_signal_slice(self, time: int):
        """
        :param time: ms
        :return:
        """
        if len(self.signal) == 0:
            self.read_sbl()

        time_in_points = int(time * self.params.samplerate // 1000)

        sliced_signal: list = self.signal[time_in_points:]

        print(sliced_signal)



new_sbl = Sbl(r"D:\corpres\cta\cta0001-0010\cta0001.sbl", r"D:\corpres\cta\cta0001-0010\cta0001.seg_B1")
new_sbl.get_signal_slice(500)

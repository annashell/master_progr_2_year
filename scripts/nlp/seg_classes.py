class Params:
    def __init__(self, samplerate: int, sampwidth: int, num_channels: int):
        self.samplerate: int = samplerate
        self.sampwidth: int = sampwidth
        self.numchannels: int = num_channels


def detect_encoding(filename):
    encoding = "utf-8"
    try:
        l = open(filename, 'r', encoding="utf-8").read()
        if l.startswith("\ufeff"):
            encoding = "utf-8-sig"
    except UnicodeDecodeError:
        try:
            open(filename, 'r', encoding="utf-16").read()
            encoding = "utf-16"
        except UnicodeError:
            encoding = "cp1251"
    return encoding


class Seg:
    """
    чтение
    сохранение в csv
    добавить метку
    удалить метку
    объединить два сега
    """

    def __init__(self, filename: str = None):
        self.filename: str = filename
        self.poses: list = []
        self.labels = []
        self.params: Params = self.init_params()

    def return_name(self):
        return self.filename

    def read_seg(self):
        lines: list = [line.strip() for line in open(self.filename, encoding=detect_encoding(self.filename))]
        lines = lines[7:]
        for label in lines:
            splt = label.split(',')
            self.poses.append(int(splt[0]))
            self.labels.append(",".join(splt[2:]))

    def count(self):
        return len(self.poses)

    def append(self, pos, label):
        self.labels.append(label)
        if len(self.poses) != 0:
            self.poses.append(self.poses[-1] + pos)
        else:
            self.poses.append(pos)

    def delete(self, index: int):
        pass

    def init_params(self):
        try:
            with open(self.filename, "r", encoding=detect_encoding(self.filename)) as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(self.filename, "не найден")
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


myseg = Seg(r"D:\corpres\cta\cta0001-0010\cta0001.seg_B1")
myseg.read_seg()

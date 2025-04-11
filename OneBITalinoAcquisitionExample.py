import platform
import sys

# OS detection setup
osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
if platform.mac_ver()[0] != "":
    import subprocess
    from os import linesep

    p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8").split(str("\t"))[2].split(linesep)[0]
    if result.startswith("12."):
        print("macOS version is Monterrey!")
        osDic["Darwin"] = "MacOS/Intel310"
        if (
            int(platform.python_version().split(".")[0]) <= 3
            and int(platform.python_version().split(".")[1]) < 10
        ):
            print(f"Python version required is ≥ 3.10. Installed is {platform.python_version()}")
            exit()

# Add path to PLUX API
sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

# Threshold for muscle contraction (adjust this value as needed)
EMG_THRESHOLD = 600


class NewDevice(plux.SignalsDev):
    def __init__(self, address, emg_threshold=600):
        super().__init__(address)
        self.duration = 0
        self.frequency = 0
        self.emg_threshold = emg_threshold


    def onRawFrame(self, nSeq, data):
        emg_value = data[0]  # EMG sur le canal 1
        if emg_value > self.emg_threshold:
            print(f"Muscle contraction detected at frame {nSeq}: value={emg_value}")
        return nSeq > self.duration * self.frequency


def exampleAcquisition(
    address="BTH00:07:80:4D:2E:76",
    duration=20,
    frequency=1000,
    active_ports=[1],
):
    device = NewDevice(address)
    device.duration = int(duration)
    device.frequency = int(frequency)

    device.start(device.frequency, active_ports, 16)
    device.loop()
    device.stop()
    device.close()


if __name__ == "__main__":
    exampleAcquisition(*sys.argv[1:])

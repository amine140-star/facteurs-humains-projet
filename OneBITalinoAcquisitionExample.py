import platform
import sys
import numpy as np
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


sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

import plux

def detect_left_right_movement(acc_x, threshold=1.5):
    """
    Detects left or right hand movement from X-axis acceleration.

    Args:
        acc_x (float): X-axis acceleration value (in g or m/s²).
        threshold (float): Sensitivity threshold.

    Returns:
        str or None: "left", "right", or None if no movement detected.
    """
    if acc_x > threshold:
        return "right"
    elif acc_x < -threshold:
        return "left"
    return None

def calibrate_acc_baseline(acc_x_values):
    """
    Computes the baseline and optimal threshold from calibration data.

    Args:
        acc_x_values (list of float): List of X-axis values while the hand is at rest.

    Returns:
        tuple: (baseline, threshold)
    """
    

    baseline = np.mean(acc_x_values)
    std_dev = np.std(acc_x_values)
    threshold = std_dev * 3  # 3-sigma rule for outliers
    return baseline, threshold


class NewDevice(plux.SignalsDev):
    def __init__(self, address, emg_threshold=500):
        super().__init__(address)
        self.duration = 0
        self.frequency = 0
        self.emg_threshold = emg_threshold  # seuil de détection EMG
        self.emg_detected = False

    def onRawFrame(self, nSeq, data):
        emg_value = data[0]  # Port 1 supposé être EMG

        # Détection de contraction musculaire
        if abs(emg_value) > self.emg_threshold:
            print(f"Mouvement détecté (EMG = {emg_value}) à la frame {nSeq}")
            self.emg_detected = True

        return self.emg_detected or nSeq > self.duration * self.frequency



# example routines


def exampleAcquisition(
    address="BTH98:D3:11:FE:03:67",
    duration=20,
    frequency=100,
    active_ports=[1],  # Port 1 seulement si EMG est là
    emg_threshold=500,  # à ajuster selon calibration
):
    device = NewDevice(address, emg_threshold)
    device.duration = int(duration)
    device.frequency = int(frequency)
    device.start(device.frequency, active_ports, 16)
    device.loop()
    device.stop()
    device.close()



if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])



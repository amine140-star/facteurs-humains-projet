import pygame
import threading
import time
import plux
import os

# Seuils
BPM_STRESS_THRESHOLD = 109
ECG_PEAK_THRESHOLD = 550


shared_state = {
    "ecg": 0,
    "last_peak_time": 0,
    "bpm": 0,
    "beat_times": [],
    "stress_level": "Calme",
    "last_level": "Calme"
}

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__()
        self.address = address

    def onRawFrame(self, nSeq, data):
        ecg_value = data[0] if len(data) > 0 else 0
        shared_state["ecg"] = ecg_value

        current_time = time.time()
        if ecg_value > ECG_PEAK_THRESHOLD:
            if current_time - shared_state["last_peak_time"] > 0.3:
                shared_state["beat_times"].append(current_time)
                shared_state["last_peak_time"] = current_time

                shared_state["beat_times"] = [t for t in shared_state["beat_times"] if current_time - t <= 10]

                if len(shared_state["beat_times"]) >= 2:
                    intervals = [shared_state["beat_times"][i+1] - shared_state["beat_times"][i] for i in range(len(shared_state["beat_times"]) -1)]
                    avg_interval = sum(intervals) / len(intervals)
                    shared_state["bpm"] = 60 / avg_interval if avg_interval > 0 else 0

        bpm = shared_state["bpm"]
        if bpm >= BPM_STRESS_THRESHOLD:
            shared_state["stress_level"] = "Stressé"
        elif bpm >= 100:
            shared_state["stress_level"] = "Moyen"
        else:
            shared_state["stress_level"] = "Calme"

def lancer_capteurs():
    address = "98:D3:11:FE:02:64"
    device = NewDevice(address)
    device.start(100, [1], 16)
    device.loop()
    device.stop()
    device.close()

# --------- PYGAME ----------
pygame.init()
SW, SH = 1000, 600
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Stress Detector - ECG (Enhanced)")
clock = pygame.time.Clock()
font = pygame.font.SysFont('courier', 24)

base_path = os.path.dirname(__file__)
avatar_paths = {
    "Calme": [os.path.join(base_path, 'Sprites', 'calm1.png'), os.path.join(base_path, 'Sprites', 'calm2.png')],
    "Moyen": [os.path.join(base_path, 'Sprites', 'medium1.png'), os.path.join(base_path, 'Sprites', 'medium2.png')],
    "Stressé": [os.path.join(base_path, 'Sprites', 'stress1.png'), os.path.join(base_path, 'Sprites', 'stress2.png')]
}
background_image_path = os.path.join(base_path, 'Sprites', 'background.png')
background_image = pygame.image.load(background_image_path) if os.path.exists(background_image_path) else None

sound_paths = {
    "Calme": os.path.join(base_path, 'Sounds', 'calm.wav'),
    "Moyen": os.path.join(base_path, 'Sounds', 'medium.wav'),
    "Stressé": os.path.join(base_path, 'Sounds', 'stress.wav')
}
sounds = {k: pygame.mixer.Sound(v) for k, v in sound_paths.items() if os.path.exists(v)}

avatars = {}
for key, paths in avatar_paths.items():
    avatars[key] = [pygame.image.load(p) for p in paths if os.path.exists(p)]

frame_index = 0
frame_timer = 0
animation_speed = 10
scroll_text = "Niveau de stress en cours de surveillance... "
scroll_x = SW

def draw_pulsing_circles(level):
    color = (0, 255, 0) if level == "Calme" else (255, 200, 0) if level == "Moyen" else (255, 0, 0)
    radius = 50 + (frame_index % 20) * 2
    pygame.draw.circle(screen, color, (SW // 2, SH // 2), radius, 5)

def draw_bar(bpm, level):
    bar_width = int((bpm / 200) * (SW - 40))
    color = (0, 200, 0) if level == "Calme" else (255, 200, 0) if level == "Moyen" else (255, 0, 0)
    pygame.draw.rect(screen, (100, 100, 100), (20, SH - 60, SW - 40, 30))
    pygame.draw.rect(screen, color, (20, SH - 60, bar_width, 30))

def afficher_valeurs():
    ecg = shared_state["ecg"]
    bpm = int(shared_state["bpm"])
    level = shared_state["stress_level"]
    txt_ecg = f"ECG: {ecg}"
    txt_bpm = f"BPM: {bpm}  Niveau: {level}"
    text_surface_ecg = font.render(txt_ecg, True, (255, 255, 255))
    text_surface_bpm = font.render(txt_bpm, True, (255, 255, 255))
    screen.blit(text_surface_ecg, (20, 20))
    screen.blit(text_surface_bpm, (20, 60))

def draw_scrolling_text():
    global scroll_x
    scroll_surface = font.render(scroll_text, True, (255, 255, 255))
    screen.blit(scroll_surface, (scroll_x, SH - 100))
    scroll_x -= 2
    if scroll_x < -scroll_surface.get_width():
        scroll_x = SW

def game_loop():
    global frame_index, frame_timer
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_level = shared_state["stress_level"]
        bpm_value = shared_state["bpm"]

        if current_level != shared_state["last_level"]:
            if current_level in sounds:
                sounds[current_level].play()
            shared_state["last_level"] = current_level

        frame_timer += 1
        if frame_timer >= animation_speed:
            if avatars[current_level]:
                frame_index = (frame_index + 1) % len(avatars[current_level])
            frame_timer = 0

        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((50, 50, 50))

        draw_pulsing_circles(current_level)

        if avatars[current_level]:
            avatar_image = avatars[current_level][frame_index]
            screen.blit(avatar_image, (SW // 4 - avatar_image.get_width() // 2, SH // 2 - avatar_image.get_height() // 2))

        afficher_valeurs()
        draw_bar(bpm_value, current_level)
        draw_scrolling_text()

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    t = threading.Thread(target=lancer_capteurs)
    t.daemon = True
    t.start()
    game_loop()
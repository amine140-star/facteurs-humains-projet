import pygame
import os
import threading
import plux
import math

# Seuils ajustés (à adapter selon tes tests)
THRESHOLDS = {
    "low": 455,
    "medium": 556,
    "high": 600
}

shared_state = {
    "acc": 0,
    "stress_level": "Calme"
}

lock = threading.Lock()

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__()
        self.address = address

    def onRawFrame(self, nSeq, data):
        with lock:
            if len(data) >= 3:
                x, y, z = data[0], data[1], data[2]
                magnitude = math.sqrt(x**2 + y**2 + z**2)
                shared_state["acc"] = magnitude

                if magnitude < THRESHOLDS["low"]:
                    shared_state["stress_level"] = "Calme"
                elif magnitude < THRESHOLDS["medium"]:
                    shared_state["stress_level"] = "Moyen"
                else:
                    shared_state["stress_level"] = "Stressé"
                    pygame.mixer.Sound.play(alert_sound)
            else:
                print(f"Attention : données incomplètes reçues : {data}")

def lancer_capteurs():
    address = "98:D3:11:FE:02:64"
    device = NewDevice(address)
    try:
        # IMPORTANT : demander les trois canaux ACC (1, 2, 3) ou vérifier lesquels sont configurés pour X, Y, Z
        device.start(10, [1, 2, 3], 16)
        device.loop()
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
    finally:
        device.stop()
        device.close()

# --------- PYGAME ----------
pygame.init()
SW, SH = 800, 600
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Avatar Stress Detector - ACC")
clock = pygame.time.Clock()
font = pygame.font.SysFont('courier.ttf', 24)

# Initialisation du son
pygame.mixer.init()
alert_sound_path = os.path.join(os.path.dirname(__file__), 'alert.wav')
if os.path.exists(alert_sound_path):
    alert_sound = pygame.mixer.Sound(alert_sound_path)
else:
    alert_sound = pygame.mixer.Sound(buffer=b'\x00' * 44100)  # Son vide fallback

# Chargement des images animées
base_path = os.path.dirname(__file__)
avatar_paths = {
    "Calme": [os.path.join(base_path, 'Sprites', 'calm1.png'), os.path.join(base_path, 'Sprites', 'calm2.png')],
    "Moyen": [os.path.join(base_path, 'Sprites', 'medium1.png'), os.path.join(base_path, 'Sprites', 'medium2.png')],
    "Stressé": [os.path.join(base_path, 'Sprites', 'stress1.png'), os.path.join(base_path, 'Sprites', 'stress2.png')]
}

avatars = {}
for key, paths in avatar_paths.items():
    avatars[key] = [pygame.image.load(p) for p in paths if os.path.exists(p)]

frame_index = 0
frame_timer = 0
animation_speed = 10

def draw_bar(acc, level):
    bar_width = int(min(acc / 1023, 1.0) * (SW - 40))
    if level == "Calme":
        color = (0, 200, 0)
    elif level == "Moyen":
        color = (255, 200, 0)
    else:
        color = (255, 0, 0)

    pygame.draw.rect(screen, (100, 100, 100), (20, SH - 60, SW - 40, 30))
    pygame.draw.rect(screen, color, (20, SH - 60, bar_width, 30))

def afficher_valeurs():
    with lock:
        acc = shared_state["acc"]
        level = shared_state["stress_level"]
    txt = f"ACC: {acc:.2f}  Niveau: {level}"
    text_surface = font.render(txt, True, (255, 255, 255))
    screen.blit(text_surface, (20, 20))

def game_loop():
    global frame_index, frame_timer
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        with lock:
            current_level = shared_state["stress_level"]
            acc_value = shared_state["acc"]

        frame_timer += 1
        if frame_timer >= animation_speed:
            if avatars.get(current_level):
                frame_index = (frame_index + 1) % len(avatars[current_level])
            frame_timer = 0

        screen.fill((30, 30, 30))

        if avatars.get(current_level):
            avatar_image = avatars[current_level][frame_index]
            screen.blit(avatar_image, (SW // 2 - avatar_image.get_width() // 2, SH // 2 - avatar_image.get_height() // 2))

        afficher_valeurs()
        draw_bar(acc_value, current_level)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    t = threading.Thread(target=lancer_capteurs)
    t.daemon = True
    t.start()
    game_loop()

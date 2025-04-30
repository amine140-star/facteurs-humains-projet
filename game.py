import random
import pygame
import time
import os
import threading
import platform
import sys

# -------- BITALINO / EMG + PZT SETUP ----------
osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")
import plux

def detect_change(prev, curr, threshold=10):
    return abs(curr - prev) > threshold

shared_state = {
    "gauche": False,
    "droite": False,
    "respiration": 512  # valeur par défaut
}

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        super().__init__()
        self.address = address
        self.duration = 0
        self.frequency = 0
        self.prev_value = None
        self.prev_value2 = None

    def onRawFrame(self, nSeq, data):
        current_value = data[0] # hetha el port A1 ta3 bitalino 7atet fih emg 
        current_value2 = data[1] # hetha el port A2 ta3 bitalino 7atet fih pression ( emg le5or mawjoud ama 3ana sensors ta3 lmuscle ou l emg bidou le )
        respiration_value = data[2]    # canal A3 lel respiration (PZT)

        changement_detecte = False
        changement_detecte2 = False

        if self.prev_value is not None and self.prev_value2 is not None:
            if detect_change(self.prev_value, current_value):
                changement_detecte = True
            if current_value2 > 600:  # seuil pression à ajuster
                changement_detecte2 = True

        self.prev_value = current_value
        self.prev_value2 = current_value2

        shared_state["gauche"] = changement_detecte
        shared_state["droite"] = changement_detecte2
        shared_state["respiration"] = respiration_value

        return nSeq > self.duration * self.frequency

def lancer_emg():
    address = "98:D3:11:FE:03:67"
    device = NewDevice(address)
    device.duration = 9999
    device.frequency = 10
    device.start(device.frequency, [1, 2, 3], 16)
    device.loop()
    device.stop()
    device.close()

# -------- GAME SETUP ----------
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()
pygame.font.init()

SW, SH = 800, 600
SS = pygame.display.set_mode((SW, SH))
pygame.display.set_caption('Dogers')
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)

car_img = pygame.image.load(os.path.join('Sprites', "Car.png"))
enemy_img = pygame.image.load(os.path.join('Sprites', "Enemycar.png"))
road_img = pygame.image.load(os.path.join('Sprites', "Road.png"))

lanes = [248, 330, 420, 504]
button_w, button_h = 100, 50

class Enemy:
    def __init__(self, img, x, y, speed):
        self.img = img
        self.x = x
        self.y = y
        self.speed = speed
        self.halfway = False
        self.off_screen = False
        self.crashed = False

    def move(self):
        if self.y > SH:
            self.off_screen = True
        else:
            self.y += self.speed
            if self.y > (SH - enemy_img.get_height() * 2) / 2:
                self.halfway = True

    def detect_crash(self, x, y):
        if self.y + enemy_img.get_height() >= y and self.y <= y:
            if self.x == x:
                self.crashed = True

    def show(self, x, y):
        self.move()
        self.detect_crash(x, y)
        SS.blit(self.img, (self.x, self.y))

def text_objects(text, font, colour):
    textSurface = font.render(text, True, colour)
    return textSurface, textSurface.get_rect()

def message_display(text, x, y, textsize, colour):
    thetext = pygame.font.SysFont('courier.ttf', textsize)
    TextSurf, TextRect = text_objects(text, thetext, colour)
    TextRect.center = (x, y)
    SS.blit(TextSurf, TextRect)

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(SS, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(SS, ic, (x, y, w, h))
    message_display(msg, x + w / 2, y + h / 2, 20, WHITE)

def game_quit():
    pygame.quit()
    quit()

def generate_enemy(enemycars, speed):
    temp_list = []
    lanes_taken = []
    enemy_amount = random.randrange(1, 4)
    for i in range(enemy_amount):
        generated = False
        while not generated:
            enemy_x = random.choice(lanes)
            if enemy_x not in lanes_taken:
                temp_list.append(Enemy(enemy_img, enemy_x, 0 - enemy_img.get_height() * 2, speed))
                lanes_taken.append(enemy_x)
                generated = True
    enemycars.append(temp_list)
    return enemycars

def crash(dodged):
    message_display("You Crashed!", SW / 2, SH / 6, 80, WHITE)
    message_display("Your Score: " + str(dodged), SW / 2, SH / 4, 80, WHITE)
    freeze = True
    while freeze:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                freeze = False
                game_quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    freeze = False
                    game_loop()
                if event.key == pygame.K_2:
                    freeze = False
                    game_quit()

        button("Replay", (SW/4 - button_w/2), SH*0.6, button_w, button_h, GREEN, BRIGHT_GREEN, game_loop)
        button("Quit", ((3*SW)/4 - button_w/2), SH*0.6, button_w, button_h, RED, BRIGHT_RED, game_quit)

        pygame.display.update()
        clock.tick(FPS)

def game_loop():
    emg_lock = {"gauche": False, "droite": False}

    running = True
    road_y = -369
    dodged = 0
    speed = 6
    end = False
    enemycars = []

    car_x = random.choice([lanes[1], lanes[2]])
    car_y = (SH - car_img.get_height() - 40)

    generate_enemy(enemycars, speed)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

 # mouvment mta3 l emg lehne taya7na fil lanes bech ira pic fi signal mech mouvi direct lel e5er lane         if shared_state["gauche"] and not emg_lock["gauche"]:
            for i in range(1, len(lanes)):
                if car_x == lanes[i]:
                    car_x = lanes[i - 1]
                    break
            emg_lock["gauche"] = True
        if not shared_state["gauche"]:
            emg_lock["gauche"] = False

        if shared_state["droite"] and not emg_lock["droite"]:
            for i in range(0, len(lanes) - 1):
                if car_x == lanes[i]:
                    car_x = lanes[i + 1]
                    break
            emg_lock["droite"] = True
        if not shared_state["droite"]:
            emg_lock["droite"] = False

        # Vitesse de respiration
        respiration = shared_state.get("respiration", 512)
        respiration_norm = min(1.0, max(0.0, (respiration - 400) / 300))  # ajustable
        road_speed = 3 + respiration_norm * 4

        # Affichage route
        SS.blit(road_img, (0, road_y))
        road_y += road_speed
        if road_y >= 0:
            road_y = -369

        count = 0
        while count < len(enemycars):
            for object in enemycars[count]:
                object.speed = road_speed  # vitesse des ennemis aussi
                object.show(car_x, car_y)
                if object.crashed:
                    end = True
            if enemycars[count][0].halfway and len(enemycars) < 2:
                generate_enemy(enemycars, road_speed)
            if enemycars[count][0].off_screen:
                del enemycars[count]
                generate_enemy(enemycars, road_speed)
                count -= 1
                dodged += 1
            else:
                count += 1

        message_display(str(dodged), 700, 50, 30, WHITE)
        SS.blit(car_img, (car_x, car_y))

        if end:
            crash(dodged)

        pygame.display.update()
        clock.tick(FPS)

# --------- MAIN START ---------
if __name__ == "__main__":
    emg_thread = threading.Thread(target=lancer_emg)
    emg_thread.daemon = True
    emg_thread.start()

    game_loop()

import random
import pygame
import time
import os

# centering the display
os.environ["SDL_VIDEO_CENTERED"] = "1"

# initialising pygame
pygame.init()
pygame.font.init()

# creating and setting the display surface
SW = 800
SH = 600

pygame.display.set_caption('Dogers')
SS = pygame.display.set_mode((SW, SH))
clock = pygame.time.Clock()
FPS = 60


# setting colours
BLACK = (0,  0,  0)
WHITE = (255, 255, 255)
RED = (200,  0,  0)
GREEN = (0, 200,  0)
BLUE = (0,  0, 200)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_BLUE = (0, 0, 255)

# loading images
car_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Car.png"))
enemy_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Enemycar.png"))
road_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Road.png"))
car_icon = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Caricon.png"))
tree_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Tree.png"))
rainbow_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "RainbowCar.png"))
fast_img = pygame.image.load(os.path.join(
    os.path.dirname(__file__), 'Sprites', "Fast.png"))

# array of x pos of each lane
lanes = [248, 330, 420, 504]

button_w = 100
button_h = 50

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
    mouse = pygame.mouse.get_pos()  # gets the mouse position
    click = pygame.mouse.get_pressed()  # gets the mouse pressed status
    # set up for boundaries, if mouse is within button boudaries
    # then the button is overwritten with a lighter colour
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
    temp_list = []  # create 1 wave of cars as a individual list
    lanes_taken = []  # list for the lanes that have already been taken
    enemy_amount = random.randrange(1, 4)  # generates a number of enemies
    for i in range(enemy_amount):
        generated = False
        while not generated:
            enemy_x = random.choice(lanes)  # picks a random lane
            if enemy_x not in lanes_taken:
                temp_list.append(
                    Enemy(enemy_img, enemy_x, 0 - enemy_img.get_height() * 2, speed))
                lanes_taken.append(enemy_x)
                generated = True  # if the lane hasn't been taken, a car is generated in that lane and the lane appended to the taken list
    enemycars.append(temp_list)
    return enemycars  # after generating the amount of cars, the updated list is returned


def crash(dodged):
    message_display("You Crashed!", SW / 2, SH / 6, 80, WHITE)
    message_display("Your Score: " + str(dodged), SW / 2, SH / 4, 80, WHITE)
    freeze = True
    while freeze:  # this loop will freeze the screen as it is
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
    running = True
    road_y = -369  # road image will start from -369 as that is the value to be looped
    road_speed = 3  # will be added to the road's y value every frame
    dodged = 0  # keep track how many waves the player has dodged
    speed = 6
    end = False
    enemycars = []

    # let the car start from one of the middle 2 lanes
    car_x = random.choice([lanes[1], lanes[2]])
    car_y = (SH - car_img.get_height() - 40)

    generate_enemy(enemycars, speed)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    game_quit()
                if event.key == pygame.K_LEFT:
                    # loops through all the lanes and changes the x value accordingly
                    for i in range(1, len(lanes)):
                        if car_x == lanes[i]:
                            car_x = lanes[i - 1]
                            break
                if event.key == pygame.K_RIGHT:
                    for i in range(0, len(lanes) - 1):
                        if car_x == lanes[i]:
                            car_x = lanes[i + 1]
                            break

        # displaying and moving road
        SS.blit(road_img, (0, road_y))
        road_y += road_speed
        if road_y == 0:
            road_y = -369

        # loop though the enemycars list and shows each object
        count = 0
        while count < len(enemycars):
            for object in enemycars[count]:
                object.show(car_x, car_y)
                if object.crashed:
                    end = True
            # if the wave has passed halfway and there is 1 or no waves, generate another wave
            if enemycars[count][0].halfway and len(enemycars) < 2:
                generate_enemy(enemycars, speed)
            # once the wave has gone off screen, delete the wave and generate another wave
            if enemycars[count][0].off_screen:
                del enemycars[count]
                generate_enemy(enemycars, speed)
                count -= 1
                dodged += 1
                if dodged % 5 == 0 and dodged != 0:
                    speed += 0.25
            else:
                count += 1

        message_display(str(dodged), 700, 50, 30, WHITE)
        SS.blit(car_img, (car_x, car_y))

        if end:
            # make sure that all sprites are loaded before we run the crash function (otherwise sprites go missing)
            crash(dodged)

        pygame.display.update()
        clock.tick(FPS)


game_loop()

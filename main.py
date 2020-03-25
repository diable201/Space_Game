import pygame
import random

from os import path

# initialize the game

WIDTH = 800
HEIGHT = 600
FPS = 60
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music.ogg')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(10)

clock = pygame.time.Clock()
pygame.display.set_caption("S.Space")
screen = pygame.display.set_mode((WIDTH, HEIGHT))

enemy_img = pygame.image.load('Textures/Enemy/enemy.png').convert_alpha()
enemy_bullet_img = pygame.image.load('Textures/Enemy/laser.png').convert()
player_bullet_img = pygame.image.load('Textures/Player/laser.png').convert()
asteroid_img = path.join(path.dirname(__file__), 'Textures/Asteroids')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

asteroid_images = []
asteroid_list = [
    'asteroid_1.png',
    'asteroid_2.png',
    'asteroid_3.png',
    'asteroid_4.png'
]

for image in asteroid_list:
    asteroid_images.append(pygame.image.load(path.join(asteroid_img, image)).convert_alpha())


class PlayerShip(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Initialize player attributes, coordinates
        self.radius = 30
        self.image = pygame.image.load("Textures/Player/player.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        # Other attributes
        self.speedx = 0
        self.speedy = 0
        self.health = 100
        self.shoot_delay = 175
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Move 0 if no buttons are pressed
        self.speedx = 0
        self.speedy = 0
        # Settings for keyboard
        press = pygame.key.get_pressed()
        if press[pygame.K_a]:
            self.speedx = -6
        if press[pygame.K_d]:
            self.speedx = 6
        if press[pygame.K_w]:
            self.speedy = -6
        if press[pygame.K_s]:
            self.speedy = 6
        if press[pygame.K_SPACE]:
            self.shoot()

        # Acceleration
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Borders
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    # Auto-Fire
    def shoot(self):
        timer = pygame.time.get_ticks()
        if timer - self.last_shot > self.shoot_delay:
            self.last_shot = timer
            bullet = PlayerBullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)


class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, enemy_image, bullet_image, sprites_list, bullet_list):
        pygame.sprite.Sprite.__init__(self)
        # Sprites
        self.image = pygame.transform.scale(enemy_image, (60, 60))
        self.rect = self.image.get_rect()
        self.sprites = sprites_list

        # Start position
        self.rect.x = random.randint(20, WIDTH - 20)
        self.rect.y = random.randrange(-140, -30)
        self.speedy = random.randrange(2, 6)

        # Bullet settings
        self.bullet_image = bullet_image
        self.bullets = bullet_list
        self.shoot_delay = random.randint(1250, 1500)
        self.last_shot = pygame.time.get_ticks()
        self.num_of_shots = 1

    def update(self):
        if self.rect.top > HEIGHT + 15 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(50, WIDTH - 50)
            self.rect.y = random.randrange(-100, -50)
        self.rect.y += self.speedy

        # Shoot
        for shoot in range(self.num_of_shots):
            self.shoot()

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullet = EnemyBullet(self.bullet_image, self.rect.centerx, self.rect.bottom)
            self.sprites.add(bullet)
            self.bullets.add(bullet)


class Asteroids(pygame.sprite.Sprite):

    def __init__(self, asteroid_image):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(asteroid_image)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-3, 2)
        self.rot = 0
        self.rot_speed = random.randrange(-5, 5)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.image_original, self.rot)
            new_image = pygame.transform.rotate(self.image_original, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)
        self.rotate()


class PlayerBullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_bullet_img, (8, 23))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10  # negative for movement up

    def update(self):
        self.rect.y += self.speedy
        # if bullet goes off bottom of window, destroy it
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, bullet_image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # scale bullet size
        self.image = pygame.transform.scale(bullet_image, (8, 23))
        self.rect = self.image.get_rect()

        # bullet position is according the player position
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = 15

    def update(self):
        self.rect.y += self.speedy
        # if bullet goes off bottom of window, destroy it
        if self.rect.bottom > HEIGHT:
            self.kill()


all_sprites = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
enemy_ships = pygame.sprite.Group()
player = PlayerShip()
all_sprites.add(player)


def new_asteroid():
    asteroid_enemy = Asteroids(asteroid_images)
    all_sprites.add(asteroid_enemy)
    asteroids.add(asteroid_enemy)


for asteroid in range(5):
    new_asteroid()

for enemy in range(4):
    enemy = EnemyShip(enemy_img, enemy_bullet_img, all_sprites, enemy_bullets)
    all_sprites.add(enemy)
    enemy_ships.add(enemy)

player_scores = 0


def draw_player_scores(surface, text, size, x, y):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_health_bar(surface, x, y, health):
    if health < 0:
        health = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (health / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)  # white border
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)  # health border
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        pressed = pygame.key.get_pressed()
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False
        if pressed[pygame.K_ESCAPE]:
            running = False

    all_sprites.update()

    # Удары по врагу
    hits_player = pygame.sprite.groupcollide(enemy_ships, bullets, True, True)
    for hit_player in hits_player:
        player_scores += 10
        e = EnemyShip(enemy_img, enemy_bullet_img, all_sprites, enemy_bullets)
        all_sprites.add(e)
        enemy_ships.add(e)

    # Проверка, не ударил ли моб игрока
    # hits_asteroids = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle)
    # for hit_asteroids in hits_asteroids:
    #     player.health -= hit_asteroids.radius
    #     new_asteroid()
    #     if player.health <= 0:
    #         running = False

    hits_asteroids = pygame.sprite.groupcollide(enemy_ships, asteroids, False, pygame.sprite.collide_circle)
    for hit_asteroids in hits_asteroids:
        running = True

    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_player_scores(screen, str(player_scores), 25, WIDTH / 2, 20)
    draw_health_bar(screen, 5, 5, player.health)
    # screen.blit(backgroundImage, (0, 0))
    pygame.display.flip()

pygame.quit()

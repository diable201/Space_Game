import pygame
import random

from os import path

# initialize the game

WIDTH = 800
HEIGHT = 600
FPS = 60
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("S.Space")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
img_dir = path.join(path.dirname(__file__), 'Textures')
enemy_img = pygame.image.load('Textures/Enemy/enemy.png').convert_alpha()
enemy_bullet_img = pygame.image.load('Textures/Enemy/laser.png').convert()
player_bullet_img = pygame.image.load('Textures/Player/laser.png').convert()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class PlayerShip(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image = pygame.image.load("Textures/Player/player.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0

    def update(self):
        # движение 0, если не нажаты кнопки, код проще, фпс больше
        self.speedx = 0
        self.speedy = 0
        press = pygame.key.get_pressed()
        if press[pygame.K_a]:
            self.speedx = -6
        if press[pygame.K_d]:
            self.speedx = 6
        if press[pygame.K_w]:
            self.speedy = -6
        if press[pygame.K_s]:
            self.speedy = 6

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

    def shoot(self):
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
        self.speedy = random.randrange(2, 7)
        self.speedx = random.randrange(-1, 1)

        # Bullet settings
        self.bullet_image = bullet_image
        self.bullets = bullet_list
        self.shoot_delay = random.randint(1200, 1500)
        self.last_shot = pygame.time.get_ticks()
        self.num_of_shots = 1

    def update(self):
        if self.rect.top > HEIGHT + 15 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

        # Shoot
        for shoot in range(self.num_of_shots):
            self.shoot()

        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullet = EnemyBullet(self.bullet_image, self.rect.centerx, self.rect.bottom)
            self.sprites.add(bullet)
            self.bullets.add(bullet)


class PlayerBullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_bullet_img, (8, 23))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10  # отрицательное для движения вверх

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
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

    # update bullet
    def update(self):
        self.rect.y += self.speedy
        # if bullet goes off bottom of window, destroy it
        if self.rect.bottom > HEIGHT:
            self.kill()


all_sprites = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bullets = pygame.sprite.Group()
# mobs = pygame.sprite.Group()
enemy_ships = pygame.sprite.Group()
player = PlayerShip()
all_sprites.add(player)
for i in range(5):
    enemy = EnemyShip(enemy_img, enemy_bullet_img, all_sprites, enemy_bullets)
    all_sprites.add(enemy)
    enemy_ships.add(enemy)

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
        elif event.type == pygame.KEYDOWN:
            if pressed[pygame.K_ESCAPE]:
                running = False
            if pressed[pygame.K_SPACE]:
                player.shoot()

    all_sprites.update()

    # Удары по врагу
    hits_player = pygame.sprite.groupcollide(enemy_ships, bullets, True, True)
    for hit_player in hits_player:
        e = EnemyShip(enemy_img, enemy_bullet_img, all_sprites, enemy_bullets)
        all_sprites.add(e)
        enemy_ships.add(e)

    # Проверка, не ударил ли моб игрока
    # hits_mob = pygame.sprite.spritecollide(player, EnemyShip, False)
    # if hits_mob:
    #     running = False

    screen.fill(BLACK)
    all_sprites.draw(screen)
    # screen.blit(backgroundImage, (0, 0))
    pygame.display.flip()

pygame.quit()

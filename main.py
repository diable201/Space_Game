import pygame
import random

from os import path

# Initialize the game parameters
WIDTH = 800
HEIGHT = 600
FPS = 60

# Next colors are using for health bar and background
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Initialize the game
pygame.init()
pygame.display.set_caption("S.Space")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# Load directories for objects
player_dir = path.join(path.dirname(__file__), 'Textures/Player')
asteroid_dir = path.join(path.dirname(__file__), 'Textures/Asteroids')
explosion_dir = path.join(path.dirname(__file__), 'Textures/Explosions')
background_dir = path.join(path.dirname(__file__), 'Textures/Background')
enemy_dir = path.join(path.dirname(__file__), 'Textures/Enemy')

# Load textures for objects
enemy_bullet_img = pygame.image.load('Textures/Enemy/laser.png').convert()
player_bullet_img = pygame.image.load('Textures/Player/laser.png').convert()
player_logo = pygame.image.load(path.join(player_dir, "live.png")).convert()
player_mini_logo = pygame.transform.scale(player_logo, (25, 30))
player_mini_logo.set_colorkey(BLACK)
background = pygame.image.load(path.join(background_dir, "back.png")).convert()
background_rect = background.get_rect()


# Load sound directory and main theme for game
sound_dir = path.join(path.dirname(__file__), 'Sound')
pygame.mixer.init()
pygame.mixer.music.load(path.join(sound_dir, 'ost.ogg'))
pygame.mixer.music.play(-1)  # for loop
pygame.mixer.music.set_volume(10)

# Sounds for game play (shoot sounds, explosion sounds, etc)
shoot_sound_player = pygame.mixer.Sound(path.join(sound_dir, 'shoot_player.ogg'))
shoot_sound_enemy = pygame.mixer.Sound(path.join(sound_dir, 'shoot_enemy.ogg'))
explosion_sound_asteroid = pygame.mixer.Sound(path.join(sound_dir, 'explosion_asteroid.ogg'))
explosion_sound_ship = pygame.mixer.Sound(path.join(sound_dir, 'explosion_ship.ogg'))
health_sound_player = pygame.mixer.Sound(path.join(sound_dir, 'health.ogg'))

# Sprites for choosing different player models and enemies
images_of_enemies = []
for enemy in range(1, 21):
    filename = 'enemy_{}.png'.format(enemy)
    image_of_enemy = pygame.image.load(path.join(enemy_dir, filename)).convert()
    image_of_enemy.set_colorkey(BLACK)
    img_main = pygame.transform.scale(image_of_enemy, (60, 60))
    images_of_enemies.append(img_main)

images_of_player = []
for player in range(1, 12):
    filename = 'player_{}.png'.format(player)
    image_of_player = pygame.image.load(path.join(player_dir, filename)).convert()
    image_of_player.set_colorkey(BLACK)
    img_main = pygame.transform.scale(image_of_player, (60, 60))
    images_of_player.append(img_main)

images_of_asteroids = []
for animation in range(1, 5):
    filename = 'asteroid_{}.png'.format(animation)
    image_of_asteroid = pygame.image.load(path.join(asteroid_dir, filename)).convert()
    image_of_asteroid.set_colorkey(BLACK)
    img_small = pygame.transform.scale(image_of_asteroid, (32, 32))
    images_of_asteroids.append(img_small)

# Sprites for animating various explosions
animation_of_explosion = {'large': [], 'small': [], 'player': []}
for animation in range(1, 10):
    filename = 'explosion_{}.png'.format(animation)
    img = pygame.image.load(path.join(explosion_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_large = pygame.transform.scale(img, (75, 75))
    animation_of_explosion['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    animation_of_explosion['small'].append(img_small)
    filename = 'player_explosion_{}.png'.format(animation)
    img = pygame.image.load(path.join(explosion_dir, filename)).convert()
    img.set_colorkey(BLACK)
    animation_of_explosion['player'].append(img)


# Main classes for game
class PlayerShip(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Initialize player attributes, coordinates
        self.radius = 30
        self.image = random.choice(images_of_player)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        # Other attributes
        self.speedx = 0
        self.speedy = 0
        self.health = 100
        self.shoot_delay = 175
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

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

        # Show player after death
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 500:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

    # Auto-Fire
    def shoot(self):
        timer = pygame.time.get_ticks()
        if timer - self.last_shot > self.shoot_delay:
            self.last_shot = timer
            bullet = PlayerBullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            shoot_sound_player.play()

    # Hide player after death
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT - 10)


class EnemyShip(pygame.sprite.Sprite):

    def __init__(self, enemy_image, bullet_image, sprites_list, bullet_list):
        pygame.sprite.Sprite.__init__(self)
        # Sprites
        self.image_original = random.choice(enemy_image)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
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

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullet = EnemyBullet(self.bullet_image, self.rect.centerx, self.rect.bottom)
            self.sprites.add(bullet)
            self.bullets.add(bullet)
            shoot_sound_enemy.play()

    # If enemy goes off bottom of window, re-spawn it
    def update(self):
        if self.rect.top > HEIGHT + 15 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(50, WIDTH - 50)
            self.rect.y = random.randrange(-100, -50)
        self.rect.y += self.speedy

        # Shoot
        for shoot in range(self.num_of_shots):
            self.shoot()


class Asteroids(pygame.sprite.Sprite):

    # Initial positions
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

    # Rotation around its own axis
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

    # If asteroid goes off bottom of window, re-spawn it
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

        # Scale bullet size
        self.image = pygame.transform.scale(player_bullet_img, (9, 24))
        self.rect = self.image.get_rect()

        # Bullet position is according the player position
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10  # Negative for movement up

    def update(self):
        self.rect.y += self.speedy
        # If bullet goes off bottom of window, destroy it
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, bullet_image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Scale bullet size
        self.image = pygame.transform.scale(bullet_image, (8, 23))
        self.rect = self.image.get_rect()

        # Bullet position is according the enemy position
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = 15

    def update(self):
        self.rect.y += self.speedy
        # if bullet goes off bottom of window, destroy it
        if self.rect.bottom > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)

        # Position of explosion
        self.size = size
        self.image = animation_of_explosion[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        # Drawing explosion sprites until all sprites are drawn
        timer = pygame.time.get_ticks()
        if timer - self.last_update > self.frame_rate:
            self.last_update = timer
            self.frame += 1
            if self.frame == len(animation_of_explosion[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = animation_of_explosion[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class FirstAidKit(pygame.sprite.Sprite):

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        # Position of FirstAidKit, velocity, texture
        self.image = pygame.image.load(path.join(player_dir, "first_aid_kit.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        # if FirstAidKit goes off bottom of window, destroy it
        if self.rect.top > HEIGHT:
            self.kill()


# Putting all the sprites in groups for rendering
all_sprites = pygame.sprite.Group()
enemy_ships = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
firs_ait_kit = pygame.sprite.Group()
player_ship = PlayerShip()
all_sprites.add(player_ship)


# Render text in the window
def render(surface, text, size, x, y):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


# Create asteroid after destruction
def new_asteroid():
    asteroid_enemy = Asteroids(images_of_asteroids)
    all_sprites.add(asteroid_enemy)
    asteroids.add(asteroid_enemy)


# Create enemy ship after destruction
def new_enemy_ship():
    enemy_ship = EnemyShip(images_of_enemies, enemy_bullet_img, all_sprites, enemy_bullets)
    all_sprites.add(enemy_ship)
    enemy_ships.add(enemy_ship)


# Draw lives in the upper right corner
def draw_lives(surf, x, y, lives, image):
    for live in range(lives):
        image_rect = image.get_rect()
        image_rect.x = x + 30 * live
        image_rect.y = y
        surf.blit(image, image_rect)


# Initial values for a new game
def create_object():
    for asteroid in range(5):
        new_asteroid()
    for enemy_ship in range(3):
        new_enemy_ship()


# Draw lives in the upper left corner
def draw_health_bar(surface, x, y, health):
    if health <= 0:
        health = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (health / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)  # white border
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)  # health border
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


# Start menu for a new game
def start_menu():
    screen.blit(background, background_rect)
    render(screen, "S.Space", 64, WIDTH / 2, HEIGHT / 4)
    render(screen, "Arrow WADS move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    render(screen, "Press a key to begin", 22, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    menu = True
    while menu:
        clock.tick(FPS)
        for key in pygame.event.get():
            if key.type == pygame.QUIT:
                pygame.quit()
            if key.type == pygame.KEYUP:
                menu = False


# End Menu after game over of player
def end_menu():
    screen.blit(background, background_rect)
    render(screen, "Game Over", 64, WIDTH / 2, HEIGHT / 4)
    render(screen, "Press any key to begin again", 22, WIDTH / 2, HEIGHT / 2)
    render(screen, "Or close the window to end", 22, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    end = True
    while end:
        clock.tick(FPS)
        for key in pygame.event.get():
            if key.type == pygame.QUIT:
                pygame.quit()
            if key.type == pygame.KEYUP:
                end = False


# Winner Menu after 750 or more scores
def winner_menu():
    screen.blit(background, background_rect)
    render(screen, "YOU ARE WINNER", 64, WIDTH / 2, HEIGHT / 4)
    render(screen, "THANK YOU FOR PLAYING", 22, WIDTH / 2, HEIGHT / 2)
    render(screen, "Do you want to start again? Press any key", 30, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    pygame.display.flip()
    winner = True
    while winner:
        clock.tick(FPS)
        for key in pygame.event.get():
            if key.type == pygame.QUIT:
                pygame.quit()
            if key.type == pygame.KEYUP:
                winner = False


# Initial settings for game
Player_Scores = 0
Game_Over = False
New_Game = True
Game = True
Winner = False


while Game:
    # Keep the cycle at the right speed
    clock.tick(FPS)
    # Create start menu after a new game
    if New_Game:
        start_menu()
        New_Game = False
        # Putting all the sprites in groups for rendering
        all_sprites = pygame.sprite.Group()
        enemy_ships = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        firs_ait_kit = pygame.sprite.Group()
        player_ship = PlayerShip()
        all_sprites.add(player_ship)
        # Create enemies
        create_object()

    # Create end menu after death of player
    if Game_Over:
        end_menu()
        Game_Over = False
        all_sprites = pygame.sprite.Group()
        enemy_ships = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        firs_ait_kit = pygame.sprite.Group()
        player_ship = PlayerShip()
        all_sprites.add(player_ship)
        # Create enemies
        create_object()
        # After death zero points
        Player_Scores = 0

    # Create winner menu after 750 or more scores
    if Winner:
        winner_menu()
        Winner = False
        all_sprites = pygame.sprite.Group()
        enemy_ships = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        firs_ait_kit = pygame.sprite.Group()
        player_ship = PlayerShip()
        all_sprites.add(player_ship)
        # Create enemies
        create_object()
        # After death zero points
        Player_Scores = 0

    # Check to close the game
    for event in pygame.event.get():
        pressed = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            Game = False
        if pressed[pygame.K_ESCAPE]:
            Game = False

    # Always update sprites
    all_sprites.update()

    # Hits on the enemy
    hits_player = pygame.sprite.groupcollide(enemy_ships, player_bullets, True, True)
    for hit_player in hits_player:
        Player_Scores += 10
        explosion = Explosion(hit_player.rect.center, 'large')
        explosion_sound_ship.play()
        all_sprites.add(explosion)
        # The appearance of boost with a probability of 15%
        if random.random() > 0.85:
            health_boost = FirstAidKit(hit_player.rect.center)
            all_sprites.add(health_boost)
            firs_ait_kit.add(health_boost)
        # Create new ship after destruction
        new_enemy_ship()
        if Player_Scores >= 750:
            Winner = True

    # Hits on the asteroids
    hits_player = pygame.sprite.groupcollide(asteroids, player_bullets, True, True)
    for hit_player in hits_player:
        Player_Scores += 5
        explosion = Explosion(hit_player.rect.center, 'small')
        all_sprites.add(explosion)
        explosion_sound_asteroid.play()
        # Create new asteroid after destruction
        new_asteroid()
        if Player_Scores >= 750:
            Winner = True

    # Asteroid hit on player
    hits_asteroids = pygame.sprite.spritecollide(player_ship, asteroids, True, pygame.sprite.collide_circle)
    for hit_asteroid in hits_asteroids:
        player_ship.health -= hit_asteroid.radius
        explosion = Explosion(hit_asteroid.rect.center, 'small')
        all_sprites.add(explosion)
        explosion_sound_asteroid.play()
        new_asteroid()
        if player_ship.health <= 0:
            player_explosion = Explosion(player_ship.rect.center, 'player')
            all_sprites.add(player_explosion)
            explosion_sound_ship.play()
            player_ship.hide()
            player_ship.lives -= 1
            player_ship.health = 100

        if player_ship.lives == 0:
            Game_Over = True

    # Hitting an enemy with asteroids
    hits_asteroids = pygame.sprite.groupcollide(enemy_ships, asteroids, True, True)
    for hit_asteroid in hits_asteroids:
        explosion = Explosion(hit_asteroid.rect.center, 'large')
        all_sprites.add(explosion)
        explosion_sound_ship.play()
        # Create new ship and asteroid after destruction
        new_asteroid()
        new_enemy_ship()

    # Boost collision with player
    hits_first_aid_kit = pygame.sprite.spritecollide(player_ship, firs_ait_kit, True)
    for hit_first_aid_kit in hits_first_aid_kit:
        health_sound_player.play()
        player_ship.health += random.randrange(15, 25)
        if player_ship.health >= 100:
            player_ship.health = 100

    # Enemy hit on player
    hits_enemy = pygame.sprite.spritecollide(player_ship, enemy_bullets, True, pygame.sprite.collide_circle)
    for hit_enemy in hits_enemy:
        player_ship.health -= 10
        explosion = Explosion(hit_enemy.rect.center, 'small')
        all_sprites.add(explosion)
        explosion_sound_asteroid.play()
        if player_ship.health <= 0:
            player_explosion = Explosion(player_ship.rect.center, 'player')
            all_sprites.add(player_explosion)
            explosion_sound_ship.play()
            player_ship.hide()
            player_ship.lives -= 1
            player_ship.health = 100

        if player_ship.lives == 0:
            Game_Over = True

    # Drawing background, health, scores, lives
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    render(screen, str(Player_Scores), 30, WIDTH / 2, 20)
    draw_health_bar(screen, 10, 10, player_ship.health)
    draw_lives(screen, WIDTH - 100, 10, player_ship.lives, player_mini_logo)
    pygame.display.flip()


pygame.quit()

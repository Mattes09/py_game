import pygame
import random
import math

WIDTH = 800
HEIGHT = 600
FPS = 45

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

background = pygame.image.load("background.jpeg")

explosion_sheet = pygame.image.load("explosion.png")

# Fonts
font = pygame.font.Font("freesansbold.ttf", 32)
menu_font = pygame.font.Font("freesansbold.ttf", 64)
over_font = pygame.font.Font("freesansbold.ttf", 64)

WHITE = (255, 255, 255)

def load_frames(sheet, frame_width, frame_height, num_frames):
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames

explosion_frames = load_frames(explosion_sheet, 64, 64, 12)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5

        self.rect.x += self.speed_x

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("alien.png")
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(50, 150)
        self.speed_x = 4
        self.speed_y = 40

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1
            self.rect.y += self.speed_y
        if self.rect.bottom > HEIGHT:
            self.rect.y = random.randint(50, 150)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("rocket.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_y = -10
        self.state = "ready"

    def update(self):
        if self.state == "fire":
            self.rect.y += self.speed_y
            if self.rect.bottom < 0:
                self.state = "ready"
                self.rect.bottom = HEIGHT - 10

    def fire(self, x, y):
        if self.state == "ready":
            self.rect.centerx = x
            self.rect.bottom = y
            self.state = "fire"

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = explosion_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150  

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame == len(self.frames):
                self.current_frame = 0  
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect(center=self.rect.center)

def draw_tile_background():
    tile = pygame.image.load("tile.png")
    tile_rect = tile.get_rect()
    for y in range(0, HEIGHT, tile_rect.height):
        for x in range(0, WIDTH, tile_rect.width):
            screen.blit(tile, (x, y))

def show_score(x, y, score):
    score_text = font.render("SCORE: " + str(score), True, WHITE)
    screen.blit(score_text, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, WHITE)
    screen.blit(over_text, (200, 250))

def show_menu():
    draw_tile_background()
    menu_text = menu_font.render("Space Invaders", True, WHITE)
    start_text = font.render("Press ENTER to start", True, WHITE)
    screen.blit(menu_text, (150, 150))
    screen.blit(start_text, (225, 300))

def main_menu():
    in_menu = True
    explosion_group = pygame.sprite.Group()
    explosion = Explosion((WIDTH // 2, 400))  
    explosion_group.add(explosion)

    while in_menu:
        screen.fill((0, 0, 0))  
        show_menu()
        explosion_group.update()
        explosion_group.draw(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_menu = False

def main_game():
    player = Player()
    rocket = Rocket()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites.add(player)

    for _ in range(6):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and rocket.state == "ready":
                    rocket.fire(player.rect.centerx, player.rect.top)
                    all_sprites.add(rocket)

        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.spritecollide(rocket, enemies, True)
        for hit in hits:
            score += 1
            rocket.state = "ready"
            rocket.rect.bottom = HEIGHT - 10
            new_enemy = Enemy()
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)
            all_sprites.remove(rocket)  

        # Check if rocket is not in fire state
        if rocket.state == "ready":
            all_sprites.remove(rocket)

        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        show_score(10, 10, score)

        if pygame.sprite.spritecollideany(player, enemies):
            game_over_text()
            pygame.display.flip()
            pygame.time.wait(3000)
            main_menu()  
            main_game()  
            running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_menu()
    main_game()




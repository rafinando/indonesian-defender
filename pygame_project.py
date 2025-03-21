import pygame
from random import randint

pygame.init()

# Game window settings
win_width = 780
win_height = 640
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Indonesian Defender")
FPS = 60

# Load and scale images
backgrounds = [
    pygame.transform.scale(pygame.image.load("backgroundfinal1.png"), (20 * win_width, win_height)),
    pygame.transform.scale(pygame.image.load("backgroundfinal2.png"), (20 * win_width, win_height)),
    pygame.transform.scale(pygame.image.load("backgroundfinal3.png"), (20 * win_width, win_height)),
    pygame.transform.scale(pygame.image.load("unnecesary.png"), (20 * win_width, win_height))
]
player_img = pygame.transform.scale(pygame.image.load("player.png"), (100, 60))
bullet_img = pygame.transform.scale(pygame.image.load("bullet.png"), (40, 20))

# Example placeholders for enemy images
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (90, 50))
fast_enemy_img = pygame.transform.scale(pygame.image.load("fast_enemy.png"), (50, 50))
big_enemy_img = pygame.transform.scale(pygame.image.load("big_enemy.png"), (70, 70))


# Sound effects
shooting_sound = pygame.mixer.Sound("shooting.wav")
game_over_sound = pygame.mixer.Sound("gameoversound.wav")
bgm = [
    "bgm1.mp3",
    "bgm2.mp3",
    "bgm3.mp3",
]

explosion_images = [pygame.image.load(f"explosion{i}.png") for i in range(1, 2)]  # Adjust for your sprite sheet
explosion_sound = pygame.mixer.Sound("explosion.wav")

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, image, x, y, speed):
        super().__init__(image, x, y, speed)
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 50
        self.last_shot_time = pygame.time.get_ticks()
        self.health = 10
        self.shooting = False
        self.base_speed = speed

    def update(self):
        global bg_speed
        keys = pygame.key.get_pressed()

        # Adjust speed with Shift and Ctrl
        if keys[pygame.K_LSHIFT]:
            bg_speed = 10
        elif keys[pygame.K_LCTRL]:
            bg_speed = 3
        else:
            self.speed = self.base_speed

        if keys[pygame.K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.x < win_width - self.rect.width - 5:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.y < win_height - self.rect.height - 5:
            self.rect.y += self.speed

        if self.shooting:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            bullet = Bullet(bullet_img, self.rect.centerx - -10, self.rect.centery, -8)
            self.bullets.add(bullet)
            self.last_shot_time = now



class Bullet(GameSprite):
    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.kill()


class Enemy(GameSprite):
    def update(self):
        self.rect.x -= self.speed  # Move from right to left
        if self.rect.x < -self.rect.width:  # Check if off-screen on the left
            self.respawn()

    def respawn(self):
        self.rect.x = randint(win_width + 40, win_width + 100)  # Spawn off-screen to the right
        self.rect.y = randint(0, win_height - self.rect.height)
        self.speed = randint(10, 20)


class FastEnemy(Enemy):
    def update(self):
        self.rect.x -= self.speed + 3  # Move faster from right to left
        if self.rect.x < -self.rect.width:
            self.respawn()


class BigEnemy(Enemy):
    def __init__(self, image, x, y, speed):
        super().__init__(image, x, y, speed)
        self.image = pygame.transform.scale(image, (70, 70))
        self.health = 3

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()


class Explosion(GameSprite):
    def __init__(self, images, x, y):
        super().__init__(images[0], x, y, 0)
        self.images = images
        self.frame = 0
        self.animation_speed = 3  # Adjust for slower or faster animation
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.frame += 1
            if self.frame < len(self.images):
                self.image = self.images[self.frame]
            else:
                self.kill()  # Remove explosion once animation ends


# Initialize game objects
player = Player(player_img, win_width // 2 - 32, win_height - 100, 5)
enemies = pygame.sprite.Group()

# Add enemies
for _ in range(3):
    enemy = Enemy(enemy_img, randint(0, win_width - 50), randint(-150, -50), randint(4, 8))
    enemies.add(enemy)

for _ in range(0):
    fast_enemy = FastEnemy(fast_enemy_img, randint(0, win_width - 50), randint(-150, -50), randint(4, 6))
    enemies.add(fast_enemy)

for _ in range(0):
    big_enemy = BigEnemy(big_enemy_img, randint(0, win_width - 70), randint(-200, -100), randint(1, 3))
    enemies.add(big_enemy)

# Background scrolling
bg_offsets = [0] * len(backgrounds)
current_bg_index = 0  # Start with the first background
score = 0
kills = 0
speed_level = 1
bg_speed = 5

# Place names for each background
place_names = ["Stage 1 : Jogja", "Stage 2 : Jakarta", "Stage 3 : Bali"]

# Game font for displaying text
font = pygame.font.SysFont("comicsans", 30)

def reset_game():
    global player, enemies, score, kills, current_bg_index, bg_offsets, powerups
    player.health = 10
    player.shoot_cooldown = 50
    play_bgm(current_bg_index)
    score = 0
    kills = 0
    current_bg_index = 0
    bg_offsets = [0] * len(backgrounds)
    player.rect.x, player.rect.y = win_width // 2 - 32, win_height - 100
    enemies.empty()
    for _ in range(3):
        enemy = Enemy(enemy_img, randint(0, win_width - 50), randint(-150, -50), randint(4, 8))
        enemies.add(enemy)

def game_finished():
    if current_bg_index == 3:
        game_over_text = font.render("Mission Success", True, (0, 255, 0))
        game_over_text1 = font.render("Press 'R' to return to start menu or 'Q' to Quit", True, (255, 255, 255))
        window.fill((0, 0, 0))
        window.blit(game_over_text, (win_width // 2 - 100, win_height // 2 - 20))
        window.blit(game_over_text1, (win_width // 2 - 200, win_height // 2 + 20))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_menu()
                        return False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
        return True
    return False

def draw_ui():
    """Display score, kills, and player health."""
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    kills_text = font.render(f"Kills: {kills}", True, (255, 255, 255))
    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    window.blit(score_text, (10, 10))
    window.blit(kills_text, (10, 40))
    window.blit(health_text, (10, 70))


def check_game_over():
    """End the game if the player's health reaches 0."""
    if player.health <= 0:
        game_over_sound.play()
        game_over_text = font.render("Game over", True, (255, 0, 0))
        game_over_text1 = font.render("Press 'R' to return to start menu or 'Q' to Quit", True, (255, 255, 255))
        pygame.mixer.music.stop()
        window.fill((0, 0, 0))
        window.blit(game_over_text, (win_width // 2 - 100, win_height // 2 - 20))
        window.blit(game_over_text1, (win_width // 2 - 200, win_height // 2 + 20))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_menu()
                        return False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
        return True
    return False


def fade_screen():
    fade = pygame.Surface((win_width, win_height))
    fade.fill((0, 0, 0))  # Black fade
    for alpha in range(0, 255, 5):  # Adjust step size for faster/slower fade
        fade.set_alpha(alpha)
        window.blit(backgrounds[current_bg_index], (bg_offsets[current_bg_index], 0))
        window.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)


def display_place_name(name):
    """Display the name of the place temporarily."""
    place_text = font.render(name, True, (255, 255, 255))
    text_rect = place_text.get_rect(center=(win_width // 2, win_height // 2))
    play_bgm(current_bg_index)
    window.fill((0, 0, 0))  # Optional: Fill the screen with black
    window.blit(place_text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)  # Display for 2 seconds


def pause_game():
    paused = True
    pause_text = font.render("Paused - Press 'P' to Resume", True, (255, 255, 255))
    instructions_text = font.render("Use W/A/S/D to move, Space to shoot", True, (255, 255, 255))
    instructions_text2 = font.render("SHIFT to speed up, CTRL to slow down", True, (255, 255, 255))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:  # Unpause
                paused = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    start_menu()
                    return False

        window.fill((0, 0, 0))  # Black screen during pause
        window.blit(pause_text, (win_width // 2 - 150, win_height // 2 - 50))
        window.blit(instructions_text, (win_width // 2 - 200, win_height // 2))
        window.blit(instructions_text2, (win_width // 2 - 200, win_height // 3))
        pygame.display.update()

def start_menu():
    menu_running = True
    title_font = pygame.font.SysFont("comicsans", 60)
    option_font = pygame.font.SysFont("comicsans", 40)
    
    title_text = title_font.render("Indonesian Defender", True, (255, 255, 255))
    start_text = option_font.render("Press 'S' to Start", True, (255, 255, 255))
    instructions_text = option_font.render("Press 'I' for Instructions", True, (255, 255, 255))
    quit_text = option_font.render("Press 'Q' to Quit", True, (255, 255, 255))
    
    while menu_running:
        window.fill((0, 0, 0))  # Black background
        window.blit(title_text, (win_width // 2 - title_text.get_width() // 2, 100))
        window.blit(start_text, (win_width // 2 - start_text.get_width() // 2, 300))
        window.blit(instructions_text, (win_width // 2 - instructions_text.get_width() // 2, 400))
        window.blit(quit_text, (win_width // 2 - quit_text.get_width() // 2, 500))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Start game
                    menu_running = False
                    reset_game()
                    current_bg_index = 0
                elif event.key == pygame.K_i:  # Show instructions
                    instructions_menu()
                elif event.key == pygame.K_q:  # Quit game
                    pygame.quit()
                    quit()

def play_bgm(index):
    """Plays the background music corresponding to the given index."""
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.stop()  # Stop current music
    pygame.mixer.music.load(bgm[index])  # Load the new music file
    pygame.mixer.music.play(-1)  # Loop the music indefinitely

def instructions_menu():
    menu_running = True
    instruction_font = pygame.font.SysFont("comicsans", 40)
    instructions = [
        "Instructions:",
        "Use W/A/S/D to move",
        "Press SPACE to shoot",
        "SHIFT to speed up, CTRL to slow down",
        "defend the city from enemies",
        "Press 'P' to pause the game",
    ]
    back_text = instruction_font.render("Press 'B' to Go Back", True, (255, 255, 255))
    
    while menu_running:
        window.fill((0, 0, 0))  # Black background
        for i, line in enumerate(instructions):
            instruction_text = instruction_font.render(line, True, (255, 255, 255))
            window.blit(instruction_text, (win_width // 2 - instruction_text.get_width() // 2, 100 + i * 50))
        window.blit(back_text, (win_width // 2 - back_text.get_width() // 2, 500))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:  # Back to start menu
                    menu_running = False

start_menu()

# Display the name of the first place when the game starts
display_place_name(place_names[current_bg_index])

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Shooting
                player.shooting = True
            if event.key == pygame.K_p:  # Pause game
                pause_game()
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            player.shooting = False

    # Change background based on score
    if score >= 1000 * (current_bg_index + 1):  # Adjusted threshold for faster transitions
        current_bg_index = (current_bg_index + 1) % len(backgrounds)
        fade_screen()  # Add fade effect here
        play_bgm(current_bg_index)  # Play the new BGM
        if current_bg_index < 3:
            display_place_name(place_names[current_bg_index])

    # Scroll active backgrounds
    for i in range(len(bg_offsets)):
        bg_offsets[i] -= bg_speed
        if bg_offsets[i] <= -backgrounds[current_bg_index].get_width():
            bg_offsets[i] = 0

    # Draw the active background
    window.blit(backgrounds[current_bg_index], (bg_offsets[current_bg_index], 0))
    window.blit(backgrounds[current_bg_index], (bg_offsets[current_bg_index] + backgrounds[current_bg_index].get_width(), 0))

    # Update objects
    player.update()
    player.bullets.update()
    enemies.update()   

    # Draw sprites and UI
    player.reset()
    player.bullets.draw(window)
    enemies.draw(window)
    draw_ui()

    # Collision handling
    collisions = pygame.sprite.groupcollide(player.bullets, enemies, True, False)
    for bullet, hit_enemies in collisions.items():
        for enemy in hit_enemies:
             # Trigger explosion
            explosion = Explosion(explosion_images, enemy.rect.centerx - 25, enemy.rect.centery - 25)
            enemies.add(explosion)
    
            if isinstance(enemy, BigEnemy):
                enemy.hit()
                if enemy.health <= 0:
                    score += 50
                    kills += 1
                    explosion_sound.set_volume(0.5)
                    explosion_sound.play()
            elif isinstance(enemy, Enemy):  # Regular enemy
                score += 50
                kills += 1
                explosion_sound.set_volume(0.5)
                explosion_sound.play()
            if hasattr(enemy, 'respawn') and callable(getattr(enemy, 'respawn', None)):
                enemy.respawn()


    # Check if an enemy has collided with the player
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            player.health -= 1
            if hasattr(enemy, 'respawn') and callable(getattr(enemy, 'respawn', None)):
                enemy.respawn()

    # Check for game over
    if check_game_over():
        running = False

    if game_finished():
        running = False

    # Update the display and control frame rate
    pygame.display.update()
    clock.tick(FPS)
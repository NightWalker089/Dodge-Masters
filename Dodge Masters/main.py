import pygame
import cv2
import random
import os

from objects import Player, Bar, Ball, Block, ScoreCard, Message, Particle, generate_particles

def capture_photo():
    """Capture a photo using the webcam."""
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Your Photo")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Your Photo", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Capture cancelled.")
            break
        elif k % 256 == 32:
            # SPACE pressed
            photo_path = "player_photo.png"
            cv2.imwrite(photo_path, frame)
            print(f"Photo saved at {photo_path}")
            break

    cam.release()
    cv2.destroyAllWindows()
    return photo_path

pygame.init()
SCREEN = WIDTH, HEIGHT = 512, 768  # Adjusted for PC view

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

pygame.display.set_caption("DODGE MASTERS")
clock = pygame.time.Clock()
FPS = 45

# COLORS
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (54, 69, 79)
c_list = [RED, BLACK, WHITE]

# Fonts
pygame.font.init()
score_font = pygame.font.Font('Fonts/BubblegumSans-Regular.ttf', 50)

# Sounds
coin_fx = pygame.mixer.Sound('Sounds/coin.mp3')
death_fx = pygame.mixer.Sound('Sounds/death.mp3')
move_fx = pygame.mixer.Sound('Sounds/move.mp3')

# Background Music
pygame.mixer.music.load('Sounds/BGM.mp3')  # Load your background music file
pygame.mixer.music.set_volume(0.5)  # Set default volume
pygame.mixer.music.play(-1)  # Loop indefinitely
music_muted = False

# Backgrounds
bg_list = []
for i in range(1, 5):
    ext = "png" if i == 2 else "png"
    img = pygame.image.load(f"Assets/Backgrounds/bg{i}.{ext}")
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    bg_list.append(img)

home_bg = pygame.image.load(f"Assets/Backgrounds/home.jpg")
home_bg = pygame.transform.scale(home_bg, (WIDTH, HEIGHT))  # Resize for new screen size
bg = home_bg

# Objects
bar_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()
destruct_group = pygame.sprite.Group()
win_particle_group = pygame.sprite.Group()
bar_gap = 180  # Adjusted gap for larger screen size

particles = []
p = Player(win)
score_card = ScoreCard(WIDTH // 2, 50, win)

# Startup menu
def startup_menu():
    """Displays the startup menu."""
    running = True
    photo_captured = False

    while running:
        win.blit(home_bg, (0, 0))
        title_font = pygame.font.Font("Fonts/Robus-BWqOd.otf", 50)
        title_text = title_font.render("Dodge Masters", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        win.blit(title_text, title_rect)

        instruction_font = pygame.font.Font("Fonts/DebugFreeTrial-MVdYB.otf", 25)
        instruction_text = instruction_font.render("Press SPACE to capture your photo to start", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    photo_path = capture_photo()
                    if photo_path:
                        p.image = pygame.image.load(photo_path)
                        p.image = pygame.transform.scale(p.image, (60, 60))  # Adjusted size for larger screen
                        photo_captured = True
                if photo_captured:
                    running = False

        pygame.display.update()
        clock.tick(FPS)

startup_menu()

# Variables
home_page = True
score_page = False
score = 0
high_score = 0
move_left = False
move_right = True
prev_x = 0
p_count = 0

# Main game loop
def show_score_page():
    """Display the score page with the player's icon and scores."""
    global score_page, home_page

    while score_page:
        win.blit(home_bg, (0, 0))

        font = "Fonts/BubblegumSans-Regular.ttf"
        if score < high_score:
            score_msg = Message(WIDTH // 2, 100, 55, "Score", font, WHITE, win)
        else:
            score_msg = Message(WIDTH // 2, 100, 55, "New High", font, WHITE, win)

        score_point = Message(WIDTH // 2, 160, 45, f"{score}", font, WHITE, win)
        score_msg.update()
        score_point.update()

        p.update()  # Show the player's icon

        instruction_font = pygame.font.Font("Fonts/DebugFreeTrial-MVdYB.otf", 25)
        instruction_text = instruction_font.render("Press SPACE to Restart", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        win.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    score_page = False
                    home_page = True

        pygame.display.update()
        clock.tick(FPS)

running = True
while running:
    win.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_m:  # Mute/Unmute music
                if music_muted:
                    pygame.mixer.music.set_volume(0.5)
                else:
                    pygame.mixer.music.set_volume(0.0)
                music_muted = not music_muted

        if event.type == pygame.MOUSEBUTTONDOWN and (home_page or score_page):
            home_page = False
            score_page = False
            win_particle_group.empty()

            bg = random.choice(bg_list)

            particles = []
            last_bar = pygame.time.get_ticks() - 1200
            next_bar = 0
            score = 0
            p_count = 0
            score_list = []

            for _ in range(15):
                x = random.randint(30, WIDTH - 30)
                y = random.randint(60, HEIGHT - 60)
                max = random.randint(8, 16)
                b = Block(x, y, max, win)
                block_group.add(b)

        if event.type == pygame.MOUSEBUTTONDOWN and not home_page:
            if p.rect.collidepoint(event.pos):
                touched = True
                x, y = event.pos
                offset_x = p.rect.x - x

        if event.type == pygame.MOUSEBUTTONUP and not home_page:
            touched = False

        if event.type == pygame.MOUSEMOTION and not home_page:
            if touched:
                x, y = event.pos
                if move_right and prev_x > x:
                    move_right = False
                    move_left = True
                    move_fx.play()
                if move_left and prev_x < x:
                    move_right = True
                    move_left = False
                    move_fx.play()

                prev_x = x
                p.rect.x = x + offset_x

    if home_page:
        bg = home_bg
        particles = generate_particles(p, particles, WHITE, win)
        p.update()

    elif score_page:
        show_score_page()

    else:
        next_bar = pygame.time.get_ticks()
        if next_bar - last_bar >= 1200:
            bwidth = random.choice([i for i in range(40, 150, 10)])

            b1prime = Bar(0, 0, bwidth + 3, GRAY, win)
            b1 = Bar(0, -3, bwidth, WHITE, win)

            b2prime = Bar(bwidth + bar_gap + 3, 0, WIDTH - bwidth - bar_gap, GRAY, win)
            b2 = Bar(bwidth + bar_gap, -3, WIDTH - bwidth - bar_gap, WHITE, win)

            bar_group.add(b1prime)
            bar_group.add(b1)
            bar_group.add(b2prime)
            bar_group.add(b2)

            color = random.choice(["red", "white"])
            pos = random.choice([0, 1])
            if pos == 0:
                x = bwidth + 12
            elif pos == 1:
                x = bwidth + bar_gap - 12
            ball = Ball(x, 10, 1, color, win)

            ball_group.add(ball)
            last_bar = next_bar

        for ball in ball_group:
            if ball.rect.colliderect(p):
                if ball.color == "white":
                    ball.kill()
                    coin_fx.play()
                    score += 1
                    if score > high_score:
                        high_score = score
                    score_card.animate = True
                elif ball.color == "red":
                    death_fx.play()
                    

                    score_page = True
                    break

        if pygame.sprite.spritecollide(p, bar_group, False):
            death_fx.play()
            

            score_page = True

        block_group.update()
        bar_group.update(4)
        ball_group.update(4)

        destruct_group.update()
        score_card.update(score)

        particles = generate_particles(p, particles, WHITE, win)
        p.update()

        if score and score % 10 == 0:
            rem = score // 10
            if rem not in score_list:
                score_list.append(rem)

    clock.tick(FPS)
    pygame.display.update()

pygame.quit()

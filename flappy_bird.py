import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 880, 414
BIRD_WIDTH, BIRD_HEIGHT = 60, 60
PIPE_WIDTH, PIPE_HEIGHT, PIPE_GAP = 170, 180, 200
GRAVITY, BIRD_JUMP = 0.008, -0.5
BACKGROUND_COLOR, BIRD_COLOR, PIPE_COLOR = (135, 206, 235), (255, 215, 0), (0, 128, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

bird_image = pygame.image.load("images/bird1.png")
bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))

background_image = pygame.image.load("images/flappy-background.png")

pipe_image = pygame.image.load("images/pipe.png")
pipe_image = pygame.transform.scale(pipe_image, (PIPE_WIDTH, HEIGHT))
flipped_pipe_image = pygame.transform.flip(pipe_image, False, True)

hit_sound = pygame.mixer.Sound("sounds/hit.wav")
point_sound = pygame.mixer.Sound("sounds/point.wav")
flap_sound = pygame.mixer.Sound("sounds/swoosh.wav")

bird_x, bird_y, bird_velocity = WIDTH // 4, HEIGHT // 2 - BIRD_HEIGHT // 2, 0
pipes, pipe_velocity, pipe_spawn_timer = [], -1, time.time()
MAX_PIPES = 3

FPS, fixed_time_step, accumulated_time = 60, 1 / 60, 0
font, game_over_font = pygame.font.Font(None, 36), pygame.font.Font(None, 48)
game_started, game_over, previous_time, score = False, False, time.time(), 0


def draw_bird(x, y):
    screen.blit(bird_image, (x, y))


def draw_score():
    score_display = font.render(f"{score}", True, (255, 255, 255))
    score_rect = score_display.get_rect()
    score_rect.topleft = (WIDTH // 2 - score_rect.width // 2, 10)

    # score outline
    outline_thickness = 2
    score_outline = font.render(f"{score}", True, (0, 0, 0))
    screen.blit(score_outline, (score_rect.left - outline_thickness, score_rect.top))
    screen.blit(score_outline, (score_rect.left + outline_thickness, score_rect.top))
    screen.blit(score_outline, (score_rect.left, score_rect.top - outline_thickness))
    screen.blit(score_outline, (score_rect.left, score_rect.top + outline_thickness))

    screen.blit(score_display, score_rect)


def start_screen():
    screen.blit(background_image, (0, 0))
    text = font.render("Press SPACE to start", True, (0, 0, 0))
    screen.blit(text, (WIDTH // 6, HEIGHT // 3))
    bird_x = WIDTH // 4
    bird_y = HEIGHT // 2 - BIRD_HEIGHT // 2
    draw_bird(bird_x, bird_y)
    draw_score()
    pygame.display.update()


def reset_game():
    global bird_y, bird_velocity, pipes, score, game_started
    bird_y, bird_velocity, pipes, score, game_started = HEIGHT // 2 - BIRD_HEIGHT // 2, 0, [], 0, True


# Game Start
start_screen()

bird_falling, bird_fall_timer, ready_to_jump = False, 0, False

# Game Loop
while True:
    current_time = time.time()
    elapsed_time = current_time - previous_time
    previous_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not game_started:
                game_over, game_started, ready_to_jump = False, True, True
                reset_game()
                flap_sound.play()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and ready_to_jump:
                bird_velocity = BIRD_JUMP

    if not game_started or game_over:
        continue

    if ready_to_jump:
        bird_velocity += GRAVITY
        bird_y += bird_velocity

    if bird_y > HEIGHT:
        hit_sound.play()
        game_over = True
        game_started = False

    if current_time - pipe_spawn_timer >= 2:
        if len(pipes) < MAX_PIPES:
            pipe_x = WIDTH
            gap = random.randint(100, HEIGHT - PIPE_GAP - 100)
            pipes.append((pipe_x, gap))
        pipe_spawn_timer = current_time

    for i, (pipe_x, gap) in enumerate(pipes):
        pipes[i] = (pipe_x + pipe_velocity, gap)
        if bird_x == pipe_x:
            point_sound.play()
            score += 1
        if pipe_x < -PIPE_WIDTH:
            pipes.pop(i)
        if bird_x < pipe_x + PIPE_WIDTH and bird_x + BIRD_WIDTH > pipe_x:
            if bird_y < gap or bird_y + BIRD_HEIGHT > gap + PIPE_GAP:
                hit_sound.play()
                game_over = True
                game_started = False
                ready_to_jump = False

    screen.blit(background_image, (0, 0))
    draw_bird(bird_x, bird_y)

    for pipe_x, gap in pipes:
        screen.blit(flipped_pipe_image, (pipe_x, gap - pipe_image.get_height()))
        screen.blit(pipe_image, (pipe_x, gap + PIPE_GAP))

    draw_score()

    if game_over:
        start_screen()
        ready_to_jump = False

    pygame.display.update()

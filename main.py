import random
import sys

import pygame

from games import BreakoutGame, PongGame, SnakeGame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Games")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)
tiny_font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 88)
title_font = pygame.font.Font(None, 92)

COLORS = {
    "sky_top": (244, 251, 255),
    "sky_bottom": (224, 239, 255),
    "panel": (255, 255, 255),
    "panel_soft": (245, 249, 255),
    "panel_border": (184, 209, 240),
    "ink": (36, 55, 95),
    "ink_soft": (92, 116, 160),
    "player": (49, 168, 255),
    "cpu": (255, 109, 161),
    "ball": (255, 204, 87),
    "ball_glow": (255, 238, 176),
    "ball_outline": (36, 55, 95),
    "accent": (255, 194, 76),
    "accent_dark": (216, 135, 27),
    "snake_body": (93, 214, 187),
    "divider": (175, 198, 255),
    "mint": (173, 239, 221),
    "lavender": (215, 205, 255),
}
BRICK_COLORS = [(255, 126, 163), (255, 174, 89), (255, 214, 102), (106, 214, 173)]

state = "menu"
active_game = "pong"
game_over_message = ""
selected_setup = "pong"
particles = []
shake_timer = 0.0

SETUP_OPTIONS = {
    "pong": {
        "title": "Pong Setup",
        "subtitle": "Pick your match style",
        "options": [
            ("1", "Easy CPU", "Relaxed rallies, slower tracking"),
            ("2", "Medium CPU", "Balanced back-and-forth"),
            ("3", "Hard CPU", "Fast, punishing returns"),
            ("4", "Vs Player", "Left paddle W/S, right paddle arrows"),
        ],
    },
    "snake": {
        "title": "Snake Setup",
        "subtitle": "Choose the pace",
        "options": [
            ("1", "Chill", "More breathing room between turns"),
            ("2", "Classic", "Arcade baseline speed"),
            ("3", "Turbo", "Sharper, faster runs"),
        ],
    },
    "breakout": {
        "title": "Breakout Setup",
        "subtitle": "Choose the challenge",
        "options": [
            ("1", "Zen", "More lives and a wider paddle"),
            ("2", "Classic", "Standard balance"),
            ("3", "Rush", "Fewer lives, smaller paddle, faster ball"),
        ],
    },
}


def spawn_particles(x, y, color):
    global shake_timer
    shake_timer = 0.18
    for _ in range(12):
        particles.append(
            [[x, y], [random.uniform(-160, 160), random.uniform(-160, 160)], random.randint(2, 5), color]
        )


def update_particles(dt):
    for particle in particles[:]:
        particle[0][0] += particle[1][0] * dt
        particle[0][1] += particle[1][1] * dt
        particle[2] -= 8 * dt
        if particle[2] <= 0:
            particles.remove(particle)


pong = PongGame(WIDTH, HEIGHT, font, small_font, COLORS, spawn_particles)
snake = SnakeGame(WIDTH, HEIGHT, font, COLORS, spawn_particles)
breakout = BreakoutGame(WIDTH, HEIGHT, font, COLORS, BRICK_COLORS, spawn_particles)
games = {"pong": pong, "snake": snake, "breakout": breakout}


def center_text(text, text_font, color, y):
    surface = text_font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def draw_wrapped_text(text, text_font, color, x, y, max_width, line_gap):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_font.size(trial)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    for index, line in enumerate(lines):
        surface = text_font.render(line, True, color)
        screen.blit(surface, (x, y + index * line_gap))


def draw_background():
    for y in range(HEIGHT):
        progress = y / HEIGHT
        color = (
            int(COLORS["sky_top"][0] * (1 - progress) + COLORS["sky_bottom"][0] * progress),
            int(COLORS["sky_top"][1] * (1 - progress) + COLORS["sky_bottom"][1] * progress),
            int(COLORS["sky_top"][2] * (1 - progress) + COLORS["sky_bottom"][2] * progress),
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    pygame.draw.circle(screen, COLORS["mint"], (120, 110), 120)
    pygame.draw.circle(screen, COLORS["lavender"], (690, 100), 105)
    pygame.draw.circle(screen, (255, 230, 170), (740, 520), 145)
    pygame.draw.circle(screen, (204, 238, 255), (90, 520), 130)

    panel_rect = pygame.Rect(44, 36, WIDTH - 88, HEIGHT - 72)
    shadow_rect = panel_rect.move(0, 10)
    pygame.draw.rect(screen, (205, 221, 245), shadow_rect, border_radius=34)
    pygame.draw.rect(screen, COLORS["panel"], panel_rect, border_radius=34)
    pygame.draw.rect(screen, COLORS["panel_border"], panel_rect, 3, border_radius=34)


def start_game(game_name):
    global active_game, state, game_over_message
    active_game = game_name
    game_over_message = ""
    games[game_name].reset()
    state = "play"


def set_game_over(message):
    global state, game_over_message
    game_over_message = message
    state = "game_over"


def open_setup(game_name):
    global selected_setup, state
    selected_setup = game_name
    state = "setup"


def apply_setup_choice(choice):
    if selected_setup == "pong":
        if choice == pygame.K_1:
            pong.set_difficulty("Easy")
            pong.reset("cpu")
            start_game("pong")
        elif choice == pygame.K_2:
            pong.set_difficulty("Medium")
            pong.reset("cpu")
            start_game("pong")
        elif choice == pygame.K_3:
            pong.set_difficulty("Hard")
            pong.reset("cpu")
            start_game("pong")
        elif choice == pygame.K_4:
            pong.reset("player")
            start_game("pong")
    elif selected_setup == "snake":
        if choice == pygame.K_1:
            snake.set_preset("Chill")
            start_game("snake")
        elif choice == pygame.K_2:
            snake.set_preset("Classic")
            start_game("snake")
        elif choice == pygame.K_3:
            snake.set_preset("Turbo")
            start_game("snake")
    elif selected_setup == "breakout":
        if choice == pygame.K_1:
            breakout.set_preset("Zen")
            start_game("breakout")
        elif choice == pygame.K_2:
            breakout.set_preset("Classic")
            start_game("breakout")
        elif choice == pygame.K_3:
            breakout.set_preset("Rush")
            start_game("breakout")


def draw_home_card(x, y, width, height, accent, number, title, body):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, COLORS["panel_soft"], rect, border_radius=24)
    pygame.draw.rect(screen, accent, rect, 3, border_radius=24)
    bubble = pygame.Rect(x + 18, y + 18, 42, 42)
    pygame.draw.ellipse(screen, accent, bubble)
    num_surface = small_font.render(number, True, COLORS["panel"])
    screen.blit(num_surface, num_surface.get_rect(center=bubble.center))
    title_surface = font.render(title, True, COLORS["ink"])
    screen.blit(title_surface, (x + 18, y + 76))
    draw_wrapped_text(body, tiny_font, COLORS["ink_soft"], x + 18, y + 122, width - 36, 22)


def draw_menu():
    center_text("Arcade Daydream", title_font, COLORS["ink"], 118)
    center_text("Pick a game, then tune it on the next screen.", small_font, COLORS["ink_soft"], 170)

    draw_home_card(70, 225, 200, 170, COLORS["player"], "1", "Pong", "Snappy rallies and versus play")
    draw_home_card(300, 225, 200, 170, COLORS["accent"], "2", "Snake", "Choose a pace and chase score")
    draw_home_card(530, 225, 200, 170, COLORS["cpu"], "3", "Breakout", "Colorful bricks and paddle angles")

    center_text("Press 1, 2, or 3", font, COLORS["ink"], 455)
    center_text("Q quits from anywhere", small_font, COLORS["ink_soft"], 500)


def draw_setup():
    config = SETUP_OPTIONS[selected_setup]
    center_text(config["title"], big_font, COLORS["ink"], 118)
    center_text(config["subtitle"], small_font, COLORS["ink_soft"], 164)

    card_y = 198
    for index, (key_label, title, description) in enumerate(config["options"]):
        rect = pygame.Rect(110, card_y + index * 84, 580, 64)
        border = [COLORS["player"], COLORS["accent"], COLORS["cpu"], COLORS["lavender"]][index % 4]
        pygame.draw.rect(screen, COLORS["panel_soft"], rect, border_radius=22)
        pygame.draw.rect(screen, border, rect, 3, border_radius=22)

        key_surface = font.render(key_label, True, border if isinstance(border, tuple) else COLORS["ink"])
        title_surface = font.render(title, True, COLORS["ink"])
        desc_surface = small_font.render(description, True, COLORS["ink_soft"])

        screen.blit(key_surface, (132, rect.y + 13))
        screen.blit(title_surface, (190, rect.y + 7))
        screen.blit(desc_surface, (190, rect.y + 35))

    center_text("ESC returns to the game picker", small_font, COLORS["ink_soft"], 552)


def draw_pause():
    overlay = pygame.Rect(180, 188, 440, 180)
    pygame.draw.rect(screen, (255, 255, 255), overlay, border_radius=26)
    pygame.draw.rect(screen, COLORS["panel_border"], overlay, 3, border_radius=26)
    center_text("Paused", big_font, COLORS["ink"], 250)
    center_text("P resumes", font, COLORS["ink"], 304)
    center_text("ESC returns to the menu", small_font, COLORS["ink_soft"], 344)


def draw_game_over():
    center_text("Game Over", big_font, COLORS["ink"], 182)
    center_text(game_over_message, font, COLORS["accent_dark"], 264)
    center_text("Press any key to head back to the menu", small_font, COLORS["ink_soft"], 332)


running = True
while running:
    dt = clock.tick(120) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_ESCAPE:
                if state == "menu":
                    pygame.quit()
                    sys.exit()
                if state in ("setup", "pause", "game_over"):
                    state = "menu"
                elif state == "play":
                    state = "pause"
                continue

            if state == "menu":
                if event.key == pygame.K_1:
                    open_setup("pong")
                elif event.key == pygame.K_2:
                    open_setup("snake")
                elif event.key == pygame.K_3:
                    open_setup("breakout")
                continue

            if state == "setup":
                apply_setup_choice(event.key)
                continue

            if event.key == pygame.K_p and state == "play":
                state = "pause"
                continue
            if event.key == pygame.K_p and state == "pause":
                state = "play"
                continue

            if state == "game_over":
                state = "menu"
                continue

            if state == "play" and active_game == "snake":
                snake.handle_keydown(event.key)

    if state == "play":
        keys = pygame.key.get_pressed()
        if active_game == "pong":
            message = pong.update(dt, keys)
        elif active_game == "snake":
            message = snake.update(dt)
        else:
            message = breakout.update(dt, keys)
        if message:
            set_game_over(message)

    update_particles(dt)

    offset_x = 0
    offset_y = 0
    if shake_timer > 0:
        shake_timer -= dt
        offset_x = random.randint(-4, 4)
        offset_y = random.randint(-4, 4)

    draw_background()

    if state == "menu":
        draw_menu()
    elif state == "setup":
        draw_setup()
    elif state == "play":
        if active_game == "pong":
            pong.draw(screen, offset_x, offset_y)
        elif active_game == "snake":
            snake.draw(screen)
        else:
            breakout.draw(screen)
    elif state == "pause":
        if active_game == "pong":
            pong.draw(screen)
        elif active_game == "snake":
            snake.draw(screen)
        else:
            breakout.draw(screen)
        draw_pause()
    elif state == "game_over":
        draw_game_over()

    for particle in particles:
        pygame.draw.circle(
            screen,
            particle[3],
            (int(particle[0][0]) + offset_x, int(particle[0][1]) + offset_y),
            max(1, int(particle[2])),
        )

    pygame.display.flip()

pygame.quit()

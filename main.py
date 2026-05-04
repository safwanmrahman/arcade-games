import random
import sys

import pygame

from games import BreakoutGame, PongGame, SnakeGame, SpaceInvadersGame, SudokuGame

pygame.init()

WIDTH, HEIGHT = 1100, 860
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
CARD_COLORS = [COLORS["player"], COLORS["accent"], COLORS["cpu"], COLORS["lavender"], COLORS["divider"]]
MENU_KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]

GAME_DEFS = {
    "pong": {
        "title": "Pong",
        "body": "Snappy rallies and versus play",
        "accent": COLORS["player"],
        "setup_title": "Pong Setup",
        "setup_subtitle": "Pick your match style",
        "options": [
            ("1", "Easy CPU", "Relaxed rallies, slower tracking"),
            ("2", "Medium CPU", "Balanced back-and-forth"),
            ("3", "Hard CPU", "Fast, punishing returns"),
            ("4", "Vs Player", "Left paddle W/S, right paddle arrows"),
        ],
    },
    "snake": {
        "title": "Snake",
        "body": "Choose a pace and chase score",
        "accent": COLORS["accent"],
        "setup_title": "Snake Setup",
        "setup_subtitle": "Choose the pace",
        "options": [
            ("1", "Chill", "More breathing room between turns"),
            ("2", "Classic", "Arcade baseline speed"),
            ("3", "Turbo", "Sharper, faster runs"),
        ],
    },
    "breakout": {
        "title": "Breakout",
        "body": "Colorful bricks and paddle angles",
        "accent": COLORS["cpu"],
        "setup_title": "Breakout Setup",
        "setup_subtitle": "Choose the challenge",
        "options": [
            ("1", "Zen", "More lives and a wider paddle"),
            ("2", "Classic", "Standard balance"),
            ("3", "Rush", "Fewer lives, smaller paddle, faster ball"),
        ],
    },
    "sudoku": {
        "title": "Sudoku",
        "body": "Classic 9x9 logic board",
        "accent": COLORS["lavender"],
        "setup_title": "Sudoku Setup",
        "setup_subtitle": "Classic 9x9 board, three puzzle styles",
        "options": [
            ("1", "Easy", "More starting clues for a gentler solve"),
            ("2", "Medium", "Balanced clue count and deduction"),
            ("3", "Hard", "Fewer clues and tougher logic chains"),
        ],
    },
    "space_invaders": {
        "title": "Space Invaders",
        "body": "Clear the wave and dodge return fire",
        "accent": COLORS["divider"],
        "setup_title": "Invaders Setup",
        "setup_subtitle": "Tune the incoming wave",
        "options": [
            ("1", "Cadet", "More lives and slower enemy volleys"),
            ("2", "Arcade", "Classic pace and pressure"),
            ("3", "Elite", "Sharper waves and faster return fire"),
        ],
    },
}
GAME_ORDER = list(GAME_DEFS)

state = "menu"
active_game = "pong"
game_over_message = ""
selected_setup = "pong"
particles = []
shake_timer = 0.0


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


games = {
    "pong": PongGame(WIDTH, HEIGHT, font, small_font, COLORS, spawn_particles),
    "snake": SnakeGame(WIDTH, HEIGHT, font, COLORS, spawn_particles),
    "breakout": BreakoutGame(WIDTH, HEIGHT, font, COLORS, BRICK_COLORS, spawn_particles),
    "sudoku": SudokuGame(WIDTH, HEIGHT, font, small_font, COLORS, spawn_particles),
    "space_invaders": SpaceInvadersGame(WIDTH, HEIGHT, font, small_font, COLORS, spawn_particles),
}


def center_text(text, text_font, color, y):
    surface = text_font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def center_text_in_rect(text, text_font, color, rect):
    surface = text_font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=rect.center))


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


def option_index_from_key(key, options):
    option_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
    for index, option_key in enumerate(option_keys[: len(options)]):
        if key == option_key:
            return index
    return None


def apply_setup_choice(choice):
    index = option_index_from_key(choice, GAME_DEFS[selected_setup]["options"])
    if index is None:
        return

    if selected_setup == "pong":
        pong = games["pong"]
        if index < 3:
            pong.set_difficulty(["Easy", "Medium", "Hard"][index])
            pong.reset("cpu")
        else:
            pong.reset("player")
        start_game("pong")
        return

    preset_lookup = {
        "snake": ["Chill", "Classic", "Turbo"],
        "breakout": ["Zen", "Classic", "Rush"],
        "sudoku": ["Easy", "Medium", "Hard"],
        "space_invaders": ["Cadet", "Arcade", "Elite"],
    }
    games[selected_setup].set_preset(preset_lookup[selected_setup][index])
    start_game(selected_setup)


def draw_home_card(x, y, width, height, accent, number, title, body):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, COLORS["panel_soft"], rect, border_radius=24)
    pygame.draw.rect(screen, accent, rect, 3, border_radius=24)
    bubble = pygame.Rect(x + 18, y + 18, 42, 42)
    pygame.draw.ellipse(screen, accent, bubble)
    num_surface = small_font.render(number, True, COLORS["panel"])
    screen.blit(num_surface, num_surface.get_rect(center=bubble.center))
    title_surface = font.render(title, True, COLORS["ink"])
    screen.blit(title_surface, (x + 18, y + 68))
    draw_wrapped_text(body, tiny_font, COLORS["ink_soft"], x + 18, y + 108, width - 36, 18)


def draw_menu():
    center_text("Arcade Daydream", title_font, COLORS["ink"], 118)
    center_text("Pick a game, then tune it on the next screen.", small_font, COLORS["ink_soft"], 170)

    card_width = 300
    card_height = 150
    col_gap = 60
    row_gap = 24
    total_width = card_width * 2 + col_gap
    start_x = (WIDTH - total_width) // 2
    start_y = 210
    positions = [
        (start_x, start_y),
        (start_x + card_width + col_gap, start_y),
        (start_x, start_y + card_height + row_gap),
        (start_x + card_width + col_gap, start_y + card_height + row_gap),
        (WIDTH // 2 - card_width // 2, start_y + (card_height + row_gap) * 2),
    ]

    for index, game_name in enumerate(GAME_ORDER):
        config = GAME_DEFS[game_name]
        x, y = positions[index]
        draw_home_card(x, y, card_width, card_height, config["accent"], str(index + 1), config["title"], config["body"])

    footer_y = positions[-1][1] + card_height + 52
    center_text("Press 1, 2, 3, 4, or 5", font, COLORS["ink"], footer_y)
    center_text("Q quits from anywhere", small_font, COLORS["ink_soft"], footer_y + 32)


def draw_setup():
    config = GAME_DEFS[selected_setup]
    center_text(config["setup_title"], big_font, COLORS["ink"], 118)
    center_text(config["setup_subtitle"], small_font, COLORS["ink_soft"], 164)

    card_width = 760
    card_x = (WIDTH - card_width) // 2
    card_y = 198
    for index, (key_label, title, description) in enumerate(config["options"]):
        rect = pygame.Rect(card_x, card_y + index * 84, card_width, 64)
        border = CARD_COLORS[index % len(CARD_COLORS)]
        pygame.draw.rect(screen, COLORS["panel_soft"], rect, border_radius=22)
        pygame.draw.rect(screen, border, rect, 3, border_radius=22)

        key_surface = font.render(key_label, True, border)
        title_surface = font.render(title, True, COLORS["ink"])
        desc_surface = small_font.render(description, True, COLORS["ink_soft"])

        screen.blit(key_surface, (rect.x + 22, rect.y + 13))
        screen.blit(title_surface, (rect.x + 120, rect.y + 7))
        screen.blit(desc_surface, (rect.x + 120, rect.y + 35))

    center_text("ESC returns to the game picker", small_font, COLORS["ink_soft"], 552)


def draw_pause():
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((255, 255, 255, 125))
    screen.blit(veil, (0, 0))

    overlay = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 120, 500, 240)
    shadow = overlay.move(0, 12)
    pygame.draw.rect(screen, (203, 217, 241), shadow, border_radius=30)
    pygame.draw.rect(screen, (255, 255, 255), overlay, border_radius=30)
    pygame.draw.rect(screen, COLORS["panel_border"], overlay, 3, border_radius=30)

    title_rect = pygame.Rect(overlay.x, overlay.y + 40, overlay.width, 58)
    resume_rect = pygame.Rect(overlay.x, overlay.y + 118, overlay.width, 40)
    detail_rect = pygame.Rect(overlay.x, overlay.y + 172, overlay.width, 28)
    center_text_in_rect("Paused", big_font, COLORS["ink"], title_rect)
    center_text_in_rect("P resumes", font, COLORS["ink"], resume_rect)
    center_text_in_rect("ESC returns to the menu", small_font, COLORS["ink_soft"], detail_rect)


def draw_game_over():
    center_text("Game Over", big_font, COLORS["ink"], 182)
    center_text(game_over_message, font, COLORS["accent_dark"], 264)
    center_text("Press any key to head back to the menu", small_font, COLORS["ink_soft"], 332)


def handle_menu_key(key):
    for index, menu_key in enumerate(MENU_KEYS[: len(GAME_ORDER)]):
        if key == menu_key:
            open_setup(GAME_ORDER[index])
            return


def handle_play_keydown(event):
    if active_game == "snake":
        games["snake"].handle_keydown(event.key)
    elif active_game == "sudoku":
        message = games["sudoku"].handle_keydown(event.key, event.unicode)
        if message:
            set_game_over(message)
    elif active_game == "space_invaders":
        games["space_invaders"].handle_keydown(event.key)


def update_active_game(dt, keys):
    if active_game == "pong":
        return games["pong"].update(dt, keys)
    if active_game == "snake":
        return games["snake"].update(dt)
    if active_game == "breakout":
        return games["breakout"].update(dt, keys)
    if active_game == "space_invaders":
        return games["space_invaders"].update(dt, keys)
    return games["sudoku"].update(dt)


def draw_active_game(offset_x=0, offset_y=0):
    if active_game == "pong":
        games["pong"].draw(screen, offset_x, offset_y)
    else:
        games[active_game].draw(screen)


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
                handle_menu_key(event.key)
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

            if state == "play":
                handle_play_keydown(event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "play" and active_game == "sudoku":
                games["sudoku"].handle_mouse(event.pos)

    if state == "play":
        keys = pygame.key.get_pressed()
        message = update_active_game(dt, keys)
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
        draw_active_game(offset_x, offset_y)
    elif state == "pause":
        draw_active_game()
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

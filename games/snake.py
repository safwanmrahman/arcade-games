import random

import pygame


class SnakeGame:
    name = "snake"

    def __init__(self, width, height, font, colors, spawn_particles):
        self.width = width
        self.height = height
        self.font = font
        self.colors = colors
        self.spawn_particles = spawn_particles
        self.grid_size = 20
        self.grid_width = width // self.grid_size
        self.grid_height = height // self.grid_size
        self.snake = []
        self.previous_snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (0, 0)
        self.score = 0
        self.move_timer = 0.0
        self.step_time = 0.12
        self.speed_label = "Classic"
        self.presets = {
            "Chill": 0.16,
            "Classic": 0.12,
            "Turbo": 0.09,
        }
        self.reset()

    def random_open_cell(self):
        occupied = set(self.snake)
        choices = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in occupied
        ]
        return random.choice(choices)

    def reset(self):
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        self.previous_snake = list(self.snake)
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.random_open_cell()
        self.score = 0
        self.move_timer = 0.0

    def set_preset(self, label):
        self.speed_label = label
        self.step_time = self.presets[label]

    def handle_keydown(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.next_direction = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.next_direction = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.next_direction = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.next_direction = (1, 0)

    def update(self, dt):
        self.move_timer += dt
        while self.move_timer >= self.step_time:
            self.move_timer -= self.step_time
            self.previous_snake = list(self.snake)
            proposed = self.next_direction
            if proposed[0] != -self.direction[0] or proposed[1] != -self.direction[1]:
                self.direction = proposed

            head_x, head_y = self.snake[0]
            next_head = (head_x + self.direction[0], head_y + self.direction[1])

            if (
                next_head[0] < 0
                or next_head[0] >= self.grid_width
                or next_head[1] < 0
                or next_head[1] >= self.grid_height
                or next_head in self.snake[:-1]
            ):
                return f"Snake crashed at {self.score} points"

            self.snake.insert(0, next_head)
            if next_head == self.food:
                self.score += 1
                if len(self.snake) == self.grid_width * self.grid_height:
                    return f"Snake cleared the board with {self.score} points"
                self.food = self.random_open_cell()
                self.spawn_particles(
                    next_head[0] * self.grid_size + self.grid_size // 2,
                    next_head[1] * self.grid_size + self.grid_size // 2,
                    self.colors["accent"],
                )
            else:
                self.snake.pop()
        return None

    def draw(self, screen):
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(screen, (203, 228, 255), (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(screen, (203, 228, 255), (0, y), (self.width, y))

        food_rect = pygame.Rect(
            self.food[0] * self.grid_size,
            self.food[1] * self.grid_size,
            self.grid_size,
            self.grid_size,
        )
        pygame.draw.rect(screen, self.colors["accent"], food_rect.inflate(-4, -4), border_radius=6)

        progress = min(1.0, self.move_timer / self.step_time) if self.step_time else 1.0
        previous = list(self.previous_snake)
        if len(previous) < len(self.snake) and previous:
            previous.extend([previous[-1]] * (len(self.snake) - len(previous)))

        for index, segment in enumerate(self.snake):
            previous_segment = previous[index] if index < len(previous) else segment
            draw_x = previous_segment[0] + (segment[0] - previous_segment[0]) * progress
            draw_y = previous_segment[1] + (segment[1] - previous_segment[1]) * progress
            rect = pygame.Rect(
                int(draw_x * self.grid_size),
                int(draw_y * self.grid_size),
                self.grid_size,
                self.grid_size,
            ).inflate(-3, -3)
            color = self.colors["player"] if index == 0 else self.colors["snake_body"]
            pygame.draw.rect(screen, color, rect, border_radius=5)

        screen.blit(self.font.render(f"Snake Score: {self.score}", True, self.colors["ink"]), (20, 18))
        screen.blit(self.font.render(self.speed_label, True, self.colors["accent_dark"]), (self.width - 150, 18))

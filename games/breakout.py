import math
import random

import pygame


class BreakoutGame:
    name = "breakout"

    def __init__(self, width, height, font, colors, brick_colors, spawn_particles):
        self.width = width
        self.height = height
        self.font = font
        self.colors = colors
        self.brick_colors = brick_colors
        self.spawn_particles = spawn_particles
        self.header_height = 72
        self.paddle = pygame.Rect(width // 2 - 60, height - 45, 120, 14)
        self.ball = pygame.Rect(0, 0, 14, 14)
        self.ball_pos = [width / 2, height - 70]
        self.ball_velocity = [0.0, 0.0]
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.preset = "Classic"
        self.starting_lives = 3
        self.base_ball_speed = 280
        self.paddle_width = 120
        self.reset()

    def build_bricks(self):
        bricks = []
        rows = 5
        cols = 10
        margin_x = 56
        top = self.header_height + 20
        gap = 8
        brick_width = 62
        brick_height = 22
        for row in range(rows):
            for col in range(cols):
                x = margin_x + col * (brick_width + gap)
                y = top + row * (brick_height + gap)
                bricks.append(
                    {
                        "rect": pygame.Rect(x, y, brick_width, brick_height),
                        "color": self.brick_colors[row % len(self.brick_colors)],
                    }
                )
        return bricks

    def reset_ball(self):
        self.ball_pos = [self.paddle.centerx, self.paddle.top - 16]
        self.ball_velocity = [random.choice([-230, 230]), -self.base_ball_speed]
        self.ball.center = (int(self.ball_pos[0]), int(self.ball_pos[1]))

    def reset(self):
        self.bricks = self.build_bricks()
        self.score = 0
        self.lives = self.starting_lives
        self.paddle.width = self.paddle_width
        self.paddle.centerx = self.width // 2
        self.reset_ball()

    def set_preset(self, label):
        self.preset = label
        if label == "Zen":
            self.starting_lives = 5
            self.base_ball_speed = 250
            self.paddle_width = 140
        elif label == "Classic":
            self.starting_lives = 3
            self.base_ball_speed = 280
            self.paddle_width = 120
        else:
            self.starting_lives = 2
            self.base_ball_speed = 320
            self.paddle_width = 104

    def update(self, dt, keys):
        move_dir = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dir -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dir += 1
        self.paddle.x += int(move_dir * 430 * dt)
        self.paddle.x = max(16, min(self.paddle.x, self.width - self.paddle.width - 16))

        self.ball_pos[0] += self.ball_velocity[0] * dt
        self.ball_pos[1] += self.ball_velocity[1] * dt
        self.ball.center = (int(self.ball_pos[0]), int(self.ball_pos[1]))

        if self.ball.left <= 0:
            self.ball.left = 0
            self.ball_pos[0] = self.ball.centerx
            self.ball_velocity[0] = abs(self.ball_velocity[0])
        elif self.ball.right >= self.width:
            self.ball.right = self.width
            self.ball_pos[0] = self.ball.centerx
            self.ball_velocity[0] = -abs(self.ball_velocity[0])

        if self.ball.top <= self.header_height:
            self.ball.top = self.header_height
            self.ball_pos[1] = self.ball.centery
            self.ball_velocity[1] = abs(self.ball_velocity[1])

        if self.ball.colliderect(self.paddle) and self.ball_velocity[1] > 0:
            relative = (self.ball.centerx - self.paddle.centerx) / (self.paddle.width / 2)
            speed = min(420, math.hypot(*self.ball_velocity) + 10)
            self.ball_velocity[0] = speed * relative
            self.ball_velocity[1] = -max(220, speed * (1 - abs(relative) * 0.35))
            self.ball.bottom = self.paddle.top
            self.ball_pos[0], self.ball_pos[1] = self.ball.centerx, self.ball.centery

        hit_index = self.ball.collidelist([brick["rect"] for brick in self.bricks])
        if hit_index != -1:
            brick = self.bricks.pop(hit_index)
            self.score += 10
            self.spawn_particles(brick["rect"].centerx, brick["rect"].centery, brick["color"])

            overlap_left = self.ball.right - brick["rect"].left
            overlap_right = brick["rect"].right - self.ball.left
            overlap_top = self.ball.bottom - brick["rect"].top
            overlap_bottom = brick["rect"].bottom - self.ball.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap in (overlap_left, overlap_right):
                self.ball_velocity[0] *= -1
            else:
                self.ball_velocity[1] *= -1

        if self.ball.top > self.height:
            self.lives -= 1
            if self.lives <= 0:
                return f"Breakout over at {self.score} points"
            self.reset_ball()

        if not self.bricks:
            return f"You cleared Breakout with {self.score} points"
        return None

    def draw(self, screen):
        screen.fill((255, 247, 239))
        pygame.draw.rect(screen, (255, 236, 218), pygame.Rect(0, 0, self.width, self.header_height))
        pygame.draw.line(screen, (247, 212, 183), (0, self.header_height), (self.width, self.header_height), 2)
        for brick in self.bricks:
            pygame.draw.rect(screen, brick["color"], brick["rect"], border_radius=6)
        pygame.draw.rect(screen, self.colors["player"], self.paddle, border_radius=7)
        pygame.draw.circle(screen, self.colors["ink"], self.ball.center, 7)
        screen.blit(self.font.render(f"Score: {self.score}", True, self.colors["ink"]), (20, 18))
        heart_color = (255, 96, 132)
        heart_center_x = 668
        heart_center_y = 31
        pygame.draw.circle(screen, heart_color, (heart_center_x - 6, heart_center_y - 4), 6)
        pygame.draw.circle(screen, heart_color, (heart_center_x + 6, heart_center_y - 4), 6)
        pygame.draw.polygon(
            screen,
            heart_color,
            [
                (heart_center_x - 14, heart_center_y - 1),
                (heart_center_x + 14, heart_center_y - 1),
                (heart_center_x, heart_center_y + 16),
            ],
        )
        screen.blit(self.font.render(f"Lives: {self.lives}", True, self.colors["ink"]), (688, 18))

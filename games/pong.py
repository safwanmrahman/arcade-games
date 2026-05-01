import math
import random

import pygame


class PongGame:
    name = "pong"

    def __init__(self, width, height, font, small_font, colors, spawn_particles):
        self.width = width
        self.height = height
        self.font = font
        self.small_font = small_font
        self.colors = colors
        self.spawn_particles = spawn_particles
        self.header_height = 72
        self.difficulty = "Medium"
        self.difficulty_map = {"Easy": 2.7, "Medium": 4.5, "Hard": 6.4}
        self.win_score = 5
        self.game_mode = "cpu"
        self.paddle_speed = 420
        self.paddle = pygame.Rect(50, 250, 12, 100)
        self.cpu_paddle = pygame.Rect(width - 62, 250, 12, 100)
        self.ball = pygame.Rect(0, 0, 16, 16)
        self.ball_pos = [width / 2, height / 2]
        self.ball_velocity = [0.0, 0.0]
        self.player_score = 0
        self.cpu_score = 0
        self.trail = []
        self.reset()

    @property
    def mode_label(self):
        return f"CPU {self.difficulty}" if self.game_mode == "cpu" else "Vs Player"

    def clamp(self, value, low, high):
        return max(low, min(high, value))

    def reset_ball(self, direction):
        center_y = self.header_height + (self.height - self.header_height) / 2
        self.ball_pos = [self.width / 2, center_y]
        speed_x = random.uniform(250, 300) * direction
        speed_y = random.choice([-1, 1]) * random.uniform(120, 180)
        self.ball_velocity = [speed_x, speed_y]
        self.ball.center = (int(self.ball_pos[0]), int(self.ball_pos[1]))
        self.trail = []

    def reset(self, mode=None):
        if mode is not None:
            self.game_mode = mode
        self.player_score = 0
        self.cpu_score = 0
        center_y = self.header_height + (self.height - self.header_height) / 2
        self.paddle.y = int(center_y - self.paddle.height // 2)
        self.cpu_paddle.y = int(center_y - self.cpu_paddle.height // 2)
        self.reset_ball(random.choice([-1, 1]))

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def bounce_off_paddle(self, paddle_rect, moving_right, color):
        relative = (self.ball.centery - paddle_rect.centery) / (paddle_rect.height / 2)
        relative = self.clamp(relative, -1.0, 1.0)
        angle = relative * math.radians(58)
        speed = min(760, math.hypot(self.ball_velocity[0], self.ball_velocity[1]) + 48)
        direction = 1 if moving_right else -1
        self.ball_velocity[0] = math.cos(angle) * speed * direction
        self.ball_velocity[1] = math.sin(angle) * speed
        if abs(self.ball_velocity[1]) < 120:
            self.ball_velocity[1] = 120 if self.ball_velocity[1] >= 0 else -120
        if moving_right:
            self.ball.left = paddle_rect.right
        else:
            self.ball.right = paddle_rect.left
        self.ball_pos[0], self.ball_pos[1] = self.ball.centerx, self.ball.centery
        self.spawn_particles(*self.ball.center, color)

    def update(self, dt, keys):
        if keys[pygame.K_w]:
            self.paddle.y -= self.paddle_speed * dt
        if keys[pygame.K_s]:
            self.paddle.y += self.paddle_speed * dt

        if self.game_mode == "cpu":
            target = self.ball_pos[1] - self.cpu_paddle.centery
            self.cpu_paddle.y += target * self.difficulty_map[self.difficulty] * dt
        else:
            if keys[pygame.K_UP]:
                self.cpu_paddle.y -= self.paddle_speed * dt
            if keys[pygame.K_DOWN]:
                self.cpu_paddle.y += self.paddle_speed * dt

        self.paddle.y = self.clamp(self.paddle.y, self.header_height + 10, self.height - self.paddle.height)
        self.cpu_paddle.y = self.clamp(self.cpu_paddle.y, self.header_height + 10, self.height - self.cpu_paddle.height)

        self.ball_pos[0] += self.ball_velocity[0] * dt
        self.ball_pos[1] += self.ball_velocity[1] * dt
        self.ball.center = (int(self.ball_pos[0]), int(self.ball_pos[1]))

        if self.ball.top <= self.header_height:
            self.ball.top = self.header_height
            self.ball_pos[1] = self.ball.centery
            self.ball_velocity[1] = abs(self.ball_velocity[1])
        elif self.ball.bottom >= self.height:
            self.ball.bottom = self.height
            self.ball_pos[1] = self.ball.centery
            self.ball_velocity[1] = -abs(self.ball_velocity[1])

        self.trail.append(tuple(self.ball.center))
        if len(self.trail) > 12:
            self.trail.pop(0)

        if self.ball.colliderect(self.paddle) and self.ball_velocity[0] < 0:
            self.bounce_off_paddle(self.paddle, True, self.colors["player"])
        elif self.ball.colliderect(self.cpu_paddle) and self.ball_velocity[0] > 0:
            self.bounce_off_paddle(self.cpu_paddle, False, self.colors["cpu"])

        if self.ball.right < 0:
            self.cpu_score += 1
            self.reset_ball(1)
        elif self.ball.left > self.width:
            self.player_score += 1
            self.reset_ball(-1)

        if self.player_score >= self.win_score:
            return "You Win!" if self.game_mode == "cpu" else "Player 1 Wins!"
        if self.cpu_score >= self.win_score:
            return "You Win!" if self.game_mode == "cpu" else "Player 2 Wins!"
        return None

    def draw(self, screen, offset_x=0, offset_y=0):
        screen.fill((241, 246, 255))
        pygame.draw.rect(screen, (228, 237, 255), pygame.Rect(0, 0, self.width, self.header_height))
        pygame.draw.line(screen, (201, 216, 247), (0, self.header_height), (self.width, self.header_height), 2)
        pygame.draw.line(screen, self.colors["divider"], (self.width // 2, 0), (self.width // 2, self.height), 2)
        pygame.draw.rect(screen, self.colors["player"], self.paddle.move(offset_x, offset_y))
        pygame.draw.rect(screen, self.colors["cpu"], self.cpu_paddle.move(offset_x, offset_y))

        for index, pos in enumerate(self.trail):
            radius = max(2, 6 - (len(self.trail) - index) // 2)
            color = (145 + index * 8, 188 + index * 4, 255)
            pygame.draw.circle(screen, color, pos, radius)

        ball_rect = self.ball.move(offset_x, offset_y)
        pygame.draw.circle(screen, (24, 38, 74), ball_rect.center, 8)

        screen.blit(self.font.render(str(self.player_score), True, self.colors["player"]), (self.width // 2 - 110, 20))
        screen.blit(self.font.render(str(self.cpu_score), True, self.colors["cpu"]), (self.width // 2 + 70, 20))
        screen.blit(self.small_font.render(f"Pong - {self.mode_label}", True, self.colors["ink_soft"]), (20, 20))

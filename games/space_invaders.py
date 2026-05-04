import random

import pygame


class SpaceInvadersGame:
    name = "space_invaders"

    def __init__(self, width, height, font, small_font, colors, spawn_particles):
        self.width = width
        self.height = height
        self.font = font
        self.small_font = small_font
        self.colors = colors
        self.spawn_particles = spawn_particles
        self.header_height = 72
        self.player = pygame.Rect(0, 0, 72, 18)
        self.player_speed = 520
        self.bullets = []
        self.enemy_bullets = []
        self.aliens = []
        self.direction = 1
        self.move_timer = 0.0
        self.move_interval = 0.6
        self.enemy_fire_timer = 0.0
        self.enemy_fire_interval = 1.2
        self.enemy_drop = 18
        self.shot_cooldown = 0.0
        self.shot_delay = 0.16
        self.score = 0
        self.lives = 3
        self.preset = "Arcade"
        self.starting_lives = 3
        self.alien_rows = 3
        self.alien_cols = 6
        self.wave = 1
        self.alien_speed_label = "Arcade"
        self.presets = {
            "Cadet": {"lives": 4, "move_interval": 0.74, "fire_interval": 1.26, "shot_delay": 0.10},
            "Arcade": {"lives": 3, "move_interval": 0.60, "fire_interval": 1.02, "shot_delay": 0.09},
            "Elite": {"lives": 2, "move_interval": 0.45, "fire_interval": 0.80, "shot_delay": 0.08},
        }
        self.reset()

    def build_aliens(self):
        aliens = []
        start_x = 164
        start_y = self.header_height + 48
        gap_x = 146
        gap_y = 78
        colors = [self.colors["accent"], self.colors["cpu"], self.colors["player"], self.colors["lavender"]]
        for row in range(self.alien_rows):
            for col in range(self.alien_cols):
                rect = pygame.Rect(start_x + col * gap_x, start_y + row * gap_y, 44, 28)
                aliens.append({"rect": rect, "color": colors[row % len(colors)]})
        return aliens

    def set_preset(self, label):
        self.preset = label
        config = self.presets[label]
        self.starting_lives = config["lives"]
        self.move_interval = config["move_interval"]
        self.enemy_fire_interval = config["fire_interval"]
        self.shot_delay = config["shot_delay"]
        self.alien_speed_label = label

    def reset(self):
        self.player.midbottom = (self.width // 2, self.height - 26)
        self.bullets = []
        self.enemy_bullets = []
        self.aliens = self.build_aliens()
        self.direction = 1
        self.move_timer = 0.0
        self.enemy_fire_timer = 0.0
        self.shot_cooldown = 0.0
        self.score = 0
        self.lives = self.starting_lives
        self.wave = 1 if self.score == 0 else self.wave

    def fire_player_bullet(self):
        if len(self.bullets) >= 4 or self.shot_cooldown > 0:
            return
        bullet = pygame.Rect(0, 0, 14, 34)
        bullet.midbottom = (self.player.centerx, self.player.top - 4)
        self.bullets.append(bullet)
        self.shot_cooldown = self.shot_delay

    def handle_keydown(self, key):
        if key == pygame.K_SPACE:
            self.fire_player_bullet()

    def enemy_frontier(self):
        frontier = {}
        for alien in self.aliens:
            col = alien["rect"].centerx
            if col not in frontier or alien["rect"].bottom > frontier[col]["rect"].bottom:
                frontier[col] = alien
        return list(frontier.values())

    def update(self, dt, keys):
        self.shot_cooldown = max(0.0, self.shot_cooldown - dt)
        move_dir = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dir -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dir += 1
        if keys[pygame.K_SPACE]:
            self.fire_player_bullet()
        self.player.x += int(move_dir * self.player_speed * dt)
        self.player.x = max(24, min(self.player.x, self.width - self.player.width - 24))

        for bullet in self.bullets[:]:
            bullet.y -= int(860 * dt)
            if bullet.bottom < self.header_height:
                self.bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.y += int(320 * dt)
            if bullet.top > self.height:
                self.enemy_bullets.remove(bullet)

        live_ratio = len(self.aliens) / (self.alien_cols * self.alien_rows) if self.aliens else 0
        active_interval = max(0.18, self.move_interval * (0.56 + live_ratio * 0.44))
        self.move_timer += dt
        if self.move_timer >= active_interval:
            self.move_timer = 0.0
            edge_hit = False
            for alien in self.aliens:
                alien["rect"].x += int((14 + self.wave * 2) * self.direction)
                if alien["rect"].right >= self.width - 28 or alien["rect"].left <= 28:
                    edge_hit = True
            if edge_hit:
                self.direction *= -1
                for alien in self.aliens:
                    alien["rect"].y += self.enemy_drop

        self.enemy_fire_timer += dt
        if self.enemy_fire_timer >= self.enemy_fire_interval and self.aliens:
            self.enemy_fire_timer = 0.0
            shooters = self.enemy_frontier()
            volley_count = 1 if self.preset == "Cadet" else 2
            if self.preset == "Elite" and live_ratio < 0.5:
                volley_count = 2
            for shooter in random.sample(shooters, min(volley_count, len(shooters))):
                bullet = pygame.Rect(0, 0, 8, 24)
                bullet.midtop = shooter["rect"].midbottom
                self.enemy_bullets.append(bullet)

        for bullet in self.bullets[:]:
            hit_index = bullet.collidelist([alien["rect"] for alien in self.aliens])
            if hit_index != -1:
                alien = self.aliens.pop(hit_index)
                self.bullets.remove(bullet)
                self.score += 25
                self.spawn_particles(alien["rect"].centerx, alien["rect"].centery, alien["color"])
                continue

            for enemy_bullet in self.enemy_bullets[:]:
                if bullet.inflate(24, 24).colliderect(enemy_bullet.inflate(18, 18)):
                    self.enemy_bullets.remove(enemy_bullet)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.spawn_particles(enemy_bullet.centerx, enemy_bullet.centery, self.colors["ball"])
                    break

        for bullet in self.enemy_bullets[:]:
            if bullet.colliderect(self.player):
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                self.spawn_particles(self.player.centerx, self.player.centery, self.colors["cpu"])
                if self.lives <= 0:
                    return f"Invaders broke through at {self.score} points"

        if any(alien["rect"].bottom >= self.player.top for alien in self.aliens):
            return f"Invaders landed with {self.score} points"

        if not self.aliens:
            self.wave += 1
            self.alien_rows = min(5, 3 + (self.wave - 1) // 2)
            self.aliens = self.build_aliens()
            self.bullets = []
            self.enemy_bullets = []
            self.direction = 1
            self.move_timer = 0.0
            self.enemy_fire_timer = 0.0
            self.score += 100
            self.spawn_particles(self.width // 2, self.height // 2, self.colors["accent"])
        return None

    def draw(self, screen):
        screen.fill((244, 247, 255))
        pygame.draw.rect(screen, (228, 235, 255), pygame.Rect(0, 0, self.width, self.header_height))
        pygame.draw.line(screen, (194, 207, 247), (0, self.header_height), (self.width, self.header_height), 2)

        for x in range(90, self.width, 180):
            pygame.draw.circle(screen, (231, 238, 255), (x, 190), 2)
            pygame.draw.circle(screen, (231, 238, 255), (x + 56, 280), 3)
            pygame.draw.circle(screen, (231, 238, 255), (x + 22, 420), 2)

        for alien in self.aliens:
            body = alien["rect"]
            pygame.draw.rect(screen, alien["color"], body, border_radius=8)
            pygame.draw.rect(screen, self.colors["ink"], body, 2, border_radius=8)
            eye_y = body.y + 10
            pygame.draw.circle(screen, self.colors["panel"], (body.x + 13, eye_y), 3)
            pygame.draw.circle(screen, self.colors["panel"], (body.x + 31, eye_y), 3)

        pygame.draw.rect(screen, self.colors["player"], self.player, border_radius=8)
        turret = pygame.Rect(0, 0, 18, 10)
        turret.midbottom = (self.player.centerx, self.player.top + 4)
        pygame.draw.rect(screen, self.colors["ink"], turret, border_radius=4)

        for bullet in self.bullets:
            glow = bullet.inflate(8, 10)
            pygame.draw.rect(screen, (255, 233, 180), glow, border_radius=6)
            pygame.draw.rect(screen, self.colors["accent_dark"], bullet, border_radius=4)
            core = bullet.inflate(-6, -6)
            pygame.draw.rect(screen, (255, 248, 220), core, border_radius=3)
        for bullet in self.enemy_bullets:
            glow = bullet.inflate(8, 10)
            pygame.draw.rect(screen, (255, 212, 228), glow, border_radius=6)
            pygame.draw.rect(screen, self.colors["cpu"], bullet, border_radius=4)

        screen.blit(self.font.render(f"Invaders Score: {self.score}", True, self.colors["ink"]), (20, 18))
        screen.blit(self.small_font.render(f"{self.alien_speed_label} • Wave {self.wave}", True, self.colors["ink_soft"]), (360, 24))
        screen.blit(self.small_font.render("Hold Space to fire • Shots cancel enemy fire", True, self.colors["ink_soft"]), (650, 24))
        screen.blit(self.font.render(f"Lives: {self.lives}", True, self.colors["ink"]), (920, 18))

import random

import pygame


class SudokuGame:
    name = "sudoku"

    def __init__(self, width, height, font, small_font, colors, spawn_particles):
        self.width = width
        self.height = height
        self.font = font
        self.small_font = small_font
        self.colors = colors
        self.spawn_particles = spawn_particles
        self.header_height = 72
        self.grid_size = 9
        self.cell_size = 48
        self.board_size = self.cell_size * self.grid_size
        self.board_left = (width - self.board_size) // 2
        self.board_top = 110
        self.preset = "Easy"
        self.removals = {"Easy": 36, "Medium": 46, "Hard": 54}
        self.solution = []
        self.board = []
        self.fixed = set()
        self.selected = (0, 0)
        self.reset()

    def set_preset(self, label):
        self.preset = label

    def pattern(self, row, col):
        base = 3
        return (base * (row % base) + row // base + col) % (base * base)

    def shuffled(self, values):
        values = list(values)
        random.shuffle(values)
        return values

    def generate_solution(self):
        base = 3
        side = base * base
        rows = [g * base + r for g in self.shuffled(range(base)) for r in self.shuffled(range(base))]
        cols = [g * base + c for g in self.shuffled(range(base)) for c in self.shuffled(range(base))]
        nums = self.shuffled(range(1, side + 1))
        return [[nums[self.pattern(r, c)] for c in cols] for r in rows]

    def build_puzzle(self, solution):
        puzzle = [row[:] for row in solution]
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        for row, col in cells[: self.removals[self.preset]]:
            puzzle[row][col] = 0
        return puzzle

    def reset(self):
        self.solution = self.generate_solution()
        self.board = self.build_puzzle(self.solution)
        self.fixed = {(r, c) for r in range(9) for c in range(9) if self.board[r][c] != 0}
        self.selected = next(((r, c) for r in range(9) for c in range(9) if (r, c) not in self.fixed), (0, 0))

    def is_complete(self):
        return self.board == self.solution

    def handle_mouse(self, pos):
        x, y = pos
        if not (
            self.board_left <= x < self.board_left + self.board_size
            and self.board_top <= y < self.board_top + self.board_size
        ):
            return
        col = (x - self.board_left) // self.cell_size
        row = (y - self.board_top) // self.cell_size
        self.selected = (int(row), int(col))

    def handle_keydown(self, key, unicode_value):
        row, col = self.selected
        if key == pygame.K_LEFT:
            self.selected = (row, max(0, col - 1))
            return None
        if key == pygame.K_RIGHT:
            self.selected = (row, min(8, col + 1))
            return None
        if key == pygame.K_UP:
            self.selected = (max(0, row - 1), col)
            return None
        if key == pygame.K_DOWN:
            self.selected = (min(8, row + 1), col)
            return None

        if (row, col) in self.fixed:
            return None

        if unicode_value in "123456789":
            value = int(unicode_value)
            self.board[row][col] = value
            if value == self.solution[row][col]:
                cx = self.board_left + col * self.cell_size + self.cell_size // 2
                cy = self.board_top + row * self.cell_size + self.cell_size // 2
                self.spawn_particles(cx, cy, self.colors["player"])
            if self.is_complete():
                self.spawn_particles(self.width // 2, self.board_top + self.board_size // 2, self.colors["accent"])
                return f"Solved {self.preset} Sudoku"
            return None

        if key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            self.board[row][col] = 0
        return None

    def update(self, dt):
        return None

    def draw(self, screen):
        screen.fill((249, 244, 255))
        pygame.draw.rect(screen, (238, 229, 255), pygame.Rect(0, 0, self.width, self.header_height))
        pygame.draw.line(screen, (215, 200, 247), (0, self.header_height), (self.width, self.header_height), 2)

        panel = pygame.Rect(self.board_left - 18, self.board_top - 18, self.board_size + 36, self.board_size + 36)
        pygame.draw.rect(screen, (255, 255, 255), panel, border_radius=28)
        pygame.draw.rect(screen, (214, 199, 247), panel, 3, border_radius=28)

        selected_row, selected_col = self.selected
        row_rect = pygame.Rect(
            self.board_left,
            self.board_top + selected_row * self.cell_size,
            self.board_size,
            self.cell_size,
        )
        col_rect = pygame.Rect(
            self.board_left + selected_col * self.cell_size,
            self.board_top,
            self.cell_size,
            self.board_size,
        )
        pygame.draw.rect(screen, (245, 240, 255), row_rect)
        pygame.draw.rect(screen, (245, 240, 255), col_rect)

        box_left = self.board_left + (selected_col // 3) * self.cell_size * 3
        box_top = self.board_top + (selected_row // 3) * self.cell_size * 3
        pygame.draw.rect(
            screen,
            (239, 233, 255),
            pygame.Rect(box_left, box_top, self.cell_size * 3, self.cell_size * 3),
        )
        pygame.draw.rect(screen, (245, 240, 255), row_rect)
        pygame.draw.rect(screen, (245, 240, 255), col_rect)

        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(
                    self.board_left + col * self.cell_size,
                    self.board_top + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                if (row, col) == self.selected:
                    pygame.draw.rect(screen, (225, 214, 255), rect)
                pygame.draw.rect(screen, (220, 212, 245), rect, 1)

                value = self.board[row][col]
                if value:
                    color = self.colors["ink"] if (row, col) in self.fixed else self.colors["player"]
                    surface = self.font.render(str(value), True, color)
                    screen.blit(surface, surface.get_rect(center=rect.center))

        for step in range(10):
            thickness = 3 if step % 3 == 0 else 1
            color = (160, 141, 214) if step % 3 == 0 else (220, 212, 245)
            x = self.board_left + step * self.cell_size
            y = self.board_top + step * self.cell_size
            pygame.draw.line(screen, color, (x, self.board_top), (x, self.board_top + self.board_size), thickness)
            pygame.draw.line(screen, color, (self.board_left, y), (self.board_left + self.board_size, y), thickness)

        screen.blit(self.font.render(f"Sudoku - {self.preset}", True, self.colors["ink"]), (20, 18))
        clue_count = len(self.fixed)
        screen.blit(self.small_font.render(f"Clues: {clue_count}", True, self.colors["ink_soft"]), (20, 56))
        screen.blit(self.small_font.render("Arrows/mouse to move, 1-9 to fill", True, self.colors["ink_soft"]), (430, 22))
        screen.blit(self.small_font.render("Backspace clears a cell", True, self.colors["ink_soft"]), (520, 52))

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
        self.notes = {}
        self.selected = (0, 0)
        self.auto_check = True
        self.notes_mode = False
        self.mistakes = 0
        self.status_message = "Fill the grid"
        self.solved_by_reveal = False
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
        self.notes = {}
        self.selected = next(((r, c) for r in range(9) for c in range(9) if (r, c) not in self.fixed), (0, 0))
        self.auto_check = True
        self.notes_mode = False
        self.mistakes = 0
        self.status_message = "Auto-check on"
        self.solved_by_reveal = False

    def is_complete(self):
        return self.board == self.solution

    def has_conflict(self, row, col, value=None):
        value = self.board[row][col] if value is None else value
        if value == 0:
            return False

        for other_col in range(9):
            if other_col != col and self.board[row][other_col] == value:
                return True
        for other_row in range(9):
            if other_row != row and self.board[other_row][col] == value:
                return True

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for other_row in range(box_row, box_row + 3):
            for other_col in range(box_col, box_col + 3):
                if (other_row, other_col) != (row, col) and self.board[other_row][other_col] == value:
                    return True
        return False

    def is_wrong_value(self, row, col):
        value = self.board[row][col]
        return value != 0 and value != self.solution[row][col]

    def toggle_note(self, row, col, value):
        current = self.notes.setdefault((row, col), set())
        if value in current:
            current.remove(value)
        else:
            current.add(value)
        if not current:
            self.notes.pop((row, col), None)

    def reveal_hint(self):
        row, col = self.selected
        if (row, col) in self.fixed:
            self.status_message = "Pick an empty cell first"
            return None

        correct = self.solution[row][col]
        if self.board[row][col] == correct:
            self.status_message = "That cell is already correct"
            return None

        self.board[row][col] = correct
        self.notes.pop((row, col), None)
        self.status_message = "Hint used"
        cx = self.board_left + col * self.cell_size + self.cell_size // 2
        cy = self.board_top + row * self.cell_size + self.cell_size // 2
        self.spawn_particles(cx, cy, self.colors["accent"])
        if self.is_complete():
            self.spawn_particles(self.width // 2, self.board_top + self.board_size // 2, self.colors["accent"])
            return f"Solved {self.preset} Sudoku"
        return None

    def reveal_solution(self):
        self.board = [row[:] for row in self.solution]
        self.notes = {}
        self.solved_by_reveal = True
        self.status_message = "Solution revealed"
        self.spawn_particles(self.width // 2, self.board_top + self.board_size // 2, self.colors["accent"])
        return f"Solution shown for {self.preset} Sudoku"

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
        self.status_message = "Cell selected"

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
        if key == pygame.K_a:
            self.auto_check = not self.auto_check
            self.status_message = f"Auto-check {'on' if self.auto_check else 'off'}"
            return None
        if key == pygame.K_n:
            self.notes_mode = not self.notes_mode
            self.status_message = f"Notes {'on' if self.notes_mode else 'off'}"
            return None
        if key == pygame.K_h:
            return self.reveal_hint()
        if key == pygame.K_s:
            return self.reveal_solution()

        if (row, col) in self.fixed:
            return None

        if unicode_value and unicode_value in "123456789":
            value = int(unicode_value)
            if self.notes_mode:
                self.toggle_note(row, col, value)
                self.status_message = "Note updated"
                return None

            previous_value = self.board[row][col]
            self.board[row][col] = value
            self.notes.pop((row, col), None)
            if value == self.solution[row][col]:
                cx = self.board_left + col * self.cell_size + self.cell_size // 2
                cy = self.board_top + row * self.cell_size + self.cell_size // 2
                self.spawn_particles(cx, cy, self.colors["player"])
                self.status_message = "Looks good"
            elif self.auto_check:
                if previous_value != value:
                    self.mistakes += 1
                self.status_message = "That entry is incorrect"
            else:
                self.status_message = "Value placed"
            if self.is_complete():
                self.spawn_particles(self.width // 2, self.board_top + self.board_size // 2, self.colors["accent"])
                return f"Solved {self.preset} Sudoku"
            return None

        if key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            self.board[row][col] = 0
            self.notes.pop((row, col), None)
            self.status_message = "Cell cleared"
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
        selected_value = self.board[selected_row][selected_col]
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
                value = self.board[row][col]
                if selected_value and value == selected_value:
                    pygame.draw.rect(screen, (236, 246, 255), rect)
                if self.auto_check and (self.has_conflict(row, col) or self.is_wrong_value(row, col)):
                    pygame.draw.rect(screen, (255, 232, 238), rect)
                if (row, col) == self.selected:
                    pygame.draw.rect(screen, (225, 214, 255), rect)
                pygame.draw.rect(screen, (220, 212, 245), rect, 1)

                if value:
                    if self.auto_check and (self.has_conflict(row, col) or self.is_wrong_value(row, col)):
                        color = self.colors["cpu"]
                    else:
                        color = self.colors["ink"] if (row, col) in self.fixed else self.colors["player"]
                    surface = self.font.render(str(value), True, color)
                    screen.blit(surface, surface.get_rect(center=rect.center))
                elif (row, col) in self.notes and self.notes[(row, col)]:
                    note_color = (132, 123, 176)
                    for note in sorted(self.notes[(row, col)]):
                        note_row = (note - 1) // 3
                        note_col = (note - 1) % 3
                        note_surface = self.small_font.render(str(note), True, note_color)
                        note_x = rect.x + 8 + note_col * 14
                        note_y = rect.y + 5 + note_row * 14
                        screen.blit(note_surface, (note_x, note_y))

        for step in range(10):
            thickness = 3 if step % 3 == 0 else 1
            color = (160, 141, 214) if step % 3 == 0 else (220, 212, 245)
            x = self.board_left + step * self.cell_size
            y = self.board_top + step * self.cell_size
            pygame.draw.line(screen, color, (x, self.board_top), (x, self.board_top + self.board_size), thickness)
            pygame.draw.line(screen, color, (self.board_left, y), (self.board_left + self.board_size, y), thickness)

        screen.blit(self.font.render(f"Sudoku - {self.preset}", True, self.colors["ink"]), (20, 16))
        clue_count = len(self.fixed)
        screen.blit(self.small_font.render(f"Clues: {clue_count}", True, self.colors["ink_soft"]), (20, 54))
        screen.blit(self.small_font.render(f"Mistakes: {self.mistakes}", True, self.colors["cpu"]), (180, 54))
        status_rect = pygame.Rect(330, 16, 170, 34)
        pygame.draw.rect(screen, (255, 255, 255), status_rect, border_radius=16)
        pygame.draw.rect(screen, (214, 199, 247), status_rect, 2, border_radius=16)
        status_surface = self.small_font.render(self.status_message, True, self.colors["ink_soft"])
        screen.blit(status_surface, status_surface.get_rect(center=status_rect.center))

        controls = [
            (pygame.Rect(560, 16, 170, 34), f"Auto-check {'On' if self.auto_check else 'Off'}  A", self.colors["player"]),
            (pygame.Rect(748, 16, 140, 34), f"Notes {'On' if self.notes_mode else 'Off'}  N", self.colors["accent"]),
            (pygame.Rect(906, 16, 70, 34), "H", self.colors["lavender"]),
            (pygame.Rect(986, 16, 70, 34), "S", self.colors["cpu"]),
        ]
        for rect, label, border in controls:
            pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=16)
            pygame.draw.rect(screen, border, rect, 2, border_radius=16)
            text = self.small_font.render(label, True, self.colors["ink"])
            screen.blit(text, text.get_rect(center=rect.center))

        helper_text = "Arrows or mouse move • 1-9 fills • Backspace clears • H hint • S solve"
        screen.blit(self.small_font.render(helper_text, True, self.colors["ink_soft"]), (430, 54))

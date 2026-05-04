import unittest

import pygame

from games import BreakoutGame, PongGame, SnakeGame, SpaceInvadersGame, SudokuGame


class FakeKeys(dict):
    def __getitem__(self, key):
        return self.get(key, False)


def stub_particles(*args, **kwargs):
    return None


COLORS = {
    "ink": (36, 55, 95),
    "ink_soft": (92, 116, 160),
    "player": (49, 168, 255),
    "cpu": (255, 109, 161),
    "ball": (255, 204, 87),
    "accent": (255, 194, 76),
    "accent_dark": (216, 135, 27),
    "snake_body": (93, 214, 187),
    "divider": (175, 198, 255),
    "lavender": (215, 205, 255),
    "panel": (255, 255, 255),
}
BRICK_COLORS = [(255, 126, 163), (255, 174, 89), (255, 214, 102), (106, 214, 173)]


class SudokuTests(unittest.TestCase):
    def test_generated_solution_has_valid_rows_columns_and_boxes(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)
        expected = set(range(1, 10))

        for row in game.solution:
            self.assertEqual(set(row), expected)

        for col in range(9):
            self.assertEqual({game.solution[row][col] for row in range(9)}, expected)

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                values = {
                    game.solution[row][col]
                    for row in range(box_row, box_row + 3)
                    for col in range(box_col, box_col + 3)
                }
                self.assertEqual(values, expected)

    def test_fixed_cells_match_solution_after_reset(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)
        for row, col in game.fixed:
            self.assertEqual(game.board[row][col], game.solution[row][col])
            self.assertNotEqual(game.board[row][col], 0)

    def test_notes_mode_toggles_candidate_in_selected_cell(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)
        row, col = game.selected

        game.handle_keydown(pygame.K_n, "")
        game.handle_keydown(pygame.K_4, "4")

        self.assertIn((row, col), game.notes)
        self.assertIn(4, game.notes[(row, col)])

    def test_wrong_value_counts_mistake_when_auto_check_is_on(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)
        row, col = game.selected
        wrong_value = next(value for value in range(1, 10) if value != game.solution[row][col])

        game.handle_keydown(getattr(pygame, f"K_{wrong_value}"), str(wrong_value))

        self.assertEqual(game.board[row][col], wrong_value)
        self.assertEqual(game.mistakes, 1)

    def test_hint_reveals_correct_value(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)
        row, col = game.selected

        game.reveal_hint()

        self.assertEqual(game.board[row][col], game.solution[row][col])

    def test_empty_unicode_does_not_crash(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)

        message = game.handle_keydown(pygame.K_LSHIFT, "")

        self.assertIsNone(message)

    def test_reveal_solution_fills_board_and_returns_message(self):
        game = SudokuGame(1100, 860, None, None, COLORS, stub_particles)

        message = game.reveal_solution()

        self.assertEqual(game.board, game.solution)
        self.assertEqual(message, f"Solution shown for {game.preset} Sudoku")


class SnakeTests(unittest.TestCase):
    def test_snake_grows_and_scores_after_eating(self):
        game = SnakeGame(1100, 860, None, COLORS, stub_particles)
        head_x, head_y = game.snake[0]
        game.food = (head_x + 1, head_y)

        message = game.update(game.step_time)

        self.assertIsNone(message)
        self.assertEqual(game.score, 1)
        self.assertEqual(len(game.snake), 4)

    def test_snake_crashes_into_wall(self):
        game = SnakeGame(1100, 860, None, COLORS, stub_particles)
        game.snake = [(0, 5), (1, 5), (2, 5)]
        game.previous_snake = list(game.snake)
        game.direction = (-1, 0)
        game.next_direction = (-1, 0)

        message = game.update(game.step_time)

        self.assertEqual(message, "Snake crashed at 0 points")


class PaddleAndBrickTests(unittest.TestCase):
    def test_pong_scores_when_ball_exits_right_side(self):
        game = PongGame(1100, 860, None, None, COLORS, stub_particles)
        game.ball.left = game.width + 1
        game.ball_pos = [game.ball.centerx, game.ball.centery]
        game.ball_velocity = [120, 0]

        message = game.update(0, FakeKeys())

        self.assertIsNone(message)
        self.assertEqual(game.player_score, 1)

    def test_breakout_removes_brick_and_awards_points(self):
        game = BreakoutGame(1100, 860, None, COLORS, BRICK_COLORS, stub_particles)
        target = game.bricks[0]["rect"]
        game.ball = pygame.Rect(target.x + 10, target.y + 5, 14, 14)
        game.ball_pos = [game.ball.centerx, game.ball.centery]
        game.ball_velocity = [0, 0]

        message = game.update(0, FakeKeys())

        self.assertIsNone(message)
        self.assertEqual(game.score, 10)
        self.assertEqual(len(game.bricks), 49)


class SpaceInvadersTests(unittest.TestCase):
    def test_player_bullet_removes_alien_and_scores(self):
        game = SpaceInvadersGame(1100, 860, None, None, COLORS, stub_particles)
        alien = game.aliens[0]["rect"]
        bullet = pygame.Rect(alien.centerx - 4, alien.centery - 14, 10, 28)
        game.bullets = [bullet]

        message = game.update(0, FakeKeys())

        self.assertIsNone(message)
        self.assertEqual(game.score, 25)
        self.assertEqual(len(game.aliens), 17)

    def test_enemy_bullet_can_end_run(self):
        game = SpaceInvadersGame(1100, 860, None, None, COLORS, stub_particles)
        game.lives = 1
        bullet = pygame.Rect(0, 0, 8, 24)
        bullet.center = game.player.center
        game.enemy_bullets = [bullet]

        message = game.update(0, FakeKeys())

        self.assertEqual(message, "Invaders broke through at 0 points")

    def test_wave_clear_rebuilds_invaders_and_awards_bonus(self):
        game = SpaceInvadersGame(1100, 860, None, None, COLORS, stub_particles)
        game.aliens = []

        message = game.update(0, FakeKeys())

        self.assertIsNone(message)
        self.assertEqual(game.wave, 2)
        self.assertEqual(len(game.aliens), 18)
        self.assertEqual(game.score, 100)

    def test_player_bullet_can_cancel_enemy_bullet_with_generous_window(self):
        game = SpaceInvadersGame(1100, 860, None, None, COLORS, stub_particles)
        player_bullet = pygame.Rect(300, 400, 14, 34)
        enemy_bullet = pygame.Rect(316, 392, 8, 24)
        game.bullets = [player_bullet]
        game.enemy_bullets = [enemy_bullet]

        game.update(0, FakeKeys())

        self.assertEqual(game.bullets, [])
        self.assertEqual(game.enemy_bullets, [])


if __name__ == "__main__":
    unittest.main()

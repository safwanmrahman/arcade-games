import pygame
import random
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)

# Colors
BG = (15, 18, 40)
PLAYER_COLOR = (0, 255, 200)
CPU_COLOR = (255, 80, 180)
BALL_COLOR = (255, 255, 255)

# Paddle
paddle = pygame.Rect(50, 250, 10, 100)
paddle_speed = 300

# Right paddle
cpu_paddle = pygame.Rect(740, 250, 10, 100)

# Ball
ball = pygame.Rect(400, 300, 15, 15)
ball_pos = [400.0, 300.0]
ball_speed_x = 220
ball_speed_y = 180

# Score
player_score = 0
cpu_score = 0
WIN_SCORE = 5

# States
state = "menu"
game_mode = "cpu"
difficulty = "Medium"
prev_state = "play"

difficulty_map = {"Easy": 2.5, "Medium": 4.0, "Hard": 6.0}

particles = []
shake_timer = 0
trail = []

def reset_ball(direction):
    global ball_pos, ball_speed_x, ball_speed_y
    ball_pos = [400.0, 300.0]
    ball_speed_x = 220 * direction
    ball_speed_y = random.choice([-180, 180])

def spawn_particles(x, y, color):
    global shake_timer
    shake_timer = 0.2
    for _ in range(10):
        particles.append([
            [x, y],
            [random.uniform(-120,120), random.uniform(-120,120)],
            random.randint(3,6),
            color
        ])

running = True
while running:
    dt = clock.tick(60)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # quit anywhere
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            # ESC = go back / quit
            if event.key == pygame.K_ESCAPE:
                if state in ["settings", "pause"]:
                    state = prev_state
                elif state == "menu":
                    pygame.quit()
                    sys.exit()

            # pause toggle
            if event.key == pygame.K_p and state == "play":
                prev_state = "play"
                state = "pause"
            elif event.key == pygame.K_p and state == "pause":
                state = "play"

            # settings (O key now)
            elif event.key == pygame.K_o and state in ["play","pause"]:
                prev_state = state
                state = "settings"

            # menu
            elif state == "menu":
                if event.key == pygame.K_1:
                    game_mode = "cpu"; difficulty = "Easy"; state="start"
                elif event.key == pygame.K_2:
                    game_mode = "cpu"; difficulty = "Medium"; state="start"
                elif event.key == pygame.K_3:
                    game_mode = "cpu"; difficulty = "Hard"; state="start"
                elif event.key == pygame.K_4:
                    game_mode = "player"; state="start"

            elif state == "start":
                state = "play"

            elif state == "game_over":
                player_score = 0
                cpu_score = 0
                state = "menu"

            elif state == "settings":
                if event.key == pygame.K_1:
                    difficulty = "Easy"
                elif event.key == pygame.K_2:
                    difficulty = "Medium"
                elif event.key == pygame.K_3:
                    difficulty = "Hard"

    if state == "play":
        keys = pygame.key.get_pressed()

        # player 1
        if keys[pygame.K_w]:
            paddle.y -= paddle_speed*dt
        if keys[pygame.K_s]:
            paddle.y += paddle_speed*dt

        # right paddle
        if game_mode == "cpu":
            diff = ball_pos[1] - cpu_paddle.centery
            cpu_paddle.y += diff * difficulty_map[difficulty] * dt
        else:
            if keys[pygame.K_UP]:
                cpu_paddle.y -= paddle_speed*dt
            if keys[pygame.K_DOWN]:
                cpu_paddle.y += paddle_speed*dt

        paddle.top = max(paddle.top,0)
        paddle.bottom = min(paddle.bottom,600)
        cpu_paddle.top = max(cpu_paddle.top,0)
        cpu_paddle.bottom = min(cpu_paddle.bottom,600)

        # move ball
        ball_pos[0] += ball_speed_x*dt
        ball_pos[1] += ball_speed_y*dt

        # walls
        if ball_pos[1] - ball.height/2 <= 0:
            ball_pos[1] = ball.height/2
            ball_speed_y = abs(ball_speed_y)
        if ball_pos[1] + ball.height/2 >= 600:
            ball_pos[1] = 600 - ball.height/2
            ball_speed_y = -abs(ball_speed_y)

        ball.center = (int(ball_pos[0]), int(ball_pos[1]))

        # trail
        trail.append(tuple(ball.center))
        if len(trail) > 10:
            trail.pop(0)

        # collisions
        if ball.colliderect(paddle):
            ball.left = paddle.right
            ball_pos[0] = ball.centerx
            ball_speed_x *= -1
            spawn_particles(*ball.center, PLAYER_COLOR)

        if ball.colliderect(cpu_paddle):
            ball.right = cpu_paddle.left
            ball_pos[0] = ball.centerx
            ball_speed_x *= -1
            spawn_particles(*ball.center, CPU_COLOR)

        # scoring
        if ball.left <= 0:
            cpu_score += 1
            reset_ball(1)
        if ball.right >= 800:
            player_score += 1
            reset_ball(-1)

        if player_score >= WIN_SCORE or cpu_score >= WIN_SCORE:
            state = "game_over"

    # shake
    offset_x = offset_y = 0
    if shake_timer > 0:
        shake_timer -= dt
        offset_x = random.randint(-5,5)
        offset_y = random.randint(-5,5)

    # render
    screen.fill(BG)

    if state == "menu":
        screen.blit(big_font.render("PONG",True,(255,255,255)),(300,120))
        screen.blit(font.render("1 - Easy CPU",True,PLAYER_COLOR),(280,260))
        screen.blit(font.render("2 - Medium CPU",True,(255,255,255)),(260,310))
        screen.blit(font.render("3 - Hard CPU",True,CPU_COLOR),(280,360))
        screen.blit(font.render("4 - vs Player",True,(200,200,200)),(280,410))
        screen.blit(font.render("Q to quit",True,(150,150,150)),(310,500))

    elif state == "play":
        pygame.draw.line(screen,(100,100,255),(400,0),(400,600),2)
        pygame.draw.rect(screen,PLAYER_COLOR,paddle.move(offset_x,offset_y))
        pygame.draw.rect(screen,CPU_COLOR,cpu_paddle.move(offset_x,offset_y))
        pygame.draw.ellipse(screen,BALL_COLOR,ball.move(offset_x,offset_y))

        for pos in trail:
            pygame.draw.circle(screen,(255,255,255),pos,5)

        screen.blit(font.render(str(player_score),True,PLAYER_COLOR),(300,20))
        screen.blit(font.render(str(cpu_score),True,CPU_COLOR),(460,20))

    elif state == "pause":
        screen.blit(big_font.render("PAUSED",True,(255,255,255)),(260,250))
        screen.blit(font.render("P to resume",True,(200,200,200)),(300,320))
        screen.blit(font.render("O for settings",True,(200,200,200)),(270,370))

    elif state == "settings":
        screen.blit(big_font.render("SETTINGS",True,(255,255,255)),(240,150))
        screen.blit(font.render("1 Easy  2 Medium  3 Hard",True,(255,255,255)),(200,300))
        screen.blit(font.render(f"Current: {difficulty}",True,(200,200,200)),(260,400))
        screen.blit(font.render("ESC to go back",True,(150,150,150)),(260,500))

    elif state == "game_over":
        winner = "You Win!" if player_score > cpu_score else "CPU Wins!"
        screen.blit(big_font.render(winner,True,(255,255,255)),(200,200))
        screen.blit(font.render("Press any key",True,(200,200,200)),(280,300))

    pygame.display.flip()

pygame.quit()
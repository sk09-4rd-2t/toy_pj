import pygame
import sys
import math

# 초기화
pygame.init()

# 화면 크기 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("졸라맨 움직이기")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 69, 0)

# 졸라맨 변수
x, y = WIDTH // 2, HEIGHT // 2
speed = 5
arm_angle = 0
arm_direction = 1
leg_angle = 0
leg_direction = 1
moving = False
jumping = False
jump_power = 15
gravity = 1
velocity_y = 0

# FPS 설정
clock = pygame.time.Clock()

# 졸라맨 그리기 함수
def draw_stickman(x, y, arm_angle, leg_angle):
    # 머리
    pygame.draw.circle(screen, BLACK, (x, y - 30), 20, 2)
    # 몸통
    pygame.draw.line(screen, BLACK, (x, y - 10), (x, y + 30), 2)
    # 기본 팔
    pygame.draw.line(screen, BLACK, (x - 20, y), (x + 20, y), 2)

    # 팔 늘린 선 (45도 방향, 흔들림 반영)
    length = 50
    left_arm_end = (x - 20 - int(length * math.cos(math.radians(65))), y - int(length * math.sin(math.radians(65))) - int(arm_angle))
    right_arm_end = (x + 20 + int(length * math.cos(math.radians(65))), y - int(length * math.sin(math.radians(65))) + int(arm_angle))

    pygame.draw.line(screen, BLACK, (x - 20, y), left_arm_end, 3)
    pygame.draw.line(screen, BLACK, (x + 20, y), right_arm_end, 3)

    # 다리 (움직임 반영)
    left_leg_end = (x - 20, y + 90 + int(leg_angle))
    right_leg_end = (x + 20, y + 90 - int(leg_angle))

    pygame.draw.line(screen, BLACK, (x, y + 30), left_leg_end, 2)
    pygame.draw.line(screen, BLACK, (x, y + 30), right_leg_end, 2)

# 게임 루프
while True:
    moving = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not jumping:
                jumping = True
                velocity_y = -jump_power

    # 키 입력
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if x - speed > 30:  # 왼쪽 경계 (머리 반지름 20 고려)
            x -= speed
            moving = True
    if keys[pygame.K_RIGHT]:
        if x + speed < WIDTH - 30:  # 오른쪽 경계
            x += speed
            moving = True


    # 점프 물리
    if jumping:
        y += velocity_y
        velocity_y += gravity
        if y >= HEIGHT // 2:
            y = HEIGHT // 2
            jumping = False
            velocity_y = 0

    # 팔, 다리 흔들림 업데이트 (속도 빠르게)
    if moving:
        arm_angle += 4 * arm_direction
        if abs(arm_angle) > 10:
            arm_direction *= -1

        leg_angle += 4 * leg_direction
        if abs(leg_angle) > 10:
            leg_direction *= -1
    else:
        if arm_angle > 0:
            arm_angle -= 1
        elif arm_angle < 0:
            arm_angle += 1

        if leg_angle > 0:
            leg_angle -= 1
        elif leg_angle < 0:
            leg_angle += 1

    # 화면 그리기
    screen.fill(WHITE)
    draw_stickman(x, y, arm_angle, leg_angle)
    pygame.display.flip()

    # FPS
    clock.tick(60)

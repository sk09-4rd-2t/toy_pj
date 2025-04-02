import pygame
import sys

# 기본 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# 색상
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)

# 초기화
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 플레이어 클래스
class Player:
    def __init__(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vel_y = 0
        self.on_ground = False

    def reset(self):
        print("떨어졌습니다! 다시 시작합니다.")
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vel_y = 0

    def update(self, ground_tiles, traps):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15

        # 중력
        self.vel_y += 1
        self.rect.y += self.vel_y

        # 충돌 처리
        self.on_ground = False
        for tile in ground_tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True

        # 트랩 충돌
        for trap in traps:
            if self.rect.colliderect(trap):
                print("함정에 걸림! 다시 시작합니다.")
                self.reset()

        # 구멍에 빠짐 (y값이 화면 아래로 벗어나면)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

# 일반 바닥 (중간에 구멍 뚫려 있음)
ground_tiles = []
for x in range(20):
    if x in [5, 6, 10]:  # 5번, 6번, 10번은 구멍!
        continue
    ground_tiles.append(pygame.Rect(x * TILE_SIZE, 560, TILE_SIZE, TILE_SIZE))

# 트랩
traps = [pygame.Rect(300, 520, TILE_SIZE, TILE_SIZE)]

# 플레이어 생성
player = Player(100, 300)

# 게임 루프
running = True
while running:
    clock.tick(FPS)
    screen.fill(SKY_BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 업데이트
    player.update(ground_tiles, traps)

    # 그리기
    for tile in ground_tiles:
        pygame.draw.rect(screen, GRAY, tile)
    for trap in traps:
        pygame.draw.rect(screen, RED, trap)
    player.draw(screen)

    pygame.display.update()

pygame.quit()
sys.exit()

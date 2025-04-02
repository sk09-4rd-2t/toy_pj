import pygame
import sys
import random

# Pygame 초기화 (Initialize Pygame)
pygame.init()

# 화면 설정 (Screen settings)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 색상 정의 (Color definitions)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 화면 생성 (Create screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("환쨩의 마리오")
clock = pygame.time.Clock()

# 이미지 불러오기 함수 (Image loading function)
def load_image(filename, scale=1):
    try:
        image = pygame.image.load(filename).convert_alpha()
        original_size = image.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        return pygame.transform.scale(image, new_size)
    except:
        # 이미지를 찾을 수 없는 경우 임시 이미지 생성 (Create temporary image if file not found)
        temp_surface = pygame.Surface((50, 50))
        temp_surface.fill(RED)
        return temp_surface

# 카메라 클래스 - 맵 스크롤링 관리 (Camera class - manages map scrolling)
class Camera:
    def __init__(self, map_width):
        self.camera_x = 0
        self.camera_y = 0
        self.map_width = map_width
    
    def update(self, target):
        # 고양이가 화면의 3/5 지점을 넘어가면 카메라가 따라옴 (Camera follows when cat moves beyond 3/5 of the screen)
        screen_focus_x = SCREEN_WIDTH * 3/5
        
        # 타겟이 포커스 지점을 넘어가고 카메라가 맵 끝에 도달하지 않았을 때 (Follow target if it's beyond focus point and camera hasn't reached map edge)
        if target.x - self.camera_x > screen_focus_x and self.camera_x < self.map_width - SCREEN_WIDTH:
            self.camera_x = min(target.x - screen_focus_x, self.map_width - SCREEN_WIDTH)
        
        # 타겟이 왼쪽으로 이동할 때 (카메라 한계) (Follow when target moves left with camera limit)
        if target.x - self.camera_x < SCREEN_WIDTH * 1/5 and self.camera_x > 0:
            self.camera_x = max(target.x - SCREEN_WIDTH * 1/5, 0)
    
    def apply(self, obj):
        # 카메라 기준으로 객체의 상대적 위치 반환 (Return object's position relative to camera)
        return obj.x - self.camera_x, obj.y - self.camera_y

# 고양이 플레이어 클래스 (Cat player class)
class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.lives = 3
        
        # 점프 관련 변수 (Jump-related variables) - 이중 점프 제거
        self.jump_held = False        # 점프 키 홀드 상태 (Jump key held status)
        self.jump_time = 0            # 점프 지속 시간 (Jump duration)
        self.max_jump_time = 15       # 최대 점프 유지 시간 (Maximum jump hold time)
        
        # 실제 이미지로 나중에 대체. 현재는 도형 사용 (Replace with actual image later. Using shape for now)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)
        
    def update(self, platforms, traps, keys):
        # 이전 위치 저장 (Store previous position)
        prev_x = self.x
        prev_y = self.y
        
        # 중력 적용 (Apply gravity)
        self.velocity_y += self.gravity
        
        # 점프 키를 누른 상태에서 추가 점프력 적용 (Apply additional jump force when jump key is held)
        if keys[pygame.K_SPACE] and self.jump_held and self.jump_time < self.max_jump_time:
            self.velocity_y = self.jump_power * 0.6
            self.jump_time += 1
        
        # 위치 업데이트 (Update position) - X와 Y 분리하여 충돌 체크 개선
        self.x += self.velocity_x  # X 방향 이동
        
        # X 방향 충돌 체크 (Horizontal collision check)
        for platform in platforms:
            if self.collision_check(platform):
                # 왼쪽이나 오른쪽 충돌 (Left or right collision)
                if self.velocity_x > 0:  # 오른쪽 이동 중 (Moving right)
                    self.x = platform.x - self.width
                elif self.velocity_x < 0:  # 왼쪽 이동 중 (Moving left)
                    self.x = platform.x + platform.width
        
        # Y 방향 이동 (Vertical movement)
        self.y += self.velocity_y
        
        # 화면 경계 체크 (왼쪽만, 오른쪽은 맵 계속됨) (Check screen boundaries, only left as right side is open for map continuation)
        if self.x < 0:
            self.x = 0
        
        # 플랫폼 충돌 체크 (Platform collision check) - Y 방향만
        self.on_ground = False
        for platform in platforms:
            if self.collision_check(platform):
                # 플랫폼 위에 착지 (Landing on top of platform)
                if self.velocity_y > 0 and prev_y + self.height <= platform.y + 5:
                    self.on_ground = True
                    self.velocity_y = 0
                    self.y = platform.y - self.height
                # 플랫폼 밑에서 부딪힘 (Hitting platform from below)
                elif self.velocity_y < 0 and prev_y >= platform.y + platform.height - 5:
                    self.velocity_y = 0
                    self.y = platform.y + platform.height
                    self.jump_time = self.max_jump_time  # 점프 중단 (Stop jump)
        
        # 함정 충돌 체크 (Trap collision check)
        for trap in traps:
            if self.collision_check(trap):
                self.lives -= 1
                self.x = 100  # 리스폰 위치 (Respawn position)
                self.y = 300
                break
        
        # 화면 밖으로 떨어짐 (Falling off the screen)
        if self.y > SCREEN_HEIGHT:
            self.lives -= 1
            self.x = 100  # 리스폰 위치 (Respawn position)
            self.y = 300
    
    def jump(self, held=False):
        # 점프 키를 눌렀을 때 (When jump key is pressed)
        if held:
            # 키를 처음 눌렀을 때만 점프 시작 (Start jump only when key is first pressed)
            if not self.jump_held and self.on_ground:  # 이중 점프 제거, 바닥에서만 점프 가능
                self.velocity_y = self.jump_power
                self.on_ground = False
                self.jump_time = 0
                self.jump_held = True
        else:
            # 점프 키를 뗐을 때 홀드 상태 해제 (Release hold state when jump key is released)
            self.jump_held = False
            self.jump_time = self.max_jump_time
    
    def draw(self, camera):
        # 카메라 적용하여 화면 위치 계산 (Apply camera to calculate screen position)
        screen_x, screen_y = camera.apply(self)
        screen.blit(self.image, (screen_x, screen_y))
    
    def collision_check(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)

# 플랫폼 클래스 (Platform class)
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
    
    def draw(self, camera):
        screen_x, screen_y = camera.apply(self)
        # 화면에 보일 때만 그리기 (최적화) (Only draw if on screen - optimization)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 함정 클래스 (Trap class)
class Trap:
    def __init__(self, x, y, width, height, trap_type='basic'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.trap_type = trap_type
        self.image = pygame.Surface((width, height))
        
        # 함정 타입에 따른 색상 (Different colors based on trap type)
        if self.trap_type == 'spike':
            self.image.fill(RED)
        elif self.trap_type == 'lava':
            self.image.fill((255, 100, 0))  # 주황색 (Orange)
        elif self.trap_type == 'poison':
            self.image.fill((128, 0, 128))  # 보라색 (Purple)
        elif self.trap_type == 'hidden':
            self.image.fill((50, 50, 50))   # 어두운 회색 (바닥과 유사) (Dark gray, similar to floor)
        else:
            self.image.fill(RED)
    
    def draw(self, camera):
        screen_x, screen_y = camera.apply(self)
        # 화면에 보일 때만 그리기 (최적화) (Only draw if on screen - optimization)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 수집 아이템 클래스 (Collectible item class)
class Item:
    def __init__(self, x, y, item_type='coin'):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.item_type = item_type
        self.image = pygame.Surface((self.width, self.height))
        
        if self.item_type == 'coin':
            self.image.fill(YELLOW)
        elif self.item_type == 'life':
            self.image.fill((0, 255, 0))  # 밝은 초록색 (Bright green)
        elif self.item_type == 'powerup':
            self.image.fill((255, 0, 255))  # 분홍색 (Pink)
        else:
            self.image.fill(YELLOW)
    
    def draw(self, camera):
        screen_x, screen_y = camera.apply(self)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 맵 생성 함수 - 높이 및 간격 조정 (Map generation function - adjusted heights and spacing)
def generate_map():
    platforms = []
    traps = []
    items = []
    
    # 맵 전체 너비 (Total map width)
    map_width = 5000
    
    # 스테이지 1: 시작 영역 (Stage 1: Starting area)
    # ===================================================
    
    # 바닥 플랫폼 (Floor platforms)
    platforms.append(Platform(0, 550, 600, 50))      # 시작 지점 바닥 (Starting area floor)
    platforms.append(Platform(700, 550, 300, 50))    # 첫 번째 점프 후 바닥 (Floor after first jump)
    platforms.append(Platform(1100, 550, 400, 50))   # 두 번째 구간 바닥 (Second section floor)
    
    # 첫 번째 함정 구간 (First trap section)
    traps.append(Trap(600, 550, 100, 50, 'lava'))    # 첫 번째 구멍 (First gap)
    traps.append(Trap(1000, 550, 100, 50, 'lava'))   # 두 번째 구멍 (Second gap)
    
    # 첫 번째 아이템들 (First items)
    items.append(Item(300, 480, 'coin'))
    items.append(Item(350, 480, 'coin'))
    items.append(Item(400, 480, 'coin'))
    items.append(Item(800, 480, 'coin'))
    items.append(Item(850, 480, 'coin'))
    items.append(Item(900, 480, 'coin'))
    
    # 스테이지 2: 플랫폼 점프 영역 (Stage 2: Platform jumping area)
    # ===================================================
    
    # 메인 바닥 플랫폼 (Main floor platform)
    platforms.append(Platform(1600, 550, 700, 50))
    
    # 점프 플랫폼 시퀀스 - 단일 점프로 도달 가능하도록 조정
    # Jump platform sequence - adjusted to be reachable with a single jump
    platforms.append(Platform(1700, 470, 100, 20))   # 높이 하향 조정 (Lowered height)
    platforms.append(Platform(1850, 470, 100, 20))   # 높이 통일 (Unified height)
    platforms.append(Platform(2000, 470, 100, 20))   # 높이 통일 (Unified height)
    platforms.append(Platform(2150, 470, 100, 20))   # 높이 통일 (Unified height)
    
    # 코인 경로 조정 (Adjusted coin path)
    items.append(Item(1750, 420, 'coin'))
    items.append(Item(1900, 420, 'coin'))
    items.append(Item(2050, 420, 'coin'))
    items.append(Item(2200, 420, 'coin'))
    
    # 생명 아이템 (Life item)
    items.append(Item(2150, 420, 'life'))
    
    # 스테이지 3: 함정 도전 구간 (Stage 3: Trap challenge)
    # ===================================================
    
    # 메인 바닥 (Main floor)
    platforms.append(Platform(2400, 550, 800, 50))
    
    # 함정 배치 (Trap placement)
    traps.append(Trap(2500, 530, 50, 20, 'spike'))
    traps.append(Trap(2600, 530, 50, 20, 'spike'))
    traps.append(Trap(2700, 530, 50, 20, 'spike'))
    traps.append(Trap(2900, 530, 50, 20, 'hidden'))
    traps.append(Trap(3000, 530, 50, 20, 'hidden'))
    
    # 점프해서 피해가는 플랫폼 - 높이 조정 (Platforms to jump over traps - adjusted height)
    platforms.append(Platform(2500, 470, 300, 20))  # 높이 하향 조정 (Lowered height)
    platforms.append(Platform(2900, 470, 200, 20))  # 높이 하향 조정 (Lowered height)
    
    # 코인 배치 (Coin placement)
    for i in range(5):
        items.append(Item(2500 + i*60, 420, 'coin'))
    
    for i in range(3):
        items.append(Item(2900 + i*60, 420, 'coin'))
    
    # 파워업 아이템 (Power-up item)
    items.append(Item(3100, 420, 'powerup'))
    
    # 스테이지 4: 어려운 점프 구간 (Stage 4: Difficult jumping section)
    # ===================================================
    
    # 작은 발판 시퀀스 - 단일 점프로 도달 가능하도록 조정
    # Small platform sequence - adjusted to be reachable with a single jump
    platforms.append(Platform(3300, 550, 100, 50))
    platforms.append(Platform(3450, 490, 80, 20))  # 간격 및 높이 조정 (Adjusted spacing and height)
    platforms.append(Platform(3600, 490, 80, 20))  # 높이 통일 (Unified height)
    platforms.append(Platform(3750, 490, 80, 20))  # 높이 통일 (Unified height)
    platforms.append(Platform(3900, 550, 100, 50))
    
    # 코인 배치 (Coin placement)
    items.append(Item(3490, 440, 'coin'))
    items.append(Item(3640, 440, 'coin'))
    items.append(Item(3790, 440, 'coin'))
    
    # 스테이지 5: 최종 도전 구간 (Stage 5: Final challenge)
    # ===================================================
    
    # 마지막 바닥 구간 (Last floor section)
    platforms.append(Platform(4150, 550, 300, 50))
    
    # 최종 점프 챌린지 - 간격 및 높이 조정 (Final jump challenge - adjusted spacing and height)
    platforms.append(Platform(4500, 500, 80, 20))  # 간격 및 높이 조정 (Adjusted spacing and height)
    platforms.append(Platform(4630, 500, 80, 20))  # 높이 통일 (Unified height)
    platforms.append(Platform(4760, 500, 80, 20))  # 높이 통일 (Unified height)
    platforms.append(Platform(4890, 500, 150, 20))  # 최종 목표 플랫폼 (Final goal platform)
    
    # 최종 함정 (Final traps)
    traps.append(Trap(4450, 550, 440, 50, 'lava'))  # 큰 용암 웅덩이 (Large lava pit)
    
    # 최종 보상 (Final rewards)
    items.append(Item(4540, 450, 'coin'))
    items.append(Item(4670, 450, 'coin'))
    items.append(Item(4800, 450, 'coin'))
    items.append(Item(4950, 450, 'life'))  # 마지막 생명 아이템 (Final life item)
    
    return platforms, traps, items, map_width

# 게임 초기화 (Game initialization)
cat_player = Cat(100, 300)
platforms, traps, items, map_width = generate_map()
camera_obj = Camera(map_width)
game_running = True
font = pygame.font.SysFont('Arial', 24)  # 보다 보편적인 폰트로 변경 (Changed to a more universal font)
score = 0

# 게임 메인 루프 (Game main loop)
while game_running:
    # 이벤트 처리 (Event handling)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        
        # 키 입력 처리 (Key press handling)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                cat_player.jump(True)  # 점프 키 누름 (Jump key pressed)
            # 재시작 키 추가 (Add restart key)
            if event.key == pygame.K_r:
                cat_player = Cat(100, 300)
                platforms, traps, items, map_width = generate_map()
                camera_obj = Camera(map_width)
                score = 0
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                cat_player.jump(False)  # 점프 키 뗌 (Jump key released)
    
    # 키 상태 체크 (Key state check)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        cat_player.velocity_x = -5
    elif keys[pygame.K_RIGHT]:
        cat_player.velocity_x = 5
    else:
        cat_player.velocity_x = 0
    
    # 플레이어 업데이트 (Player update)
    cat_player.update(platforms, traps, keys)
    
    # 카메라 업데이트 (Camera update)
    camera_obj.update(cat_player)
    
    # 아이템 수집 체크 (Item collection check)
    for item_obj in items[:]:
        if (cat_player.x < item_obj.x + item_obj.width and
            cat_player.x + cat_player.width > item_obj.x and
            cat_player.y < item_obj.y + item_obj.height and
            cat_player.y + cat_player.height > item_obj.y):
            
            # 아이템 타입에 따른 효과 적용 (Apply effect based on item type)
            if item_obj.item_type == 'coin':
                score += 100
            elif item_obj.item_type == 'life':
                cat_player.lives += 1
            elif item_obj.item_type == 'powerup':
                # 파워업 효과 - 예: 점프 강화 (구현 예정) (Powerup effect - e.g. jump boost, to be implemented)
                score += 500
            
            # 수집된 아이템 제거 (Remove collected item)
            items.remove(item_obj)
    
    # 게임 오버 체크 (Game over check)
    if cat_player.lives <= 0:
        text = font.render(f"Game Over! Score: {score} - Press R to restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        
        # 재시작 대기 (Wait for restart)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    cat_player = Cat(100, 300)
                    platforms, traps, items, map_width = generate_map()
                    camera_obj = Camera(map_width)
                    score = 0
                    waiting = False
        
        if not game_running:
            break
    
    # 목표 도달 체크 (맵 끝) (Goal reached check - end of map)
    if cat_player.x >= map_width - 300:
        text = font.render(f"Congratulations! Score: {score} - Press R to restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        
        # 재시작 대기 (Wait for restart)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    cat_player = Cat(100, 300)
                    platforms, traps, items, map_width = generate_map()
                    camera_obj = Camera(map_width)
                    score = 0
                    waiting = False
        
        if not game_running:
            break
    
    # 그리기 (Drawing)
    screen.fill(BLACK)
    
    # 배경 그리드 패턴 (시각적 스크롤 참조용) (Background grid pattern for visual scrolling reference)
    grid_size = 100
    grid_offset_x = camera_obj.camera_x 
    grid_offset_y = camera_obj.camera_y
    
    for x in range(int(grid_offset_x/grid_size) - 1, int(grid_offset_x/grid_size) + int(SCREEN_WIDTH/grid_size) + 2):
        for y in range(int(grid_offset_y/grid_size) - 1, int(grid_offset_y/grid_size) + int(SCREEN_HEIGHT/grid_size) + 2):
            screen_x = x * grid_size - grid_offset_x
            screen_y = y * grid_size - grid_offset_y
            pygame.draw.rect(screen, (30, 30, 30), (screen_x, screen_y, grid_size, grid_size), 1)
    
    # 카메라 적용하여 모든 객체 그리기 (Draw all objects with camera applied)
    for platform in platforms:
        platform.draw(camera_obj)
    
    for trap in traps:
        trap.draw(camera_obj)
    
    for item_obj in items:
        item_obj.draw(camera_obj)
    
    cat_player.draw(camera_obj)
    
    # 목숨과 점수 표시 (Display lives and score)
    lives_text = font.render(f"Lives: {cat_player.lives}", True, WHITE)
    screen.blit(lives_text, (20, 20))
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 50))
    
    # 현재 위치 표시 (Display current position)
    position_text = font.render(f"Position: {int(cat_player.x)}/{map_width}", True, WHITE)
    screen.blit(position_text, (20, 80))
    
    # 점프 상태 표시 제거 (Removed jump status display)
    
    # 화면 업데이트 (Update screen)
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Pygame 종료 (Quit Pygame)
pygame.quit()
sys.exit()
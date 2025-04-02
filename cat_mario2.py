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
pygame.display.set_caption("Cat Mario")
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
        
        # 점프 관련 변수 추가 (Add jump-related variables)
        self.can_double_jump = False  # 이중 점프 가능 여부 (Double jump availability)
        self.jump_count = 0           # 점프 횟수 카운트 (Jump count)
        self.jump_held = False        # 점프 키 홀드 상태 (Jump key held status)
        self.jump_time = 0            # 점프 지속 시간 (Jump duration)
        self.max_jump_time = 15       # 최대 점프 유지 시간 (Maximum jump hold time)
        
        # 실제 이미지로 나중에 대체. 현재는 도형 사용 (Replace with actual image later. Using shape for now)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)
        
    def update(self, platforms, traps, keys):
        # 중력 적용 (Apply gravity)
        self.velocity_y += self.gravity
        
        # 점프 키를 누른 상태에서 추가 점프력 적용 (Apply additional jump force when jump key is held)
        if keys[pygame.K_SPACE] and self.jump_held and self.jump_time < self.max_jump_time:
            self.velocity_y = self.jump_power * 0.6
            self.jump_time += 1
        
        # 위치 업데이트 (Update position)
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # 화면 경계 체크 (왼쪽만, 오른쪽은 맵 계속됨) (Check screen boundaries, only left as right side is open for map continuation)
        if self.x < 0:
            self.x = 0
        
        # 플랫폼 충돌 체크 (Platform collision check)
        self.on_ground = False
        for platform in platforms:
            if self.collision_check(platform):
                # 플랫폼 위에 착지 (Landing on top of platform)
                if self.velocity_y > 0 and self.y + self.height <= platform.y + 10:
                    self.on_ground = True
                    self.velocity_y = 0
                    self.y = platform.y - self.height
                    self.jump_count = 0  # 착지 시 점프 카운트 초기화 (Reset jump count when landing)
                    self.can_double_jump = True  # 이중 점프 능력 회복 (Restore double jump ability)
                # 플랫폼 밑에서 부딪힘 (Hitting platform from below)
                elif self.velocity_y < 0 and self.y >= platform.y + platform.height - 10:
                    self.velocity_y = 0
                    self.y = platform.y + platform.height
                    self.jump_time = self.max_jump_time  # 점프 중단 (Stop jump)
        
        # 함정 충돌 체크 (Trap collision check)
        for trap in traps:
            if self.collision_check(trap):
                self.lives -= 1
                self.x = 100  # 리스폰 위치 (Respawn position)
                self.y = 300
                self.jump_count = 0  # 리스폰 시 점프 카운트 초기화 (Reset jump count on respawn)
                break
        
        # 화면 밖으로 떨어짐 (Falling off the screen)
        if self.y > SCREEN_HEIGHT:
            self.lives -= 1
            self.x = 100  # 리스폰 위치 (Respawn position)
            self.y = 300
            self.jump_count = 0  # 리스폰 시 점프 카운트 초기화 (Reset jump count on respawn)
    
    def jump(self, held=False):
        # 점프 키를 눌렀을 때 (When jump key is pressed)
        if held:
            # 키를 처음 눌렀을 때만 점프 시작 (Start jump only when key is first pressed)
            if not self.jump_held:
                if self.on_ground:
                    # 바닥에서 첫 번째 점프 (First jump from ground)
                    self.velocity_y = self.jump_power
                    self.on_ground = False
                    self.jump_count = 1
                    self.jump_time = 0
                    self.jump_held = True
                elif self.can_double_jump and self.jump_count < 2:
                    # 공중에서 이중 점프 (Double jump in air)
                    self.velocity_y = self.jump_power * 0.8
                    self.jump_count = 2
                    self.can_double_jump = False
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

# 맵 생성 함수 (많은 함정 포함) (Map generation function with many traps)
def generate_map():
    platforms = []
    traps = []
    items = []
    
    # 맵 전체 너비 (Total map width)
    map_width = 5000
    
    # 바닥 플랫폼 (여러 조각으로 나눔) (Floor platforms divided into segments)
    floor_gap = 100  # 구멍 크기 (Gap size for holes)
    current_x = 0
    
    while current_x < map_width:
        if random.random() < 0.2 and current_x > 300:  # 시작 부분에는 구멍 없음 (No holes at the beginning)
            # 구멍 생성 (Create a hole)
            hole_size = random.randint(1, 2) * floor_gap
            current_x += hole_size
        else:
            # 바닥 조각 생성 (Create floor segment)
            platform_length = random.randint(3, 8) * floor_gap
            platforms.append(Platform(current_x, 550, platform_length, 50))
            
            # 함정 추가 (바닥 위 가시) (Add traps - spikes on floor)
            trap_count = random.randint(0, int(platform_length/floor_gap/2))
            for _ in range(trap_count):
                trap_x = current_x + random.randint(1, int(platform_length/floor_gap) - 1) * floor_gap
                trap_type = random.choice(['spike', 'hidden', 'lava'])
                traps.append(Trap(trap_x, 530, 50, 20, trap_type))
            
            # 코인 추가 (Add coins)
            coin_count = random.randint(0, int(platform_length/floor_gap/2))
            for _ in range(coin_count):
                coin_x = current_x + random.randint(1, int(platform_length/floor_gap) - 1) * floor_gap
                items.append(Item(coin_x, 480, 'coin'))
            
            current_x += platform_length
    
    # 추가 플랫폼 (공중에 떠 있는 것들) (Additional floating platforms)
    for i in range(100):  # 50개에서 100개로 증가 (Increased from 50 to 100 platforms)
        x = random.randint(300, map_width - 300)
        y = random.randint(200, 500)
        width = random.randint(100, 200)
        
        platforms.append(Platform(x, y, width, 20))
        
        # 일부 플랫폼에 함정 추가 (Add traps on some platforms)
        if random.random() < 0.4:  # 40% 확률로 함정 생성 (30%에서 증가) (40% chance for a trap, increased from 30%)
            trap_x = x + random.randint(10, int(width) - 60)
            trap_type = random.choice(['spike', 'poison', 'lava'])
            traps.append(Trap(trap_x, y - 20, 40, 20, trap_type))
        
        # 플랫폼 위에 아이템 추가 (Add items on platforms)
        if random.random() < 0.3:
            item_x = x + width/2
            item_type = random.choice(['coin', 'coin', 'coin', 'life', 'powerup'])
            items.append(Item(item_x, y - 40, item_type))
    
    # 함정 지역 추가 (특별히 어려운 구간) (Add trap zones - especially difficult sections)
    for i in range(5):  # 5개의 어려운 구간 (5 difficult sections)
        start_x = random.randint(1000, map_width - 1000)
        
        # 집중된 함정 구역 만들기 (Create concentrated trap areas)
        for j in range(10):
            trap_x = start_x + j * 50
            trap_y = random.randint(300, 500)
            trap_type = random.choice(['spike', 'lava', 'poison'])
            traps.append(Trap(trap_x, trap_y, 30, 30, trap_type))
    
    # 최종 목표 지점 (Final goal)
    goal_x = map_width - 200
    goal_y = 450
    platforms.append(Platform(goal_x, goal_y, 100, 100))
    
    # 목표 근처에 생명 아이템 추가 (Add life item near goal)
    items.append(Item(goal_x - 100, goal_y - 50, 'life'))
    
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
    
    # 점프 상태 표시 (Display jump status)
    jump_text = font.render(f"Jumps: {cat_player.jump_count}/2", True, WHITE)
    screen.blit(jump_text, (20, 110))
    
    # 화면 업데이트 (Update screen)
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Pygame 종료 (Quit Pygame)
pygame.quit()
sys.exit()
import pygame
import sys
import random
from game import draw_stickman

# Pygame 초기화
pygame.init()

# 한글 폰트 직접 설정 시도 (폰트 파일 경로 구현)
pygame.font.init()  # 폰트 모듈 초기화 확인

# 화면 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 화면 생성
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("환쨩의 마리오")  # 한글 수정
clock = pygame.time.Clock()

# 한글 폰트 설정 - 다양한 시스템 폰트 시도
def get_font():
    # 시스템에 설치된 모든 폰트 확인 (디버깅 용도)
    available_fonts = pygame.font.get_fonts()
    
    # 한글 지원 가능성이 높은 폰트 목록
    korean_fonts = [
        'malgungothic', 'malgun_gothic', 'malgun gothic', 'malgun',  # 맑은 고딕 변형
        'applegothic', 'apple gothic',                               # 맥용 폰트
        'nanumgothic', 'nanum gothic', 'nanum',                      # 나눔고딕 변형
        'gulim', 'gungsuh',                                         # 굴림/궁서
        'dotum', 'batang',                                          # 돋움/바탕
        'baekmuk gulim', 'unbatang',                               # 리눅스 한글 폰트
    ]
    
    # 한글 지원 폰트 시도
    for font_name in korean_fonts:
        if font_name in available_fonts:
            try:
                return pygame.font.SysFont(font_name, 24)
            except:
                continue
    
    # 폴백: 어떤 시스템 폰트든 시도
    try:
        return pygame.font.SysFont(None, 24)
    except:
        pass
    
    # 최후의 수단: 기본 폰트
    return pygame.font.Font(None, 24)

# 폰트 설정
font = get_font()

# 카메라 클래스 - 맵 스크롤링 관리
class Camera:
    def __init__(self, map_width):
        self.camera_x = 0
        self.camera_y = 0
        self.map_width = map_width
    
    def update(self, target):
        # 고양이가 화면의 3/5 지점을 넘어가면 카메라가 따라옴
        screen_focus_x = SCREEN_WIDTH * 3/5
        
        # 타겟이 포커스 지점을 넘어가고 카메라가 맵 끝에 도달하지 않았을 때
        if target.x - self.camera_x > screen_focus_x and self.camera_x < self.map_width - SCREEN_WIDTH:
            self.camera_x = min(target.x - screen_focus_x, self.map_width - SCREEN_WIDTH)
        
        # 타겟이 왼쪽으로 이동할 때 (카메라 한계)
        if target.x - self.camera_x < SCREEN_WIDTH * 1/5 and self.camera_x > 0:
            self.camera_x = max(target.x - SCREEN_WIDTH * 1/5, 0)
    
    def apply(self, obj):
        # 카메라 기준으로 객체의 상대적 위치 반환
        return obj.x - self.camera_x, obj.y - self.camera_y

# 고양이 플레이어 클래스
class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 200
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.lives = 3
        
        # 점프 관련 변수 - 이중 점프 제거
        self.jump_held = False        # 점프 키 홀드 상태
        self.jump_time = 0            # 점프 지속 시간
        self.max_jump_time = 15       # 최대 점프 유지 시간
        

        #-------------------------------------------------250402_15h testing..

        # 졸라맨 팔/다리 흔들림 변수
        self.arm_angle = 0
        self.arm_direction = 1
        self.leg_angle = 0
        self.leg_direction = 1

        #-------------------------------------------------250402_15h testing..


        # 실제 이미지로 나중에 대체. 현재는 도형 사용
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)
        

    def update(self, platforms, traps, keys):
        # 이전 위치 저장
        prev_x = self.x
        prev_y = self.y
        
        # 중력 적용
        self.velocity_y += self.gravity
        
        # 점프 키를 누른 상태에서 추가 점프력 적용
        if keys[pygame.K_SPACE] and self.jump_held and self.jump_time < self.max_jump_time:
            self.velocity_y = self.jump_power * 0.6
            self.jump_time += 1
        

        #-------------------------------------------------250402_15h testing..

         # 이동 입력 체크
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            moving = True

        # 흔들림 업데이트
        if moving:
            self.arm_angle += 4 * self.arm_direction
            if abs(self.arm_angle) > 10:
                self.arm_direction *= -1

            self.leg_angle += 4 * self.leg_direction
            if abs(self.leg_angle) > 10:
                self.leg_direction *= -1
        else:
            if self.arm_angle > 0:
                self.arm_angle -= 1
            elif self.arm_angle < 0:
                self.arm_angle += 1

            if self.leg_angle > 0:
                self.leg_angle -= 1
            elif self.leg_angle < 0:
                self.leg_angle += 1

        #-------------------------------------------------250402_15h testing..



        # 위치 업데이트 - X와 Y 분리하여 충돌 체크 개선
        self.x += self.velocity_x  # X 방향 이동
        
        # X 방향 충돌 체크
        for platform in platforms:
            if self.collision_check(platform):
                # 왼쪽이나 오른쪽 충돌
                if self.velocity_x > 0:  # 오른쪽 이동 중
                    self.x = platform.x - self.width
                elif self.velocity_x < 0:  # 왼쪽 이동 중
                    self.x = platform.x + platform.width
        
        # Y 방향 이동
        self.y += self.velocity_y
        
        # 화면 경계 체크 (왼쪽만, 오른쪽은 맵 계속됨)
        if self.x < 0:
            self.x = 0
        
        # 플랫폼 충돌 체크 - Y 방향만
        self.on_ground = False
        for platform in platforms:
            if self.collision_check(platform):
                # 플랫폼 위에 착지
                if self.velocity_y > 0 and prev_y + self.height <= platform.y + 5:
                    self.on_ground = True
                    self.velocity_y = 0
                    self.y = platform.y - self.height
                # 플랫폼 밑에서 부딪힘
                elif self.velocity_y < 0 and prev_y >= platform.y + platform.height - 5:
                    self.velocity_y = 0
                    self.y = platform.y + platform.height
                    self.jump_time = self.max_jump_time  # 점프 중단
        
        # 함정 충돌 체크
        for trap in traps:
            if self.collision_check(trap):
                self.lives -= 1
                self.x = 100  # 리스폰 위치
                self.y = 300
                break
        
        # 화면 밖으로 떨어짐
        if self.y > SCREEN_HEIGHT:
            self.lives -= 1
            self.x = 100  # 리스폰 위치
            self.y = 300
    
    def jump(self, held=False):
        # 점프 키를 눌렀을 때
        if held:
            # 키를 처음 눌렀을 때만 점프 시작
            if not self.jump_held and self.on_ground:  # 이중 점프 제거, 바닥에서만 점프 가능
                self.velocity_y = self.jump_power
                self.on_ground = False
                self.jump_time = 0
                self.jump_held = True
        else:
            # 점프 키를 뗐을 때 홀드 상태 해제
            self.jump_held = False
            self.jump_time = self.max_jump_time
    
    def draw(self, camera):
        # 카메라 적용하여 화면 위치 계산
        screen_x, screen_y = camera.apply(self)
        
        # 중심 좌표 계산 (self.x, self.y는 왼쪽 위 기준)
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # 스틱맨 그리기 (팔/다리 흔들림 각도는 필요시 조정)
        #draw_stickman(center_x, center_y, arm_angle=0, leg_angle=0)

        draw_stickman(center_x, center_y, arm_angle=self.arm_angle, leg_angle=self.leg_angle)


        
    def collision_check(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)

# 플랫폼 클래스
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
        # 화면에 보일 때만 그리기 (최적화)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 움직이는 플랫폼 클래스 (새로 추가)
class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_range, speed, vertical=False):
        super().__init__(x, y, width, height)
        self.start_pos = x if not vertical else y
        self.move_range = move_range
        self.speed = speed
        self.direction = 1
        self.vertical = vertical
        self.image.fill((0, 200, 200))  # 움직이는 플랫폼 색상 구분
    
    def update(self):
        if self.vertical:
            self.y += self.speed * self.direction
            if self.y > self.start_pos + self.move_range or self.y < self.start_pos:
                self.direction *= -1
        else:
            self.x += self.speed * self.direction
            if self.x > self.start_pos + self.move_range or self.x < self.start_pos:
                self.direction *= -1

# 함정 클래스
class Trap:
    def __init__(self, x, y, width, height, trap_type='basic'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.trap_type = trap_type
        self.image = pygame.Surface((width, height))
        
        # 함정 타입에 따른 색상
        if self.trap_type == 'spike':
            self.image.fill(RED)
        elif self.trap_type == 'lava':
            self.image.fill((255, 100, 0))  # 주황색
        elif self.trap_type == 'poison':
            self.image.fill((128, 0, 128))  # 보라색
        elif self.trap_type == 'hidden':
            self.image.fill((50, 50, 50))   # 어두운 회색 (바닥과 유사)
        else:
            self.image.fill(RED)
    
    def draw(self, camera):
        screen_x, screen_y = camera.apply(self)
        # 화면에 보일 때만 그리기 (최적화)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 나타났다 사라지는 함정 클래스 (새로 추가)
class DisappearingTrap(Trap):
    def __init__(self, x, y, width, height, trap_type='basic', interval=60):
        super().__init__(x, y, width, height, trap_type)
        self.interval = interval
        self.timer = 0
        self.visible = True
    
    def update(self):
        self.timer += 1
        if self.timer >= self.interval:
            self.visible = not self.visible
            self.timer = 0
    
    def draw(self, camera):
        if self.visible:
            super().draw(camera)

# 수집 아이템 클래스
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
            self.image.fill((0, 255, 0))  # 밝은 초록색
        elif self.item_type == 'powerup':
            self.image.fill((255, 0, 255))  # 분홍색
        else:
            self.image.fill(YELLOW)
    
    def draw(self, camera):
        screen_x, screen_y = camera.apply(self)
        if -self.width < screen_x < SCREEN_WIDTH and -self.height < screen_y < SCREEN_HEIGHT:
            screen.blit(self.image, (screen_x, screen_y))

# 맵 생성 함수 - 더 어렵게 만듦
def generate_map():
    platforms = []
    moving_platforms = []
    traps = []
    disappearing_traps = []
    items = []
    
    # 맵 전체 너비
    map_width = 8000  # 맵 확장
    
    # 스테이지 1: 시작 영역
    # ===================================================
    
    # 바닥 플랫폼
    platforms.append(Platform(0, 550, 500, 50))      # 시작 지점 바닥
    platforms.append(Platform(650, 550, 200, 50))    # 첫 번째 점프 후 바닥 - 간격 확대
    platforms.append(Platform(950, 550, 300, 50))    # 두 번째 구간 바닥 - 간격 확대
    
    # 첫 번째 함정 구간
    traps.append(Trap(500, 550, 150, 50, 'lava'))    # 첫 번째 구멍 - 너비 확대
    traps.append(Trap(850, 550, 100, 50, 'lava'))    # 두 번째 구멍
    
    # 첫 번째 아이템들
    items.append(Item(300, 480, 'coin'))
    items.append(Item(350, 480, 'coin'))
    items.append(Item(400, 480, 'coin'))
    items.append(Item(700, 480, 'coin'))
    items.append(Item(750, 480, 'coin'))
    
    # 스테이지 2: 움직이는 플랫폼 챌린지 (새로운 스테이지)
    # ===================================================
    
    # 메인 바닥 플랫폼
    platforms.append(Platform(1350, 550, 500, 50))
    
    # 움직이는 플랫폼 추가
    moving_platforms.append(MovingPlatform(1250, 450, 100, 20, 200, 2))  # 좌우 이동 플랫폼
    moving_platforms.append(MovingPlatform(1500, 350, 100, 20, 150, 3, True))  # 상하 이동 플랫폼
    moving_platforms.append(MovingPlatform(1700, 400, 100, 20, 250, 4))  # 좌우 이동 플랫폼 (빠름)
    
    # 코인 배치
    for i in range(5):
        items.append(Item(1450 + i*50, 300, 'coin'))
    
    # 스테이지 3: 플랫폼 점프 영역 - 더 어렵게
    # ===================================================
    
    # 메인 바닥 플랫폼
    platforms.append(Platform(2000, 550, 600, 50))
    
    # 점프 플랫폼 시퀀스 - 간격 확대, 높이 증가로 난이도 상승
    platforms.append(Platform(2100, 470, 80, 20))
    platforms.append(Platform(2250, 440, 80, 20))   # 약간 더 높게
    platforms.append(Platform(2400, 410, 80, 20))   # 더 높게
    platforms.append(Platform(2550, 380, 80, 20))   # 더 높게
    
    # 좁은 점프 플랫폼 추가
    platforms.append(Platform(2700, 380, 40, 20))   # 더 좁은 플랫폼
    platforms.append(Platform(2800, 380, 40, 20))   # 더 좁은 플랫폼
    
    # 코인 경로 조정
    items.append(Item(2140, 420, 'coin'))
    items.append(Item(2290, 390, 'coin'))
    items.append(Item(2440, 360, 'coin'))
    items.append(Item(2590, 330, 'coin'))
    items.append(Item(2720, 330, 'coin'))
    items.append(Item(2820, 330, 'powerup'))  # 파워업 아이템
    
    # 스테이지 4: 함정 도전 구간 - 더 위험하게
    # ===================================================
    
    # 메인 바닥
    platforms.append(Platform(3000, 550, 1000, 50))
    
    # 함정 배치 - 더 많은 함정, 더 조밀하게
    for i in range(8):
        if i % 2 == 0:
            traps.append(Trap(3100 + i*100, 530, 50, 20, 'spike'))
        else:
            disappearing_traps.append(DisappearingTrap(3100 + i*100, 530, 50, 20, 'poison', 45))
    
    # 나타났다 사라지는 함정 추가
    for i in range(3):
        disappearing_traps.append(DisappearingTrap(3500 + i*120, 430, 80, 20, 'lava', 60))
    
    # 점프해서 피해가는 플랫폼
    platforms.append(Platform(3100, 470, 250, 20))
    platforms.append(Platform(3400, 470, 200, 20))
    platforms.append(Platform(3650, 470, 150, 20))
    
    # 더 높은 플랫폼 & 움직이는 플랫폼 조합
    platforms.append(Platform(3850, 400, 100, 20))
    moving_platforms.append(MovingPlatform(3600, 350, 100, 20, 200, 3))
    
    # 코인 배치
    for i in range(5):
        items.append(Item(3100 + i*90, 420, 'coin'))
    
    items.append(Item(3750, 350, 'life'))  # 생명 아이템
    
    # 스테이지 5: 매우 어려운 점프 구간
    # ===================================================
    
    # 베이스 플랫폼
    platforms.append(Platform(4200, 550, 200, 50))
    
    # 극단적으로 작은 발판들
    platforms.append(Platform(4450, 520, 40, 20))
    platforms.append(Platform(4550, 490, 40, 20))
    platforms.append(Platform(4650, 460, 30, 20))  # 더 작게
    platforms.append(Platform(4750, 430, 30, 20))
    platforms.append(Platform(4850, 400, 20, 20))  # 매우 작게
    platforms.append(Platform(4950, 400, 100, 20))  # 도착 플랫폼
    
    # 움직이는 플랫폼 구간
    moving_platforms.append(MovingPlatform(5100, 400, 60, 20, 100, 2))
    moving_platforms.append(MovingPlatform(5250, 400, 60, 20, 150, 3, True))
    moving_platforms.append(MovingPlatform(5400, 350, 60, 20, 200, 4))
    
    # 함정 구간
    traps.append(Trap(4400, 550, 700, 50, 'lava'))  # 큰 용암 웅덩이
    
    # 아이템
    items.append(Item(4950, 350, 'powerup'))  # 파워업
    
    # 스테이지 6: 움직임 타이밍 챌린지
    # ===================================================
    
    # 베이스 플랫폼
    platforms.append(Platform(5600, 550, 300, 50))
    
    # 복잡한 움직이는 플랫폼 패턴 (상하 & 좌우)
    moving_platforms.append(MovingPlatform(5950, 500, 80, 20, 150, 3))
    moving_platforms.append(MovingPlatform(6150, 450, 80, 20, 200, 5, True))
    moving_platforms.append(MovingPlatform(6350, 500, 80, 20, 180, 4))
    moving_platforms.append(MovingPlatform(6550, 550, 80, 20, 250, 6, True))
    moving_platforms.append(MovingPlatform(6750, 450, 80, 20, 200, 5))
    
    # 사라지는 함정 배치
    for i in range(5):
        disappearing_traps.append(DisappearingTrap(6000 + i*200, 600, 150, 50, 'lava', 90-i*10))
    
    # 코인 배치
    for i in range(5):
        items.append(Item(6000 + i*200, 400, 'coin'))
    
    # 스테이지 7: 최종 도전 구간
    # ===================================================
    
    # 최종 시작 플랫폼
    platforms.append(Platform(7000, 550, 200, 50))
    
    # 최종 점프 챌린지 - 매우 어렵게
    # 점점 작아지고 높아지는 플랫폼들
    platforms.append(Platform(7250, 520, 40, 20))
    platforms.append(Platform(7350, 490, 35, 20))
    platforms.append(Platform(7450, 460, 30, 20))
    platforms.append(Platform(7550, 430, 25, 20))
    platforms.append(Platform(7650, 400, 20, 20))
    
    # 이동하는 최종 목표 플랫폼
    moving_platforms.append(MovingPlatform(7750, 370, 100, 20, 150, 3))
    
    # 최종 함정
    traps.append(Trap(7200, 550, 700, 50, 'lava'))  # 큰 용암 웅덩이
    
    # 최종 보상
    items.append(Item(7750, 320, 'life'))  # 마지막 생명 아이템
    items.append(Item(7780, 320, 'powerup'))  # 마지막 파워업
    
    return platforms, moving_platforms, traps, disappearing_traps, items, map_width

# 게임 초기화
cat_player = Cat(100, 300)
platforms, moving_platforms, traps, disappearing_traps, items, map_width = generate_map()
camera_obj = Camera(map_width)
game_running = True
score = 0

# 게임 메인 루프
while game_running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        
        # 키 입력 처리
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                cat_player.jump(True)  # 점프 키 누름
            # 재시작 키 추가
            if event.key == pygame.K_r:
                cat_player = Cat(100, 300)
                platforms, moving_platforms, traps, disappearing_traps, items, map_width = generate_map()
                camera_obj = Camera(map_width)
                score = 0
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                cat_player.jump(False)  # 점프 키 뗌
    
    # 키 상태 체크
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        cat_player.velocity_x = -5
    elif keys[pygame.K_RIGHT]:
        cat_player.velocity_x = 5
    else:
        cat_player.velocity_x = 0
    
    # 움직이는 플랫폼 업데이트
    for platform in moving_platforms:
        platform.update()
    
    # 사라지는 함정 업데이트
    for trap in disappearing_traps:
        trap.update()
    
    # 플레이어 업데이트 - 모든 플랫폼(고정+움직이는) 포함
    all_platforms = platforms + moving_platforms
    all_traps = traps + disappearing_traps
    cat_player.update(all_platforms, all_traps, keys)
    
    # 카메라 업데이트
    camera_obj.update(cat_player)
    
    # 아이템 수집 체크
    for item_obj in items[:]:
        if (cat_player.x < item_obj.x + item_obj.width and
            cat_player.x + cat_player.width > item_obj.x and
            cat_player.y < item_obj.y + item_obj.height and
            cat_player.y + cat_player.height > item_obj.y):
            
            # 아이템 타입에 따른 효과 적용
            if item_obj.item_type == 'coin':
                score += 100
            elif item_obj.item_type == 'life':
                cat_player.lives += 1
            elif item_obj.item_type == 'powerup':
                # 파워업 효과 - 점프 강화
                cat_player.jump_power = -18  # 점프력 강화
                score += 500
            
            # 수집된 아이템 제거
            items.remove(item_obj)
    
    # 게임 오버 체크
    if cat_player.lives <= 0:
        # UTF-8 텍스트 직접 렌더링 방식 시도
        try:
            text = font.render("게임 오버! 점수: {} - R키를 눌러 재시작".format(score), True, WHITE)
        except:
            # 렌더링 실패 시 영어로 대체
            text = font.render("Game Over! Score: {} - Press R to restart".format(score), True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        
        # 재시작 대기
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    cat_player = Cat(100, 300)
                    platforms, moving_platforms, traps, disappearing_traps, items, map_width = generate_map()
                    camera_obj = Camera(map_width)
                    score = 0
                    waiting = False
        
        if not game_running:
            break
    
    # 목표 도달 체크 (맵 끝)
    if cat_player.x >= map_width - 300:
        # UTF-8 텍스트 직접 렌더링 방식 시도
        try:
            text = font.render("끝난줄 알았지? ㅋㅋㅋ", True, WHITE)
        except:
            # 렌더링 실패 시 영어로 대체
            text = font.render("You thought it was over? Haha!", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        
        # 재시작 대기
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    cat_player = Cat(100, 300)
                    platforms, moving_platforms, traps, disappearing_traps, items, map_width = generate_map()
                    camera_obj = Camera(map_width)
                    score = 0
                    waiting = False
        
        if not game_running:
            break
    
    # 그리기
    screen.fill(BLACK)
    
    # 배경 그리드 패턴 (시각적 스크롤 참조용)
    grid_size = 100
    grid_offset_x = camera_obj.camera_x 
    grid_offset_y = camera_obj.camera_y
    
    for x in range(int(grid_offset_x/grid_size) - 1, int(grid_offset_x/grid_size) + int(SCREEN_WIDTH/grid_size) + 2):
        for y in range(int(grid_offset_y/grid_size) - 1, int(grid_offset_y/grid_size) + int(SCREEN_HEIGHT/grid_size) + 2):
            screen_x = x * grid_size - grid_offset_x
            screen_y = y * grid_size - grid_offset_y
            pygame.draw.rect(screen, (30, 30, 30), (screen_x, screen_y, grid_size, grid_size), 1)
    
    # 카메라 적용하여 모든 객체 그리기
    for platform in platforms:
        platform.draw(camera_obj)
    
    for platform in moving_platforms:
        platform.draw(camera_obj)
    
    for trap in traps:
        trap.draw(camera_obj)
        
    for trap in disappearing_traps:
        trap.draw(camera_obj)
    
    for item_obj in items:
        item_obj.draw(camera_obj)
    
    cat_player.draw(camera_obj)
    
    # 목숨과 점수 표시 (영어와 한글 모두 지원)
    try:
        lives_text = font.render("목숨: {}".format(cat_player.lives), True, WHITE)
    except:
        lives_text = font.render("Lives: {}".format(cat_player.lives), True, WHITE)
    screen.blit(lives_text, (20, 20))
    
    try:
        score_text = font.render("점수: {}".format(score), True, WHITE)
    except:
        score_text = font.render("Score: {}".format(score), True, WHITE)
    screen.blit(score_text, (20, 50))
    
    # 현재 위치 표시
    try:
        position_text = font.render("위치: {}/{}".format(int(cat_player.x), map_width), True, WHITE)
    except:
        position_text = font.render("Position: {}/{}".format(int(cat_player.x), map_width), True, WHITE)
    screen.blit(position_text, (20, 80))
    
    # 스테이지 정보 표시 (새로 추가) - 한글 및 영어 대체 로직
    stage_info = ""
    if cat_player.x < 2000:
        stage_info = "스테이지 1-2: 기본 도전"
        eng_fallback = "Stage 1-2: Basic Challenge"
    elif cat_player.x < 3000:
        stage_info = "스테이지 3: 플랫폼 점프 챌린지"
        eng_fallback = "Stage 3: Platform Jump Challenge"
    elif cat_player.x < 4200:
        stage_info = "스테이지 4: 함정 도전 구간"
        eng_fallback = "Stage 4: Trap Challenge Area"
    elif cat_player.x < 5600:
        stage_info = "스테이지 5: 극한의 점프 도전"
        eng_fallback = "Stage 5: Extreme Jump Challenge"
    elif cat_player.x < 7000:
        stage_info = "스테이지 6: 움직임 타이밍 챌린지"
        eng_fallback = "Stage 6: Movement Timing Challenge"
    else:
        stage_info = "최종 스테이지: 지옥의 도전"
        eng_fallback = "Final Stage: Hell Challenge"
    
    try:
        stage_text = font.render(stage_info, True, WHITE)
    except:
        stage_text = font.render(eng_fallback, True, WHITE)
    
    screen.blit(stage_text, (SCREEN_WIDTH - stage_text.get_width() - 20, 20))
    
    # 화면 업데이트
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Pygame 종료
pygame.quit()
sys.exit()
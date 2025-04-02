import pygame
import pytest

class load_head_image():
    def __init__(self,img_path):
        super(load_head_image,self).__init__()
        self.img_path = img_path
        
    def load_image(self,x,y):
        player = pygame.image.load(self.img_path)
        player_head = pygame.transform.scale(player, (x,y))
        return player_head
    
# # 스크린 전체 크기 지정
# SCREEN_WIDTH = 400
# SCREEN_HEIGHT  = 500

# # pygame 초기화
# pygame.init()
 
# # 스크린 객체 저장
# SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("pygame test")

# # FPS를 위한 Clock 생성
# clock = pygame.time.Clock()


player = load_head_image("./image/hwan_no_bg.JPG")
player_head = player.load_image(30,40)


# # 이미지의 Rect
# player_Rect = player_head.get_rect()

# # 이미지가 가운데 올 수 있도록 좌표값 수정
# player_Rect.centerx = round(SCREEN_WIDTH / 2)
# player_Rect.centery = round(SCREEN_HEIGHT / 2)

# dx = 0
# dy = 0

# playing = True
# while playing:
#     # 이벤트 처리
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             playing = False
#             pygame.quit()

#         # 키가 눌렸을 때
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_LEFT:
#                 dx = -5
#             if event.key == pygame.K_RIGHT:
#                 dx = 5

#             if event.key == pygame.K_UP:
#                 dy = -5
#             if event.key == pygame.K_DOWN:
#                 dy = 5

#         # 키가 떼졌을 때
#         if event.type == pygame.KEYUP:
#             if event.key == pygame.K_LEFT:
#                 dx = 0
#             if event.key == pygame.K_RIGHT:
#                 dx = 0

#             if event.key == pygame.K_UP:
#                 dy = 0
#             if event.key == pygame.K_DOWN:
#                 dy = 0

#     # 스크린 배경색 칠하기
#     SCREEN.fill((255, 255, 255))

#     # 키에 의해 증가된 값을 이미지의 좌표에 적용시킨다.
#     player_Rect.x += dx
#     player_Rect.y += dy

 

#     # 스크린의 원하는 좌표에 이미지 복사하기, 좌표값은 Rect를 이용
#     SCREEN.blit(player_head, player_Rect)

#     # 작업한 스크린의 내용을 갱신하기
#     pygame.display.flip()

#     clock.tick(60)
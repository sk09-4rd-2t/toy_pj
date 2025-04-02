import pygame
import pytest
from image_loader import load_head_image


def test_load_image_surface(tmp_path):
    # 테스트용 더미 이미지 만들기
    dummy_image_path = tmp_path / "dummy.png"
    surface = pygame.Surface((100, 100))
    pygame.image.save(surface, str(dummy_image_path))

    # 클래스 테스트
    loader = load_head_image(str(dummy_image_path))
    result = loader.load_image(50, 50)

    # 검증
    assert isinstance(result, pygame.Surface)
    assert result.get_size() == (50, 50)

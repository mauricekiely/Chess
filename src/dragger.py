import pygame

from const import *
from piece import Piece

class Dragger:
    def __init__(self) -> None:
        self.piece = None

        self.dragging = False

        self.mouse_x = 0
        self.mouse_y = 0

        self.initial_row = 0
        self.initial_col = 0


    def update_blit(self, surface):
        self.piece.set_texture(size=128)
        texture = self.piece.texture

        img = pygame.image.load(texture)
        img_centre = (self.mouse_x, self.mouse_y)
        self.piece.texture_rect = img.get_rect(center=img_centre)

        surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, position):
        self.mouse_x, self.mouse_y = position

    def save_initial_pos(self, pos):
        self.initial_row = pos[1] // SQ_SIZE
        self.initial_col = pos[0] // SQ_SIZE


    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False

import pygame
import sys

from const import *
from board import Board
from dragger import Dragger

class Game:
    def __init__(self) -> None:
        self.next_player = "white"
        self.hovered_square = None
        self.board = Board()
        self.dragger = Dragger()

    def show_blank_board(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                color = (234, 235, 200) if (row + col) % 2 == 0 else (119, 154, 88)

                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)     # (x_start, y_start, width, height)

                pygame.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # All pieces not being moved
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_centre = col * SQ_SIZE + SQ_SIZE//2, row * SQ_SIZE + SQ_SIZE//2
                        piece.texture_rect = img.get_rect(center = img_centre)
                        surface.blit(img, piece.texture_rect)


    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece
            color = (211,211,211)
            rad = SQ_SIZE // 3
            for move in piece.moves:
                centre_x = (move.final.col * SQ_SIZE) + (SQ_SIZE//2)
                centre_y = (move.final.row * SQ_SIZE) + (SQ_SIZE//2)
                pygame.draw.circle(surface, color, (centre_x, centre_y), rad)


    def show_last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = (244,247, 116) if (pos.row + pos.col) % 2 == 0 else (172, 195, 51)
                rect = (pos.col * SQ_SIZE, pos.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(surface, color, rect)


    # Highlight square of the mouse
    def show_hover(self, surface):
        if self.hovered_square:
            color = (240, 180, 180)
            rect = (self.hovered_square.col * SQ_SIZE, self.hovered_square.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(surface, color, rect, width=4)


    def set_hover(self, row, col):
        try:
            self.hovered_square = self.board.squares[row][col]
        except IndexError:
            return


    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'


    def check_for_game_end(self, surface):
        font = pygame.font.SysFont("Arial", 24)  
        if self.board.is_mate(self.next_player):
            message = f"Game Over - {self.next_player.title()} Wins"
            text_surface = font.render(message, True, (0, 0, 0)) if self.next_player == 'black' else font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(text_surface, text_rect) 
            pygame.display.update()  
            pause = True
            while pause:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  
                            pygame.quit()
                            sys.exit()



    def reset(self):
        self.__init__()

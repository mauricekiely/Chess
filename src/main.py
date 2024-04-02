import pygame
import sys
from game import Game
from piece import Pawn

from square import Square
from const import *
from move import Move

class Main:
    def __init__(self) -> None:
        # Initialize board
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()


    def mainloop(self):
        game, screen, board, dragger = self.game, self.screen, self.game.board, self.game.dragger
        while True:
            # Print graphics of board
            game.show_blank_board(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            

            # Update screen if piece being moved
            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # Clicking on Piece
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouse_y // SQ_SIZE
                    clicked_col = dragger.mouse_x // SQ_SIZE

                    # Check if clickedf square has a piece
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        # Check valid color
                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col)

                            dragger.save_initial_pos(event.pos)
                            dragger.drag_piece(piece)

                            game.show_blank_board(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)


                # Moving Piece
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQ_SIZE
                    motion_col = event.pos[0] // SQ_SIZE
                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        try:
                            dragger.update_mouse(event.pos)
                        except IndexError:
                            continue


                        game.show_blank_board(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)

                        dragger.update_blit(screen)


                # Releasing a Piece
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row, released_col = dragger.mouse_y//SQ_SIZE, dragger.mouse_x//SQ_SIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        if board.valid_move(dragger.piece, move):
                            board.move(dragger.piece, move, testing=False)

                            game.show_blank_board(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)

                            game.check_for_game_end(screen)


                            game.next_turn()
                        
                    dragger.undrag_piece()


                # Restart game with r
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        game, screen, board, dragger = self.game, self.screen, self.game.board, self.game.dragger

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



            pygame.display.update()

main = Main()
main.mainloop()

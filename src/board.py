from const import *
from square import *
from piece import *
from move import *

from copy import deepcopy
import pygame
import sys

class Board:
    def __init__(self) -> None:
        self.squares = [[0 for _ in range(ROWS)] for _ in range(COLS)]
        self._create()
        self.last_move = None
        self.turn = "white"
        self._add_pieces('white')
        self._add_pieces('black')


    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        # Check for en passant validity
        en_passant_empty = self.squares[final.row][final.col].is_empty()

        #console board move
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        
        # Perform en passant or promotion check
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
            if self.en_passant(initial, final):
                piece.en_passant = True
            else:
                self.check_promotion(piece, final)

        piece.moved = True
        piece.clear_moves()

        # Add castling to available moves if possible
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if diff < 0 else piece.right_rook
                self.move(rook, rook.moves[-1])

        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    # Promote to queen (will ge changed to include all pieces)
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7 and isinstance(piece, Pawn):
            self.squares[final.row][final.col].piece = Queen(piece.color)


    
    def castling(self, inital, final):
        return abs(inital.col - final.col) == 2
    
    def en_passant(self, initial, final):
        return abs(initial.row - final.row) == 2
    
    # Check whether a move will result in a way of taking king on next move
    def in_check(self, piece, move):
        temp_piece = deepcopy(piece)
        temp_board = deepcopy(self)
        temp_board.move(temp_piece, move, True)
        
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_opponent_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False
    

    # Check if game over
    def is_mate(self, next_player):
        opponent_color = "black" if next_player == "white" else "white"
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if not square.is_empty() and square.piece.color == opponent_color:
                    piece = square.piece
                    piece.moves = []
                    self.calc_moves(piece, row, col, bool=True)
                    if piece.moves: 
                        return False
        print("Mate")
        return True



    def calc_moves(self, piece, row, col, bool=True):
        """
        Calculates all valid moves for a piece given its location on the board
        """
        def knight_moves():
            possible_moves = [
                (row-2, col-1),
                (row-1, col-2),
                (row+2, col-1),
                (row+1, col-2),
                (row-2, col+1),
                (row-1, col+2),
                (row+2, col+1),
                (row+1, col+2)
            ]
            for possible_move in possible_moves:
                possible_row, possible_col = possible_move
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].is_empty_or_opponent(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        # create new move
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)


        def pawn_moves():
            steps = 1 if piece.moved else 2
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))

            # Add forward moves
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].is_empty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        move = Move(initial, final)

                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    # blocked
                    else: break
                # not in range
                else: break


            # Add Pawn Captures
            possible_row = row + piece.dir
            possible_cols = [col-1, col+1]
            for possible_col in possible_cols:
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].has_opponent_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)


            r = 3 if piece.color == 'white' else 4
            final_r = 2 if piece.color == 'white' else 5
            for i in [1, -1]:
                if Square.in_range(col + i) and row == r:
                    if self.squares[row][col + i].has_opponent_piece(piece.color):
                        p = self.squares[row][col+i].piece
                        if isinstance(p, Pawn):
                            if p.en_passant:
                                initial = Square(row, col)
                                final = Square(final_r, col+i, p)
                                move = Move(initial, final)
                                
                                # check potencial checks
                                if bool:
                                    if not self.in_check(piece, move):
                                        piece.add_move(move)
                                else:
                                    piece.add_move(move)

           

        def straight_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_row = row + row_incr
                possible_col = col + col_incr

                while True:
                    if Square.in_range(possible_row, possible_col):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_row][possible_col].piece
                        final = Square(possible_row, possible_col, final_piece)
                        move = Move(initial, final)

                        if self.squares[possible_row][possible_col].is_empty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        elif self.squares[possible_row][possible_col].has_opponent_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        elif self.squares[possible_row][possible_col].has_team_piece(piece.color):
                            break
                    
                    else: break

                    possible_row = possible_row + row_incr
                    possible_col = possible_col + col_incr

        def king_moves():
            adjs = [
                (row+1, col+1),
                (row+1, col),
                (row+1, col-1),
                (row, col+1),
                (row, col-1),
                (row-1, col+1),
                (row-1, col),
                (row-1, col-1),
            ]
            for possible_move in adjs:
                possible_row, possible_col = possible_move
                if Square.in_range(possible_row, possible_col):
                    if self.squares[possible_row][possible_col].is_empty_or_opponent(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_row, possible_col)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move) :
                                piece.add_move(move)
                                break
                        else:
                            piece.add_move(move)

            if not piece.moved:
                for direction in ('left', 'right'):
                    if direction == 'left':
                        rook_col, end_col, range_cols = 0, 3, range(1, 4)
                    else:
                        rook_col, end_col, range_cols = 7, 5, range(5, 7)

                    rook = self.squares[row][rook_col].piece
                    if isinstance(rook, Rook) and not rook.moved:
                        # Check if all squares between king and rook are empty
                        if all(not self.squares[row][c].has_piece() for c in range_cols):
                            # Setting the rook for castling
                            setattr(piece, f"{direction}_rook", rook)

                            # Add rook move
                            rook_move = Move(Square(row, rook_col), Square(row, end_col))

                            # Add king move
                            king_move = Move(Square(row, col), Square(row, 2 if direction == 'left' else 6))
                            if bool:
                                if not self.in_check(piece, rook_move) and not self.in_check(rook, king_move):
                                    rook.add_move(rook_move)
                                    piece.add_move(king_move)
                                    break
                            else:
                                rook.add_move(rook_move)
                                piece.add_move(king_move)


        if isinstance(piece, Pawn): pawn_moves()

        if isinstance(piece, Knight): knight_moves()

        if isinstance(piece, Bishop):
            # Check all directions incrementally 
            straight_moves([
                (-1,1),
                (-1,-1),
                (1,1),
                (1,-1)
            ])

        if isinstance(piece, Rook):
            straight_moves([
                (-1,0),
                (0,1),
                (1,0),
                (0,-1)
            ])

        if isinstance(piece, Queen):
            straight_moves([
                (-1,1),
                (-1,-1),
                (1,1),
                (1,-1),
                (-1,0),
                (0,1),
                (1,0),
                (0,-1)
            ])

        if isinstance(piece, King): king_moves()


    # Initialize the board 
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)


    def _add_pieces(self, color):
        row_pawn, row_piece = (6, 7) if color == 'white' else (1, 0)

        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        self.squares[row_piece][1] = Square(row_piece, 1, Knight(color))
        self.squares[row_piece][6] = Square(row_piece, 6, Knight(color))

        self.squares[row_piece][2] = Square(row_piece, 2, Bishop(color))
        self.squares[row_piece][5] = Square(row_piece, 5, Bishop(color))

        self.squares[row_piece][0] = Square(row_piece, 0, Rook(color))
        self.squares[row_piece][7] = Square(row_piece, 7, Rook(color))

        self.squares[row_piece][3] = Square(row_piece, 3, Queen(color))
        self.squares[row_piece][4] = Square(row_piece, 4, King(color))
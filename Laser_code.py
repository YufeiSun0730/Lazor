import copy


class Block:
    def __init__(self, position, category):
        self.position = position
        self.category = category

    def findedges(self):
        return [(self.position[0] + i[0], self.position[1] + i[1]) for i in [(0, -1), (0, 1), (-1, 0), (1, 0)]]

    def __eq__(self, other):
        if self.position == other.position and self.category == other.category:
            return True
        else:
            return False


class Grid:
    def __init__(self, position):
        self.position = position

    def findentdir(self):
        if self.position[0] % 2 == 0 and self.position[1] % 2 == 0: #find entering point of the laser on the block
            return 'prohibited'
        elif self.position[1] % 2 == 0:
            return 'side'
        else:
            return 'vert'

    def __eq__(self, other):
        if self.position == other.position:
            return True
        else:
            return False


class Board_filler:
    def __init__(self, initial_board, arrangement_list, available_list):
        self.initial_board = initial_board
        self.arrangement_list = arrangement_list
        self.arrangement_history = []
        self.available_list = available_list
        self.filled = 0

    def next(self):
        self.arrangement_history.append(self.arrangement_list.pop())
        arrangement = self.arrangement_history[-1]
        self.filled = copy.deepcopy(self.initial_board)
        for i in range(len(self.available_list)):
            self.filled[arrangement[i][0]][arrangement[i]
                                           [1]].category = self.available_list[i]

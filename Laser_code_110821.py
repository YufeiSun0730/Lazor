#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
code organization
1. class solver
    1. read_file
    2. interpret_board
        turn into A:n1, B:n2, C:n3, start point, need to pass point, end point
    3. move
    4. check_position
    5. solution
2. class block?
3. class lazor(x, y, vx, vy)
    1. init
    2. interaction_A
    3. interaction_B
    4. interaction_C

'''


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






def read_bff(filename):


    file = open(filename, 'r')
    contents = []
    for line in file:
        stripped = line.strip()
        contents.append(stripped)
    file.close()
    ind1 = contents.index('GRID START')
    ind2 = contents.index('GRID STOP')
    vals = []
    for row in contents[ind1 + 1:ind2]:
        row = list(row.replace(' ', ''))
        vals.append(row)
    contents = contents[ind2 + 1:]
    xlen = len(vals[0])
    grid = [[0 for i in range(2 * xlen + 1)]
            for j in range(2 * (ind2 - ind1) - 1)]
    for x in range(2 * xlen + 1):
        for y in range(len(grid)):
            if (x % 2) == 0 or (y % 2) == 0:
                grid[y][x] = Grid((x, y))
            else:
                block_category = vals[(y - 1) // 2][(x - 1) // 2]
                grid[y][x] = Block((x, y), block_category)
    A = 0
    B = 0
    C = 0
    lazors = []
    points = []
    for line in contents:
        if 'A' in line:
            A = int(line[-1])
        if 'B' in line:
            B = int(line[-1])
        if 'C' in line:
            C = int(line[-1])
        if 'L' in line:
            lazors.append([int(x) for x in line.split(' ')[1:]])
        if 'P' in line:
            points.append([int(x) for x in line.split(' ')[1:]])

    usable_blocks = {'A': A, 'B': B, 'C': C}

    def trans(m):
        a = [[] for i in m[0]]
        for i in m:
            for j in range(len(i)):
                a[j].append(i[j])
        return a

    return trans(grid), usable_blocks, lazors, points


# In[ ]:


def generate_laser(board, initial_laser):
    '''
        Generate the laser path according to board and initial laser condition.

            **Parameters**
                board: *list*
                    2D list representing the board filled with all blocks.
                initial_laser: *list, tuple*
                    List of tuples of coordinates and direction for each laser
                    to start.

            **Returns**
                final_laser_path: *list, list, tuple*
                    List of all laser paths.
    '''

    def is_in_board(coord):
        if 0 <= coord[0] <= len(board) - 1 and 0 <= coord[1] <= len(board[0]) - 1:
            return True
        else:
            return False

    def find_next_block(coord, direction_in):
        if board[coord[0]][coord[1]].findcategory() == 'vertical':
            next_block_coord = (coord[0] + direction_in[0], coord[1])
        if board[coord[0]][coord[1]].findcategory() == 'horizontal':
            next_block_coord = (coord[0], coord[1] + direction_in[1])
        return next_block_coord

    def find_direction_out(coord, direction_in, next_block):
        if next_block.category == 'B':
            direction_out = (0, 0)
        if next_block.category == 'o' or next_block.category == 'x':
            direction_out = direction_in
        if next_block.category == 'A':
            if board[coord[0]][coord[1]].findcategory() == 'vertical':
                direction_out = (-direction_in[0], direction_in[1])
            if board[coord[0]][coord[1]].findcategory() == 'horizontal':
                direction_out = (direction_in[0], -direction_in[1])
        if next_block.category == 'C':
            if board[coord[0]][coord[1]].findcategory() == 'vertical':
                direction_out = [
                    (-direction_in[0], direction_in[1]), direction_in]
            if board[coord[0]][coord[1]].findcategory() == 'horizontal':
                direction_out = [
                    (direction_in[0], -direction_in[1]), direction_in]
        return direction_out

    final_laser_path = []
    initial_directions = []
    for i in range(len(initial_laser)):
        final_laser_path.append([(initial_laser[i][0], initial_laser[i][1])])
        initial_directions.append((initial_laser[i][2], initial_laser[i][3]))
    current_laser_index = 0
    while current_laser_index < len(final_laser_path) - 1:
        laser = final_laser_path[current_laser_index]
        initial_direction = initial_directions[current_laser_index]
        while True:
            if len(laser) == 1:
                direction_in = initial_direction
            else:
                direction_in = (laser[-1][0] - laser[-2][0],
                                laser[-1][1] - laser[-2][1])
            next_block_coord = find_next_block(laser[-1], direction_in)
            if is_in_board(next_block_coord) is False:
                final_laser_path[current_laser_index] = laser
                break
            else:
                next_block = board[next_block_coord[0]][next_block_coord[1]]
            direction_out = find_direction_out(
                laser[-1], direction_in, next_block)
            if next_block.category == 'C':
                next_coord_0 = (laser[-1][0] + direction_out[0][0],
                                laser[-1][1] + direction_out[0][1])
                next_coord_1 = (laser[-1][0] + direction_out[1][0],
                                laser[-1][1] + direction_out[1][1])
                final_laser_path.append(laser + [next_coord_0])
                laser.append(next_coord_1)
            else:
                next_coord = (laser[-1][0] + direction_out[0],
                              laser[-1][1] + direction_out[1])
                laser.append(next_coord)
            if is_in_board(laser[-1]) is False or laser[-1] == laser[-2]:
                final_laser_path[current_laser_index] = laser[:-1]
                break
        current_laser_index += 1

    return final_laser_path


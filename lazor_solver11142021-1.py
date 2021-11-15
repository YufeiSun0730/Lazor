import copy


def pos_check(coord, grid): # check if given position is in grid
    if coord[0] >= 0 and coord[0] < len(grid) and coord[1] >= 0 and coord[1] < len(grid[0]):

        return True
    else:
        return False

def blk_pos_check(coord, grid, block_grid):
    x_block_coord = int((coord[0] - 1) / 2)
    y_block_coord = int((coord[1] - 1) / 2)
    if coord[0] >= 0 and coord[0] < len(grid) and coord[1] >= 0 and coord[1] < len(grid[0]) and \
            block_grid[x_block_coord][y_block_coord] == '0':

        return True
    else:
        return False

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
            return 'vert'
        elif self.position[0] % 2 == 0:
            return 'side'

    def __eq__(self, other):
        if self.position == other.position:
            return True
        else:
            return False






def read_bff(filename):


    file = open(filename, 'r') # open file
    contents = []
    for line in file:
        stripped = line.strip()
        contents.append(stripped)
    file.close()
    ind1 = contents.index('GRID START')
    ind2 = contents.index('GRID STOP')
    vals = []
    for row in contents[ind1 + 1:ind2]:  # extract grid info
        row = list(row.replace(' ', ''))
        vals.append(row)


    contents = contents[ind2 + 1:]
    xlen = len(vals[0])
    ylen = len(vals)
    blkvals = vals
    xxlen = len(blkvals[0])
    yylen = len(blkvals)
    for i in range(yylen):
        for j in range(xxlen):
            if blkvals[i][j] == 'o':
                blkvals[i][j] = '0'
            else:
                blkvals[i][j] = '1'

    block_grid = blkvals


    grid = [[0 for i in range(2 * xlen + 1)]
            for j in range(2 * (ind2 - ind1) - 1)]

    for x in range(2 * xlen + 1): # set up grid coordinate system
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
    for line in contents: # extract usable block info
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

    for i in range(len(lazors)):
        start_point = [lazors[i][0], lazors[i][1]]
        direction = [lazors[i][2], lazors[i][3]]

    def trans(m): #reverse coordinate system to fit current coordinate system
        a = [[] for i in m[0]]
        for i in m:
            for j in range(len(i)):
                a[j].append(i[j])
        return a
    return trans(grid), usable_blocks, start_point, direction, points, block_grid  # return grid info


class Lasor():
    def __init__(self, start, direction):
        self.start = start
        self.dir = direction

    def collide_A(self, collision_dir, currentD):
        if collision_dir == "vertical":
            direction_out = (currentD[0], -currentD[1])
        if collision_dir == "horizontal":
            direction_out = (-currentD[0], currentD[1])
        return direction_out

    def collide_B(self, collision_dir):
        direction_out = (0, 0)
        return direction_out

    def collide_C(self, collision_dir, currentD):
        if collision_dir == "vertical":
            direction_out = [(currentD[0], -currentD[1]), currentD]
        if collision_dir == "horizontal":
            direction_out = [(-currentD[0], currentD[1]), currentD]
        return direction_out

    def current_lazor_path(self, start, direction, grid):
        def check_grid_type(position, direction, grid):
            if position[0] % 2 == 1:
                if direction[1] > 0:
                    # check the lower grid type
                    if position[1] < int(len(grid) * 2):
                      grid_type = grid[int(position[1] // 2)][position[0] // 2]
                      collision_dir = "vertical"
                      return grid_type, collision_dir
                else:
                    # check the upper grid type
                    if position[1] > 0:
                      grid_type = grid[int(position[1] // 2 - 1)][position[0] // 2]
                      collision_dir = "vertical"
                      return grid_type, collision_dir
            else:
                if direction[0] > 0:
                    # check the right grid type
                    if position[0] < int(len(grid[0]) * 2):
                      grid_type = grid[position[1] // 2][int(position[0] // 2)]
                      collision_dir = "horizontal"
                      return grid_type, collision_dir
                else:
                    # check the left grid type
                    if position[0] > 0:
                      grid_type = grid[position[1] // 2][int(position[0] // 2 - 1)]
                      collision_dir = "horizontal"
                      return grid_type, collision_dir
        path = []
        dir = []
        current_pos = start
        current_dir = direction
        path.append(current_pos)
        dir.append(current_dir)

        while (pos_check(current_pos, grid)): 
            if current_dir[0] < 0 and current_dir[1] < 0:
                next_pos = (current_pos[0] - 1, current_pos[1] - 1) # (current_pos[0] - 1, current_pos[1] - 1)
            elif current_dir[0] > 0 and current_dir[1] > 0:
                next_pos = (current_pos[0] + 1, current_pos[1] + 1) # (current_pos[0] + 1, current_pos[1] + 1)
            elif current_dir[0] < 0 and current_dir[1] > 0:
                next_pos = (current_pos[0] - 1, current_pos[1] + 1) # (current_pos[0] - 1, current_pos[1] + 1)
            else:
                next_pos = (current_pos[0] + 1, current_pos[1] - 1) # (current_pos[0] + 1, current_pos[1] - 1)

            if check_grid_type(next_pos, current_dir, grid) != None:
                grid_type = check_grid_type(next_pos, current_dir, grid)[0]
                collision_dir = check_grid_type(next_pos, current_dir, grid)[1]
            else:
                next_dir = current_dir

            if grid_type == "A":
                next_dir = self.collide_A(collision_dir, current_dir)
            elif grid_type == "B":
                next_dir = self.collide_B(collision_dir)
            elif grid_type == "C":
                next_dir = self.collide_C(collision_dir, current_dir)
            else:
                next_dir = current_dir

            if type(next_dir) == list:
                print("contain block C", next_dir)
                path.append(next_pos)
                dir.append(next_dir)
                return path, dir
            
            current_pos = next_pos
            current_dir = next_dir
            if next_pos[0] >= 0 and next_pos[1] >= 0:
              path.append(current_pos)
              dir.append(current_dir)
              print("path", path)

            if current_dir == (0, 0):
              return path, dir

            print("current_pos ", next_pos)
            print(next_dir)

            print(path, dir)
        return path, dir


def type_and_number(num_A, num_B, num_C):
    block_A = []
    block_B = []
    block_C = []

    for i in range(num_A):
        block_A.append("A")
    for j in range(num_B):
        block_B.append("B")
    for v in range(num_C):
        block_C.append("C")
    return block_A, block_B, block_C


def find_path(currentPos, currentDir, need_to_cross, block_A, block_B, block_C, path, grid):
    print(type(currentPos))
    score = 0
    for i in range(len(need_to_cross)):
        if need_to_cross[i] in path:
            score += 1

    if score == len(need_to_cross):
        return path

    path.append(currentPos)

    lazor_pos = []
    lazor_dir = []
    potential_blockpos = []
    for i in range(len(currentPos)):
        lazor = Lasor(currentPos, currentDir)
        lazor_pos.append(lazor.current_lazor_path(currentPos[i], currentDir[i], grid)[0][1])
        lazor_dir.append(lazor.current_lazor_path(currentPos[i], currentDir[i], grid)[1][1])
        potential_blockpos.append(find_block_coord(current_lazor_path(currentPos[i], currentDir[i], grid)))

    # for pos, direction in currentPos, currentDir:
    #     lazor_pos.append(current_lazor_path(pos, direction)[0][1])
    #     lazor_dir.append(current_lazor_path(pos, direction)[1][1])
    #     potential_blockpos.append(find_block_coord(current_lazor_path(pos, direction)))

    if len(block_A) != 0:
        for p in potential_blockpos:
            # change grid to A
            temp = grid[p[1]][p[0]]
            grid[p[1]][p[0]] = "A"
            newPos = lazor_pos
            newDir = lazor_dir
            find_path(newPos, newDir, need_to_cross, block_A.pop(), block_B, block_C, path.copy)
            grid[p[1]][p[0]] = temp

    if len(block_B) != 0:
        for p in potential_blockpos:
            # change grid to B
            temp = grid[p[1]][p[0]]
            grid[p[1]][p[0]] = "B"
            newPos = lazor_pos
            newDir = lazor_dir
            find_path(newPos, newDir, need_to_cross, block_A, block_B.pop(), block_C, path.copy)
            grid[p[1]][p[0]] = temp

    if len(block_C) != 0:
        for p in potential_blockpos:
            # change grid to B
            temp = grid[p[1]][p[0]]
            grid[p[1]][p[0]] = "C"
            newPos = lazor_pos
            newDir = lazor_dir
            find_path(newPos, newDir, need_to_cross, block_A, block_B, block_C.pop(), path.copy)
            grid[p[1]][p[0]] = temp


def path_with_C(start, dir, grid):
    path = []
    l = Lasor(start, dir)
    previous_pos, previous_dir = l.current_lazor_path(start=start, direction=dir, grid=grid)
    print("previous_pos", previous_pos)
    previous_pos = previous_pos[-1]
    previous_dir1 = previous_dir[-1][0]
    previous_dir2 = previous_dir[-1][1]
    n1 = Lasor(previous_pos, previous_dir1)
    a1, a2 = n1.current_lazor_path(start=previous_pos, direction=previous_dir1, grid=grid)
    n2 = Lasor(previous_pos, previous_dir2)
    b1, b2 = n2.current_lazor_path(start=previous_pos, direction=previous_dir2, grid=grid)
    path.append(previous_pos)
    path.append(a1[1:])
    path.append(b1[1:])
    return path

def find_block_coord_1(path, dir, grid, blk_grid): # find possible block position coordinates
    block_coord_list = []

    xlen = len(path)

    for x in range(xlen):# for given laser intersection coordinates, find block coordinates
        block_coord = []

        if dir[x][0] < 0 and dir[x][1] < 0:  # predict block position with given point and direction vector
            if path[x][0] % 2 == 0:
                block_coord = [path[x][0] - 1, path[x][1]]
            elif path[x][1] % 2 == 0:
                block_coord = [path[x][0], path[x][1] - 1]

        elif dir[x][0] > 0 and dir[x][1] < 0:
            if path[x][0] % 2 == 0:

                block_coord = [path[x][0] + 1, path[x][1]]
            elif path[x][1] % 2 == 0:

                block_coord = [path[x][0], path[x][1] - 1]

        elif dir[x][0] > 0 and dir[x][1] > 0:
            if path[x][0] % 2 == 0:
                block_coord = [path[x][0] + 1, path[x][1]]
            elif path[x][1] % 2 == 0:
                block_coord = [path[x][0], path[x][1] + 1]

        elif dir[x][0] < 0 and dir[x][1] > 0:
            if path[x][0] % 2 == 0:
                block_coord = [path[x][0] - 1, path[x][1]]
            elif path[x][1] % 2 == 0:
                block_coord = [path[x][0], path[x][1] - 1]

        if blk_pos_check(block_coord, grid, blk_grid):
            block_coord_list.append(block_coord)  # append coordinate list
    return block_coord_list

grid_1, usable_blocks, start_point, direction, points, block_grid = read_bff('mad_1.bff')
path =[(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (8, 1)]
dir = [(1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1), (1, -1)]
block_coord_list = find_block_coord_1(path, dir, grid_1, block_grid)
print(block_coord_list)



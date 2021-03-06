from itertools import permutations
import copy
import time


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

    print(vals)
    contents = contents[ind2 + 1:]
    xlen = len(vals[0])
    ylen = len(vals)
    blkvals = vals
    xxlen = len(blkvals[0])
    yylen = len(blkvals)
    for i in range(yylen):
        for j in range(xxlen):
            if blkvals[i][j] == 'o':
                blkvals[i][j] = 'o'
            elif blkvals[i][j] == 'A':
                blkvals[i][j] = 'A'
            elif blkvals[i][j] == 'B':
                blkvals[i][j] = 'B'
            elif blkvals[i][j] == 'C':
                blkvals[i][j] = 'C'
            else:
                blkvals[i][j] = 'x'

    block_grid = blkvals


    grid = [[0 for i in range(2 * xlen + 1)]
            for j in range(2 * (ind2 - ind1) - 1)]

    for x in range(2 * xlen + 1): # set up grid coordinate system
        for y in range(len(grid)):
            block_category = vals[(y - 1) // 2][(x - 1) // 2]
            if (x % 2) == 0 or (y % 2) == 0:
                grid[y][x] = Grid((x, y), block_category)
            else:
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

    start_point = []
    direction = []
    point = []
    for i in range(len(lazors)):
        start_point.append((lazors[i][0], lazors[i][1]))
        direction.append((lazors[i][2], lazors[i][3]))

    for i in range(len(points)):
    	point.append((points[i][0], points[i][1]))

    def trans(m): #reverse coordinate system to fit current coordinate system
        a = [[] for i in m[0]]
        for i in m:
            for j in range(len(i)):
                a[j].append(i[j])
        return a
    return trans(grid), usable_blocks, start_point, direction, point, block_grid  # return grid info


def pos_check(coord, grid): # check if given position is in grid
    if coord[0] >= 0 and coord[0] < len(grid[0]) and coord[1] >= 0 and coord[1] < len(grid):

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
    def __init__(self, position, category):
        self.position = position
        self.category = category

    def findentdir(self):
        if self.position[0] % 2 == 0 and self.position[1] % 2 == 0: #find entering point of the laser on the block
            return 'prohibited'
        elif self.position[1] % 2 == 0:
            return 'vert'
        elif self.position[0] %2 == 0:
            return 'side'

    def __eq__(self, other):
        if self.position == other.position:
            return True
        else:
            return False


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
                    if position[1] < len(grid):
                      grid_type = grid[position[1]][position[0]]
                      collision_dir = "vertical"
                      return grid_type, collision_dir
                else:
                    # check the upper grid type
                    if position[1] > 0:
                      grid_type = grid[int(position[1] - 1)][position[0]]
                      collision_dir = "vertical"
                      return grid_type, collision_dir
            else:
                if direction[0] > 0:
                    # check the right grid type
                    if position[0] < len(grid[0]):
                      grid_type = grid[position[1]][position[0]]
                      collision_dir = "horizontal"
                      return grid_type, collision_dir
                else:
                    # check the left grid type
                    if position[0] > 0:
                      grid_type = grid[position[1]][int(position[0] - 1)]
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

            grid_content = None
            if pos_check(next_pos, grid):
            	if check_grid_type(next_pos, current_dir, grid) != None:
                	grid_content = check_grid_type(next_pos, current_dir, grid)[0]
                	collision_dir = check_grid_type(next_pos, current_dir, grid)[1]
            else:
                next_dir = current_dir

            if grid_content == "A":
                next_dir = self.collide_A(collision_dir, current_dir)
            elif grid_content == "B":
                next_dir = self.collide_B(collision_dir)
            elif grid_content == "C":
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
            if pos_check(current_pos, grid):
              path.append(current_pos)
              dir.append(current_dir)
              #print("path", path)

            if current_dir == (0, 0):
              return path, dir

            #print("current_pos ", next_pos)
            #print(next_dir)

        return path, dir


def format(block_grid, block_A, block_B, block_C):
    grid = []
    not_move = []
    for i in range(len(block_grid)):
        for j in range(len(block_grid[0])):
            if block_grid[i][j] == "o":
                grid.append('o')
            else:
                not_move.append(block_grid[i][j])

    num_of_0 = grid.count('o')
    num_of_A = len(block_A)
    num_of_B = len(block_B)
    num_of_C = len(block_C)
    useable_grid_num = num_of_0 - num_of_A - num_of_B - num_of_C

    useable_grid = []

    for i in range(useable_grid_num):
    	useable_grid.append("o")
    
    useable_grid.extend(block_A)
    useable_grid.extend(block_B)
    useable_grid.extend(block_C)



    return useable_grid


def check_results(lazor_starts, directions, new_grid, points):
    def points_through(lazor_starts, directions, new_grid):
        l = []
        list_of_pos = []
        for i in range(len(lazor_starts)):
            l.append(Lasor(start_point[i], direction[i]))
            a, b = l[i].current_lazor_path(start_point[i], direction[i], new_grid)
            list_of_pos.extend(a)
        #print("position", list_of_pos)
        return list_of_pos

    path = points_through(lazor_starts, directions, new_grid)
    print("path", path)
    print("points", points)

    score = 0
    for i in range(len(points)):
        if points[i] in path:
            score += 1
            print("score", score)

    if score == len(points):
        print("Success!")
        return path
    else:
        return None


def grid_transform(block_grid):

    grid = [[ 1 for i in range(2 * len(block_grid[0]) + 1)] for j in range(2 * len(block_grid) + 1)]
    for x in range(len(block_grid)):
        for y in range(len(block_grid[0])):
            print(2*x+1)
            grid[2*x+1][2*y+1] = block_grid[x][y]

    return grid



def fill_grid(possible_boards, grid, original_grid, lazor_starts, directions, points, useable_grid):
    instance = possible_boards[0]
    useable_grid2 = [x if x != 'o' else '0' for x in useable_grid]
    def transform_to_ori(instance, useable_grid):
        generated = list(set(instance))
        original = list(set(useable_grid))
        frequency = {}
        transformation = {}
        for object in generated:
            frequency[object] = instance.count(object)
        keys = list(frequency.keys())
        values = list(frequency.values())
        for i in original:
            index = values.index(useable_grid.count(i))
            transformation[keys[index]] = i
            values.pop(index)
            frequency.pop(keys[index])
            keys.pop(index)
        return transformation



    transformation = transform_to_ori(instance, useable_grid2)
    print(transformation)
    temp = copy.deepcopy(original_grid)
    print("temp1", temp)
    for item in list(possible_boards):
        print(item)
        iteration = 0
        for i in range(len(original_grid)):
            for j in range(len(original_grid[0])):
                if original_grid[i][j] == "o":
                    print((i, j))
                    original_grid[i][j] = transformation[item[j + len(original_grid[0]) * i]]
                    iteration += 1
                    print(iteration)
                    print("original_grid", original_grid)
                    print(j + len(original_grid[0]) * i)
                else:
                	print("oops")
                	original_grid[i][j] = original_grid[i][j]
        
        new_grid = grid_transform(original_grid)
        print("new_grid", new_grid)
        original_grid = copy.deepcopy(temp)
        print("original_grid", original_grid)
        result = check_results(lazor_starts, directions, new_grid, points)
        if result != None:
            return new_grid
        else:
            continue

			


def permutation(items):
    '''
    Yield the permutations of `items` where items is either a list
    of integers representing the actual items or a list of hashable items.
    The output are the unique permutations of the items given as a list
    of integers 0, ..., n-1 that represent the n unique elements in
    `items`.

    Examples
    ========

    >>> for i in msp('xoxox'):
    ...   print(i)

    [1, 1, 1, 0, 0]
    [0, 1, 1, 1, 0]
    [1, 0, 1, 1, 0]
    [1, 1, 0, 1, 0]
    [0, 1, 1, 0, 1]
    [1, 0, 1, 0, 1]
    [0, 1, 0, 1, 1]
    [0, 0, 1, 1, 1]
    [1, 0, 0, 1, 1]
    [1, 1, 0, 0, 1]

    Reference: "An O(1) Time Algorithm for Generating Multiset Permutations", Tadao Takaoka
    https://pdfs.semanticscholar.org/83b2/6f222e8648a7a0599309a40af21837a0264b.pdf
    '''

    def visit(head):
        (rv, j) = ([], head)
        for i in range(N):
            (dat, j) = E[j]
            rv.append(dat)
        return rv

    u = list(set(items))
    E = list(reversed(sorted([u.index(i) for i in items])))
    N = len(E)
    # put E into linked-list format
    (val, nxt) = (0, 1)
    for i in range(N):
        E[i] = [E[i], i + 1]
    E[-1][nxt] = None
    head = 0
    afteri = N - 1
    i = afteri - 1
    yield visit(head)
    while E[afteri][nxt] is not None or E[afteri][val] < E[head][val]:
        j = E[afteri][nxt]  # added to algorithm for clarity
        if j is not None and E[i][val] >= E[j][val]:
            beforek = afteri
        else:
            beforek = i
        k = E[beforek][nxt]
        E[beforek][nxt] = E[k][nxt]
        E[k][nxt] = head
        if E[k][val] < E[head][val]:
            i = k
        afteri = E[i][nxt]
        head = k
        yield visit(head)



def blk_pos_check(coord, grid, block_grid):
    x_block_coord = int((coord[0] - 1) / 2)
    y_block_coord = int((coord[1] - 1) / 2)
    if coord[0] >= 0 and coord[0] < len(grid) and coord[1] >= 0 and coord[1] < len(grid[0]) and \
            block_grid[x_block_coord][y_block_coord] == 'o':

        return True
    else:
        return False



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





if __name__ == "__main__":
    #l = set(list(permutations(['o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'A', 'A', 'C'])))
    #print(len(l))

    #block_grid = [['0', 'B', '0'], ['0', '0', '0'], ['0', '0', '0']]

    grid, usable_blocks, start_point, direction, points, block_grid = read_bff("/Users/mordredyuan/Downloads/Lazor-main/LazorProjectFall2021/mad_4.bff")
    block_A, block_B, block_C = type_and_number(usable_blocks["A"], usable_blocks["B"], usable_blocks["C"])


    items = format(block_grid, block_A, block_B, block_C)
    possible_boards = list(permutation(items))
    fill_grid(possible_boards, grid, block_grid, start_point, direction, points, items)

    # grid, usable_blocks, start_point, direction, points, block_grid = read_bff("/Users/mordredyuan/Downloads/Lazor-main/LazorProjectFall2021/tiny_5.bff")
    # block_A, block_B, block_C = type_and_number(usable_blocks["A"], usable_blocks["B"], usable_blocks["C"])
    # print(block_grid)
    # print(grid_transform(block_grid))
    # alpha = grid_transform(block_grid)
    # l = []
    # list_of_pos = []
    # list_of_dir = []
    # start_points = []
    # directions = []

    # for i in range(len(start_point)):
    #     l.append(Lasor(start_point[i], direction[i]))
    #     a, b = l[i].current_lazor_path(start_point[i], direction[i], alpha)
    #     start_points.extend(start_point[i])
    #     directions.extend(direction[i])
    #     list_of_pos.extend(a)
    #     list_of_dir.extend(b)

    # print(list_of_pos)






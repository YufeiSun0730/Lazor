'''
EN.640.635 Software Carpentry
Lazor Project

In this project, a lazor game solver was created to
read and solve a lazor puzzle from the lazor mobile app.
In the solver, we used multiset permutation and searchh method to find
the place to place blocks that will give the winning solutions.

'''

import copy
import time


def read_bff(filename):
    '''
    This will read the lazor game from a bff file into a 2d list with values
    along with board information.

    **Parameters**

        filename: *str*
            The name of the maze.png file to load.

    **Returns**

        trans(grid): *list, list, int*
            A 2D array holding integers specifying each block's type
            with a new coordinate system.

        usable_blocks: *dictionary*
            A dictionary of block types along with counts.

        start_point: *list*
            A list of lazor start points.

        direction: *list*
            A list of lazor directions.

        point: *list*
            A list of points that needs to be passed through.

        block_grid: *list, list, int*
            A 2D array holding information for the smaller version grid.
    '''

    file = open(filename, 'r')  # open file
    contents = []
    for line in file:
        stripped = line.strip()
        contents.append(stripped)
    file.close()
    # get the grid in the file
    ind1 = contents.index('GRID START')
    ind2 = contents.index('GRID STOP')
    vals = []
    for row in contents[ind1 + 1:ind2]:  # extract grid info
        row = list(row.replace(' ', ''))
        vals.append(row)

    contents = contents[ind2 + 1:]
    xlen = len(vals[0])
    blkvals = vals

    # this is the original grid
    block_grid = blkvals

    # generate new grid with new coordinate system
    grid = [[0 for i in range(2 * xlen + 1)]
            for j in range(2 * (ind2 - ind1) - 1)]

    for x in range(2 * xlen + 1):  # set up grid coordinate system
        for y in range(len(grid)):
            block_category = vals[(y - 1) // 2][(x - 1) // 2]
            if (x % 2) == 0 or (y % 2) == 0:
                grid[y][x] = Grid((x, y), block_category)
            else:
                grid[y][x] = Block((x, y), block_category)

    # here we get the block type and number information
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

    # this gets the start points and directions information for the lazor
    start_point = []
    direction = []
    point = []
    for i in range(len(lazors)):
        start_point.append((lazors[i][0], lazors[i][1]))
        direction.append((lazors[i][2], lazors[i][3]))

    for i in range(len(points)):
        point.append((points[i][0], points[i][1]))

    def trans(m):  # reverse coordinate system to fit current coordinate system
        a = [[] for i in m[0]]
        for i in m:
            for j in range(len(i)):
                a[j].append(i[j])
        return a
    return trans(grid), usable_blocks, start_point, direction,\
        point, block_grid  # return grid info


def pos_check(coord, grid):
    # this function checks if the given position is in grid
    if coord[0] >= 0 and coord[0] < len(grid[0]) and\
       coord[1] >= 0 and coord[1] < len(grid):

        return True
    else:
        return False


class Block:
    '''
    This class acts as a initializer for the grid class and contains
    findedges and __eq__ function.
    '''
    def __init__(self, position, category):
        self.position = position
        self.category = category

    def findedges(self):
        '''
        This function returns a list of coordinates for the

        edges of thhe block.
        '''
        return [(self.position[0] + i[0], self.position[1] + i[1])
                for i in [(0, -1), (0, 1), (-1, 0), (1, 0)]]

    def __eq__(self, other):
        if self.position == other.position and self.category == other.category:
            return True
        else:
            return False


class Grid:
    '''
    This class acts as a initializer for the grid class and contains
    findentdir and __eq__ function.
    '''
    def __init__(self, position, category):
        self.position = position
        self.category = category

    def findentdir(self):
        '''
        This function returns the entering direction of the lazor

        to the grid. ('prohibited', 'vert', 'side')
        '''
        if self.position[0] % 2 == 0 and self.position[
           1] % 2 == 0:  # find entering point of the laser on the block
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


class Lasor():
    '''
    This class acts as a initializer for the lasor class and contains
    collide_A, collide_B, collide_C and current_lazor_path function.
    '''
    def __init__(self, start, direction):
        self.start = start
        self.dir = direction

    def collide_A(self, collision_dir, currentD):
        '''
        This function returns the new direction when the lazor hits block A.
        '''
        if collision_dir == "vertical":
            direction_out = (currentD[0], -currentD[1])
        if collision_dir == "horizontal":
            direction_out = (-currentD[0], currentD[1])
        return direction_out

    def collide_B(self, collision_dir):
        '''
        This function returns the new direction when the lazor hits block B.
        '''
        direction_out = (0, 0)
        return direction_out

    def collide_C(self, collision_dir, currentD):
        '''
        This function returns the new direction when the lazor hits block C.
        '''
        if collision_dir == "vertical":  # two directions
            direction_out = [(currentD[0], -currentD[1]), currentD]
        if collision_dir == "horizontal":  # two directions
            direction_out = [(-currentD[0], currentD[1]), currentD]
        return direction_out

    def current_lazor_path(self, start, direction, grid):
        '''
        This function checks if the current board is the solution

        to the game.

        **Parameters**

            start: *list, tuple*
                A list of tuples that contains the lazor start points.
            direction: *list, tuple*
                A list of tuples that contains the lazor directions.
            grid: *list, list, int*
                A 2d array of the given grid.

        **Returns**

            path: *list, tuple*
                A list tuples that represents the positions that the lazors
                pass through.

            dir: *list, tuple*
                A list tuples that represents the directions that the lazors
                exhibited.
        '''

        # initialize the current_pos and current_dir variables
        path = []
        dir = []
        current_pos = start
        current_dir = direction
        path.append(current_pos)
        dir.append(current_dir)
        # for checking if lazor starts point to a block
        start_point_near_block = 0

        # create a while loop to get the positions and directions
        while (pos_check(current_pos, grid)):

            # check for situation when the lazor does not start with pointing
            # at Block A
            if check_grid_type(current_pos, current_dir, grid) is not None:
                if check_grid_type(current_pos, current_dir,
                                   grid)[0] == "0" or \
                   check_grid_type(current_pos, current_dir,
                                   grid)[0] == "x" or \
                   check_grid_type(current_pos, current_dir, grid)[0] == "C":
                    # situation when direction is (-1, -1)
                    if current_dir[0] < 0 and current_dir[1] < 0:
                        next_pos = (current_pos[0] - 1, current_pos[1] - 1)
                    # situation when direction is (1, 1)
                    elif current_dir[0] > 0 and current_dir[1] > 0:
                        next_pos = (current_pos[0] + 1, current_pos[1] + 1)
                    # situation when direction is (-1, 1)
                    elif current_dir[0] < 0 and current_dir[1] > 0:
                        next_pos = (current_pos[0] - 1, current_pos[1] + 1)
                    # situation when direction is (1, -1)
                    else:
                        next_pos = (current_pos[0] + 1, current_pos[1] - 1)

                else:
                    next_pos = current_pos
                    start_point_near_block += 1
                    path.pop()
            else:
                # situation when direction is (-1, -1)
                if current_dir[0] < 0 and current_dir[1] < 0:
                    next_pos = (current_pos[0] - 1, current_pos[1] - 1)
                # situation when direction is (1, 1)
                elif current_dir[0] > 0 and current_dir[1] > 0:
                    next_pos = (current_pos[0] + 1, current_pos[1] + 1)
                # situation when direction is (-1, 1)
                elif current_dir[0] < 0 and current_dir[1] > 0:
                    next_pos = (current_pos[0] - 1, current_pos[1] + 1)
                # situation when direction is (1, -1)
                else:
                    next_pos = (current_pos[0] + 1, current_pos[1] - 1)

            # when the lazor is stuck between two blocks...
            if start_point_near_block > 1:
                return path, dir

            # check the grid type of the grid that the lazor is pointing to
            grid_content = None
            if pos_check(next_pos, grid):
                if check_grid_type(next_pos, current_dir, grid) is not None:
                    grid_content = check_grid_type(next_pos,
                                                   current_dir, grid)[0]
                    collision_dir = check_grid_type(next_pos,
                                                    current_dir, grid)[1]
                else:
                    next_dir = current_dir
            # when lazor is at the edges of the whole grid
            else:
                next_dir = current_dir

            # use different collision function according to grid type
            # and collision direction
            if grid_content == "A":
                next_dir = self.collide_A(collision_dir, current_dir)
            elif grid_content == "B":
                next_dir = self.collide_B(collision_dir)
            elif grid_content == "C":
                next_dir = self.collide_C(collision_dir, current_dir)
            else:
                next_dir = current_dir

            # here is the situation when the lazor meets Block C
            if type(next_dir) == list:
                print("contain block C")
                path.append(next_pos)
                dir.append(next_dir)
                path_with_C(path, dir, grid)

                return path, dir

            # update the two variables and enter into next iteration
            current_pos = next_pos
            current_dir = next_dir
            if pos_check(current_pos, grid):
                path.append(current_pos)
                dir.append(current_dir)

            if current_dir == (0, 0):
                return path, dir

        return path, dir


def check_grid_type(position, direction, grid):
    '''
    This function can check the grid type of the grid 

    that the lazor is pointing to. The function returns

    grid_type as a string and collision direction as a 

    string as well.

    '''
    if position[0] % 2 == 1:
        if direction[1] > 0:
            # check the lower grid type
            if position[1] < len(grid) - 1:
                grid_type = grid[position[1] + 1][position[0]]
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
            if position[0] < len(grid[0]) - 1:
                grid_type = grid[position[1]][position[0] + 1]
                collision_dir = "horizontal"
                return grid_type, collision_dir
        else:
            # check the left grid type
            if position[0] > 0:
                grid_type = grid[position[1]][int(position[0] - 1)]
                collision_dir = "horizontal"
                return grid_type, collision_dir


def path_with_C(path, direction, grid):
    '''
    This function returns the path of lazor when it meets block C.
    '''
    # here is the previous positions of the lazor
    previous_pos_point = path[-1]
    previous_dir1 = direction[-1][0]
    previous_dir2 = direction[-1][1]
    # initialize a new lazor to get new path
    n1 = Lasor(previous_pos_point, previous_dir1)
    a1, a2 = n1.current_lazor_path(start=previous_pos_point,
                                   direction=previous_dir1, grid=grid)
    # initialize a second new lazor to get new path
    n2 = Lasor(previous_pos_point, previous_dir2)
    b1, b2 = n2.current_lazor_path(start=previous_pos_point,
                                   direction=previous_dir2, grid=grid)
    # combine the two path
    path.extend(a1[1:])
    path.extend(b1[1:])
    return path


def format(block_grid, block_A, block_B, block_C):
    '''
    This function returns the correct format as input for the

    permutation function.

    '''
    grid = []
    not_move = []
    # get the movable blocks and grid
    for i in range(len(block_grid)):
        for j in range(len(block_grid[0])):
            if block_grid[i][j] == "o":
                grid.append('o')
            else:
                not_move.append(block_grid[i][j])

    # get numbers for each type of blocks and grid
    num_of_0 = grid.count('o')
    num_of_A = len(block_A)
    num_of_B = len(block_B)
    num_of_C = len(block_C)
    useable_grid_num = num_of_0 - num_of_A - num_of_B - num_of_C

    useable_grid = []

    # generate available grids
    for i in range(useable_grid_num):
        useable_grid.append("o")

    useable_grid.extend(block_A)
    useable_grid.extend(block_B)
    useable_grid.extend(block_C)

    return useable_grid


def check_results(lazor_starts, directions, new_grid, points):
    '''
    This function checks if the current board is the solution

    to the game.

    **Parameters**

        lazor_starts: *list, tuple*
            A list of tuples that contains the lazor start points.
        directions: *list, tuple*
            A list of tuples that contains the lazor directions.
        new_grid: *list, list, int*
            A 2d array of the newly generated grid.
        points: *list, tuple*
            A list of tuples that contains points the lazor(s) need to pass.

    **Returns**

        new_grid: *list, list, int*
            A 2D array holding integers and letter specifying
            each block's type.
    '''
    def points_through(lazor_starts, directions, new_grid):
        '''
        This function returns the points of path that the lazor(s) go.
        '''
        lazor = []
        list_of_pos = []
        # situation when we have multiple lazors
        for i in range(len(lazor_starts)):
            # create Lasor class instance
            lazor.append(Lasor(lazor_starts[i], directions[i]))

            path1, dir1 = lazor[i].current_lazor_path(lazor_starts[i],
                                                      directions[i], new_grid)
            list_of_pos.extend(path1)

        return list_of_pos

    # get the lazor path for the current board
    path = points_through(lazor_starts, directions, new_grid)

    # return the solution if all required points are crossed
    score = 0
    for i in range(len(points)):
        if points[i] in path:
            score += 1

    if score == len(points):
        print("Success!")
        return path
    else:
        return None


def grid_transform(block_grid):
    '''
    This function returns the transformed grid from small

    coordinate system to big coordinate system.
    '''
    grid = [[1 for i in range(2 * len(block_grid[0]) + 1)]
            for j in range(2 * len(block_grid) + 1)]
    for x in range(len(block_grid)):
        for y in range(len(block_grid[0])):
            grid[2 * x + 1][2 * y + 1] = block_grid[x][y]

    return grid


def fill_grid(possible_boards, original_grid, lazor_starts,
              directions, points, useable_grid):
    '''
    This function returns the solution to the lazor game

    if there is any.

    **Parameters**

        possible_boards: *list*
            A list of possible boards as potential solution.
        original_grid: *list, list, int*
            A 2d array of the original grid.
        lazor_starts: *list, tuple*
            A list of tuples that contains the lazor start points.
        directions: *list, tuple*
            A list of tuples that contains the lazor directions.
        points: *list, tuple*
            A list of tuples that contains points the lazor(s) need to pass.
        useable_grid: *list*
            A list of potential useful grid.


    **Returns**

        new_grid: *list, list, int*
            A 2D array holding integers and letter specifying
            each block's type.
    '''
    # get a instance from possible boards
    instance = possible_boards[0]
    # replace 'o' with '0' in useable_grid
    useable_grid2 = [x if x != 'o' else '0' for x in useable_grid]

    def transform_to_ori(instance, useable_grid):
        '''
        This function returns the dictionary of corresponding values
        for differenct block types.
        '''
        # this gives the unique values
        generated = list(set(instance))
        original = list(set(useable_grid))
        frequency = {}
        transformation = {}
        # get the counts from the instance
        for object in generated:
            frequency[object] = instance.count(object)
        # get the keys and values
        keys = list(frequency.keys())
        values = list(frequency.values())
        # get the corresponding values as keys
        for i in original:
            index = values.index(useable_grid.count(i))
            transformation[keys[index]] = i
            values.pop(index)
            frequency.pop(keys[index])
            keys.pop(index)
        return transformation

    print("checking now...")
    transformation = transform_to_ori(instance, useable_grid2)
    # make a deepcopy of the original grid
    temp = copy.deepcopy(original_grid)
    # refill the boards with eachh permutations
    for item in list(possible_boards):
        iteration = 0
        for i in range(len(original_grid)):
            for j in range(len(original_grid[0])):
                if original_grid[i][j] == "o":
                    original_grid[i][j] = transformation[item[iteration]]
                    iteration += 1
                else:
                    original_grid[i][j] = original_grid[i][j]

        # transform the generated board to big coordinate system
        new_grid = grid_transform(original_grid)
        original_grid = copy.deepcopy(temp)

        # get the solution
        result = check_results(lazor_starts, directions, new_grid, points)
        if result is not None:
            return new_grid
        else:
            continue


def permutation(list_of_objects):
    '''
    The following function is directly adapted from this website:
    https://newbedev.com/how-to-generate-all-the-permutations-of-a-multiset

    This function returns the permutations of the list of objects where
    it should be a list of integers representing the blocks and movable
    blank grid. The output are the unique permutations of these objects
    given as a list of integers 0, ..., n-1.

    Reference: "An O(1) Time Algorithm for Generating Multiset Permutations",
    Tadao Takaoka

    https://pdfs.semanticscholar.org/83b2/6f222e8648a7a0599309a40af21837a0264b.pdf
    '''

    # define a function that will return the list
    def function(head):
        (list, number) = ([], head)
        for i in range(length):
            (dat, number) = list_new[number]
            list.append(dat)
        return list

    # get the unique values as a list
    unique = list(set(list_of_objects))
    list_new = list(reversed(sorted([
        unique.index(i) for i in list_of_objects])))
    length = len(list_new)
    # put list_new into linked-list format
    (val, nxt) = (0, 1)
    for i in range(length):
        list_new[i] = [list_new[i], i + 1]
    list_new[-1][nxt] = None
    head = 0
    afteri = length - 1
    i = afteri - 1
    yield function(head)
    while list_new[afteri][nxt] is not None or \
            list_new[afteri][val] < list_new[head][val]:
        j = list_new[afteri][nxt]
        # create a new var beforek
        if j is not None and list_new[i][val] >= list_new[j][val]:
            beforek = afteri
        else:
            beforek = i
        k = list_new[beforek][nxt]
        list_new[beforek][nxt] = list_new[k][nxt]
        list_new[k][nxt] = head
        if list_new[k][val] < list_new[head][val]:
            i = k
        afteri = list_new[i][nxt]
        head = k
        yield function(head)


def type_and_number(num_A, num_B, num_C):
    '''
    This function returns the type and number of the

    available blocks. It returns three lists of available

    blocks.
    '''
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


def solver(filename):
    '''
    This function is to save the solution as a txt file with filename

    as an input.
    '''
    # read in the boards
    grid, usable_blocks, start_point, direction, points, block_grid = read_bff(
        filename)
    # get the type and number for the three block types
    block_A, block_B, block_C = type_and_number(
        usable_blocks["A"], usable_blocks["B"], usable_blocks["C"])

    # format the available blocks and open grid
    items = format(block_grid, block_A, block_B, block_C)
    possible_boards = list(permutation(items))

    # solve the game
    solution = fill_grid(possible_boards,
                         block_grid, start_point, direction, points, items)

    # convert the resulting solution with more readable code
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if solution[i][j] == 1:
                solution[i][j] = 'x'
            elif solution[i][j] == '0':
                solution[i][j] = 'o'
            else:
                solution[i][j] = solution[i][j]

    # save the solution as a txt file
    with open('solution.txt', 'w') as f:
        if solution is None:
            f.write('IMPOSSIBLE')
        else:
            f.write('\n'.join(' '.join(map(str, row)) for row in solution))


if __name__ == "__main__":

    # please input the file path to the bff file here
    filename = "/Users/mordredyuan/Downloads/Lazor-main/LazorProjectFall2021/Yarn_5.bff"
    start = time.time()
    solver(filename)
    end = time.time()
    print('Total time taken: ', end - start)

    # "/Users/mordredyuan/Downloads/Lazor-main/LazorProjectFall2021/mad_1.bff")
    # The following code are for unit testing purposes.
    # test_grid1 = Grid([['o', 'o', 'C', 'o'],
    #                    ['o', 'o', 'o', 'A'],
    #                    ['A', 'o', 'o', 'o'],
    #                    ['o', 'o', 'o', 'o']])
    # test_grid2 = Grid([['o', 'o', 'o', 'A'],
    #                    ['o', 'o', 'o', 'o'],
    #                    ['A', 'o', 'o', 'C'],
    #                    ['o', 'o', 'A', 'o']])
    # Dark_1.bff
    # grid = [['x', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'x']]
    # A_blocks = 0
    # B_blocks = 3
    # C_blocks = 0
    # lazors = [[(3, 0), (-1, 1)], [(1, 6), (1, -1)],
    #           [(3, 6), (-1, -1)], [(4, 3), (1, -1)]]
    # points = [(0, 3), (6, 1)]
    # Mad_1.bff
    # grid = [['o', 'o', 'o', 'o'], ['o', 'o', 'o', 'o'],
    #         ['o', 'o', 'o', 'o'], ['o', 'o', 'o', 'o']]
    # A_blocks = 2
    # B_blocks = 0
    # C_blocks = 1
    # lazors = [[(2, 7), (1, -1)]]
    # points = [(3, 0), (4, 3), (2, 5), (4, 7)]
    # Mad_4.bff
    # grid = [['o', 'o', 'o', 'o'], ['o', 'o', 'o', 'o'],
    #         ['o', 'o', 'o', 'o'], ['o', 'o', 'o', 'o'], ['o', 'o', 'o', 'o']]
    # A_blocks = 5
    # B_blocks = 0
    # C_blocks = 0
    # lazors = [[(7, 2), (-1, 1)]]
    # points = [(3, 4), (7, 4), (5, 8)]

'''
EN.640.635 Software Carpentry
Lazor Project

In this assignment, a lazor game solver was created to
read and solve a lazor puzzle from the lazor mobile app.
In the solver, we used Depth First Search method to find
the place to place blocks that will give the winning solutions.

'''
from collections import Counter
from typing import Tuple, List, Dict, Optional, Set
import argparse


# Defines lazor direction constants
DIRECTION_UPPER_LEFT = (-1, -1)
DIRECTION_UPPER_RIGHT = (1, -1)
DIRECTION_BOTTOM_LEFT = (-1, 1)
DIRECTION_BOTTOM_RIGHT = (1, 1)
DIRECTIONS = [DIRECTION_UPPER_LEFT, DIRECTION_UPPER_RIGHT, 
                DIRECTION_BOTTOM_LEFT, DIRECTION_BOTTOM_RIGHT]


# class block
class Block(object):
    '''
    This class acts as a initializer for a the block class and contains 
    pass_through and type_str function.
    '''
    def __init__(self, central: Tuple[int, int], grid: 'Grid'):
        '''
        Initialize the block class.
        '''
        self.central = central
        self.grid = grid

    def pass_through(self, in_position: Tuple[int, int], direction: Tuple[int, int]) -> List['Lazor']: # Lasor path through
        '''
        This function raises NotImplementedError when pass through.
        '''
        raise NotImplementedError

    def type_str(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.central})'

    def __repr__(self):
        return self.__str__()


class EmptyBlock(Block): #class block X
    def pass_through(self, in_position: Tuple[int, int], direction: Tuple[int, int]) -> List['Lazor']:
        '''
        **functions**

        This function takes in two tuple arguments and will return return new lazor object 

        after interaction with emptyblock.

        **Parameters**


        in_position: the position in

        direction: the reflect position

        '''

        new_lazor = Lazor(grid=self.grid, start=in_position, direction=direction)
        if self.grid.within_grid(position=new_lazor.end):
            return [new_lazor]
        else:
            return []

    def type_str(self) -> str:
        return 'o'


class ReflectBlock(Block): #class block A
    def pass_through(self, in_position: Tuple[int, int], direction: Tuple[int, int]) -> List['Lazor']:
        '''
        **functions**

        This function takes in two tuple arguments and will return new lazor object 

        after interaction with ReflectBlock.

        **Parameters**

        in_position: the position in

        direction: the reflect position

        '''

        reflect_direction = in_position[0] % 2
        if reflect_direction == 0:
            new_direction = (- direction[0], direction[1]) # reflect on the side
        else:
            new_direction = (direction[0], - direction[1]) # redlect on top and bot

        return [Lazor(grid=self.grid, start=in_position, direction=new_direction)]

    def type_str(self) -> str:
        return 'A'


class OpaqueBlock(Block): #class block B
    '''
    **class**

    This is the class for OpaqueBlock (Type B).

    '''
    def pass_through(self, in_position: Tuple[int, int], direction: Tuple[int, int]) -> List['Lazor']:
        '''
        **functions**

        This function takes in two tuple arguments and will return new lazor object (which is none)

        after interaction with OpaqueBlock.


        **Parameters**


        in_position: the position in

        direction: the reflect position

        '''
        return []

    def type_str(self) -> str:
        return 'B'


class RefractBlock(Block): #class block C
    def __init__(self, central: Tuple[int, int], grid: 'Grid'):
        super().__init__(central, grid)
        self.empty_block = EmptyBlock(central, grid)
        self.reflect_block = ReflectBlock(central, grid)

    def pass_through(self, in_position: Tuple[int, int], direction: Tuple[int, int]) -> List['Lazor']:
        '''
        **functions**

        This function takes in two tuple arguments and will return two lazor objects

        after interaction with RefractBlock.


        **Parameters**


        in_position: the position in

        direction: the reflect position

        '''
        to_return = []
        to_return.extend(self.empty_block.pass_through(in_position, direction)) 
        #laser paththrough
        to_return.extend(self.reflect_block.pass_through(in_position, direction)) 
        #laser also reflect
        return to_return

    def type_str(self) -> str:
        return 'C'


class Lazor(object):
    '''
    **functions**

    get_path: get start point and path from start point

    next_lazor: get laser path location if within grid


    '''

    def __init__(self, grid: 'Grid', start: Tuple[int, int], direction: Tuple[int, int]):
        self.grid = grid
        self.direction = direction
        self.start = start
        self.end = (start[0] + direction[0], start[1] + direction[1])

    def get_path(self) -> Tuple[Tuple[int, int], Tuple[int, int]]: 
        # This function gets the path of the lazor
        return self.start, self.end

    def next_lazor(self) -> Optional['Lazor']: 
        # find next lazor object
        if self.grid.within_grid(position=self.end):
            return Lazor(self.grid, self.end, self.direction)
        return None

    def __eq__(self, other):
        return self.start == other.start and self.direction == other.direction \
                                         and self.end == other.end

    def __str__(self):
        return f'Lazor({self.start}, {self.direction})'

    def __repr__(self):
        return self.__str__()


class LazorPath(object):
    '''
    generate laser path for object in contact
                
    **function**
    
    get_full_path: obtain block type and coordinates on laser path

    get_passed_positions: obtain passed location in list for laser

    has_reached: obtain reached position

    add_lazor: append lazor to lazor path

    '''

    def __init__(self):
        self.lazors: List[Lazor] = []

    def get_full_path(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        '''
        This function returns the full path that the lazor has passed.
        '''
        full_path: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        for lazor in self.lazors:
            full_path.append(lazor.get_path())

        return full_path

    def get_passed_positions(self) -> Set[Tuple[int, int]]:
        '''
        This is where the passed positions of the lazor has been returned.
        '''
        passed = set()
        for lazor in self.lazors:
            passed.add(lazor.start)
            passed.add(lazor.end)
        return passed

    def has_reached(self, positions: List[Tuple[int, int]]) -> bool:
        full_passed_positions = self.get_passed_positions()
        for pos in positions:
            if pos not in full_passed_positions:
                return False
        return True

    def add_lazor(self, lazor: 'Lazor'):
        self.lazors.append(lazor)

    def __str__(self):
        return f'LazorPath({self.lazors})'


class Grid(object):
    '''
    **functions**

    is_block_available: check center coordinates for available block position

    central_to_block_idx: return edge coordinates

    place_block: place block if position available

    revert_block: remove block position to empty block

    within_grid: position check if position is in grid

    reach_boundary: position check for boundary


    **Returns**


    '''
    def __init__(self, blocks: List[List[str]]):
        # Limits are right exclusive
        self.x_limit = len(blocks[0]) * 2 + 1
        self.y_limit = len(blocks) * 2 + 1

        self.grid: List[List[Block]] = []
        self.forbidden_centrals: List[Tuple[int, int]] = []
        for i, row in enumerate(blocks):
            new_row: List[Block] = []
            for j, block in enumerate(row):
                central_pos = (j * 2 + 1, i * 2 + 1)
                if block == 'o':
                    new_row.append(EmptyBlock(central_pos, self))
                elif block == 'A':
                    new_row.append(ReflectBlock(central_pos, self))
                elif block == 'B':
                    new_row.append(OpaqueBlock(central_pos, self))
                elif block == 'C':
                    new_row.append(RefractBlock(central_pos, self))
                elif block == 'x':
                    self.forbidden_centrals.append(central_pos)
                else:
                    raise ValueError(f'Unknown block type: {block}')
            self.grid.append(new_row)

    def is_block_available(self, central: Tuple[int, int]) -> bool:
        '''
        This function is to check the center coordinates for available block position.
        '''
        if central in self.forbidden_centrals:
            return False
        block_x, block_y = self.central_to_block_idx(central=central)
        return isinstance(self.grid[block_y][block_x], EmptyBlock)

    @staticmethod
    def central_to_block_idx(central: Tuple[int, int]) -> Tuple[int, int]:
        '''
        This function returns the edge coordinates for the given grid.
        '''
        return (central[0] - 1) // 2, (central[1] - 1) // 2

    def place_block(self, central: Tuple[int, int], block: Block) -> bool:
        '''
        This function helps with placing the blocks if position is available.
        '''
        if self.is_block_available(central=central):
            block_x, block_y = self.central_to_block_idx(central=central)
            self.grid[block_y][block_x] = block
            return True
        return False

    def revert_block(self, central: Tuple[int, int]) -> bool:
        '''
        This function removes some block position as empty block.
        '''

        if central in self.forbidden_centrals:
            return False
        block_x, block_y = self.central_to_block_idx(central=central)
        self.grid[block_y][block_x] = EmptyBlock(central, self)
        return True

    def within_grid(self, position: Tuple[int, int]) -> bool:
        # position check if position is in grid
        return 0 <= position[0] < self.x_limit and 0 <= position[1] < self.y_limit

    def reach_boundary(self, position: Tuple[int, int]) -> bool:
        # position check for boundary
        return (
                position[0] == 0
                or position[0] == self.x_limit - 1
                or position[1] == 0
                or position[1] == self.y_limit - 1
        )

    @staticmethod
    def nearby_centrals(x, y) -> Set[Tuple[int, int]]:
        # This function return the central coordinates for nearby grid.
        if x % 2 == 0:
            return {(x - 1, y), (x + 1, y)}
        elif y % 2 == 0:
            return {(x, y - 1), (x, y + 1)}

    def get_laser_in_block(self,
                           in_position: Tuple[int, int],
                           direction: Tuple[int, int]) -> Block:
        # This function get the laser in block and returns a grid object.
        start_point_centrals = self.nearby_centrals(in_position[0], in_position[1])
        end_point_centrals = self.nearby_centrals(in_position[0] + direction[0], 
                                                    in_position[1] + direction[1])
        block_central: Tuple[int, int] = start_point_centrals.intersection(
                                                        end_point_centrals).pop()
        block_i = (block_central[0] - 1) // 2
        block_j = (block_central[1] - 1) // 2
        return self.grid[block_j][block_i]

    def __str__(self):
        return '\n'.join([''.join([f'[{block.type_str()}]' for block in row]) 
                                                                for row in self.grid])

    def to_output(self) -> str:
        return '\n'.join([' '.join([f'{block.type_str()}' for block in row]) 
                                                                for row in self.grid])


class Game(object):
    '''
    This is the class for the game objects.
    '''
    def __init__(self,
                 grid: Grid,
                 intersection_points: List[Tuple[int, int]],
                 blocks_to_place: Counter,
                 init_lazor: Lazor):
        self.grid: Grid = grid
        self.intersection_points = intersection_points
        self.blocks_to_place = blocks_to_place
        self.init_lazor = init_lazor

    def is_winning(self, lazor_path: LazorPath) -> bool:
        return lazor_path.has_reached(positions=self.intersection_points)

    @classmethod

    def read_bff(cls, filename: str) -> 'Game':
        '''
        Reads in .bff file, returning relevant board parameters
            
        **Parameters**
                
            None
            
        **Returns**
                
        filename: str
                Name of bff file
        block_strs: list of list
                Type of blocks
        blocks_to_place: Dict
                Block type and corresponding number
        init_lazor: None type
                initial lazor point and vector
        intersection_points: list
                List of intersection point
        init_grid: Grid
                initial grid info

            '''

        block_strs: List[List[str]] = []
        blocks_to_place: Dict[str, int] = {}
        init_lazor: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
        intersection_points: List[Tuple[int, int]] = []

        with open(filename, 'r') as f:
            # open the file and read the contents
            read_grid: bool = False
            for line in f:
                if line.startswith('#'):
                    continue
                if line.startswith('GRID START'):
                    read_grid = True
                elif line.startswith('GRID STOP'):
                    read_grid = False
                elif read_grid:
                    #append block information to block strings
                    block_strs.append(line.strip().split())
                elif line.startswith('A') or line.startswith('B') or line.startswith('C'):
                    line_splits = line.split()
                    blocks_to_place[line_splits[0]] = int(line_splits[1])
                elif line.startswith('L') and init_lazor is None:
                    line_splits = line.split()
                    init_lazor = (
                        (int(line_splits[1]), int(line_splits[2])),
                        (int(line_splits[3]), int(line_splits[4]))
                    )
                    assert init_lazor[1] in DIRECTIONS, 'Direction invalid.'
                elif line.startswith('P'):
                    line_splits = line.split()
                    intersection_points.append((int(line_splits[1]), int(line_splits[2])))
        init_grid = Grid(block_strs)
        return cls(grid=init_grid, intersection_points=intersection_points, 
                blocks_to_place=Counter(blocks_to_place), 
            init_lazor=Lazor(grid=init_grid, start=init_lazor[0], direction=init_lazor[1]),)


def build_lazor_path(grid: Grid,
                     lazor_path: LazorPath,
                     current_lazor: Lazor,
                     blocks_along_path: List[Tuple[int, int]],
                     is_init: bool = False):
    '''
    This function takes in a grid obj, a lazer_path obj, a Lazor obj, a list, and a bool,
    and returns function.
    '''
    if not is_init:
        has_visited = lazor_path.add_lazor(current_lazor)
        if has_visited:
            return

    if not is_init and grid.reach_boundary(current_lazor.end):
        return

    block_in_pos = current_lazor.end if not is_init else current_lazor.start
    laser_in_block: Block = grid.get_laser_in_block(in_position=block_in_pos, 
                                                    direction=current_lazor.direction)
    blocks_along_path.append(laser_in_block.central)
    new_lazors = laser_in_block.pass_through(in_position=block_in_pos, 
                                             direction=current_lazor.direction)
    for new_lazor in new_lazors:
        build_lazor_path(grid=grid, current_lazor=new_lazor, 
                         lazor_path=lazor_path, blocks_along_path=blocks_along_path, 
                         is_init=False)

# Set up DFS
def solve_game(game: Game) -> Optional[Grid]:
    '''
    This is the main solver in this project. Depth First Search algorithms
    are used in creating this solver.
    '''

    has_placed: Set[Tuple[int, int]] = set()


    def _solve() -> bool: #check empty value

        current_lazor_path = LazorPath()
        current_available_blocks: List[Tuple[int, int]] = []
        build_lazor_path(grid=game.grid, lazor_path=current_lazor_path, 
                         current_lazor=game.init_lazor, 
                         blocks_along_path=current_available_blocks, is_init=True)

        # Whether this left some blocks unused
        if game.is_winning(lazor_path=current_lazor_path):
            return True

        for block in current_available_blocks:
            if block in has_placed:
                continue

            # Actions
            has_placed.add(block)

            remaining_actions: List[str] = ['o'] + [k for k, v in game.blocks_to_place.items() if v > 0]
            for action in remaining_actions:  # need to figure out the action type
                if action == 'o':
                    place_success = True
                elif action == 'A':
                    new_block = ReflectBlock(central=block, grid=game.grid)
                    place_success = game.grid.place_block(central=block, block=new_block)
                elif action == 'B':
                    new_block = OpaqueBlock(central=block, grid=game.grid)
                    place_success = game.grid.place_block(central=block, block=new_block)
                elif action == 'C':
                    new_block = RefractBlock(central=block, grid=game.grid)
                    place_success = game.grid.place_block(central=block, block=new_block)
                else:
                    raise ValueError('Invalid action.') # raise error for Invalid action

                if action != 'o' and place_success:
                    game.blocks_to_place[action] -= 1

                if place_success and _solve():
                    return True
                else:
                    game.grid.revert_block(central=block)
                    if action != 'o' and place_success:
                        game.blocks_to_place[action] += 1
                    continue
            has_placed.remove(block)

        return False

    return game.grid if _solve() else None


if __name__ == '__main__':
    game = Game.read_bff(filename='/Users/mordredyuan/Downloads/Lazor-main/LazorProjectFall2021/mad_4.bff')
    solution = solve_game(game)
    with open('solution.txt', 'w') as f:
        if solution is None:
            f.write('IMPOSSIBLE')
        else:
            f.write(solution.to_output())


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
    #grid = [['x', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'x']]
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

import numpy as np

# Constants
MINE = 1000
OPEN = 2000
FLAG = 3000

# board metadata
board_meta = {
    'easy': {
        'board_size': (9, 9),
        'mine_num': 10,
        'annot_size': 20
    },
    'medium': {
        'board_size': (16, 16),
        'mine_num': 25,
        'annot_size': 10
    },
    'hard': {
        'board_size': (16, 30),
        'mine_num': 99,
        'annot_size': 8
    }
}

# GameAgent
class Board:
    def __init__(self, level="easy", free=1):
        '''
        initialize the board information with the given level
        '''
        meta = board_meta[level]
        self.board_size = meta["board_size"]
        self.mine_num = meta["mine_num"]
        self.annot_size = meta["annot_size"]
        self.cell_num = self.board_size[0] * self.board_size[1]
        self.unmark_mine_num = self.mine_num
        self.unmark_cell_num = self.cell_num
        self.init_safe_cell_num = int(free*(np.round(np.sqrt(self.cell_num))))
        self.ans, self.init_safe_cell = self.generate_board()

    def generate_board(self):
        '''
        genearte the borad with the initialized information. 
        
        output: 
            ans: board_size numpy array storing answer
            safe_call[idx]: the initialized save call positions
        '''
        mines = set()
        while len(mines) < self.mine_num:
            i = np.random.randint(0, self.board_size[0])
            j = np.random.randint(0, self.board_size[1])
            mines.add((i, j))
        
        # Set the size of and to (board_size.x+2, board_size.y+2) for easier calculation
        ans = np.zeros((self.board_size[0]+2, self.board_size[1]+2), dtype=np.int32)
        for mine in mines:
            i, j = mine[0]+1, mine[1]+1
            ans[i, j] = MINE
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    new_i = i + di
                    new_j = j + dj
                    if ans[new_i, new_j] == MINE:
                        continue
                    ans[new_i, new_j] += 1
        # Set ans back to (board_size.x, board_size.y)
        ans = ans[1:-1, 1:-1]
        safe_cell = np.argwhere(ans!=MINE)
        idx = np.random.choice(np.arange(0, safe_cell.shape[0]), self.init_safe_cell_num, replace=False)

        return ans, safe_cell[idx]    
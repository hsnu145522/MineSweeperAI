import numpy as np
import matplotlib.pyplot as plt
# from itertools import combinations as comb
from collections import OrderedDict
from Board import Board
from Player import PlayerAgent
import os
import time

# Constants
MINE = 1000
OPEN = 2000
FLAG = 3000

class MineSweeper:
    def __init__(self, level, free):
        self.board = Board(level, free)
        # print(initial_board.ans, initial_board.init_safe_cell)
        self.playerAgent = PlayerAgent(self.board)
        # print(playerAgent.KB, playerAgent.KB0)
        # print(playerAgent.board.board_size)
        # self.foldername = f'{level}_{self.board.init_safe_cell_num}_{int(time.time())}'
        # os.mkdir(self.foldername)
    
    def start(self):
        print("Game Started ...")
        while self.checkEnd():
            flag = self.playerAgent.iter()
            if flag > 0:
                self.board = self.playerAgent.board
                # if flag == 1:
                    # self.plot_board()
                    # plt.savefig(f'{self.playerAgent.cnt}_{int(time.time())}final.png', dpi=300, transparent=True)
                    # plt.clf()
            else:
                break
        print('--------------------')
        print(f'{self.playerAgent.cnt} / {self.board.cell_num} cells marked/ all cells')
        print(f'Pairwise matching: {self.playerAgent.not_found} times')
        print("--------------------")
        if self.playerAgent.cnt < self.board.cell_num:
            self.plot_board()
            plt.savefig(f'test/{level}_{self.playerAgent.cnt}_{int(time.time())}final.png', dpi=300, transparent=True)
            plt.clf()
            return 0, self.playerAgent.not_found 
        return 1, self.playerAgent.not_found 
        # os.rename(folder, f'{folder} {cnt} {not_found}')

    def checkEnd(self):
        # print(len(self.playerAgent.KB0))
        return self.playerAgent.KB
    
    def plot_board(self):
        status = self.playerAgent.status
        ans = self.board.ans
        annot_size = self.board.annot_size
        l, w = status.shape
        args_mine = OrderedDict(
            color='r',
            fontsize=annot_size,
            horizontalalignment='center',
            verticalalignment='center')
        args_hint = OrderedDict(
            fontsize=annot_size,
            horizontalalignment='center',
            verticalalignment='center')

        for i in range(l):
            for j in range(w):
                if status[i, j] == -1:
                    plt.fill([j, j, j+1, j+1], [l-i-1, l-i, l-i, l-i-1], c='gray', alpha=0.3)
                elif status[i, j] == FLAG:
                    plt.fill([j, j, j+1, j+1], [l-i-1, l-i, l-i, l-i-1], c='yellow', alpha=0.3)
                elif status[i, j] == OPEN:
                    plt.fill([j, j, j+1, j+1], [l-i-1, l-i, l-i, l-i-1], c='lime', alpha=0.3)
                if ans[i, j] == MINE:
                    plt.annotate('x', (j+0.5, l-i-0.5), **args_mine)
                else:
                    plt.annotate(ans[i, j], (j+0.5, l-i-0.6), **args_hint)

        plt.gca().set_xticks(np.arange(w+1))
        plt.gca().set_yticks(np.arange(l+1))
        plt.gca().set_xlim([0, w])
        plt.gca().set_ylim([0, l])
        plt.gca().tick_params(bottom=False, top=False, left=False, right=False)
        plt.gca().tick_params(labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        plt.gca().grid(which='major', color='k', linestyle='-')
        plt.gca().set_aspect('equal')


if __name__ == "__main__":
    level = "hard"
    timestoplay = 1
    win = 0
    num_matches = []
    free = 2
    for i in range(timestoplay):
        # if i%25:
        #     free+=1
        game = MineSweeper(level, free)
        flag, num = game.start()
        num_matches.append(num)
        if flag:
            win+=1
    
    print("-----------------------------------")
    print(f"level: {level}  {win}/{timestoplay}")
    print(f"matches per play {sum(num_matches)/len(num_matches)}")
    print("-----------------------------------")




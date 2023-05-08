import numpy as np
import os
import matplotlib.pyplot as plt
from itertools import combinations as comb
# from Board import Board

# Constants
MINE = 1000
OPEN = 2000
FLAG = 3000

# PlayerAgent
class PlayerAgent:
    def __init__(self, board):
        self.board = board
        self.KB0 = {}
        self.KB = []
        init_safe_cell = self.board.init_safe_cell
        for cell in init_safe_cell:
            clause = ",".join(cell.astype(str))
            clause = f'not {clause}'
            self.KB.append([clause])

        # initialize the status
        # -1 for unmarked
        # OPEN for marked as safe
        # FLAG for marked as mine
        self.status = np.ones(self.board.board_size, dtype=np.int32) * -1
        self.cnt, self.not_found = 0, 0

    # get the eight neighbors of given cell
    def get_neighbors(self, i, j):
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di==0 and dj==0:
                    continue
                new_i = i + di
                new_j = j + dj
                if (new_i<0 or new_i>=self.board.board_size[0] or
                        new_j<0 or new_j>=self.board.board_size[1]):
                    continue
                neighbors.append(f'{new_i},{new_j}')
        return neighbors


    # get all unmarked cells
    def get_unmark_cells(self):
        cells = []
        for i in range(self.board.board_size[0]):
            for j in range(self.board.board_size[1]):
                if f'{i},{j}' not in self.KB0:
                    cells.append(f'{i},{j}')
        return cells

    # check whether the two clauses are identical
    # Both clause1 and clause2 are lists.
    def isduplicate_pairwise(self,clause1, clause2):
        match = 0
        for literal in clause1:
            if literal in clause2:
                match += 1
        if match==len(clause2) and len(clause1)==len(clause2):
            return True
        return False


    # check whether there exists any clause identical to the given clause in the
    # knowledge base 
    # targetclause is a list contain strings in it.
    def hasduplicate(self,targetclause):
        if type(targetclause)==type(""):
            targetclause = [targetclause]
        for clause in self.KB:
            if self.isduplicate_pairwise(targetclause, clause):
                return True
        return False


    # subsumption for single-literal clause
    # clause is just a string in this function
    def literal_subsumption(self, clause):
        for i in range(len(self.KB)):
            if clause in self.KB[i]:
                self.KB[i] = []
            

    # subsumption between two clauses
    def subsumption_pairwise(self, i, j):
        '''
        See if there are stricter clauses that we can eliminate.
        return true if updated, false if not updated
        '''
        clause1, clause2 = self.KB[i], self.KB[j]
        match = 0
        for literal in clause1:
            if literal in clause2:
                match += 1
        if match==len(clause1) and len(clause1)<len(clause2):
            self.KB[j] = []
            return True
        elif match==len(clause2) and len(clause2)<len(clause1):
            self.KB[i] = []
            return True
        return False


    # subsumption for given clause to the knowledge base
    # clause is a list with strings in it.
    def subsumption(self, clause):
        insert = True
        update = False
        for i in range(len(self.KB)):
            sentence = self.KB[i]
            if not len(sentence):
                continue
            match = 0
            for literal in clause:
                if literal in sentence:
                    match += 1
            if match==len(sentence) and len(sentence)<=len(clause):
                insert = False
            elif match==len(clause) and len(sentence)>len(clause):
                self.KB[i] = []
                update = True
        if insert:
            self.KB.append(clause)
            update = True
        return update


    # generate new clause if there is only one pair on complementary literals
    # between two clauses
    # both clauses are lists.
    def comp(self, clause1, clause2):
        c1 = list(clause1)
        c2 = list(clause2)
        match = 0
        for literal in clause1:
            if 'not' in literal:
                l = literal[4:]
            else:
                l = f'not {literal}'
            if l in clause2:
                c1.remove(literal)
                c2.remove(l)
                match += 1
        '''
        If there is only one pair of complementary literals:
        Apply resolution to generate a new clause, which will be inserted into the KB
        '''
        if match == 1:
            return list(set(c1+c2))
        else:
            return []
    
    def iter(self):
        flag = 0
        # Late game, when unmark_cell_num is less than 10, add global constraints. 
        unmark_cell_num = self.board.unmark_cell_num
        unmark_mine_num = self.board.unmark_mine_num           
        if unmark_cell_num <= 10 and unmark_cell_num>=unmark_mine_num:
            # print("Late Game ...")
            unmark_cells = self.get_unmark_cells()
            for clause in list(comb(unmark_cells, unmark_cell_num-unmark_mine_num+1)):
                clause = list(clause)
                if not self.hasduplicate(clause):
                    self.subsumption(clause)
            for clause in list(comb(unmark_cells, unmark_mine_num+1)):
                clause = list(clause)
                for i in range(len(clause)):
                    clause[i] = f'not {clause[i]}'
                if not self.hasduplicate(clause):
                    self.subsumption(clause)
        
        # Normal Loop
        self.KB = sorted(self.KB, key=lambda c:len(c))
        found = False
        for i in range(len(self.KB)):
            clause = self.KB[i]
            # First case: If there is a single-lateral clause in KB:
            if len(clause) == 1:
                self.cnt+=1
                found = True
                # print("Step count:", self.cnt,"Clause name:", clause[0])

                # Mark that cell as safe or mined.
                # safe case
                if clause[0].startswith('not'):
                    targetname = clause[0][4:]
                    # Move the clause to KB0
                    self.KB0[targetname] = False
                    self.KB[i] = []
                    self.board.unmark_cell_num -=1

                    # remove clause[0] (not {targetgame})
                    self.literal_subsumption(clause[0])

                    # Process the "matching" of that clause to all the remaining clauses in the KB.

                    # remove targetname
                    for j in range(len(self.KB)):
                        if targetname in self.KB[j]:
                            self.KB[j].remove(targetname)
                    cell = targetname.split(',')
                    x, y = int(cell[0]), int(cell[1])
                    self.status[x, y] = OPEN
                    hint = self.board.ans[x, y]
                    neighbors = self.get_neighbors(x, y)
                    for j in range(len(neighbors)):
                        # only consider the unmarked cells
                        if neighbors[j] in self.KB0:
                            if self.KB0[neighbors[j]] == True:
                                hint -= 1
                            neighbors[j] = ''
                    neighbors = [n for n in neighbors if len(n) > 0]
                    # m = number of unmarked neighbors
                    # n = hint
                    m = len(neighbors)
                    n = hint
                    # (m == n): insert the m single-literal positive clauses
                    # to the knowledge base, one for each unmarked neighbor
                    if m == n:
                        for neighbor in neighbors:
                            if not self.hasduplicate(neighbor):
                                self.KB.append([neighbor])
                    # (n == 0): insert the m single-literal negative clauses
                    # to the knowledge base, one for each unmarked neighbor
                    elif n == 0:
                        for neighbor in neighbors:
                            if not self.hasduplicate(f'not {neighbor}'):
                                self.KB.append([f'not {neighbor}'])
                    # (m > n > 0): generate CNF clauses and add them to the
                    # knowledge base
                    elif m > n:
                        for clause in list(comb(neighbors, len(neighbors)-hint+1)):
                            clause = list(clause)
                            if not self.hasduplicate(clause):
                                self.subsumption(clause)
                        for clause in list(comb(neighbors, hint+1)):
                            clause = list(clause)
                            for i in range(len(clause)):
                                clause[i] = f'not {clause[i]}'
                            if not self.hasduplicate(clause):
                                self.subsumption(clause)
                    else:
                        print(f'ERROR: hint: {hint}, neighbors: {len(neighbors)}')                  
                
                # Mine case
                else:
                    # put the marked cell into KB0
                    self.KB0[clause[0]] = True
                    # remove that literal from knowledge base
                    self.KB[i]  = []
                    self.board.unmark_cell_num -= 1
                    self.board.unmark_mine_num -= 1
                    self.literal_subsumption(clause[0])
                    # clause[0] is true, so remove all not {clause[0]}
                    for j in range(len(self.KB)):
                        if f'not {clause[0]}' in self.KB[j]:
                            self.KB[j].remove(f'not {clause[0]}')
                    cell = clause[0].split(',')
                    x, y = int(cell[0]), int(cell[1])
                    self.status[x, y] = FLAG
                
                break
            
        # The case we could not find single-lateral clause in the KB.
        if not found:
            # print('Pairwise matching ...')
            update = False
            self.not_found += 1
            # print(f'size of KB: {len(self.KB)}')
            for i in range(len(self.KB)):
                if len(self.KB[i]) ==0:
                    continue
                for j in range(i+1, len(self.KB)):
                    if len(self.KB[j])==0:
                        continue
                    # check whether the two clauses are identical
                    if not self.isduplicate_pairwise(self.KB[i], self.KB[j]):
                        if not self.subsumption_pairwise(i, j):
                            '''
                            For the step of pairwise matching, to keep the KB from growing too fast, only
                            match clause pairs where one clause has only two literals.
                            '''
                            if len(self.KB[i])>2 and len(self.KB[j])>2:
                                continue
                            new_clause = self.comp(self.KB[i], self.KB[j])
                            if new_clause:
                                if not self.hasduplicate(new_clause):
                                    if self.subsumption(new_clause):
                                        update = True
                        else:
                            update = True
                    else:
                        self.KB[j] = []
                        update = True
            # stop if the knowledge base didn't update after pairwise matching
            # (can neither find a single-literal clause nor generate any new
            # clause from the knowkedge base)
            if not update:
                return 0
            else:
                flag = 1
            
        self.KB = [c for c in self.KB if len(c)>0]
        if flag:
            # haven't found a single-literal clause
            return 2
        else:
            # found a single-literal clause
            return 1
        
        


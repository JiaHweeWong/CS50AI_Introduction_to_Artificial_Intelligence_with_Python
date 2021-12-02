import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # print("add_knowledge")
        ###### (1) ######
        # print("add_knowledge 1")
        self.moves_made.add(cell)

        ###### (2) ######
        # print("add_knowledge 2")
        self.mark_safe(cell)

        ###### (3) ######
        # print("add_knowledge 3")
        # Find the neighbouring cells
        # (row_num, col_num)
        neighbouring_cells = set()
        row = cell[0]
        col = cell[1]
        
        # Neighbours Above
        if (row - 1 >= 0): # if cell is not at the top row
            neighbouring_cells.add((row-1, col))

            if (col-1 >= 0): # if neighbour cell diagonally above is not at the first column
                neighbouring_cells.add((row-1, col-1))
            if (col+1 <= self.width-1): # if neighbour cell diagonally above is not at the last column
                neighbouring_cells.add((row-1, col+1))
        
        # Neighbours Either Side
        if (col-1 >= 0): # if left neighbour cell is not at the first column
            neighbouring_cells.add((row, col-1))
        if (col+1 <= self.width-1): # if right neighbour cell is not at the last column
            neighbouring_cells.add((row, col+1))

        # Neighbours Below
        if (row + 1 <= self.height - 1): # if cell is not at the last row
            neighbouring_cells.add((row+1, col))

            if (col-1 >= 0): # if neighbour diagonally below is not at the first column
                neighbouring_cells.add((row+1, col-1))
            if (col+1 <= self.width-1): # if neighbour diagonally below is not at the last column
                neighbouring_cells.add((row+1, col+1))
        
        num_mines_neighbours = count
        neighbours_to_remove = set()
        for neighbour in neighbouring_cells:
            if neighbour in self.mines:
                neighbours_to_remove.add(neighbour)
                num_mines_neighbours -= 1
            if neighbour in self.safes:
                neighbours_to_remove.add(neighbour)
        
        neighbouring_cells -= neighbours_to_remove

        sentence = Sentence(neighbouring_cells, num_mines_neighbours) # create the sentence
        
        # append sentence into knowledge base
        self.knowledge.append(sentence)

        ###### (4) ######
        # print("add_knowledge 4")
        # Obtain the additional mines and safes that can be concluded from the sentence
        # sentence_mines = sentence.known_mines().copy() 
        # sentence_safes = sentence.known_safes().copy()

        # # mark the mines and safes
        # for mine in sentence_mines:
        #     self.mark_mine(mine)
        # for safe in sentence_safes:
        #     self.mark_safe(safe)
        
        ###### (5) ######
        # print("add_knowledge 5")
        # for sent in self.knowledge: # for each sentence in KB
        #     for mine in self.mines: # for each known mine
        #         sent.mark_mine(mine) # mark the mine in the sentence
        #     for safe in self.safes: # for each known safe
        #         sent.mark_safe(safe) # mark the safe in the sentence
        #     sent_mines = sent.known_mines().copy() # obtain any new inferences about mines
        #     sent_safes = sent.known_safes().copy() # obtain any new inferences about safes
        #     for mine in sent_mines: # for each new known mines
        #         self.mark_mine(mine) # mark the mine for all sentences
        #     for safe in sent_safes: # for each new known safe
        #         self.mark_safe(safe) # mark the safe for all sentences

        # Mark cells as safe or mines based on updated knowledge base
        mines_to_be_marked = []
        safes_to_be_marked = []
        for sent in self.knowledge:
            for mine in sent.known_mines():
                mines_to_be_marked.append(mine)
            for safe in sent.known_safes():
                safes_to_be_marked.append(safe)
        for mine in mines_to_be_marked:
            self.mark_mine(mine)
        for safe in safes_to_be_marked:
            self.mark_safe(safe)

        # Update AI's knowledge base if there are any new inferences made
        new_knowledge = []
        for sent in self.knowledge:
            if sentence.cells and sent.cells != sentence.cells: # if sentence is not empty and sentence is not sent
                if sent.cells.issubset(sentence.cells): # if sent is a subset of sentence
                    inferred_sent = Sentence(sentence.cells-sent.cells, max(sentence.count-sent.count, 0))
                    new_knowledge.append(inferred_sent)
                if sentence.cells.issubset(sent.cells): # if sentence is a subset of sent
                    inferred_sent = Sentence(sent.cells-sentence.cells, max(sent.count-sentence.count,0))
                    new_knowledge.append(inferred_sent)
            
        self.knowledge.extend(new_knowledge) # extend the new knowledge
        # print("add_knowledge done")

        # # print current knowledge base
        # print("Number of sentenes in knowledge base: {}".format(len(self.knowledge)))
        # for sentence in self.knowledge:
        #     print("{} = {}".format(sentence.cells, sentence.count))
                     
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # print("make_safe_move")
        for safe in self.safes: # for each safe cell
            if safe not in self.moves_made: # if move has not been made on the safe cell
                # print("safe move:", safe)
                return safe # return safe cell to be the next move
        return None # if there are no safe cells available to move to, return a random move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # print("make_random_move")
        all_moves = set() # all moves/cells
        for row in range(0,8):
            for col in range(0,8):
                move = (row, col)
                all_moves.add(move)
        all_moves = all_moves - self.moves_made - self.mines # from set of all moves, remove moves that have been made or are mines
        if len(all_moves) == 0:
            return None
        else:
            return random.choice(list(all_moves))
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
        if self.count == len(self.cells):
            return set(self.cells)
        return set()
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
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
        Atualiza o conhecimento com base na célula revelada e seu número de vizinhos com minas.
        """
        # Marca a célula como uma jogada feita
        self.moves_made.add(cell)

        # Marca a célula como segura
        self.mark_safe(cell)

        # Determina os vizinhos da célula
        neighbors = set()
        i, j = cell
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if (di, dj) == (0, 0):
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbor = (ni, nj)
                    if neighbor not in self.safes and neighbor not in self.mines:
                        neighbors.add(neighbor)

        # Cria uma nova sentença considerando as minas conhecidas
        count -= len(neighbors & self.mines)  # Reduz o contador para minas conhecidas
        neighbors -= self.mines  # Remove minas conhecidas
        new_sentence = Sentence(neighbors, count)

        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # Atualiza o conhecimento para inferir novas minas ou seguras
        self.update_knowledge()

    def update_knowledge(self):
        """
        Atualiza o conhecimento para inferir novas minas, células seguras e combinações de sentenças.
        """
        changes = True
        while changes:
            changes = False

            # Identifica minas e células seguras conhecidas
            for sentence in self.knowledge:
                for mine in sentence.known_mines():
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        changes = True
                for safe in sentence.known_safes():
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        changes = True

            # Remove sentenças vazias
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            # Combina sentenças para inferir novas informações
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                        inferred_cells = sentence2.cells - sentence1.cells
                        inferred_count = sentence2.count - sentence1.count
                        inferred_sentence = Sentence(inferred_cells, inferred_count)
                        if inferred_sentence not in self.knowledge:
                            self.knowledge.append(inferred_sentence)
                            print(f"Sentença inferida: {inferred_sentence}")
                            changes = True


    def infer_new_sentences(self):
        """
        Infers new sentences based on the current knowledge base.
        """
        new_sentences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    inferred_cells = sentence2.cells - sentence1.cells
                    inferred_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(inferred_cells, inferred_count)
                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)

        self.knowledge.extend(new_sentences)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        return random.choice(choices) if choices else None

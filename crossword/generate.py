import sys
from collections import deque
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):

        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency() #remove as palavras do dominio que nao tem comprimento correto
        self.ac3() #usa ac3 para garantir que as palavras que se cruzam tenham pelo menos um valor consistente
        return self.backtrack(dict()) #usa o backtrack para atribuir palavras a cada variavel ate a solucao

    def enforce_node_consistency(self):
        #percorre todas as variaveis do CSP, verifica se alguma palavra do dominio nao tem o tamanho correto
        #remove as invalidas
        print("enforce node conssitency")
        for variable in self.domains:
            lenght = variable.length
            invalid_words = {word for word in self.domains[variable] if len(word) != lenght}
            for word in invalid_words:
                self.domains[variable].remove(word)

   
            
    def revise(self, x, y):
        #verifica se x e y tem sobreposicao, se tiverem, verifica se ha palavras em x que nunca 
        #podem ser compativeis com y e as remove do dominio de x
        print("revise")
        if (x,y) not in self.crossword.overlaps:
            return False
        
        overlap = self.crossword.overlaps[(x,y)]
        if overlap is None:
            return False
        
        i,j = overlap
        revise = False
        remove = set()

        for wx in self.domains[x]:
            match = False
            for wy in self.domains[y]:
                if i < len(wx) and j < len(wy) and wx[i] == wy[j]:
                    match = True
                    break
            if not match:
                remove.add(wx)

        if remove:
            print("removeu")
            self.domains[x] -= remove
            revise = True
            if not self.domains[x]:
                print(f"Domínio de {x} ficou vazio! Impossível resolver.")
        
        return revise

        

    def ac3(self, arcs=None):
        #se arcs nao for passado, cria uma fila de pares (x,y), com sobreposicao
        print("ac3")
        if arcs is not None:
            queue = deque(arcs)
        else:
            
            queue = deque()
            for x in self.domains:
                for y in self.domains:
                    if x != y and self.crossword.overlaps.get((x, y)) is not None:
                        queue.append((x, y))
        #para cada par(x,y) chama revise(x,y), que pode reduzir o dominio de x
        while queue:
            x, y = queue.popleft()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False  #dominio vazio

                #se revise(x,y) remove valores, adiciona (z,x) para verificar os vizinhos
                for z in self.crossword.neighbors(x):
                    if z != y:  
                        queue.append((z, x))

        return True #consistencia aplicada e nenhum dominio vazio

    def assignment_complete(self, assignment):
        #retorna true se todas as variaveis tem uma palavra atribuida
        print("assignment compleete")
        for var in self.crossword.variables:
            if var not in assignment:
                return False
            elif assignment[var] is None:
                return False
        return True

    def consistent(self, assignment):
        #verifica se a atribuicao esta correta
        used_words = set()
        print("consistetn")
        for var, word in assignment.items():
            #if the word repeat
            if word in used_words:
                return False
            used_words.add(word)
            #if the lenght does not match
            if len(word) != var.length:
                return False
            
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps.get((var, neighbor))
                    
                    if overlap is not None:
                        i,j = overlap

                        #if the intersection matches
                        if word[i] != assignment[neighbor][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):

        #Retorna uma lista de valores no domínio de `var`, ordenados pelo número de valores que eles eliminam 
        #para variáveis vizinhas ainda não atribuídas.
        #O primeiro valor da lista deve ser aquele que elimina o menor número de opções para os vizinhos.

        elim_count = {}  # Dicionário para armazenar a contagem de eliminações para cada valor no domínio de `var`

        for value in self.domains[var]:  # Para cada palavra possível no domínio da variável `var`
            count = 0  # Conta quantas palavras serão eliminadas dos domínios dos vizinhos
            for neighbor in self.crossword.neighbors(var):  # Percorre os vizinhos da variável
                if neighbor not in assignment:  # Apenas considera vizinhos ainda não atribuídos
                    count += sum(1 for n_value in self.domains[neighbor] 
                                if not self.consistent({var: value, neighbor: n_value}))

            elim_count[value] = count  # Associa a palavra ao número de valores eliminados nos vizinhos

        return sorted(self.domains[var], key=lambda v: elim_count[v])  
        # Ordena os valores com base no número de eliminações (menor primeiro)

        
    def select_unassigned_variable(self, assignment):
        """
        Retorna uma variável não atribuída que ainda não está em `assignment`.
        Escolhe a variável com:
        1. O menor número de valores restantes em seu domínio.
        2. Em caso de empate, a variável com o maior número de vizinhos.
        3. Se ainda houver empate, qualquer uma das empatadas pode ser escolhida.
        """
        print("select unasigned variables")
        unassigned = [v for v in self.crossword.variables if v not in assignment]  # Lista de variáveis não atribuídas
        if not unassigned:
            return None  # Se não houver mais variáveis, retorna None (todos já foram atribuídos)
        
        sorted_variables = []
        for v in unassigned:
            num_values = len(self.domains[v])  # Quantidade de valores no domínio da variável
            num_neighbors = len(self.crossword.neighbors(v))  # Quantidade de vizinhos no grafo do problema
            
            sorted_variables.append((v, num_values, num_neighbors))  # Armazena a variável com suas métricas
        
        sorted_variables.sort(key=lambda x: (x[1], -x[2]))  # Ordena por: menos valores no domínio e mais vizinhos
        
        return sorted_variables[0][0]  # Retorna a variável com menor domínio e mais vizinhos (se houver empate)


    def backtrack(self, assignment):
    # Se a atribuição está completa, retorna a solução.
    # Escolhe uma variável e tenta atribuir um valor.
    # Se a atribuição é consistente, chama backtrack() recursivamente.
    # Se não encontrar solução, desfaz a escolha (backtracking).
        print("backtrack")
        if len(assignment) == len(self.crossword.variables):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            assignment[var] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
        
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
import sys, copy

from PIL.Image import FLOYDSTEINBERG

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
        """
        Return 2D array representing a given assignment.
        """
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
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        copied_domains = copy.deepcopy(self.domains)
        for cell, words in copied_domains.items():
            for word in words:
                if cell.length != len(word):
                    self.domains[cell].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        copied_x_domains = copy.deepcopy(self.domains[x])

        # Searching for all the overlaps between x and y
        if overlap:
            # Remove Xs words that don't match with Ys
            for x_word in copied_x_domains:
                for y_word in self.domains[y]:
                    match = False
                    if x_word[overlap[0]] == y_word[overlap[1]]: 
                        match = True
                        break
                if match == False:
                    self.domains[x].remove(x_word)
                    revised = True
                else:
                    continue
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # Creating the queue
        queue = []

        if arcs:
            queue = arcs
        else:
            copied_arcs = copy.deepcopy(self.domains)
            for arc1 in copied_arcs:
                for arc2 in copied_arcs:
                    if arc1 == arc2:
                        continue
                    elif self.crossword.overlaps[arc1, arc2]:
                        queue.append((arc1, arc2))

        # Start checking the elements 
        for arc in queue:
            queue.remove(arc)
            if self.revise(arc[0], arc[1]):
                if self.domains[arc[0]] == 0:
                    return False
                for neighbor in self.crossword.neighbors(arc[0]):
                    if neighbor != arc[1]:
                        queue.append((arc[0], neighbor))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable1, word1 in assignment.items():
            # No conflicts between neighboring variables
            neighbors = self.crossword.neighbors(variable1)
            for neighbor in neighbors:
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[variable1, neighbor]
                    if assignment[variable1][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False

            # Every word has the correct length
            c = 0
            if variable1.length != len(word1):
                return False
            
            # Check for a word used twice
            for variable2, word2 in assignment.items():
                if word1 == word2:
                    c += 1
                    if c > 1:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        var_domain = self.domains[var]
        neighbors = self.crossword.neighbors(var)
        words_dict = {}
        words_list = []

        for word in var:
            # Dictionaire with neighbors' domains values, higher the value less the ruled out words will be
            for neighbor in neighbors:
                # Words already assigned
                if neighbor in assignment:
                    continue
                else:
                    overlap = self.crossword.overlaps[var, neighbor]
                    for neighbor_word in self.domains[neighbor]:
                        if word[overlap[0]] != neighbor_word[overlap[1]]:
                            words_dict[word] += 1
        # Sorting the dictionaire by values, function found on https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        words_dict = {k: v for k, v in sorted(words_dict.items(), key=lambda item: item[1])}
        words_list = words_dict.keys()
        return words_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        free_variables = {}
        same_length_variables = []
        for variable in self.domains.keys():
            if variable not in assignment:
                free_variables[variable] = len(self.domains[variable])
            else:
                continue   
        
        # Sorting the dictionaire by number of words in the domain
        {k: v for k, v in sorted(free_variables.items(), key=lambda item: item[1])}

        # Check if two or more variables have the same length and create an array with them
        for free_var in free_variables:
            if not same_length_variables:
                same_length_variables.append(free_var)
            else:
                if free_variables[same_length_variables[0]] == free_variables[free_var]:
                    same_length_variables.append(free_var)
                else:
                    continue
        
        # If only one element in the array return it
        if len(same_length_variables) <= 1:
            return same_length_variables[0]
        else:
            max_neighbors = 0
            # Check who has more neighbors
            for var in same_length_variables:
                if max_neighbors < len(self.crossword.neighbors(var)):
                    returning_var = var
                    max_neighbors = len(self.crossword.neighbors(var))
                else:
                    continue
        return var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.domains.keys()):
            return assignment
            
        var = self.select_unassigned_variable(assignment)
        for word in self.domains[var]:
            assignment_copy = assignment.copy()
            assignment_copy[var] = word
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                if result != None:
                    return result
                del assignment_copy[var]
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

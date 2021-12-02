import sys

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
        
        for key, vals in self.domains.items():
            to_be_removed = []
            for val in vals:
                if len(val) != key.length:
                    to_be_removed.append(val)
            for val in to_be_removed:        
                self.domains[key].remove(val)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False
        overlaps = self.crossword.overlaps[x,y]
        if overlaps == None:
            return revision_made
        else:
            xi = overlaps[0] # overlap at ith char of x
            yj = overlaps[1] # overlap at jth char of y
            x_vals = self.domains[x] # values of x
            y_vals = self.domains[y] # values of y

            to_remove_lst = [] # initialize a list to store x_vals to be removed
            for x_val in x_vals: # for each x_val in x_vals
                has_matches = False # initialize flag has_matches = False for each x_val
                for y_val in y_vals: # for each y_val in y_vals
                    if x_val[xi] == y_val[yj]: # if the x_val has a match with y_val
                        has_matches = True # set has_matches = True
                if has_matches == False: # if x_val does not match any y_val
                    to_remove_lst.append(x_val) # append it to a list to be removed later

            for x_val in to_remove_lst: # for each x_val to be removed
                    self.domains[x].remove(x_val) # remove the x_val
                    revision_made = True # set revision_made = True

            return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs != None: # If arcs is not None
            queue = arcs # Use the specified arc as queue
        else: # else, if arcs is None, enqueue all possible arcs
            vars = list(self.domains.keys()) # all the variables
            queue = [] # initialize the queue

            while len(vars) != 0: # while vars is not empty
                var1 = vars.pop(0) # pop the first var
                for var2 in vars: # for each remaining var
                    # if var2 in self.crossword.neighbors(var1): # if var2 is a neighbor of var1
                    pair = (var1, var2) # create a tuple of (var1, var2)
                    queue.append(pair) # enqueue the tuple

        while len(queue) != 0: # while queue is not empty
            pair = queue.pop(0) # dequeue a tuple
            x = pair[0] # assign the first var to x
            y = pair[1] # assign the second var to y
            if self.revise(x,y): # revise x and y. If there are modifications,
                if len(self.domains[x])  == 0: # check if the domain of x is empty
                    return False # return False if domain of x is empty, no solution can be found
                for z in self.crossword.neighbors(x): # else, for each neighbour of x
                    if z == y: # if neighbour is y
                        continue # ignore
                    else: # otherwise, enqueue (z,x)
                        pair = (z,x)
                        queue.append(pair)
        return True # return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        completed = True
        assigned_vars = assignment.keys() # all the assigned variables
        vars = self.domains.keys() # all the variables

        for var in vars: # for each var in vars
            # if there is an unassigned var or assigned var does not have a value
            if (var not in assigned_vars) | (assignment[var] == False):
                completed = False # assignment is incomplete            
        return completed

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Inconsistent if not all values are distinct
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False
        for var, val in assignment.items():
            # Check node consistenct (value length)
            if var.length != len(val): # if the value has the wrong length
                return False # assignment is not consistent
            # Check arc consistency (conflicts w neighbors)
            for neighbor_var in self.crossword.neighbors(var):
                if neighbor_var not in assignment.keys():
                    continue
                # Check for overlaps
                overlaps = self.crossword.overlaps[var, neighbor_var]
                val_ith_char = overlaps[0] # val ith char overlap
                neighbor_val_jth_char = overlaps[1] # neighbor val jth char overlap
                neighbor_val = assignment[neighbor_var]
                if val[val_ith_char] != neighbor_val[neighbor_val_jth_char]: # if the overlap char does not match
                    return False # return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        vals = self.domains[var] # values in the domain of var
        neighbor_vars = self.crossword.neighbors(var) # neighboring variables of var
        val_dict = {} # dictionary to store (val:n) pairs for sorting
        for val in vals: # for each value in domain of var
            val_dict[val] = 0 # initialize n = 0
            for neighbor_var in neighbor_vars:
                if neighbor_var in assignment: # if neighbor already has an assignment
                    continue # ignore neighbor
                else:
                    neighbor_vals = self.domains[neighbor_var] # the values in the domain of neighbor var
                    overlaps = self.crossword.overlaps[var, neighbor_var] # overlaps between var and neighbor_var
                    var_i = overlaps[0] # ith position of var that overlaps with neighbor_var
                    neighbor_var_j = overlaps[1]  # jth position of neighbor_var that overlaps with var
                    val_ith_char = val[var_i] # val's char at which there is an overlap
                    for neighbor_val in neighbor_vals: # for each neighbor value
                        neighbor_val_jth_char = neighbor_val[neighbor_var_j] # neighbor_val's char at which there is an overlap
                        if val_ith_char != neighbor_val_jth_char: # if the overlapping chars dont match
                            val_dict[val] += 1 # elimination needed, n += 1
        sorted_val_list = sorted(val_dict.items(), key=lambda x : x[1]) # [(val1:n1), (val2:n2),...]
        sorted_val_list2 = []
        for pair in sorted_val_list: # for each val:n pair that is sorted by n in sorted_val_list 
            sorted_val_list2.append(pair[0])  # we append val into sorted_val_list2, in ascending order of n

        return sorted_val_list2

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = {} # dict that stores all unassigned variables as keys and domain size as value
        vars = self.domains.keys() # all variables
        assigned_vars = set(assignment.keys())
        for var in vars: # for each var in vars
            if var not in assigned_vars: # if var is not assigned
                unassigned_vars[var] = len(self.domains[var]) # add the var to the unassigned_vars dict

        smallest_domain_size = 1000 # initialize constant
        for var, domain_size in unassigned_vars.items(): # for var and domain_size
            # Condition 1: var with the fewest number of remaining values in its domain
            if domain_size < smallest_domain_size: # if domain_size is smaller than current smallest_domain_size
                smallest_domain_size = domain_size # update smallest_domain_size
                var_w_smallest_domain_size = var # update var w smallest domain size
            # Condition 2: If domain_size == smallest_domain size, choose the var with largest degree
            elif domain_size == smallest_domain_size:
                var1 = var_w_smallest_domain_size
                var2 = var
                var1_degree = len(self.crossword.neighbors(var1)) # var1's degree
                var2_degree = len(self.crossword.neighbors(var2)) # var2's degree
                if var1_degree >= var2_degree: # if var1_degree >= var2_degree
                    var_w_smallest_domain_size = var1 # assign var1 to be var_w_smallest_domain_size
                else: # else, if var2_degree > var1_degree
                    var_w_smallest_domain_size = var2 # assign var2 to be var_w_smallest_domain_size
        return var_w_smallest_domain_size # return the variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if assignment is complete
        assignment_complete = True
        vars = self.domains.keys()
        assigned_vars = assignment.keys()
        for var in vars:
            if var not in assigned_vars: # if a variable is not in assignment
                assignment_complete = False # assignment is not complete
                break
        if assignment_complete == True: # if assignment is complete
            return assignment # return the assignment
        else: # else, if assignment is incomplete
            var = self.select_unassigned_variable(assignment) # get the best unassigned variable
            for val in self.order_domain_values(var, assignment): # for each val that var can take on in the best order
                assignment_copy = assignment.copy() # create a copy of assignment to test consistency
                assignment_copy[var] = val # assign val to var for testing
                if self.consistent(assignment_copy): # if assignment is consistent
                    assignment[var] = val # assign val to var
                    result = self.backtrack(assignment) # backtrack on the new assignment
                    if result != None:
                        return result
                assignment.pop(var, None)
            return None # if assignment is impossible, return None

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
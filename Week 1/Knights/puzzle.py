from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# character A is either a Knight or a Knave, but not both
char_A = And(Or(AKnight, AKnave), Not(And(AKnight, AKnave)))    

# character A is either a Knight or a Knave, but not both
char_B = And(Or(BKnight, BKnave), Not(And(BKnight, BKnave)))

# character C is either a Knight or a Knave, but not both
char_C = And(Or(CKnight, CKnave), Not(And(CKnight, CKnave)))

bg_knowledge = And( # Background Knowledge
    char_A,
    char_B,
    char_C, 
)

# Puzzle 0
# A says "I am both a knight and a knave."
what_A_said = And(AKnight, AKnave)
knowledge0 = And(
    # TODO
    bg_knowledge, # Background Knowledge
    # what_A_said is true if and only if A is AKnight
    # else, what_A_said is false and A cannot be AKnight, and is therefore AKnave
    Biconditional(what_A_said, AKnight)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
what_A_said = And(AKnave, BKnave)
knowledge1 = And(
    # TODO
    bg_knowledge, # Background Knowledge
    # what_A_said is true if and only if A is AKnight
    # else, what_A_said is false and A cannot be AKnight, and is therefore AKnave
    Biconditional(AKnight, what_A_said),
    Biconditional(what_A_said, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."

# A said that the 2 of them are together 
# either Knights or Knaves 
# but not both combinations at once
both_Knights = And(AKnight, BKnight) # both are Knights
both_Knaves = And(AKnave, BKnave) # both are Knaves
what_A_said = And(Or(both_Knights, both_Knaves), Not(And(both_Knights, both_Knaves)))

# B said that
# either A is AKnight and B is Kbnave
# or A is AKnave and B is AKnight
# but not both combinations at once
pair1 = And(AKnight, BKnave)
pair2 = And(AKnave, BKnight)
what_B_said = And(Or(pair1, pair2),Not(And(pair1, pair2)))

knowledge2 = And(
    # TODO
    bg_knowledge, # Background Knowledge

    # what_A_said is true if and only if A is AKnight
    # else, what_A_said is false and A cannot be AKnight, therefore A is AKnave
    Biconditional(what_A_said, AKnight),

    # what_B_said is true if and only if B is BKnight
    # else, what_B_said is false and B cannot be BKnight, therefore B is BKnave
    Biconditional(what_B_said, BKnight)    
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

# A said A is either AKnight or AKnave
what_A_said = Or(AKnight, AKnave)

### B'S FIRST STATEMENT ###
# Case 1 : B is BKnight, A is AKnave. i.e. A indeed said that B is a Knave and B made a truthful claim
# Case 2: B is BKnave, A is AKnight i.e. A made a truthful claim that B is BKnave (or no claim at all), but B lied
# Case 3: B is BKnight, A is AKnight. Impossible
# Case 4: B is BKnave, A is AKnave i.e. A lies that B is BKnight, and B lies that A said B is BKnave
what_B_first_said = And(
    Biconditional(BKnight, AKnave), # Case 1
    Implication(AKnight, BKnave), # Case 2
    Implication(AKnave, BKnave), # Case 4
)

### B's SECOND STATEMENT ###
# C is CKnave if and only if B is BKnight
what_B_second_said = Biconditional(CKnave, BKnight)

# A is AKnight if and only if C is CKnight
what_C_said = Biconditional(AKnight, CKnight)

knowledge3 = And(
    # TODO
    bg_knowledge, # Background Knowledge
    what_A_said,
    what_B_first_said,
    what_B_second_said,
    what_C_said
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

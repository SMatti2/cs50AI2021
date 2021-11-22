from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")
BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")
CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

generalKnowledge = And(
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),
    Or(BKnave, BKnight),
    Not(And(BKnave, BKnight)),
    Or(CKnave, CKnight),
    Not(And(CKnave, CKnight)),
)


# Puzzle 0
# A says "I am both a knight and a knave."
sentence0 = And(AKnave, AKnight)
knowledge0 = And(
    generalKnowledge,
    Implication(AKnight, sentence0),
    Implication(AKnave, Not(sentence0))
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
sentence1 = And(AKnave, BKnave)
knowledge1 = And(
    generalKnowledge,
    Implication(AKnight, sentence1),
    Implication(AKnave, Not(sentence1))
)


# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
a_sentence2 = Or(
    And(AKnight, BKnight),
    And(AKnave, BKnave)
)
b_sentence2 = Not(a_sentence2)

knowledge2 = And(
    generalKnowledge,
    Implication(AKnave, b_sentence2),
    Implication(AKnight, a_sentence2),
    Implication(BKnave, a_sentence2),
    Implication(BKnight, b_sentence2)
)


# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    generalKnowledge,
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Or(
        # "I am a knight."
        And(
            Implication(AKnight, AKnight),
            Implication(AKnave, Not(AKnight))
        ),
        
        # "I am a knave."
        And(
            Implication(AKnight, AKnave),
            Implication(AKnave, Not(AKnave))
        )
    ),
    # B says "A said 'I am a knave'."
    Implication(BKnight, And(
        Implication(AKnight, AKnave),
        Implication(AKnave, Not(AKnave))
    )),
    Implication(BKnave, And(
        Implication(AKnight, AKnight),
        Implication(AKnave, Not(AKnight))
    )),
    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),
    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
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
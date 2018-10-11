organs = [(0, 1), (2, 2), (8, 4)]


def move(currPos, newPos):
    op = currPos
    currPos = newPos
    print(currPos)
    return op

oldPosition = move((0, 0), (1, 1))

for i in range(len(organs)):
    print(i)
    print("Old:")
    print(oldPosition)
    print("")
    print("New:")
    oldPosition = move(organs[i], oldPosition)

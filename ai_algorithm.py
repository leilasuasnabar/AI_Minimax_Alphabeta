import sys
from copy import deepcopy

negInf = -sys.maxint - 1
posInf = sys.maxint

directions = ([-1, -1], [-1, 1],
              [1, -1],  [1, 1])

size = 8  # Number of rows in the board
row = ["1", "2", "3", "4", "5", "6", "7", "8"]
col = ["H", "G", "F", "E", "D", "C", "B", "A"]

class board(object):

    def __init__(self):
        self.player1 = ""
        self.player2 = ""
        self.board = []
        self.player1pass = False
        self.player2pass = False
        self.farutil = negInf

    def readFile(self, inputfile):
        board = []
        with open(inputfile, "r") as filename:
            player = filename.readline().strip("\n")
            if player == "Star":
                player1, player2 = "S", "C"

            else:
                player1, player2 = "C", "S"

            algorithm = filename.readline().strip("\n")
            depth = filename.readline().strip("\n")
            counter = 0
            for line in filename:
                currentline = line.strip("\n").split(",")
                # Obtain the initial board positions
                board.append(currentline)
                counter = counter + 1
                # Obtain the weights
                if counter == size + 1:
                    weights = map(int, currentline)
                    board.pop()
            filename.close()
            self.initializeBoard(player1, player2, board)
            return algorithm, depth, weights

    def initializeBoard(self,player1,player2,board, pass1=False, pass2=False):
        self.player1 = player1
        self.player2 = player2
        self.board = board
        self.player1pass = pass1
        self.player2pass = pass2

    def setBoard(self,newboard):
        self.board = newboard

    def setPass1(self, state):
        self.player1pass = state

    def setPass2(self, state):
        self.player2pass = state

    def equalBoards(self, board2):
        b1 = self.board
        b2 = board2.board

        for i in range(size):
            for j in range(size):
                if b1[i][j] != b2[i][j]:
                    return False
        return True

    def checkEndgame(self):
        flagstar = False
        flagcircle = False
        status = False
        for i in range(size):
            for j in range(size):
                if self.board[i][j][0] == "S":
                    flagstar = True
                elif self.board[i][j][0] == "C":
                    flagcircle = True

                # Check if there's at least one of each
                if flagcircle and flagstar:
                    return status
        status = True
        return status

    def outputBoard(self):
        boardout = self.board
        for i in range(size):
            print boardout[i]
        # None appears after this function is called


class Minimax(object):

    def __init__(self,b,depth,weights):
        self.board = b
        self.depth = int(depth)
        self.weights = weights
        self.player1 = b.player1
        self.player2 = b.player2
        self.nodes = 0
        self.farutil = []
        self.temputil = negInf
        self.nextchild = []

    def outputBoard(self, boardobject):
        board = boardobject.board
        print "\n"
        for i in range(size):
            print board[i]

    def updateBoard(self, moves, boardobject):
        updated = deepcopy(boardobject)
        board = boardobject.board
        newboard = deepcopy(boardobject.board)

        if moves:
            moves.pop(0)

            for [old,new] in moves:
                newboard[old[0]][old[1]] = "0"
                if new != "remove":
                    player = board[old[0]][old[1]][0]  # S or C
                    if player == "S":
                        current = newboard[new[0]][new[1]]  # Check new position in old board
                        if current != "0":
                            newboard[new[0]][new[1]] = "S" + str(int(current[1]) + 1)
                        else:
                            newboard[new[0]][new[1]] = "S1"

                    else:  # Player Circle
                        current = newboard[new[0]][new[1]]
                        if current != "0":
                            newboard[new[0]][new[1]] = "C" + str(int(current[1]) + 1)
                        else:
                            newboard[new[0]][new[1]] = "C1"

        else:
            return updated  # No new moves to update

        updated.setBoard(newboard)
        return updated

    def nextBoard(self):
        initialdepth = 0
        newboard = self.runMinimax(self.player1, initialdepth, self.board)

        myopicutil = self.getUtility(newboard, self.player1)
        return self.nodes, myopicutil, self.farutil

    def checkMove(self, move):
        if move[0] >= 0 and move[0] <= size - 1 and move[1] >= 0 and move[1] <= size - 1:
            return True
        else:
            return False

    def getUtility(self, boardobject,player):
        board = boardobject.board
        utilS = 0
        utilC = 0
        for i in range(size):
            for j in range(size):
                if board[i][j] is not "0":
                    if board[i][j][0] == "S":
                        utilS = utilS + int(board[i][j][1]) * self.weights[size - i - 1]
                    else:
                        utilC = utilC + int(board[i][j][1]) * self.weights[i]

        util = utilS - utilC if player is "S" else utilC - utilS
        return util


    def runMinimax(self, player, depth, board):
        # Keep track of number of nodes visited
        self.nodes = self.nodes + 1

        if depth == self.depth:
            self.farutil.append(self.temputil)
            return board  # We have reached the max depth

        if board.checkEndgame() or (board.player1pass and board.player2pass):
            self.farutil.append(self.temputil)
            return board

        if player == board.player1:
            util = negInf
            return self.maxStep(player, depth, board, util)
        else:
            util = posInf
            return self.minStep(player, depth, board, util)

    def maxStep(self, player, depth, board, maxutility):
        maxboard = deepcopy(board)
        newdepth = depth + 1

        for i in range(size):
            for j in range(size):
                depthboard = deepcopy(board)
                children = self.nextMove([i, j], depthboard, player)
                for child in children:
                    updatedboard = self.updateBoard(child, depthboard)
                    self.temputil = self.getUtility(updatedboard,self.player1)
                    newplayer = updatedboard.player2
                    updatedboard.setPass1(False)
                    updatedboard.setPass2(False)
                    newboard = self.runMinimax(newplayer, newdepth, updatedboard)
                    newutility = self.getUtility(newboard, updatedboard.player1)

                    if maxutility < newutility:
                        self.nextchild = child
                        maxutility = newutility
                        maxboard = updatedboard

        # Same boards, meaning it was a pass
        if board.equalBoards(maxboard):
            maxboard.setPass1(True)
            newplayer = maxboard.player2
            self.temputil = self.getUtility(maxboard, self.player1)
            newboard = self.runMinimax(newplayer, newdepth, maxboard)

        return maxboard

    def minStep(self, player, depth, board, minutility):
        minboard = deepcopy(board)
        newdepth = depth + 1

        for i in range(size):
            for j in range(size):
                depthboard = deepcopy(board)
                children = self.nextMove([i, j], depthboard, player)
                for child in children:
                    updatedboard = self.updateBoard(child, depthboard)
                    self.temputil = self.getUtility(updatedboard,self.player1)
                    newplayer = updatedboard.player1
                    updatedboard.setPass1(False)
                    updatedboard.setPass2(False)
                    newboard = self.runMinimax(newplayer, newdepth, updatedboard)
                    newutility = self.getUtility(newboard, updatedboard.player2)

                    if minutility > newutility:
                        minutility = newutility
                        minboard = updatedboard

        # Same boards, meaning it was a pass
        if board.equalBoards(minboard):
            minboard.setPass2(True)
            newplayer = minboard.player1
            self.temputil = self.getUtility(minboard, self.player1)
            newboard = self.runMinimax(newplayer, newdepth, minboard)

        return minboard

    def nextMove(self, pos, boardObject, player1):
        board = boardObject.board
        children = []
        if board[pos[0]][pos[1]][0] == player1:
            player2 = "C" if player1 is "S" else "S"
            direction = directions[0:2] if player1 is "S" else directions[2:4]

            # Check valid moves and if an enemy piece can be removed
            for d in direction:
                move = [pos[0] + d[0], pos[1] + d[1]]
                if self.checkMove(move):  # Valid Move
                    player = board[move[0]][move[1]][0]  # Player at new move:"S","C" or empty
                    if player == player1:
                        if (move[0] != 0 and player is "S") or (move[0] != 7 and player is "C"):  # Friendly piece in new move, do nothing
                            continue
                        else:  # Friendly piece in new move and at the last row
                            children.append([player1, [pos,move]])
                            continue

                    elif player == player2:  # Check if enemy can be eaten
                        if self.checkMove([move[0] + d[0], move[1] + d[1]]):
                            newmove = [move[0] + d[0], move[1] + d[1]]
                            pos1 = (pos, newmove)
                            pos2 = (move, "remove")
                            player = board[newmove[0]][newmove[1]][0]


                            if (player == player1 and newmove[0] == 0) or player == "0":  # friendly or empty
                                children.append([player1, pos1,pos2])
                                continue
                            elif player == player2:
                                continue

                    else:  # empty
                        children.append([player1, [pos,move]])
                        continue
        # No possible moves
        return children


class Alphabeta(object):

    def __init__(self,b,depth,weights):
        self.board = b
        self.depth = int(depth)
        self.weights = weights
        self.player1 = b.player1
        self.player2 = b.player2
        self.nodes = 0
        self.farutil = []
        self.temputil = negInf
        self.nextchild = []

    def outputBoard(self, boardobject):
        board = boardobject.board
        print "\n"
        for i in range(size):
            print board[i]

    def updateBoard(self, moves, boardobject):
        updated = deepcopy(boardobject)
        board = boardobject.board
        newboard = deepcopy(boardobject.board)

        if moves:
            moves.pop(0)

            for [old,new] in moves:
                newboard[old[0]][old[1]] = "0"
                if new != "remove":
                    player = board[old[0]][old[1]][0]  # S or C
                    if player == "S":
                        current = newboard[new[0]][new[1]]  # Check new position in old board
                        if current != "0":
                            newboard[new[0]][new[1]] = "S" + str(int(current[1]) + 1)
                        else:
                            newboard[new[0]][new[1]] = "S1"

                    else:  # Player Circle
                        current = newboard[new[0]][new[1]]
                        if current != "0":
                            newboard[new[0]][new[1]] = "C" + str(int(current[1]) + 1)
                        else:
                            newboard[new[0]][new[1]] = "C1"

        else:
            return updated  # No new moves to update

        updated.setBoard(newboard)
        return updated

    def nextBoard(self):
        initialdepth = 0
        newboard = self.runAlphabeta(self.player1, initialdepth, self.board, negInf, posInf)

        myopicutil = self.getUtility(newboard, self.player1)
        return self.nodes, myopicutil, self.farutil

    def checkMove(self, move):
        if move[0] >= 0 and move[0] <= size - 1 and move[1] >= 0 and move[1] <= size - 1:
            return True
        else:
            return False

    def getUtility(self, boardobject,player):
        board = boardobject.board
        utilS = 0
        utilC = 0
        for i in range(size):
            for j in range(size):
                if board[i][j] is not "0":
                    if board[i][j][0] == "S":
                        utilS = utilS + int(board[i][j][1]) * self.weights[size - i - 1]
                    else:
                        utilC = utilC + int(board[i][j][1]) * self.weights[i]

        util = utilS - utilC if player is "S" else utilC - utilS
        return util

    def runAlphabeta(self, player, depth, board, alpha, beta):

        # Keep track of number of nodes visited
        self.nodes = self.nodes + 1

        if depth == self.depth:
            self.farutil.append(self.temputil)
            return board  # We have reached the max depth

        if board.checkEndgame() or (board.player1pass and board.player2pass):
            self.farutil.append(self.temputil)
            return board

        if player == board.player1:
            util = negInf
            return self.maxStep(player, depth, board, util, alpha, beta)
        else:
            util = posInf
            return self.minStep(player, depth, board, util, alpha, beta)

    def maxStep(self, player, depth, board, maxutility, alpha, beta):
        maxboard = deepcopy(board)
        newdepth = depth + 1

        for i in range(size):
            for j in range(size):
                depthboard = deepcopy(board)
                children = self.nextMove([i, j], depthboard, player)
                for child in children:
                    updatedboard = self.updateBoard(child, depthboard)
                    self.temputil = self.getUtility(updatedboard,self.player1)
                    newplayer = updatedboard.player2
                    updatedboard.setPass1(False)
                    updatedboard.setPass2(False)
                    newboard = self.runAlphabeta(newplayer, newdepth, updatedboard, alpha, beta)
                    newutility = self.getUtility(newboard, updatedboard.player1)

                    if maxutility < newutility:
                        self.nextchild = child
                        maxutility = newutility
                        maxboard = updatedboard

                        if maxutility > alpha: alpha = maxutility
                        if maxutility >= beta: return maxboard

        # Same boards, meaning it was a pass
        if board.equalBoards(maxboard):
            maxboard.setPass1(True)
            newplayer = maxboard.player2
            self.temputil = self.getUtility(maxboard, self.player1)
            newboard = self.runAlphabeta(newplayer, newdepth, maxboard, alpha, beta)

        return maxboard

    def minStep(self, player, depth, board, minutility, alpha, beta):
        minboard = deepcopy(board)
        newdepth = depth + 1

        for i in range(size):
            for j in range(size):
                depthboard = deepcopy(board)
                children = self.nextMove([i, j], depthboard, player)
                for child in children:
                    updatedboard = self.updateBoard(child, depthboard)
                    self.temputil = self.getUtility(updatedboard, self.player1)
                    newplayer = updatedboard.player1
                    updatedboard.setPass1(False)
                    updatedboard.setPass2(False)
                    newboard = self.runAlphabeta(newplayer, newdepth, updatedboard, alpha, beta)
                    newutility = self.getUtility(newboard, updatedboard.player2)

                    if minutility > newutility:
                        minutility = newutility
                        minboard = updatedboard

                        # Compare alpha and beta, and update
                        if minutility < beta: beta = minutility
                        if minutility <= alpha: return minboard

        if board.equalBoards(minboard):
            minboard.setPass2(True)
            newplayer = minboard.player1
            self.temputil = self.getUtility(minboard, self.player1)
            newboard = self.runAlphabeta(newplayer, newdepth, minboard, alpha, beta)

        return minboard

    def nextMove(self, pos, boardObject, player1):
        board = boardObject.board
        children = []
        if board[pos[0]][pos[1]][0] == player1:
            player2 = "C" if player1 is "S" else "S"
            direction = directions[0:2] if player1 is "S" else directions[2:4]

            # Check valid moves and if an enemy piece can be removed
            for d in direction:
                move = [pos[0] + d[0], pos[1] + d[1]]
                if self.checkMove(move):  # Valid Move
                    player = board[move[0]][move[1]][0]  # Player at new move:"S","C" or empty
                    if player == player1:
                        if (move[0] != 0 and player is "S") or (move[0] != 7 and player is "C"):  # Friendly piece in new move, do nothing
                            continue
                        else:  # Friendly piece in new move and at the last row
                            children.append([player1, [pos,move]])
                            continue

                    elif player == player2:  # Check if enemy can be eaten
                        if self.checkMove([move[0] + d[0], move[1] + d[1]]):
                            newmove = [move[0] + d[0], move[1] + d[1]]
                            pos1 = (pos, newmove)
                            pos2 = (move, "remove")
                            player = board[newmove[0]][newmove[1]][0]


                            if (player == player1 and newmove[0] == 0) or player == "0":  # friendly or empty
                                children.append([player1, pos1,pos2])
                                continue
                            elif player == player2:
                                continue
                        #else:
                        #    continue

                    else:  # empty
                        children.append([player1, [pos,move]])
                        continue
                #else:
                #    continue

        # No possible moves
        return children


def writeOutput(nextmove,myopicutil,farutil,nodes):
    if nextmove:
        if len(nextmove) == 1:
            [nextmove] = nextmove
            oldmove = nextmove[0]
            newmove = nextmove[1]
        else:
            oldmove = nextmove[0][0]
            newmove = nextmove[0][1]

        move = col[oldmove[0]]+row[oldmove[1]]+"-"+col[newmove[0]]+row[newmove[1]]

    else:
        move = "pass"

    with open("output.txt", "w") as f:
        f.write(move+"\n")
        f.write(str(myopicutil)+"\n")
        f.write(str(max(farutil))+"\n")
        f.write(str(nodes))
        f.close()


if __name__ == '__main__':
    filename = "input.txt"
    b = board()
    algorithm, depth, weights = b.readFile(filename)

    if algorithm == "MINIMAX":
        turn = Minimax(b,depth,weights)
        nodes, myopicutil, farutil = turn.nextBoard()
        # Write output file
        writeOutput(turn.nextchild,myopicutil,farutil,nodes)

    elif algorithm == "ALPHABETA":
        turn = Alphabeta(b,depth,weights)
        nodes, myopicutil, farutil = turn.nextBoard()
        # Write output file
        writeOutput(turn.nextchild,myopicutil,farutil,nodes)

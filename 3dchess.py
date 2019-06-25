from vpython import vector
from vpython.vpython import *
import time
import copy

### Referenced site-packages eventHandlers.py for using event data
### Referenced vpython website for learning about the module's 3-d figures
### and coordinates
### Referenced vpython website for information on input and to look at
### examples of using the built-in parts of the module
### Took memoized from course website
"""

Project Proposal:
I want to write a 3-D chess game that allows two players to play a game of
chess rendered in 3-D for them in vpython.  The perspective will be
changeable, and the player's turn will be displayed textually near the board.
I would like to write a class for the board game itself and allow the pieces
to be defined as subclasses with individual rules for moves that can be made
and such override a superclass's movePiece function to use those rules.


Competitive Analysis:
    I saw some sample programs that have decent graphics, but the ones
    in vpython only had basic shapes for pieces, so I want to use
    the actual piece shapes, similar to those found in the panda3d
    sample program.
    One sample program used mouse-based movements, whereas another used
    text-based movements as input from the user.  I'd like to use mouse-
    based because it is more intuitive and better interface for the user.


Potential add-on features:
    AI
    Animation for capturing pieces
    "Gravity"
    Tempest Chess
    Spaces that cannot be off-limits for both players
    toggle which pieces are on the board (can have two teams of all pawns
        or two teams of half queens and half bishops for example)
    choose player colors
    .exe file for user
    add wraparound moves
    a single undo move for each player that can only be used during
        their turns click piece and view name (opponent's/your pieceName) and
        prior moves in that game
    confirm move screen
    timer
    animation to show a capture (or capture count
        to show which pieces are captured)
    warn player when in check
    toggle piece labels
    show moves available by highlighting destinations on board
    show the general legal moves for pieces
    
"""




   
class Chess(object):
    
    def __init__(self,rows=8,cols=8,gravity=[None,None]):
        self.scene = canvas()
        self.gravity=gravity
        #feature to be added: "gravity" allows a space on the board
        # to be specified to pull pieces toward that space a certain amount
        # every so many turns
        self.cellSize=1
        self.boardRows=rows
        self.boardCols=cols
        self.inCheck=[None,False,False]
        self.players=[None,1,2]
        self.playerTurn=1
        self.otherPlayer=2
        self.board=[[None]*cols for row in range(rows)]
        self.isGameOver=False
        self.playerFirstMove=[None,True,True]
        self.boardHeight=0.1
        self.firstSelected=False
        self.selection1=None
        self.selection2=None
        self.playerColors=[None,color.cyan,color.red]
        self.keyHeld=False
        # player 1 and player 2 at index 0 and 1 respectively
        # for playerColors and playerFirstMove
        self.scene.center=vector(3.5,6,3)
        self.scene.title="Chess"
        self.scene.width=800
        self.scene.height=800
        self.scene.bind("click",self.mouseClick)
        self.scene.bind("keydown",self.keyDown)
        self.scene.bind("keyup",self.keyUp)
        self.loadPieces()
        self.loadBoard()
        self.loadLegalMoves()
        self.printInstructions()


    def printInstructions(self,version=0):
        if (version==0):
            print("Welcome to Chess in 3-D.  To begin the game")
            print("player 1 may select a piece with the mouse")
            print("and make the first move.")
            print("The window is resizeable, and you may pan the")
            print("'camera' by holding the right mouse button and")
            print("moving the mouse.  You may zoom in and out by")
            print("holding both the right and left mouse buttons")
            print("and scrolling the mouse up and down.")
            print("")
            print("For more information, press H to see these instructions")
            print("again, press P to see information on the pieces and")
            print("piece moves, press N to see the piece count for each player,")
            print("press R to restart the game, and press Q to quit.")
        elif (version==1):
            print("The pieces are represented in the standard setup, but with")
            print("different shapes used in vpython.\n")
            print("Setup: inner rows are all pawns, outer rows: rook,knight,")
            print("bishop,queen,king,bishop,knight,rook")
            print("Pawns: Spheres (can move 2 spaces forward for the first move")
            print("of that pawn, one space forward for any subsequent moves,")
            print("and diagonally one space to capture an enemy piece.")
            print("If they reach the other side of the board, they are awarded")
            print("queen status and can move in the same way as a queen.\n")
            print("Rooks: Wide cylinders starting at the corners; can move")
            print("any horizontal or vertical distance as long as it is not")
            print("blocked.\n")
            print("Knights: can move a total of 2 rows and 1 column or vice-")
            print("versa in an L-shape and can jump over pieces.\n")
            print("Bishops: can move any diagonal distance as long as they are")
            print("not blocked.\n")
            print("Queens: can move any row,column, and diagonal distance as")
            print("long as they are not blocked.\n")
            print("Kings: can move any one space around them (row, column,")
            print("or diagonal as long as they are not blocked.")
        elif (version==2):
            print(self.pieceCounts())

    def pieceCounts(self):
        board=self.boardWithPieces
        count1=0
        count2=0
        for row in range(self.boardRows):
            for col in range(self.boardCols):
                if (board[row][col]>0):
                    count2+=1
                elif (board[row][col]<0 and board[row][col]!=None):
                    count1+=1
        return("Player 1 has %d pieces; Player 2 has %d pieces"%(count1,count2))



    def loadBoard(self):
        (pawn,rook,knight,bishop,queen,king)=(1,2,3,4,5,6)
        setupTop=[[rook,knight,bishop,king,queen,bishop,knight,rook],
                  [pawn]*self.boardCols]
        setupBot=[[pawn]*self.boardRows,
                  [rook,knight,bishop,king,queen,bishop,knight,rook]]
        (botRow,secondToBotRow)=(self.boardRows-1,self.boardRows-2)
        self.board[0]=copy.deepcopy(setupTop[0])
        self.board[1]=copy.deepcopy(setupTop[1])
        self.board[botRow]=copy.deepcopy(setupBot[1])
        self.board[secondToBotRow]=copy.deepcopy(setupBot[0])
        self.drawBoard()
        # first element of the list is the list of player1's pawns
        # second element of list is list of player2's pawns
        
    
    def drawBoard(self):
        # for box(pos=vector(p,q,r),options) increasing values of r come out toward
        # the user's view, q is in the vertical direction (up and down in
        # user's initial perspective), and p is in horizontal (left and
        # right in user's initial perspective
        board=copy.deepcopy(self.board)
        size=self.cellSize
        (rows,cols)=(self.boardRows,self.boardCols)
        self.drawLights()
        player=self.playerTurn
        for col in range(cols):
            for row in range(rows):
                self.drawPiece(row,col)
                if ((row+col)%2==0):
                    box(pos=vector(size*col,0,size*row),length=size,
                          height=self.boardHeight,width=size,
                          color=color.white)
                else:
                    box(pos=vector(size*col,0,size*row),length=size,
                          height=self.boardHeight,width=size,
                          color=color.blue)
        if (player==1):
            self.turnText1=text(text=("Player turn"), align="center",
                          depth=-0.2,color=color.cyan,axis=vector(1,0,0),
                          pos=vector(-1.5,6,0))
            self.turnText2=text(text=("Player turn"),align="center",
                          depth=-0.2,color=color.cyan,axis=vector(-1,0,0),
                          pos=vector(self.boardRows*self.cellSize+1.5,6,
                               self.boardRows*self.cellSize))
        else:
            self.turnText1=text(text=("Player turn"), align="center",
                      depth=-0.2,color=color.cyan,axis=vector(1,0,0),
                      pos=vector(-1.5,6,0))
            self.turnText2=text(text=("Player turn"),align="center",
                      depth=-0.2,color=color.cyan,axis=vector(-1,0,0),
                      pos=vector(self.boardRows*self.cellSize+1.5,6,
                           self.boardRows*self.cellSize))

    def drawLights(self):
        # referenced vpython.org for assistance in creating the lights
        # for aesthetic purposes in the game to create glowing effect
        light1=local_light(pos=vector(self.boardCols*self.cellSize/2-0.5,
                            self.boardHeight,
                        self.boardRows*self.cellSize/2-0.5),color=color.yellow)
                
    def drawPiece(self,row,col):
        (pawn,rook,knight,bishop,queen,king)=(0,1,2,3,4,5)
        playBoard=copy.deepcopy(self.boardWithPieces)
        piece=playBoard[row][col]
        objPieces=self.gameplayPieces
        size=self.cellSize
        rad=size/2
        if (self.playerFirstMove[1]==True):
            if not(row>1 and row<self.boardRows-2 and piece==None):
                self.drawForDrawPieces(piece,size,row,col,objPieces)
        else:
            self.drawForDrawPieces(piece,size,row,col,objPieces)
    
    def drawForDrawPieces(self,piece,size,row,col,objPieces):
        if (piece<0 and piece!=None):
            if (piece==-1):
                objPieces[row][col]=sphere(pos=vector(size*col,self.boardHeight+0.5,
                                    size*row),radius=0.5,color=color.cyan)
            elif (piece==-2):
                objPieces[row][col]=cylinder(pos=vector(size*col,self.boardHeight,
                                            size*row),axis=vector(0,0.8,0),
                                             radius=0.5,color=color.cyan)
            elif (piece==-3):
                objPieces[row][col]=ellipsoid(pos=vector(size*col,
                                            self.boardHeight+0.5,size*row),
                                        size=vector(1,1.2,0.3),color=color.cyan)
            elif (piece==-4):
                objPieces[row][col]=cylinder(pos=vector(size*col,self.boardHeight,
                                            size*row),axis=vector(0,1.2,0),
                                             radius=0.3,color=color.cyan)
            elif (piece==-5):
                objPieces[row][col]=ring(pos=vector(size*col,self.boardHeight+0.5,
                                        size*row),axis=vector(0,0,1),radius=0.3,
                                         thickness=0.2,color=color.cyan)
            elif (piece==-6):
                objPieces[row][col]=ellipsoid(pos=vector(size*col,
                                            self.boardHeight+0.5,size*row),
                                              size=vector(0.6,1.2,0.6),
                                              color=color.cyan)
        elif (piece>0 and piece!=None):
            if (piece==1):
                objPieces[row][col]=sphere(pos=vector(size*col,self.boardHeight+0.5,
                                    size*row),radius=0.5,color=color.red)
            elif (piece==2):
                objPieces[row][col]=cylinder(pos=vector(size*col,self.boardHeight,
                                            size*row),axis=vector(0,0.8,0),
                                             radius=0.5,color=color.red)
            elif (piece==3):
                objPieces[row][col]=ellipsoid(pos=vector(size*col,
                                            self.boardHeight+0.5,size*row),
                                        size=vector(1,1.2,0.3),color=color.red)
            elif (piece==4):
                objPieces[row][col]=cylinder(pos=vector(size*col,self.boardHeight,
                                            size*row),axis=vector(0,1.2,0),
                                             radius=0.3,color=color.red)
            elif (piece==5):
                objPieces[row][col]=ring(pos=vector(size*col,self.boardHeight+0.5,
                                        size*row),axis=vector(0,0,1),radius=0.3,
                                         thickness=0.2,color=color.red)
            elif (piece==6):
                objPieces[row][col]=ellipsoid(pos=vector(size*col,
                                            self.boardHeight+0.5,size*row),
                                        size=vector(0.6,1.2,0.6),color=color.red)
                
            

    def updateBoard(self,board,objBoard):
        player=self.playerTurn
        if (player==1):
            self.turnText1=text(text=("Player turn"), align="center",
                          depth=-0.2,color=color.cyan,axis=vector(1,0,0),
                          pos=vector(-1.5,6,0))
            self.turnText2=text(text=("Player turn"),align="center",
                          depth=-0.2,color=color.cyan,axis=vector(-1,0,0),
                          pos=vector(self.boardRows*self.cellSize+1.5,6,
                               self.boardRows*self.cellSize))
        if (player==2):
            self.turnText1=text(text=("Player turn"), align="center",
                          depth=-0.2,color=color.red,axis=vector(1,0,0),
                          pos=vector(-1.5,6,0))
            self.turnText2=text(text=("Player turn"),align="center",
                          depth=-0.2,color=color.red,axis=vector(-1,0,0),
                          pos=vector(self.boardRows*self.cellSize+1.5,6,
                               self.boardRows*self.cellSize))
        for row in range(self.boardRows):
            for col in range(self.boardCols):
                if (board[row][col]==None and objBoard[row][col]!=0):
                    objBoard[row][col].visible=False
                elif (board[row][col]!=None and (objBoard[row][col]==0 or
                                        objBoard[row][col].visible==False)):
                    self.drawPiece(row,col)
                elif (objBoard[row][col]!=0 and
                      self.playerColors[self.playerTurn]!=\
                      objBoard[row][col].color):
                    objBoard[row][col].visible=False
                    self.drawPiece(row,col)
        self.checkForChecks(board)

    def escapeCheckMate(self,board):
        pass
        """playerInCheck=self.inCheck.index(True)
        moves=self.pieceMoves
        kingPos=self.kingPos[playerInCheck]
        self.selection1=(kingPos[1],None,kingPos[0])
        sign=-1 if (playerInCheck==1) else 1
        for row in range(self.boardRows):
            for col in range(self.boardCols):
                if (board[row][col]!=None and board[row][col]*sign>0):
                    for piece in range(6):
                        for move in moves[piece]:
                            for drow in range(self.boardRows-row):
                                for dcol in range(self.boardCols-col):
                                    if (self.canMoveInDirection(
                                        (col,row),drow,dcol)):
                                        self.selection1=None
                                        return True
        self.selection1=None
        return False"""




    
    def checkForChecks(self,board):
        for row in range(self.boardRows):
            for col in range(self.boardCols):
                piece=board[row][col]
                check=self.canReachKing(board,piece,row,col)
                if ((piece!= None) and check):
                    playerInCheck=self.players[1] if piece>0 else\
                                                    self.players[2]
                    self.inCheck[playerInCheck] = True
                    print("Player",playerInCheck," in check")
                    if (not self.escapeCheckMate(board)):
                        return True
                    else:
                        print("CHECKMATE!")
                        self.gameOver()
                    return True
        self.inCheck=[None,False,False]    
        return False


    
    def canReachKing(self,board,piece,row,col,):
        # keep track of king pos. and see if piece is diagonal from
        # or in same row/col as king with drow/dcol
        if (piece == None):
            return
        (pawn,rook,knight,bishop,queen,king)=(1,2,3,4,5,6)
        if (piece>0):
            otherPlayer=1
            # pawns move in positive drow direction
            kingPos=self.kingPos[otherPlayer]
            (drow,dcol)=(kingPos[0]-row,kingPos[1]-col)
            otherKing=king*-1
            if (piece==1):
                print("pawn",row,col)
                if (abs(drow)==abs(dcol)==1 and drow<0):
                    return True
                return False
            elif (piece==2):
                print("rook",row,col)
                return self.canRookMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==3):
                print("knight",row,col)
                return self.canKnightMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==4):
                print("bishop",row,col)
                return self.canBishopMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==5):
                print("kingPos",kingPos)
                print("queen",row,col)
                return self.canQueenMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==6):
                print("king",row,col)
                return self.canKingMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
        elif (piece<0):
            otherPlayer=2
            kingPos=self.kingPos[otherPlayer]
            (drow,dcol)=(kingPos[0]-row,kingPos[1]-col)
            otherKing=king
            if (piece==-1):
                print("pawn",row,col)
                if (abs(drow)==abs(dcol)==1 and drow<0):
                    return True
                return False
            elif (piece==-2):
                print("rook",row,col)
                return self.canRookMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==-3):
                print("knight",row,col)
                return self.canKnightMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==-4):
                print("bishop",row,col)
                return self.canBishopMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==-5):
                print("kingPos",kingPos)
                print("queen",row,col)
                return self.canQueenMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
            elif (piece==-6):
                print("king",row,col)
                return self.canKingMove(kingPos,drow,dcol,otherKing,
                                                            [col,0,row])
        return [False,otherKing,None]
                
                

    def loadPieces(self):
        rows=self.boardRows
        (pawn,rook,knight,bishop,queen,king)=(1,2,3,4,5,6)
        # negatives for opposite side's pieces
        self.kingPos=[None,[7,4],[0,4]]
        self.boardWithPieces=[[2,3,4,5,6,4,3,2],
                              [1,1,1,1,1,1,1,1],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [None,None,None,None,None,None,None,None],
                              [-1,-1,-1,-1,-1,-1,-1,-1],
                              [-2,-3,-4,-5,-6,-4,-3,-2]]
        (rows,cols)=(self.boardRows,self.boardCols)
        self.gameplayPieces=[[0]*cols for row in range(rows)]
        self.checkGameplayPieces=[[str(0)]*cols for row in range(rows)]
        #2*2 rows for each player's pieces
        

    def loadLegalMoves(self):
        (pawn,rook,knight,bishop,queen,king)=(1,2,3,4,5,6)
        # legal moves are in self.pieceMoves in order of above indices
        # self.pieceMoves=[[pawn],[rook],[knight],[bishop],[queen],[king]]
        # moves in form: (change in row, change in col)
        self.pieceMoves=[[(1,0),(2,0),(1,1)],
                         # only (2,0) for first move per player,(1,1) captures
                         [(1,0),(0,1)],
                         # any multuple move of these (no diagonal moves
                         # for rooks)
                         [(1,2),(2,1)],
                         # abs(drow)=2*abs(dcol) and vice versa for knight
                         [(1,1)],
                         # abs(drow)=abs(dcol) for bishop
                         [(1,0),(0,1),(1,1)],
                         # any multiple of these for queen
                         [(1,0),(0,1),(1,1)]]
                         # only single space moves for king
        # if a pawn makes it to the other side of the board, it becomes a queen
        self.pawnsAreQueens=[[False]*self.boardCols,
                             [False]*self.boardCols]

    def keyDown(self,event):
        if self.keyHeld==True:
            return
        else:
            if (event.key=="q"):
                pass 
                # quit
            elif (event.key=="n"):
                self.printInstructions(2)
                # show piece count for players
            elif (event.key=="p"):
                self.printInstructions(1)
                # show piece labels
            elif (event.key=="h"):
                self.printInstructions(0)

    def keyUp(self,event):
        self.keyHeld=False

    def mouseClick(self,event):
        piece=self.scene.mouse.pick
        if (self.isGameOver==False): 
            if ((piece==None) and (self.firstSelected==False)):
                print("You must select a piece on the board")
                return False
            elif((piece==None) and (self.firstSelected==True)):
                print("You must select a space on the board")
                return False
            self.selection(piece,event)
        else:
            self.scene.exit


    def selection(self,piece,event):
        player=self.playerTurn
        side=1 if player==2 else -1
        board=self.boardWithPieces
        self.checkForChecks(board)
        colour=color.cyan if (player==1) else color.red
        if (not self.firstSelected) or (self.selection1==None):
            if (piece==None):
                return
            elif (piece.color==self.playerColors[player]):
                self.firstSelected=True
                self.selection1=piece
                piece.color=color.magenta
            elif (piece.color==self.playerColors[self.otherPlayer]):
                print("You cannot move your opponent's pieces")
                self.selection1=None
                self.firstSelected=False
            else:
                print("You must select one of your pieces to move")
                self.selection1=None
                self.firstSelected=False
        else:
            (drow,dcol)=self.getMove(piece.pos,event)
            self.selection2=piece
            if self.isLegalMove(piece.pos,event,drow,dcol):
                self.selection1.color=colour
                self.movePiece(piece,event,drow,dcol)
                self.firstSelected=False
                self.updateBoard(board,self.gameplayPieces)
            else:
                self.selection1.color=colour
            self.selection1=None
            self.selection2=None
                    
                
            
            

    def getMove(self,piecePos,event):
        sel1=self.selection1.pos
        sel2=piecePos
        (drow,dcol)=(sel2.z-sel1.z,sel2.x-sel1.x)
        return (int(drow),int(dcol))


    
    def movePiece(self,piece,event,drow,dcol):
        player=self.playerTurn
        playBoard=self.boardWithPieces # with number representation
        objPieces=self.gameplayPieces # with piece objects
        piecePos=self.selection1.pos
        willCapture=False
        sign=-1 if player==1 else 1
        (queen,king)=(5,6)
        willQueen=False
        (row0,col0,row1,col1)=(int(round(piecePos.z)),int(round(piecePos.x)),
            int(round(piecePos.z+drow)),int(round(piecePos.x+dcol)))
        if (abs(playBoard[row0][col0])==1 and (row1==0 or row1==7)):
            willQueen=True
        if ((objPieces[row1][col1]!=0) and
            objPieces[row1][col1].color!=self.playerColors[self.playerTurn]):
            willCapture=True
        if (abs(playBoard[row0][col0])==king):
            kingPos=[row1,col1]
        if (willQueen):
            playBoard[row1][col1]=5*sign
        else:
            (playBoard[row0][col0],playBoard[row1][col1])=\
            (playBoard[row1][col1],playBoard[row0][col0])
        self.checkForChecks(playBoard)
        if (self.inCheck[player]):
            (playBoard[row0][col0],playBoard[row1][col1])=\
            (playBoard[row1][col1],playBoard[row0][col0])
            print("That move is not valid due to you being in check.")
        else:       
            if (willCapture):
                objPieces[row0][col0].visible=False
            if (playBoard[row0][col0]!=None and abs(playBoard[row0][col0])\
                                                                    ==king):
                self.kingPos[player]=kingPos
            playBoard[row0][col0]=None
            (self.turnText1.visible,self.turnText2.visible)=(False,False)
            (self.turnText1,self.turnText2)=(None,None)
            self.updateBoard(playBoard,objPieces)
            self.playerTurnSwap()
            if (self.playerFirstMove[player]==True):
                self.playerFirstMove[player]=False
                self.pieceMoves[0]=[(1,0),(1,1)]

        
    
    def isLegalMove(self,piece,event,drow,dcol):
        (pawn,rook,knight,bishop,queen,king)=(1,2,3,4,5,6)
        pieceToMove=self.selection1
        spaceToMoveTo=piece
        moves=self.pieceMoves
        direction=1 if self.playerTurn==2 else -1
        move=(drow,dcol)
        player=self.playerTurn
        if (self.inCheck[player]==True):
            for move in moves[5]:
                for chessPiece in moves:
                    for move in chessPiece:
                        if (self.canMoveInDirection(spaceToMoveTo,
                                                        drow,dcol)):
                            return True
        else:          
            if (drow==dcol==0):
                print("You must select space to move your piece to")
            else:
                for chessPiece in moves:
                    for move in chessPiece:
                        if (self.canMoveInDirection(spaceToMoveTo,drow,dcol)):
                            return True
        print("That move is not legal")
        return False
    
     
        
                    
            
    def canMoveInDirection(self,nextSpace,drow,dcol):
        player=self.playerTurn
        direction=1 if self.playerTurn==2 else -1
        board = self.boardWithPieces
        piece0=(int(round(self.selection1.pos.x)),None,\
                int(round(self.selection1.pos.z)))
        movingPiece=board[int(round(piece0[2]))][int(round(piece0[0]))]
        destination=board[int(round(nextSpace.z))][int(round(nextSpace.x))]
        if (movingPiece!=None):
            if (abs(movingPiece)%10==1):
                print("pawn moving")
                if (abs(movingPiece)==1):
                    return self.canPawnMove(nextSpace,drow,dcol,destination,piece0)
                # queened pawns represented by (multiples of 10) + 1
                elif (abs(movingPiece)>1):
                    return self.canQueenMove(nextSpace,drow,dcol,destination,piece0)
            elif (abs(movingPiece)==2):
                print("rook moving")
                return self.canRookMove(nextSpace,drow,dcol,destination,piece0)
            elif (abs(movingPiece)==3):
                print("knight moving")
                return self.canKnightMove(nextSpace,drow,dcol,destination,piece0)
            elif (abs(movingPiece)==4):
                print("bishop moving")
                return self.canBishopMove(nextSpace,drow,dcol,destination,piece0)
            elif (abs(movingPiece)==5):
                print("queen moving")
                return self.canQueenMove(nextSpace,drow,dcol,destination,piece0)
            elif (abs(movingPiece)==6):
                print("king moving")
                return self.canKingMove(nextSpace,drow,dcol,destination,piece0)
        return False

    
    def canPawnMove(self,nextSpace,drow,dcol,destination,piece0):
        player=self.playerTurn
        direction=1 if self.playerTurn==2 else -1
        board=self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        if (self.playerFirstMove[player]==True):
            if ((destination==None) and (abs(drow)==2 or abs(drow)==1) and
                abs(dcol)==0):
                return True
        elif (self.playerFirstMove[player]==False):
            if (destination!=None and board[row0][col0]!=None and
                (destination*board[row0][col0]<0) and abs(drow)==abs(dcol)==1):
                if (direction==1):
                    if (drow>0):
                        return True
                elif (direction==-1):
                    if (drow<0):
                        return True
            elif (destination==None and dcol==0):
                if (direction==1):
                    if (drow==1 or drow==2):
                        return True
                elif (direction==-1):
                    if (drow==-1 or drow==-2):
                        return True
        return False

    
    def canRookMove(self,nextSpace,drow,dcol,destination,piece0):
        player=self.playerTurn
        board=self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        if (((abs(drow)>0 and dcol==0) or (abs(dcol)>0 and drow==0)) and
            (destination==None or destination*board[row0][col0]<0)):
            if (abs(drow)>0):
                direction=1 if drow>0 else -1
                for step in range(1,abs(drow)):
                    if (board[row0+step*direction][col0]!=None):
                        return False
                return True
            elif (abs(dcol)>0):
                direction=1 if dcol>0 else -1
                for step in range(1,abs(dcol)):
                    if (board[row0][col0+step*direction]!=None):
                        return False
                return True
        return False

    
    def canKnightMove(self,nextSpace,drow,dcol,destination,piece0):
        player = self.playerTurn
        board = self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        if (destination==None or destination*board[row0][col0]<0):
            if ((abs(drow)==2 and abs(dcol)==1) or
                (abs(dcol)==2 and abs(drow)==1)):
                return True

    
    def canBishopMove(self,nextSpace,drow,dcol,destination,piece0):
        player=self.playerTurn
        board=self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        sign=1 if player==2 else -1
        if ((abs(drow)>0) and (abs(drow)==abs(dcol)) and
            (destination==None or destination*board[row0][col0]<0)):
            rowDir=1 if drow>0 else -1
            colDir=1 if dcol>0 else -1
            minrangeDrow=2 if (abs(drow)==1) else drow
            for step in range(1,abs(minrangeDrow)):
                if (step!=abs(drow) and
                    board[row0+step*rowDir][col0+step*colDir]!=None):
                    return False
            return True
        return False

    
    def canQueenMove(self,nextSpace,drow,dcol,destination,piece0):
        board=self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        if self.canBishopMove(nextSpace,drow,dcol,destination,piece0):
            return True
        elif self.canRookMove(nextSpace,drow,dcol,destination,piece0):
            return True
        return False

    
    def canKingMove(self,nextSpace,drow,dcol,destination,piece0):
        player=self.playerTurn
        board=self.boardWithPieces
        (row0,col0)=(piece0[2],piece0[0])
        if (((abs(drow)==1 and dcol==0) or (abs(dcol)==1 and drow==0) or
            (abs(drow)==abs(dcol)==1)) and
            (destination==None or destination*board[row0][col0]<0)):
            return True
        return False

    
        
        

    
    def gameOver(self):
        # prints game over message
        if (self.isGameOver==True):
            print("Game Over!  Click anywhere in the game screen to exit.")


    def playerTurnSwap(self):
        # swaps players' turns and resets position of camera to player's side
        (self.playerTurn,self.otherPlayer)=(self.otherPlayer,self.playerTurn)
        player=self.playerTurn
        direction=1 if (player==2) else -1
        self.scene.forward=vector(0,-0.3,direction)




thisGame=Chess()

       

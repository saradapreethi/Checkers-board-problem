"""
Q2: Customised Checker Board Problem
@author: Sarada Chandrasekar

Checkers simulator
Simulator uses grid to represent the board with a piece dictionary
piece database:
    sym name        side    velocity
    v   valid       --      --
    i   invalid     --      --
    r   red normal  r       1
 R==v   red king    r       1, -1
    b   black norm  b       -1
 B==v   black king  b       1, -1
"""   
import pygame    
# Board color definition
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREY = (170, 170, 170)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
# Grid dimensions in the given board   
DIM = 10 
# Grid size visualisation 
GRID = 60
# Piece dictionary representation:
# Valid space, invalid space, red norm, black norm, red king, black king
PieceDict = {
    'v' : {'name': 'valid', 'sym': '#', 'vel':[0]},
    'i' : {'name': 'invalid', 'sym': '.', 'vel':[0]},
    'r' : {'name': 'Red Norm', 'sym': 'r', 'side': 'r', 'vel':[1]},
    'R' : {'name': 'Red King', 'sym': 'R', 'side': 'r', 'vel':[1, -1]},
    'b' : {'name': 'Blk Norm', 'sym': 'b', 'side': 'b', 'vel':[-1]},
    'B' : {'name': 'Blk King', 'sym': 'B', 'side': 'b', 'vel':[1, -1]}
    }

# Checker Board class
class Board:
    # Board initialisation function
    def __init__(self, dim):
        # Set the dimension
        self.dim = dim
        self.redscore = 0
        self.blackscore = 0
        # Intialise board array
        self.board = []
        # Store the valid and invalid space in given 10x10 dimension
        for j in range(self.dim):
            row = []
            for k in range(self.dim):
                space = 'v' if (j+k)%2==0 else 'i'
                row.append(space)
            self.board.append(row)
        # Call the reset function to fill the spaces with red/black norms
        self.reset()

    # Board reset function
    def reset(self):
        self.select = []
        # Set the first play turn for Red Norm
        self.turn = 'r'
        self.preventDeselect = False
        # Fill the first 4 rows with Red Norm in alternate grids
        for y in range(4):
            for x in range(DIM):
                if (x+y)%2 == 0:
                    self.board[y][x] = 'r'
        # Fill the last 4 rows with Blk Norm in alternate grids
        for y in range(DIM-4, DIM):
            for x in range(DIM):
                if (x+y)%2 == 0:
                    self.board[y][x] = 'b'
    
     # Mouse is in grid coordinates
    def processMouse(self, mx, my):
        #nothing is selected, find a piece to select
        if len(self.select) == 0:
            if self.board[my][mx].lower() == self.turn:
                self.select = [mx, my]
        #There is a selected piece, deselect?
        elif mx == self.select[0] and my == self.select[1] and not self.preventDeselect:
            self.select = []
        #There is a selected piece: trying to move/ capture
        else:
            # Check if the capture attempt is valid or not
            if self.attemptingCapture(mx, my):
                # Initiate and execute capture
                if self.tryCapture(mx, my):
                    # Convert norm to king if the selected position is in last/first row of the board
                    self.tryMakeKing()
                    # Check if the lastest norm position in select array is not valid for selection
                    if not self.canSelectCapture():
                        # Switch the turn to opponent player
                        self.switchTurn()
            # Check if the move attempt is valid or not
            elif self.attemptingMove(mx, my) and not self.preventDeselect:
                # Try and execute move 
                if self.tryMove(mx, my):
                    # Convert norm to king if the selected position is in last/first row of the board
                    self.tryMakeKing()
                    # Switch the turn to opponent player
                    self.switchTurn()

    # Check if is valid to select the position stored in select array
    def canSelectCapture(self):
        sx = self.select[0]
        sy = self.select[1]
        # Extract the velocity information of latest norm
        yOffs = PieceDict[self.board[sy][sx]]['vel']
        # Set the x offs
        xOffs = [-2, 2]
        # Return true if any one position is a vaild capture, else false
        for y in yOffs:
            for x in xOffs:
                if self.validCapture(sx+x, sy+2*y):
                    return True
        return False

    # Validate the capture attempt : 
    # Check if the capture X Y coordinates are within the dimesion limit
    # Check if the jump wrt X and Y coordinate is equal to 2
    # Check if the jump position is valid
    # If yes, return True, else False
    def attemptingCapture(self, mx, my):
        if mx >= 0 and mx < self.dim and my >= 0 and my < self.dim \
                and abs(mx - self.select[0]) == 2 \
                and abs(my - self.select[1]) == 2 \
                and self.board[my][mx] == 'v':
            return True
        return False
    
    # Initiate capture:
    # Check if it is a valid capture
    # If yes, execute capture and return True , else return False
    def tryCapture(self, mx, my):
        # Check if the capture is valid
        if self.validCapture(mx, my):
            self.executeCapture(mx, my)
            return True
        return False

    # Check if the capture is valid
    def validCapture(self, mx, my):
        # Check if the coordinates are within dimension limit, 
        # check if the jump wrt X Y coordinates is equal to 2
        # check if the jump position is valid
        # If any one condition fails, return false 
        if mx < 0 or mx >= self.dim or my < 0 or my >= self.dim \
                or abs(mx - self.select[0]) != 2 \
                or abs(my - self.select[1]) != 2 \
                or self.board[my][mx] != 'v':
            return False
        # Store selected X and Y position in variables
        sx = self.select[0]
        sy = self.select[1]
        # Extract the velocity information of select piece from dictionary
        vel = PieceDict[self.board[sy][sx]]['vel']
        # Check for valid velocity : r = 1; b = -1; R = 1,-1;B=1,-1 
        tgtOffy = 0
        for yoff in vel:
            if (sy + 2*yoff) == my:
                tgtOffy = yoff
        # If the target Y position is still 0, then return false
        if tgtOffy == 0: 
            return False
        # If the selected X position is greater than original position, set target X as 1, else -1
        tgtOffx = 1 if mx > sx else -1
        # Check if the target selected to capture is opponent norm, if yes return true, else false
        tgtSide = self.board[sy+tgtOffy][sx+tgtOffx].lower()
        if (tgtSide == 'r' and self.board[sy][sx].lower() == 'b') \
                or (tgtSide == 'b' and self.board[sy][sx].lower() == 'r'):
            return True
        return False
    
    # Execute the valid capture
    def executeCapture(self, mx, my):
        # Update sx and sy position from select array
        sx = self.select[0]
        sy = self.select[1]
        # Update target position based on the norm move
        tgtOffx = 1 if mx > sx else -1
        tgtOffy = 1 if my > sy else -1
        # Update the new position in board with the selected norm
        self.board[my][mx] = self.board[sy][sx]
        # Convert the old position in board to 'valid'
        self.board[sy][sx] = 'v'
        # Convert the capture position to 'valid'
        self.board[sy+tgtOffy][sx+tgtOffx] = 'v'
        if mx > sx:
            self.blackscore+=1 
        else:
             self.redscore+=1
        # Update the select array with new norm position
        self.select = [mx, my]
        # Set the prevent deselect flag
        self.preventDeselect = True

    # Validate the move attempt : 
    # Check if the move X Y coordinates are within the dimesion limit
    # Check if the jump wrt X and Y coordinate is equal to 1
    # Check if the jump position is valid
    # If yes, return True, else False
    def attemptingMove(self, mx, my):
        if mx >= 0 and mx < self.dim and my >= 0 and my < self.dim \
                and abs(mx - self.select[0]) == 1 \
                and abs(my - self.select[1]) == 1 \
                and self.board[my][mx] == 'v':
            return True
        return False

    # Try to execute the move
    def tryMove(self, mx, my):
        # Check if the selected new position is a valid grid
        if abs(mx - self.select[0]) == 1 and abs(my - self.select[1]) == 1 and self.board[my][mx] == 'v':
            sx = self.select[0]
            sy = self.select[1]
            # Extract the velocity information of the selected norm
            vel = PieceDict[self.board[sy][sx]]['vel']
            # Reset the validmove flag
            validMove = False
            # If the velocity + norm position is equal to new position : Set the validmove flag 
            for yoff in vel:
                if (sy + yoff) == my:
                    validMove = True
            # If the validmove flag is true : Execute move and return true, else return false
            if validMove:
                # Update the new position with selected norm
                self.board[my][mx] = self.board[self.select[1]][self.select[0]]
                # Convert the old position to 'valid'
                self.board[self.select[1]][self.select[0]] = 'v'
                # Update the select array with new position
                self.select = [mx, my]
                return True
        return False

    # Check if the selected board position is first / last row. 
    # If yes, make the selected Norm to King
    def tryMakeKing(self):
        sx = self.select[0]
        sy = self.select[1]
        pt = self.board[sy][sx]
        if pt == 'r' or pt == 'b':
            # Set ky as 0 if the norm is 'b' else set it as DIM-1
            ky = 0 if pt.lower() == 'b' else DIM-1
            # Check if the selected position is equal to ky
            # If yes convert the norm to king
            if sy == ky:
                self.board[sy][sx] = 'v'
                if pt.lower() == 'r':
                    self.redscore+=5
                else:
                    self.blackscore+=5

    # Switch the valid turn to opponent player
    def switchTurn(self):
        # Clear the select array
        self.select = []
        # Change the turn to opposite player
        self.turn = 'r' if self.turn == 'b' else 'b'
        # Set the prevent Deselect flag to false
        self.preventDeselect = False

    # Function to draw the checkers board in the given screen
    def draw(self, scrn):
        # Set the screen Y coordinate to 0
        sy = 0
        # Define the length of rectangle grids and radius of norms
        half = GRID//2
        rad = (half*8)//10
        # Draw the 10x10 checkers board along with 20 Red norms and 20 Black norms
        for y in range(self.dim):
            # Set the screen X coordinate to 0
            sx = 0
            for x in range(self.dim):
                # Check if the board position is valid. If yes draw a grey rectangle
                if self.board[y][x] == 'v':
                    pygame.draw.rect(scrn, GREY, [sx, sy, GRID, GRID])
                # Check if the board position is invalid. If yes draw a white rectangle
                elif self.board[y][x] == 'i':
                    pygame.draw.rect(scrn, WHITE, [sx, sy, GRID, GRID])
                # Check if the board position should contain red Norm. If yes draw a grey rect and red filled circle
                elif self.board[y][x] == 'r':
                    pygame.draw.rect(scrn, GREY, [sx, sy, GRID, GRID])
                    pygame.draw.circle(scrn, RED, [sx+half,sy+half], rad)
                # Check if the board position should contain black Norm. If yes draw a grey rect and black filled circle
                elif self.board[y][x] == 'b':
                    pygame.draw.rect(scrn, GREY, [sx, sy, GRID, GRID])
                    pygame.draw.circle(scrn, BLACK, [sx+half,sy+half], rad)
                # Else display the yellow rectangle around the slected grid.
                else:
                    pygame.draw.rect(scrn, YELLOW, [sx, sy, GRID, GRID])
                # Increment screen X coordinate by grid size
                sx += GRID
            # Increment screen Y coordinate by grid size
            sy += GRID
        # Display a yellow rectangle around the selected grid
        if len(self.select) > 0:
            sx = self.select[0]*GRID
            sy = self.select[1]*GRID
            pygame.draw.rect(scrn, YELLOW, [sx, sy, GRID, GRID], 5)


def main():
    # Initialise pygame
    pygame.init()   
    # Set the width and height of the screen [width, height]
    size = (DIM*GRID, DIM*GRID)
    screen = pygame.display.set_mode(size)
    # Set caption for the game 
    pygame.display.set_caption("Checkers Board Game")
    # Loop until the user clicks the close button.
    done = False 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock() 
    # Intialise the board with "10x10" as dimension
    board = Board(DIM)   
    # Main Program Loop
    while not done:
        # Main event loop. Get the pygame event 
        for event in pygame.event.get():
            # Event:User clicks close button. Set done = true
            if event.type == pygame.QUIT:
                done = True
            # Event:User clicks the mouse at postion in the board grid
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Extract the mouse click position
                mpos = pygame.mouse.get_pos()
                mx = mpos[0]
                # Process the move based on the click position
                board.processMouse(mpos[0]//GRID, mpos[1]//GRID)
            # Event: User press a keyboard key
            elif event.type == pygame.KEYDOWN:
                # Close the game if user press the escape key
                if event.key == pygame.K_ESCAPE:
                    done = True
                # Print the board game in terminal if user press the space bar key
                elif event.key == pygame.K_SPACE:
                    print (board)
                # Print unkown key in the terminal if user press a key other than escape/spacebar
                else:
                    print ("Unknown key " + str(event.key))
        # Fill the screen with WHITE color
        screen.fill(WHITE)  
        # Draw the grids, red norm and black norms in the board
        board.draw(screen)
        # Display the drawn board
        pygame.display.flip()
        # Limit to 60 frames per second
        clock.tick(60)    
    # Close the window and quit.
    pygame.quit()
    print("Red Score:", board.redscore)
    print("Black Score:",board.blackscore)
    if(board.redscore >board.blackscore):
        print("Red is the WINNER :)")
    else:
        print("Black is the WINNER :)")

if __name__ == '__main__':
    main()
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import ImageGrab
import time
import win32gui
import wx
import tkinter as tk


# have all the defined thingy bobs up here.
def templatematching(fullimg, templateimg, threshold, indicator, thelist):
    """
    Method for returning a list of coordinates of where the template has matched image.
    :param fullimg: the full image.
    :param templateimg: the template used for the matching.
    :param threshold: the threshold at which it considers a match.
    :param indicator: the value to be returned so type of match can be distinguished in list.
    :param thelist: the list where values will be appended.
    :return: a list of lists with len 3 with format (x,y,indicator)
    """
    # run the template matching function
    result = cv2.matchTemplate(fullimg, templateimg, cv2.TM_CCOEFF_NORMED)
    # remove all below a certain threshold
    locations = np.where(result >= threshold)

    for point in zip(*locations[::-1]):
        # append to list all pairs of coordinates.
        thelist.append([point[0], point[1], indicator])

    return thelist


def coordinatesort(thelist, width=6):
    """
    Sorts the coordinates based on the number of objects wide, sorting by height first and then in width batches
    :param thelist: the list of values passed in to be returned.
    :param width: the width of set of coordinates this defaults 6.
    :return: sorted list.
    """
    # sort all into order by height.
    thelist.sort(key=lambda x: x[1])
    # best on the width we will be able to resort left to right for each row
    # loop through incrementing by the width and sort for each section selected.
    for x in range(0, len(thelist), width):
        thelist[x:x+width] = sorted(thelist[x:x+width])
    return thelist


def puzzlebuilder(thelist, width, height, borders=0, bordervalue=["X", 0, 0]):
    """

    :param thelist: the list of values to be passed in
    :param width: the width of the puzzle
    :param height: the height of the puzzle
    :param borders: the size of the border if required.
    :param bordervalue: value for the border if specified
    :return: returns the fully built puzzle.
    """
    # create a copy of the list so we can pop off the values
    listcopy = thelist[:]
    result = [[0 for a in range(width + (2 * borders))] for b in range(height + (2 * borders))]
    # seperate method require if we want borders around the edge.
    if borders > 0:
        # create empty list with the borders.
        for x in range(len(result)):
            for y in range(len(result[x])):
                if y < borders or y >= width + borders or x < borders or x >= height + borders:
                    # if in the border region set it to the border value
                    result[x][y] = bordervalue
                else:
                    # set to the next value in the array.
                    result[x][y] = [listcopy[0][2], x, y, listcopy[0][0], listcopy[0][1]]
                    listcopy.pop(0)
    else:
        # if no border just iterate through and set to next value in list.
        for x in range(height):
            for y in range(width):
                result[x][y] = [listcopy[0][2], x, y, listcopy[0][0], listcopy[0][1]]
                listcopy.pop(0)
    return result


def setchecker(thelist):
    """
    Returns with all values in the list are the same, counts number of first element and checks if eq to len
    :param thelist: list of elements
    :return: true or false
    """
    return thelist.count(thelist[0]) == len(thelist)

def bilgeareachecker(thelist, x, y, location):
    """
    The takes the puzzle and for specific location returns the value of that move.
    :param thelist: the puzzle for checking the sets
    :param x: x location
    :param y: y location
    :param location: where in the nested list the value to check is
    :return: returns a score for that move.
    """
    total = 0
    temptotal = 0
    score = []
    # check it isn't a puffer fish or jelly fish as these should be popped immediately
    if thelist[x][y][location] in {'P', 'J'}:
        finalscore = 500
    else:
        # check the horizontal left 3
        if setchecker([thelist[x][y-2][location], thelist[x][y-1][location], thelist[x][y+1][location]]):
            total += 3
            score.append(3)

        # check the horizontal right 3
        if setchecker([thelist[x][y][location], thelist[x][y+2][location], thelist[x][y+3][location]]):
            total += 3
            score.append(3)

        # check the left vertical top 3
        if setchecker([thelist[x-2][y][location], thelist[x-1][y][location], thelist[x][y+1][location]]):
            temptotal = 3
        # check the left vertical middle 3
        if setchecker([thelist[x-1][y][location], thelist[x][y+1][location], thelist[x+1][y][location]]):
            temptotal = 3
        # check the left bottom 3
        if setchecker([thelist[x][y+1][location], thelist[x+1][y][location], thelist[x+2][y][location]]):
            temptotal = 3
        # check the left vertical top 4
        if setchecker([thelist[x-2][y][location], thelist[x-1][y][location], thelist[x][y+1][location]
                      , thelist[x+1][y][location]]):
            temptotal = 4
        # check the left bottom 4
        if setchecker([thelist[x-1][y][location], thelist[x][y+1][location], thelist[x+1][y][location]
                      , thelist[x+2][y][location]]):
            temptotal = 4
        # check the left vertical top 5
        if setchecker([thelist[x-2][y][location], thelist[x-1][y][location], thelist[x][y+1][location]
                      , thelist[x+1][y][location], thelist[x+2][y][location]]):
            temptotal = 5

        # add left downs to total
        total += temptotal
        if temptotal > 0:
            score.append(temptotal)

        # reset the temptotal for right downs
        temptotal = 0
        # check the right vertical top 3
        if setchecker([thelist[x-2][y+1][location], thelist[x-1][y+1][location], thelist[x][y][location]]):
            temptotal = 3
        # check the right vertical middle 3
        if setchecker([thelist[x-1][y+1][location], thelist[x][y][location], thelist[x+1][y+1][location]]):
            temptotal = 3
        # check the right bottom 3
        if setchecker([thelist[x][y][location], thelist[x+1][y+1][location], thelist[x+2][y+1][location]]):
            temptotal = 3
        # check the right vertical top 4
        if setchecker([thelist[x-2][y+1][location], thelist[x-1][y+1][location], thelist[x][y][location]
                      , thelist[x+1][y+1][location]]):
            temptotal = 4
        # check the right bottom 4
        if setchecker([thelist[x-1][y+1][location], thelist[x][y][location], thelist[x+1][y+1][location]
                      , thelist[x+2][y+1][location]]):
            temptotal = 4
        # check the right vertical top 5
        if setchecker([thelist[x-2][y+1][location], thelist[x-1][y+1][location], thelist[x][y][location]
                      , thelist[x+1][y+1][location], thelist[x+2][y+1][location]]):
            temptotal = 5

        # add right downs to total
        if temptotal > 0:
            score.append(temptotal)

        # (x1 + x2 ... xn) * n
        finalscore = sum(score)*len(score)
    return finalscore

def doubledepthchecker(thelist, x, y, location, bordervalue='X'):
    """
    Function to check at the current level and after a swap to calculate the score.
    :param thelist: this is the sorted puzzle
    :param x: the x coord
    :param y: the y coord
    :param location: the location in the list where the value to check is
    :param bordervalue: what the border value is
    :return: return the score and the one or two moves required to get it.
    """
    bestscore = 0
    bestmove = [x, y]
    innerbestmove = [0, 0]
    if bilgeareachecker(thelist, x, y, location) == 0:
        # if no score is returned then go one deeper.
        # swap the elements in the list.
        thelist[x][y], thelist[x][y+1] = thelist[x][y+1], thelist[x][y]
        # now loop through the square of influence
        for s in range(-2, 3):
            for t in range(-2, 3):
                # check it's in the impacted area.
                if (t != -2 and t != 2) or s == 0:
                    # check it's not a border piece and check if score is higher.
                    if bilgeareachecker(thelist, x+s, y+t, 0) > bestscore and thelist[x+s][y+t][0] != bordervalue:
                       bestscore = bilgeareachecker(thelist, x+s, y+t, 0)
                       innerbestmove = [x+s, y+t]
        thelist[x][y+1], thelist[x][y] = thelist[x][y], thelist[x][y+1]
        bestmove = [bestmove, innerbestmove]

        # return score and the move set, note that the score is divide by two because you do two moves.
        return [bestscore/2, bestmove]
    else:
        # if it does not equal 0 then it will pop so can't go a deeper level.
        bestscore = bilgeareachecker(thelist, x, y, location)
        return[bestscore, bestmove]

def ndepthchecker(thelist, x, y, location, bordervalue='X', n=0, bestscore=0, bestmovelist=[]):
    """
    Function to check at the current level and after a swap to calculate the score.
    :param thelist: this is the sorted puzzle
    :param x: the x coord
    :param y: the y coord
    :param location: the location in the list where the value to check is
    :param bordervalue: what the border value is
    :param n: depth of the search.
    :return: return the score and the one or two moves required to get it.
    """
    tempscore = 0
    tempbestmove = []

    if n == 0:
        # if the piece is not equal to the border value get the score.
        if thelist[x][y][location] != bordervalue:
            tempscore = bilgeareachecker(thelist, x, y, location)
            # if the score of the current area is higher set this as the best move.
            if tempscore > bestscore:
                bestscore = tempscore
                bestmovelist = [[x, y]]
        # return the score and best move from the area.
        return [bestscore, bestmovelist]
    if n >= 1:
        # if n >= 1 then that has depth so we need to call the area checker for all pieces in the matrix.
        # first check if it pops.
        if bilgeareachecker(thelist, x, y, location) == 0:
            # doesn't pop
            # swap the elements
            thelist[x][y], thelist[x][y + 1] = thelist[x][y + 1], thelist[x][y]
            # loop through the affected area.
            for s in range(-2, 3):
                for t in range(-3, 4):
                    # the if statement includes the sticking out bits and removes border pieces
                    if ((t > -2 and t < 2) or s == 0) and thelist[x+s][y+t][0] != bordervalue:
                        # get the score
                        tempscore = ndepthchecker(thelist, x+s, y+t, location, bordervalue, n-1)
                        # compare the best score divided by the number of moves.
                        # if it is a higher score per move OR it is the same score per move but less moves.
                        if bestscore != 999:
                            if (tempscore[0] / max(len(tempscore[1]), 1) > bestscore / max(len(bestmovelist), 1)) \
                                    or (tempscore[0] / max(len(tempscore[1]), 1) == bestscore / max(len(bestmovelist), 1)
                                        and (max(len(tempscore[1]), 1)) < (max(len(bestmovelist), 1))):
                                # assign the results to temporary varables.
                                bestscore = tempscore[0]
                                tempbestmove = [x, y]
                                bestmovelist = tempscore[1]
            # add move to the move list.
            bestmovelist.insert(0, tempbestmove)
            # swap the list back.
            thelist[x][y], thelist[x][y + 1] = thelist[x][y + 1], thelist[x][y]
            n -= 1
            return [bestscore, bestmovelist]
        else:
            # does pop
            n -= 1
            # where it pops we should return the score and the appended list.
            bestmovelist = [[x, y]]
            return [bilgeareachecker(thelist, x, y, location), bestmovelist]



def getbestmove(thelist, border=0):
    """
    function for finding the best move
    :param thelist: the puzzle to be past in
    :param border: value of the puzzle borders.
    :return: returns the score and the location [score, [x,y]]
    """
    bestmove = [0, 0]
    bestscore = 0
    for a in range(border, len(thelist) - border):
        for b in range(border, len(thelist[a]) - (border + 1)):
            if bilgeareachecker(thelist, a, b, 0) > bestscore:
                bestscore = bilgeareachecker(thelist, a, b, 0)
                bestmove = [a, b]
    return [bestscore, bestmove]


def getbestmove2(thelist, border=0):
    """
    function for finding the best move
    :param thelist: the puzzle to be past in
    :param border: value of the puzzle borders.
    :return: returns the score and the location [score, [x,y]]
    """
    bestmove = [0, 0]
    bestscore = 0
    # loop through all locations.
    for a in range(border, len(thelist) - border):
        for b in range(border, len(thelist[a]) - (border + 1)):
            # if best move for that location is great value set it to new best move.
            if doubledepthchecker(thelist, a, b, 0)[0] > bestscore:
                bestscore = doubledepthchecker(thelist, a, b, 0)[0]
                bestmove = [a, b]
    return [bestscore, bestmove, thelist[bestmove[0]][bestmove[1]]]

def getbestmoven(thelist, location, border=0, n=0):
    """
    function for finding the best move for a depth of n.
    :param thelist: the puzzle to be past in
    :param border: value of the puzzle borders.
    :return: returns the score and the location [score, [x,y]]
    """
    bestmove = [0, 0]
    bestscore = 0
    bestlist = []
    movelist = []
    # loop through all locations.
    for a in range(border, len(thelist) - border):
        for b in range(border, len(thelist[a]) - (border + 1)):
            # if best move for that location is great value set it to new best move.
            # call the ndepth checker for each location
            currentmove = ndepthchecker(thelist, a, b, location, 'X', n)
            # if the move raises a higher score per turn or if it the same score per turn but less moves.
            if (currentmove[0] / max(len(currentmove[1]), 1) > bestscore / max(len(bestlist), 1)) \
                    or ((currentmove[0] / max(len(currentmove[1]), 1)) == (bestscore / max(len(bestlist), 1))
                        and (max(len(currentmove[1]), 1)) < (max(len(bestlist), 1))):
                # set best score to new bestscore.
                bestscore = currentmove[0]
                # set best move as the move chain.
                bestlist = currentmove[1]
    movelist = bestlist
    return [bestscore,  movelist]


def movehighlighter(image, movelist, locations):
    """
    Highlights the points of an image where the move is.
    Order of moves goes: red, green, blue, purple.
    :param image: image to highlight the moves on.
    :param movelist: list of moves to be made in order.
    :param locations: list of the coordinates where to highlight.
    :return: return the image with the moves highlighted.
    """
    # set the different move colours.
    colours = [[0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 0, 255]]
    # loop through for each move and highlight it.
    for m in range(0, len(movelist)):
        # take the locations and highlight in the square the location.
        image = cv2.rectangle(image, (locations[movelist[m][0]][movelist[m][1]][3]
                                      , locations[movelist[m][0]][movelist[m][1]][4])
                              , (locations[movelist[m][0]][movelist[m][1]][3] + 10
                                 , locations[movelist[m][0]][movelist[m][1]][4] + 10)
                              , (colours[m][0], colours[m][1], colours[m][2]), 5)
    return image

def screengrabber():
    """
    Function for taking a screenshot of puzzle pirates window, worth noting that if you change char the name changes
    :return: return the frame as an image, also return the frame in colour for the final display.
    """
    # get the box dimensions.
    box = win32gui.GetWindowRect(win32gui.FindWindow(None, "Puzzle Pirates - Squidgum on the Emerald ocean"))
    # screenshot the area where program is located
    grabbedimage = ImageGrab.grab(box)
    # convert into a workable array.
    preframe = np.array(grabbedimage)
    # convert to grey.
    # this all needs cleaning upm it's hacky and horrible.
    frame = cv2.cvtColor(preframe, cv2.COLOR_BGR2GRAY)
    colourframe = cv2.cvtColor(preframe, cv2.COLOR_RGB2BGR)
    cv2.imwrite("workaround.png", frame)
    cv2.imwrite("colour.png", colourframe)
    finalframe = cv2.imread("workaround.png")
    return [finalframe, colourframe]


def runsolver():
    # load in templates.
    template1 = cv2.imread("images/token_templates3/template1.png", 0)
    template2 = cv2.imread("images/token_templates3/template2.png", 0)
    template3 = cv2.imread("images/token_templates3/template3.png", 0)
    template4 = cv2.imread("images/token_templates3/template4.png", 0)
    template5 = cv2.imread("images/token_templates3/template5.png", 0)
    template6 = cv2.imread("images/token_templates3/template6.png", 0)
    template7 = cv2.imread("images/token_templates3/jelly.png", 0)
    template8 = cv2.imread("images/token_templates3/crab.png", 0)
    template9 = cv2.imread("images/token_templates3/fish.png", 0)

    puzzle = screengrabber()
    resultsx = []

    ff2 = cv2.cvtColor(puzzle[0], cv2.COLOR_BGR2GRAY)
    templatematching(ff2, template1, 0.9, 'A', resultsx)
    templatematching(ff2, template2, 0.9, 'B', resultsx)
    templatematching(ff2, template3, 0.9, 'C', resultsx)
    templatematching(ff2, template4, 0.9, 'D', resultsx)
    templatematching(ff2, template5, 0.9, 'E', resultsx)
    templatematching(ff2, template6, 0.9, 'F', resultsx)
    # the below are untested matches.
    templatematching(ff2, template7, 0.9, 'J', resultsx)
    templatematching(ff2, template8, 0.9, 'K', resultsx)
    templatematching(ff2, template9, 0.9, 'P', resultsx)

    coordinatesort(resultsx, 6)
    resultsx = puzzlebuilder(resultsx, 6, 12, 5)
    move = getbestmoven(resultsx, 0, 5, 3)

    nextmoves = movehighlighter(puzzle[1], move[1], resultsx)

    cv2.imshow("Your Move", nextmoves)


def token_type(number):
    """
    Method returning what type of token it is best on the value of the first colour channel.
    :param number: value of first colour channel.
    :return: returns the token.
    """
    for sublist in token_values:
        if sublist[1] == number:
            return sublist[0]
            break
    return 'Z'


def puzzle_builder():
    for h in range(0, 12):
        for w in range(0, 6):
            # if it is a puffer or jelly break the loop and return the move.
            if token_type(puzzle_picture[h*45 + 90, w*45 + 100][0]) in ('P', 'J'):
                return [h+3, w+3]
                break
            # set the values in the numpy array to have the token value, note we have to add 3 because we have a buffer
            puzzle[h+3, w+3] = token_type(puzzle_picture[h*45 + 90, w*45 + 100][0])
    return 0


def score_calculator(h, w):
    if puzzle[h, w] == 'X' or puzzle[h, w] == 'K' or puzzle[h, w+1] == 'K':
        # if it is a border piece then cannot be swapped.
        # or the swapping pieces are crabs then it cannot be swapped.
        return 0
    else:
        # calculate the score.
        return 1



def main():
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    button = tk.Button(frame,
                       text="QUIT",
                       fg="red",
                       command=quit)
    button.pack(side=tk.LEFT)
    slogan = tk.Button(frame,
                       text="Hello",
                       command=runsolver)
    slogan.pack(side=tk.LEFT)

    root.mainloop()


#if __name__ == '__main__':
#     main()




# let's just create the object with the list, if it's global it's created outside.
# use strings or ints for comparison has no discernable difference


# these are the global variables okay.
token_values = [['A', 157], ['A', 160], ['B', 205], ['B', 179], ['C', 210], ['C', 181], ['D', 202], ['D', 178]
                , ['E', 196], ['E', 175], ['F', 227], ['F', 188], ['G', 244], ['G', 195], ['K', 97], ['P', 151]
                , ['P', 99], ['J', 223], ['J', 186]]

puzzle = np.full((18, 12), 'X', dtype='object')
puzzle_picture = cv2.imread("jelly under.png")


print(puzzle)

puzzle_builder()
print()
print(puzzle)
print(score_calculator(3, 3))

# now we need a method for calcing the score.

#def calculate_score


#gettingvalues = cv2.imread("puffaabove.png")
#gettingvalues2 = cv2.imread("pufferabove2.png")
#print(gettingvalues[85, 100]) # [134 123  53] dark green circley wave thing.
#print(gettingvalues[85, 145]) # [190 216 162] light green circley wavey thing.
#print(gettingvalues[130, 145]) # [212 87 25]

#print(gettingvalues[580, 235]) # crab [ 97 100  83] -> need to check another location...
#print(gettingvalues[535, 145])
#print(gettingvalues[580, 235])
#print(gettingvalues2[535, 145])

#print(gettingvalues[400, 190])
#(gettingvalues2[335, 190])

# puffa values
# above

#gettingvalues = cv2.imread("jellyover1.png")
#gettingvalues2 = cv2.imread("jelly over2.png")
#gettingvalues3 = cv2.imread("jelly under.png")

#print(gettingvalues[135, 145])
#print(gettingvalues[135, 280])
#print(gettingvalues[360, 235])

#print(gettingvalues[495, 235])
#print(gettingvalues[495, 280])

#print(gettingvalues[360, 280])
#print(gettingvalues2[315, 280])
#print(gettingvalues3[540, 280])


"""gettingvalues = cv2.imread("puffaabove.png")
gettingvalues2 = cv2.imread("pufferabove2.png")
print(gettingvalues[410, 190])
print(gettingvalues2[365, 190])
# below
gettingvalues3 = cv2.imread("puffabelow.png")
gettingvalues4 = cv2.imread("puffabelow2.png")
print(gettingvalues3[540, 100])
print(gettingvalues4[540, 190])

# crab values
# above (not possible)
# below
gettingvalues5 = cv2.imread("crabby.png")
gettingvalues6 = cv2.imread("crabby2.png")
print(gettingvalues5[585, 235])
print(gettingvalues6[540, 145])

gettingvalues7 = cv2.imread("jelleh.png")
gettingvalues7 = cv2.rectangle(gettingvalues7, (145, 405), (150, 410), (0, 0, 255), -1)
#cv2.imshow("window", gettingvalues7)
#cv2.waitKey(0)


print()
gettingvaluesx = cv2.imread("crabby.png")
print(gettingvaluesx[540, 145])
print(gettingvaluesx[495, 325])

print(type(gettingvaluesx[495, 325]))
print(gettingvaluesx[495, 325][0])



# now it's time to deprecate the template matching because it's just not required ey.



# now create a matcher function
def whattoken():
    print("A")


#tokenvalues = [['A', ['157 156  24']], ['A', ['160 107  10']], ['B', ['205 215 137']], ['B', ['179 131  55']]
#               , ['C', ['210 137  59']], ['C', ['181 100  24']], ['D', ['202 136  25']], ['D', ['178  99  10']]
#               , ['E', ['196 140   4']], []]


#print("snip bitch")
#crab = cv2.imread("bilgeframezcrab.png")
#crop_img = crab[503:513, 200:210]
#cv2.imwrite("crab.png", crop_img)
#print("snip snip")


# okay let's try and draw on the screen haha.
# so first gonna create a window.
# this can be for our game.
#class gameGUI(wx.frame):
#    def __init__(self):
#        wx.Frame.__init__(self, None, title='BilgeBot9000')
#        self.Show(True)

# okay we have something the highlights the screen
#class moveHighlighter(wx.Frame):
#    def __init__(self):
#        style = ( wx.CLIP_CHILDREN | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR |
#                  wx.NO_BORDER | wx.FRAME_SHAPED  )
#        wx.Frame.__init__(self, None, title='Fancy', style = style)
#        self.SetTransparent( 220 )
#        self.Show(True)


#app = wx.App()
#f = moveHighlighter()
#app.MainLoop()"""
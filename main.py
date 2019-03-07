from __future__ import print_function, division

import time
import rotation
import utilities
import visual

from math import pi
from copy import deepcopy

from referenceToAlgorithm import Algorithm

Algo = Algorithm()


FRONT_SIDE = "front"
BACK_SIDE = "back"
TOP_SIDE = "up"
BOTTOM_SIDE = "down"
LEFT_SIDE = "left"
RIGHT_SIDE = "right"

CORNER_BOX = 'corner_box'
CENTER_BOX = 'center_box'
SIDE_BOX = 'side_box'

CORNER_PIECES = [(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2), (2, 0, 0),
                 (2, 0, 2), (2, 2, 0), (2, 2, 2)]
SIDE_PIECES = [(0, 0, 1), (0, 2, 1), (2, 0, 1), (2, 2, 1),
               (1, 0, 0), (1, 0, 2), (1, 2, 0), (1, 2, 2),
               (0, 1, 0), (0, 1, 2), (2, 1, 0), (2, 1, 2)]
CENTER_PIECES = [(1, 0, 1), (1, 2, 1), (2, 1, 1), (0, 1, 1), (1, 1, 0),
                 (1, 1, 2)]


class ColorItem(object):
    """WHITE,RED,BLUE,etc are all instances of this class."""

    def __init__(self, name="red"):
        self.name = name
        self.color = visual.color.red
        self.opposite = None

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def getOpposite(self):
        return self.opposite

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def setOpposite(self, opposite):
        self.opposite = opposite
        opposite.opposite = self


RED = ColorItem("red")
BLUE = ColorItem("blue")
GREEN = ColorItem("green")
ORANGE = ColorItem("orange")
WHITE = ColorItem("white")
YELLOW = ColorItem("yellow")

RED.setColor(visual.color.red)
GREEN.setColor(visual.color.green)
YELLOW.setColor(visual.color.yellow)
BLUE.setColor(visual.color.blue)
WHITE.setColor(visual.color.white)
ORANGE.setColor(visual.color.orange)

RED.setOpposite(ORANGE)
BLUE.setOpposite(GREEN)
WHITE.setOpposite(YELLOW)

F2L = 50
OLL = 51
CROSS = 52
PLL = 53


def getIdFromPos(pos):
    return pos[0] + pos[1] * 3 + pos[2] * 9


def getPosFromId(myId):
    """opposite of getIDFromPos(pos)."""
    pos = [0, 0, 0]
    while myId > 8:
        pos[2] += 1
        myId -= 9
    while myId > 2:
        pos[1] += 1
        myId -= 3
    pos[0] = myId
    return pos[0], pos[1], pos[2]


class FaceObject(object):
    def __init__(self):
        self.front = GREEN
        self.back = GREEN.getOpposite()
        self.left = ORANGE
        self.right = ORANGE.getOpposite()
        self.top = WHITE
        self.bottom = WHITE.getOpposite()

    def all(self):
        return deepcopy([self.front, self.back, self.left,
                         self.right, self.top, self.bottom])

    def getSideForColor(self, color):
        if str(color) == str(self.front):
            return "front"
        elif str(color) == str(self.back):
            return "back"
        elif str(color) == str(self.right):
            return "right"
        elif str(color) == str(self.left):
            return "left"
        elif str(color) == str(self.top):
            return "top"
        elif str(color) == str(self.bottom):
            return "bottom"
        else:
            return Exception("Exception thrown by FaceColor.getSideForColor")

    def update(self, values):
        self.front = values["front"]
        self.top = values["top"]
        self.left = values["left"]
        self.back = self.front.getOpposite()
        self.bottom = self.top.getOpposite()
        self.right = self.left.getOpposite()

    def getSidesExcludingColor(self, color):
        allColors = ["front", "back", "left", "right", "top", "bottom"]
        colorName = self.getSideForColor(color)
        allColors.remove(colorName)
        return allColors


FaceColor = FaceObject()


def decodeColorFromText(color):
    """Converts text and returns its instance."""
    color = color.lower()
    if color.startswith(str(RED)):
        return RED
    elif color.startswith(str(GREEN)):
        return GREEN
    elif color.startswith(str(YELLOW)):
        return YELLOW
    elif color.startswith(str(WHITE)):
        return WHITE
    elif color.startswith(str(BLUE)):
        return BLUE
    elif color.startswith(str(ORANGE)):
        return ORANGE
    return None


class Box(object):

    def __init__(self, boxType):
        self.pos = (0, 0, 0)
        self.boxType = boxType

        self.xzBox = None
        self.xyBox = None
        self.yzBox = None

    def getType(self):
        return self.boxType

    def setPos(self, x, y, z):
        self.pos = (x, y, z)

    def getPos(self):
        return self.pos

    def getSides(self):
        ret = []
        if self.xz:
            ret.append(self.xz)
        if self.yz:
            ret.append(self.yz)
        if self.xy:
            ret.append(self.xy)
        return ret

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "%s at " % (self.boxType) + str(self.pos) + " , xz= " + str(
            self.xz) + " , yz= " + str(self.yz) + " , xy= " + str(
            self.xy) + "\n"

    def hasColor(self, *colors):
        ret = True
        for color in colors:
            colorFound = False
            if self.xy is not None and self.xy.color == color.color:
                colorFound = True
            if self.xz is not None and self.xz.color == color.color:
                colorFound = True
            if self.yz is not None and self.yz.color == color.color:
                colorFound = True
            if not colorFound:
                ret = False
                break
        # print ret
        return ret


class CornerBox(Box):
    """A corner box. has 3 faces."""

    def __init__(self):
        Box.__init__(self, CORNER_BOX)

        self.xy = FaceColor.bottom  # the colors of the box
        self.yz = FaceColor.left
        self.xz = FaceColor.front

        self.pos = (0, 0, 0)


class SideBox(Box):
    """A side box. has 2 faces."""

    def __init__(self):
        Box.__init__(self, SIDE_BOX)

        self.xy = None
        self.yz = FaceColor.left
        self.xz = FaceColor.front

        self.pos = (0, 0, 1)


class CenterBox(Box):
    """A center box. has 1 face."""

    def __init__(self):
        Box.__init__(self, CENTER_BOX)

        self.xz = FaceColor.front
        self.yz = None
        self.xy = None


def decode(line):
    actions = line.split(',')
    if len(actions) < 8: return None

    pos = (int(actions[0]), int(actions[1]), int(actions[2]))
    obj = None
    if actions[3].startswith('s'):
        obj = SideBox()
    elif actions[3].startswith("cent"):
        obj = CenterBox()
    elif actions[3].startswith("corn"):
        obj = CornerBox()
    obj.pos = pos

    obj.xz = decodeColorFromText(actions[4])
    obj.yz = decodeColorFromText(actions[5])
    obj.xy = decodeColorFromText(actions[6])

    return obj


def encode(box):
    encode = "{x},{y},{z},{box_type},{xz},{yz},{xy},"
    if box.getType() == SIDE_BOX:
        box_type = "side"
    elif box.getType() == CORNER_BOX:
        box_type = "corner"
    elif box.getType() == CENTER_BOX:
        box_type = "center"
    else:
        raise SystemError("invalid box type to encode(box)")
    encode = encode.format(
        x=box.pos[0], y=box.pos[1], z=box.pos[2],
        box_type=box_type, xy=box.xy, xz=box.xz, yz=box.yz)

    return encode


def loadCubeFromFile(fileName):
    boxes = []
    with open(fileName, 'r') as f:
        lines = f.read().split("\n")
        for line in lines:
            if line.startswith("#"):
                continue
            elif len(line) < 12:
                continue
            else:
                obj = decode(line)
                if obj:
                    boxes.append(obj)
    return boxes


def saveCubeToFile(cube, fileName):
    print("saving to %s" % fileName)
    with open(fileName, 'w') as f:
        for a_box in cube.boxes:
            line = encode(a_box) + "\n"
            f.write(line)

    return True


_GRAPHICS = None

_PAUSED = visual.text(text='-', pos=(0, 2, 0), align="center", depth=-0.3,
                      color=visual.color.red)
_PAUSED.visible = False
_FPS = 70


class GUI(object):
    def stopAction(self, event):
        # if space  pressed,
        # stop  action in cube
        # wait for a keyup of space key
        # resume the action in cube
        # if reset pressed,
        # delay some time
        # reset the cube
        # empty actions to be performed
        # baam
        try:
            global _GRAPHICS
            cube = _GRAPHICS.cube
            if (event.key == " "):
                global _PAUSED
                cube.pauseAction()


        except:
            raise SystemError("GRAPHICS not initialised")
        return None

    def waitForUnpause(self):
        _PAUSED.visible = True
        while True:
            event = visual.scene.waitfor('keyup')
            if event.key == " ":
                _PAUSED.visible = False
                break
        return None

    def __init__(self, c):
        self.cube = c
        self.rendering = False
        global _GRAPHICS
        _GRAPHICS = self

    def init(self):
        """Assigns boxes with their respective colorBoxes."""
        # self.black=visual.box(pos=(0,0,0), size=(2,2,2),color=color.black)
        for box in self.cube.boxes:
            if box.xy:
                pos = box.pos
                pos = [pos[0] - 1, -1.5 * (abs(pos[2] - 1) / (1 - pos[2])),
                       1 - pos[1]]
                size = [0.97, 0.05, 0.97]
                box.xyBox = self.drawBox(pos, size, box.xy.color)
            if box.xz:
                pos = box.pos
                pos = [pos[0] - 1, pos[2] - 1,
                       -1.5 * (abs(pos[1] - 1) / (pos[1] - 1))]
                size = [0.97, 0.97, 0.05]
                box.xzBox = self.drawBox(pos, size, box.xz.color)
            if box.yz:
                pos = box.pos
                pos = [-1.5 * (abs(pos[0] - 1) / (1 - pos[0])), pos[2] - 1,
                       1 - pos[1]]
                size = [0.05, 0.97, 0.97]
                box.yzBox = self.drawBox(pos, size, box.yz.color)

    def drawBox(self, pos, size, color):
        """Draws a box on the screen and returns its address."""
        return visual.box(pos=pos, size=size, color=color)

    def rotateBoxes(self, boxes, direction, reverse=False, angle=None):
        if not self.rendering: return None
        if not self.cube.recording:
            return None

        if not angle: angle = pi / 2
        slicedAngle = 0.07
        counts = float(angle) / slicedAngle
        if counts > int(counts): counts = int(counts) + 1
        if not reverse:
            slicedAngle = -slicedAngle

        for i in range(0, counts + 1):
            global _FPS
            visual.rate(_FPS)
            if i == counts:
                slicedAngle = angle - abs(slicedAngle) * counts
                if not reverse:
                    slicedAngle = -slicedAngle
            for box in boxes:
                if box.xzBox:
                    box.xzBox.rotate(angle=slicedAngle, axis=direction,
                                     origin=(0, 0, 0))
                if box.xyBox:
                    box.xyBox.rotate(angle=slicedAngle, axis=direction,
                                     origin=(0, 0, 0))
                if box.yzBox:
                    box.yzBox.rotate(angle=slicedAngle, axis=direction,
                                     origin=(0, 0, 0))

    def begin(self):
        self.rendering = True
        self.init()
        # visual.scene.bind('keyup', self.stopAction)
        self.cube.initialMovement()

        while True:
            key = visual.scene.waitfor("keyup")
            key = key.key
            if key == "f":
                self.cube.action("F")
            elif key == "F":
                self.cube.action("Fi")
            elif key == "b":
                self.cube.action("B")
            elif key == "B":
                self.cube.action("Bi")
            elif key == "r":
                self.cube.action("R")
            elif key == "R":
                self.cube.action("Ri")
            elif key == "l":
                self.cube.action("L")
            elif key == "L":
                self.cube.action("Li")
            elif key == "u":
                self.cube.action("U")
            elif key == "U":
                self.cube.action("Ui")
            elif key == "d":
                self.cube.action("D")
            elif key == "D":
                self.cube.action("Di")
            elif key == "x":
                self.cube.action("x")
            elif key == "y":
                self.cube.action("y")
            elif key == "z":
                self.cube.action("z")
            elif key == "X":
                self.cube.action("xi")
            elif key == "Y":
                self.cube.action("yi")
            elif key == "Z":
                self.cube.action("zi")
            elif key == "m":
                self.cube.action("M")
            elif key == "M":
                self.cube.action("Mi")
            elif key == "e":
                self.cube.action("E")
            elif key == "E":
                self.cube.action("Ei")
            elif key == "s":
                self.cube.action("S")
            elif key == "S":
                self.cube.action("Si")


def solveTheCube(cube):
    cube.stopRecording()
    cube.original = utilities.copyCube(cube.boxes)
    cube.resetMoves()

    initial = time.time()
    cube.updateFaceColors();
    chooseBestSide(cube);
    solveCross(cube)
    solveF2L(cube)
    solveOLL(cube)
    solvePLL(cube)

    print("BAAM !!!")
    timeTaken = time.time() - initial
    with open("time.txt", "a") as f:
        f.write("%s\n" % timeTaken)
    print("SOLVED in %0.2f seconds" % (timeTaken))

    moves = cube.getMoves()
    cube.resetMoves()
    cube.boxes = cube.original
    cube.startRecording()

    return moves


def chooseBestSide(cube):
    print("getting best solved side")
    bestSide = chooseBestSolvedSide(cube)

    print("orienting the cube to %s as base" % str(bestSide))
    orientCube(cube, bestSide)
    cube.updateFaceColors();


def solveCross(cube):
    print("getting base cross")
    bringCrossPiecesInPositon(cube)

    print("matching them with their respective sides")
    solveBaseCross(cube)


def solveF2L(cube):
    print("getting the base corner pieces in position")
    bringBaseCornersInPosition(cube)

    print("Solving second level")
    solveSecondLevel(cube)


def solveOLL(cube):
    # get the structure of the oll cross.

    # coded from solve-the-cube.com, advanced.html
    # structuremode
    # point
    # all_corners
    # line
    # T
    # Z
    # C
    # bigL
    # littleL
    # cross
    # W
    # P

    if cube.OLLsolved(): return
    top = FaceColor.top

    C1 = cube.boxAt(0, 0, 2).xy.color == top.color;
    C1 = C1 and cube.boxAt(2, 0, 2).xy.color == top.color;
    C1 = C1 and cube.boxAt(0, 2, 2).xy.color == top.color;
    C1 = C1 and cube.boxAt(2, 2, 2).xy.color == top.color;

    if C1:
        # all corners solved
        print("CORNER MODE")

        unsolved_side_pieces = 0
        for box in cube.getSide(TOP_SIDE):
            if box.getType() == "side_box":
                if not (box.xy.color == top.color):
                    unsolved_side_pieces += 1;
        if unsolved_side_pieces == 4:
            # type(27)
            cube.action("M' U2 M U2 M' U M U2 M' U2 M");
            return;
        C2 = cube.boxAt(1, 0, 2).xy.color == top.color
        C2 = C2 and cube.boxAt(1, 2, 2).xy.color == top.color
        if C2:
            cube.action("U");

        C3 = cube.boxAt(0, 1, 2).xy.color == top.color
        C3 = C3 and cube.boxAt(2, 1, 2).xy.color == top.color
        if C3:
            cube.action("Li R U Ri Ui L Ri F R Fi");
        else:
            # not two opposite side unsolved pieces
            while not (
                    cube.boxAt(0, 1, 2).xy.color == top.color and cube.boxAt(1,
                                                                             0,
                                                                             2).xy.color == top.color):
                cube.action("U");
            cube.action("Mi Ui M U2 Mi Ui M");
        return None

    # check for a line, a horizontal one at the 2nd row
    if (cube.boxAt(0, 1, 2).xy.color == top.color and cube.boxAt(2, 1,
                                                                 2).xy.color == top.color):
        cube.action("U");

    # check for a vertical line
    if (cube.boxAt(1, 0, 2).xy.color == top.color and cube.boxAt(1, 2,
                                                                 2).xy.color == top.color):
        if (cube.boxAt(0, 1, 2).xy.color == top.color and cube.boxAt(2, 1,
                                                                     2).xy.color == top.color):  # a cross
            # find how many pieces of corner pieces of OLL are already in place
            num = 0;
            boxes = cube.getSide(TOP_SIDE);
            for box in boxes:
                if box.getType() == "corner_box":
                    if box.xy.color == top.color:
                        num += 1;

            if num == 0:
                # no piece is correct.
                while not (cube.boxAt(2, 0, 2).yz.color == top.color):
                    cube.action("U");

                if (cube.boxAt(0, 0, 2).yz.color == top.color and cube.boxAt(2,
                                                                             2,
                                                                             2).yz.color == top.color):
                    # type(7)
                    cube.action("R U R' U R U' R' U R U2 R'")
                else:
                    # type(6)
                    if cube.boxAt(0, 0, 2).yz.color == top.color:
                        cube.action("U");

                    cube.action("L U' R' U L' U R U R' U R");
            elif num == 1:
                # a sigle piece solved.
                while not (cube.boxAt(2, 0, 2).xy.color == top.color):
                    cube.action("U");
                if cube.boxAt(0, 0, 2).yz.color == top.color:
                    # type(8)
                    cube.action("R' U2 R U R' U R")

                else:
                    # type is #(9)
                    cube.action("L' U R U' L U R'")
            elif num == 2:
                # 2 pieces solved
                while not (cube.boxAt(0, 0,
                                      2).xy.color == top.color and cube.boxAt(2,
                                                                              0,
                                                                              2).xy.color != top.color):
                    cube.action("U");
                if cube.boxAt(0, 2, 2).xy.color != top.color:
                    while not (cube.boxAt(2, 2, 2).xz.color == top.color):
                        cube.action("U");
                    # type is now #(10)
                    cube.action("R' F' L' F R F' L F")
                elif cube.boxAt(2, 0, 2).yz.color == top.color:
                    cube.action("U");
                    # type(11)
                    cube.action("R2 D R' U2 R D' R' U2 R'")
                else:
                    # type(12)
                    cube.action("R' F' L F R F' L' F");
            else:
                print(num)
                raise SystemError("invalid cube");
            return;
        else:
            # "no cross";

            number = 0;
            for box in cube.getSide(TOP_SIDE):
                if box.getType() == "corner_box":
                    if box.xy.color == top.color:
                        number += 1;
            if number == 0:
                # just a vertical line

                left_yz_solved_count = 0;
                right_yz_solved_count = 0;
                for box in cube.getSide(TOP_SIDE):
                    if box.getPos()[0] == 0:
                        if box.yz.color == top.color:
                            left_yz_solved_count += 1;
                    elif box.getPos()[0] == 2:
                        if box.yz.color == top.color:
                            right_yz_solved_count += 1;
                array = (left_yz_solved_count, right_yz_solved_count);

                if array == (2, 2):
                    while not (cube.boxAt(0, 0,
                                          2).xz.color == top.color and cube.boxAt(
                            1, 0, 2).xz.color == top.color):
                        cube.action("U");
                    # "type 15";
                    cube.action("F U R U' R' U R U' R' F'")
                elif array == (3, 1) or array == (1, 3):
                    if (array == (3, 1)):
                        cube.action("U2");
                    # "type(14)";
                    cube.action("R' U' y L' U L' y' L F L' F R");
                elif array == (3, 3):
                    # "type(13)";
                    cube.action("R U2 R2 U' R U' R' U2 F R F'");
                elif array == (1, 1):
                    # "type(16)";
                    cube.action("U L' B' L U' R' U R U' R' U R L' B L");
                else:
                    raise SystemError("invalid_line");
            elif number == 1:
                for box in [cube.boxAt(0, 0, 2), cube.boxAt(0, 2, 2)]:
                    if box.xy.color == top.color:
                        cube.action("U2");
                        break;
                if cube.boxAt(2, 2, 2).xy.color == top.color:
                    if cube.boxAt(2, 0, 2).yz.color == top.color:
                        cube.action("U");
                        cube.action("R' F R U R' F' R y L U' L'");
                    elif cube.boxAt(2, 0, 2).xz.color == top.color:
                        cube.action("U");
                        cube.action("L' B' L R' U' R U L' B L");
                    else:
                        raise SystemError("unknown Big L");
                elif cube.boxAt(2, 0, 2).xy.color == top.color:
                    if cube.boxAt(0, 0, 2).yz.color == top.color:
                        cube.action("U");
                        cube.action("L F' L' U' L F L' y' R' U R");
                    elif cube.boxAt(0, 0, 2).xz.color == top.color:
                        cube.action("U");
                        cube.action("R B R' L U L' U' R B' R'");
                else:
                    raise SystemError("unknown BigL");
            elif number == 2:
                box1 = None
                box2 = None
                for box in [cube.boxAt(0, 2, 2), cube.boxAt(2, 2, 2),
                            cube.boxAt(2, 0, 2), cube.boxAt(0, 0, 2)]:
                    if box.xy.color == top.color:
                        if box1:
                            box2 = box
                            break
                        else:
                            box1 = box
                assert (box1 and box2);

                if box1.pos[0] == box2.pos[0]:
                    if box1.pos[0] == 2:
                        cube.action("U2");
                    if cube.boxAt(2, 2, 2).yz.color == top.color:
                        cube.action("R U x' R U' R' U x U' R'");
                    else:
                        cube.action("Ui");
                        cube.action("R U R2 U' R' F R U R U' F'");
                elif box1.pos[1] == box2.pos[1]:
                    if box1.pos[1] == 2:
                        cube.action("U2");
                    if cube.boxAt(0, 2, 2).xz.color == top.color:
                        cube.action("Ui");
                        cube.action("F R U R' U' F'");
                    else:
                        cube.action("Ui");
                        cube.action("R U R' U' R' F R F'");
                else:
                    if cube.boxAt(2, 0, 2).xy.color == top.color:
                        # type like(26)
                        if not (cube.boxAt(2, 2,
                                           2).yz.color == top.color and cube.boxAt(
                                2, 1, 2).yz.color == top.color):
                            cube.action("U2");
                        cube.action("Ui");
                        # type is #26
                        cube.action("L F' L' U' L U F U' L'");
                    else:

                        if not (cube.boxAt(2, 0,
                                           2).yz.color == top.color and cube.boxAt(
                                2, 1, 2).yz.color == top.color):
                            cube.action("U2");
                        cube.action("Ui");
                        # type(25)
                        cube.action("R' F R U R' U' F' U R");
            else:
                raise SystemError("OLL ERROR ");
        return;

    number = 0
    for box in cube.getSide(TOP_SIDE):
        if box.getType() == SIDE_BOX:
            if box.xy.color == top.color:
                number += 1
    if number == 3 or number == 4:
        raise SystemError("invalid cross shape on oll")
    elif number == 2:
        print("little L")
        from algorithms import smallL_oll
        try:
            answer = smallL_oll.getAnswerFor(cube);
            cube.action(answer);
        except:
            raise SystemError("invalid oll in cube");
        return;
    else:
        print("dot")
        from algorithms import dot_oll
        answer = dot_oll.getAnswerFor(cube)
        cube.action(answer)

    return


def solvePLL(cube):
    import algorithms.pll
    answer = algorithms.pll.solve(cube)
    cube.action(answer)


def getCrossCellsCount(cube, side):
    '''Returns the number of same boxes in the given side, respective to the middle color.'''
    boxes = cube.getSide(side)

    # get the color of the centre box
    for box in boxes:
        if box.pos[0] == 1 and box.pos[1] == 1:
            color = box.xy

    count = 0  # count of the number of boxes in cross including the middle piece

    # now count the boxes of the cross that match to their boss(centre)
    for box in boxes:
        if box.pos[0] == 1 or box.pos[1] == 1:
            if box.xy.color == color.color:
                count += 1
    return count


def chooseBestSolvedSide(cube):
    '''Chooses the best side fit to be the base.'''
    array = []
    actions = ["", "Xi", "Xi", "Xi", "Z", "Z2"]
    for action in actions:
        cube.action(action)
        array.append([str(cube.boxAt(1, 1, 0).xy),
                      getCrossCellsCount(cube, BOTTOM_SIDE)])

    highest = ["green", 0]
    for item in array:
        if item[1] > highest[1]:
            highest = [item[0], item[1]]

    return highest[0]


def orientCube(cube, side):
    count = 0
    while not str(cube.boxAt(1, 1, 0).xy) == side:
        if count >= 4: break
        count += 1
        cube.action("Z")

    while not str(cube.boxAt(1, 1, 0).xy) == side:
        cube.action("Xi")


def solveSecondLevel(self):
    '''Solves the second layer.
    Given that the base corner pieces are already in their correct position.'''
    piecesThatCanHold = [(0, 0, 1), (0, 2, 1), (2, 0, 1), (2, 2, 1), (1, 0, 2),
                         (1, 2, 2), (0, 1, 2), (2, 1, 2)]
    # solve the pieces that are in the top position
    # if f2l-second phase complete:break
    # else:
    # bring the pieces of the corners which are unmatched to the top
    sides = [(0, 0, 1), (0, 2, 1), (2, 0, 1), (2, 2, 1)]
    while True:

        pieces = self.findAllWithout(piecesThatCanHold, FaceColor.top)

        assert (len(pieces) == 4);
        i = 0
        while i < len(pieces):

            box = pieces[i]
            pos = box.pos
            if pos[2] == 1:
                i = i + 1
                continue  # lies on the first line

            answer = Algo.getAnswerForf2lSecondLineTransformation(
                "f2l-secondLineSolve", box)

            self.action(answer)

            pieces = self.findAllWithout(piecesThatCanHold, FaceColor.top)

            i = 0
        if self.f2lSecondPhaseComplete():
            break
        else:
            for side in sides:
                if not self.isSolvedAt(side):
                    answer = Algo.getAnswerForF2lSecondLineBringBoxToTopTransformation(
                        side)
                    self.action(answer)


def bringCrossPiecesInPositon(self):
    '''Brings cross pieces of base layer in position.
    Are flipped correctly too.'''
    while True:
        boxes = []
        for box in self.boxes:
            if box.hasColor(FaceColor.bottom) and box.getType() == SIDE_BOX:
                boxes.append(box)

        assert (len(boxes) == 4)
        # boxes has the 4 white side_piece boxes

        update = False
        for box in boxes:
            pos = box.pos
            if pos[2] == 0:
                # print "base"
                pass
            elif pos[2] == 2:
                # bring to (1,0,2)
                while not self.boxAt(1, 0, 2).hasColor(FaceColor.bottom):
                    self.action("U")
                # empty at (1,0,0)
                while self.boxAt(1, 0, 0).hasColor(FaceColor.bottom):
                    self.action("D")
                self.action("F F")
                # bring the cube from top to bottom line
                update = True
                break
            else:
                update = True
                if box.pos[0] == 0 and box.pos[1] == 0:
                    self.action("F U Fi")
                elif box.pos[0] == 0 and box.pos[1] == 2:
                    self.action("L U Li")
                elif box.pos[0] == 2 and box.pos[1] == 0:
                    self.action("R U Ri")
                elif box.pos[0] == 2 and box.pos[1] == 2:
                    self.action("Ri U R")
                else:
                    raise SystemError("INVALID EXCEPTION")
                break

        if update: continue
        boxes = self.getSide(BOTTOM_SIDE)
        centers = []
        for item in boxes:
            if item.getType() == SIDE_BOX:
                centers.append(item)

        for item in centers:
            while not item.pos == (1, 0, 0):
                self.action("D")
            if not (self.boxAt(1, 0, 0).xy.color == FaceColor.bottom.color):
                self.action("F Di L")
        break


def solveBaseCross(self):
    '''Solves the side pairs of the cross with their centre pieces.
    Given that the cross is formed and all the base pieces in the cross are of the same color.'''

    a1 = self.boxAt(0, 1, 0).yz

    while not self.boxAt(0, 1, 0).yz.color == FaceColor.left.color:
        self.action("D")
    # piece 1 solved: FaceColor.left matched

    # front piece
    if self.boxAt(1, 0, 0).xz.color == FaceColor.front.color:
        pass
    else:
        if self.boxAt(2, 1, 0).yz.color == FaceColor.front.color:
            self.action("F F U' R R U F F")
        else:
            self.action("F F U' U' B B U U F F")
    # front matched

    # right piece
    if self.boxAt(2, 1, 0).yz.color == FaceColor.right.color:
        pass
    else:
        self.action("R R U' B B U R R")
    # the back piece is automatically correct since the others are correct
    return


def bringBaseCornersInPosition(self):
    '''Brings the base corners in position and also flips them correctly.'''
    # get the corner pieces with white in them
    corners = self.findAll(CORNER_PIECES, FaceColor.bottom)
    assert (len(corners) == 4);

    # piece of (0,0,0) as corner, process it
    for corner in corners:
        if corner.hasColor(FaceColor.left, FaceColor.front):
            break
    pos = corner.pos
    if pos == (0, 0, 0):
        # already on place
        pass
    else:

        # misplaced, bring it to (0,0,2), above the line
        if pos[2] == 0:  # lies on another corner
            if pos[0] == 0:
                # lies on (0,2,0)

                self.action("L U' L' U'")
                # brings on above the line
            else:
                # lies on either of the right base corners of the cube
                if pos[1] == 2:  # lies on (2,2,0)
                    self.action("R' U' R U'")
                else:
                    # lies on (2,0,0)
                    self.action("F' U F U")
        else:
            while not self.boxAt(0, 0, 2).hasColor(FaceColor.left,
                                                   FaceColor.front,
                                                   FaceColor.bottom):
                self.action("U")
            # came above the line
            # now send it down
        self.action("L' U' L")
    assert (self.boxAt(0, 0, 0).hasColor(FaceColor.bottom, FaceColor.front,
                                         FaceColor.left))
    # now flip it to the right orientation
    while not (self.boxAt(0, 0,
                          0).xy.color == FaceColor.bottom.color and self.boxAt(
            0, 0, 0).hasColor(FaceColor.front, FaceColor.left)):
        self.action("L' U' L U")
    assert (self.boxAt(0, 0, 0).hasColor(FaceColor.bottom, FaceColor.front,
                                         FaceColor.left))
    # solved of (0,0,0)

    # piece of (0,2,0) as corner, process it

    for corner in corners:
        if corner.hasColor(FaceColor.left, FaceColor.back):
            # print corner.pos
            break
    pos = corner.pos
    if pos == (0, 2, 0):
        # already on place
        pass
    else:
        # misplaced, bring it to (0,2,2), above the line
        if pos[2] == 0:  # lies on either of the corners
            if pos[1] == 2:  # lies on (2,2,0)
                self.action("R' U' R")
            else:
                # lies on (2,0,0)
                self.action("F' U U F")
        else:
            while not self.boxAt(0, 2, 2).hasColor(FaceColor.left,
                                                   FaceColor.back,
                                                   FaceColor.bottom):
                self.action("U")
        # came above the line
        # now send it down
        self.action("L U L'")

    assert (self.boxAt(0, 2, 0).hasColor(FaceColor.bottom, FaceColor.left,
                                         FaceColor.back))
    # now flip it to the right orientation
    while not (self.boxAt(0, 2,
                          0).xy.color == FaceColor.bottom.color and self.boxAt(
            0, 2, 0).hasColor(FaceColor.back, FaceColor.left)):
        self.action("L U L' U'")
    # solved of (0,2,0)
    assert (self.boxAt(0, 2, 0).hasColor(FaceColor.bottom, FaceColor.left,
                                         FaceColor.back))

    for corner in corners:
        if corner.hasColor(FaceColor.right, FaceColor.back):
            break
    # piece of (2,2,0) as corner, process it
    pos = corner.pos
    if pos == (2, 2, 0):
        # already on place
        pass
    else:
        # misplaced, bring it to (2,2,2), above the line
        if pos[2] == 0:  # lies on (2,0,0)
            self.action("F' U' F")
        else:
            while not self.boxAt(2, 2, 2).hasColor(FaceColor.right,
                                                   FaceColor.back,
                                                   FaceColor.bottom):
                self.action("U")
        # came above the line
        # now send it down
        self.action("R' U' R")
    assert (self.boxAt(2, 2, 0).hasColor(FaceColor.bottom, FaceColor.back,
                                         FaceColor.right))
    # now flip it to the right orientation
    while not (self.boxAt(2, 2,
                          0).xy.color == FaceColor.bottom.color and self.boxAt(
            2, 2, 0).hasColor(FaceColor.back, FaceColor.right)):
        self.action("R' U R U'")
    assert (self.boxAt(2, 2, 0).hasColor(FaceColor.bottom, FaceColor.back,
                                         FaceColor.right))
    # solved of (2,2,0)

    for corner in corners:
        if corner.hasColor(FaceColor.right, FaceColor.front):
            break
    # piece of (2,0,0) as corner, process it
    pos = corner.pos

    if pos == (2, 0, 0):
        # alread on place
        pass
    else:
        while not self.boxAt(2, 0, 2).hasColor(FaceColor.bottom):
            self.action("U")
        self.action("R U R'")

    assert (self.boxAt(2, 0, 0).hasColor(FaceColor.bottom, FaceColor.right,
                                         FaceColor.front))
    while not (self.boxAt(2, 0,
                          0).xy.color == FaceColor.bottom.color and self.boxAt(
            2, 0, 0).hasColor(FaceColor.front, FaceColor.right)):
        self.action("R U R' U'")
    assert (self.boxAt(2, 0, 0).hasColor(FaceColor.bottom, FaceColor.right,
                                         FaceColor.front))
    # solved of (2,0,0)
    return


class Cube(object):

    def __init__(self, file_name="cube.txt"):
        self.reset()
        self.boxes = self.boxes = loadCubeFromFile(file_name)

        self.gui = None
        self.recording = False
        self.initialFunction = None
        self.calledForPause = False

    def getFaceColor(self):
        return FaceColor

    def startRecording(self):
        self.recording = True

    def stopRecording(self):
        self.recording = False

    def setFunction(self, fun):
        self.initialFunction = fun

    def reset(self):
        """Reset the cube."""
        self.boxes = loadCubeFromFile("cube.txt")
        self.resetMoves()

    def save(self, fileName):
        saveCubeToFile(self, fileName)
        print("done")

    def getMoves(self):
        return utilities.optimizeMoves(self.move)

    def initialMovement(self):
        if self.initialFunction:
            self.initialFunction()

    def isSolvedAt(self, pos):
        """Check if a pos has its native colors, flipped properly."""
        # get the centre piece of box adjacent sides
        if pos[0] == 0:
            if not self.boxAt(*pos).yz.color == self.boxAt(0, 1,
                                                           1).yz.color: return False
        elif pos[0] == 2:
            if not self.boxAt(*pos).yz.color == self.boxAt(2, 1,
                                                           1).yz.color: return False
        if pos[1] == 0:
            if not self.boxAt(*pos).xz.color == self.boxAt(1, 0,
                                                           1).xz.color: return False
        elif pos[1] == 2:
            if not self.boxAt(*pos).xz.color == self.boxAt(1, 2,
                                                           1).xz.color: return False
        if pos[2] == 0:
            if not self.boxAt(*pos).xy.color == self.boxAt(1, 1,
                                                           0).xy.color: return False
        elif pos[2] == 2:
            if not self.boxAt(*pos).xy.color == self.boxAt(1, 1,
                                                           2).xy.color: return False
        return True

    def isSolved(self):
        """Check if the cube is solved."""
        for box in self.boxes:
            if not self.isSolvedAt(box.pos):
                return False
        return True

    def getSide(self, side):
        """Returns cells of a specific side."""
        ret = []
        a = self.boxes
        for box in self.boxes:
            pos = box.getPos()
            if side == FRONT_SIDE and pos[1] == 0:
                ret.append(box)
            elif side == BACK_SIDE and pos[1] == 2:
                ret.append(box)
            elif side == TOP_SIDE and pos[2] == 2:
                ret.append(box)
            elif side == BOTTOM_SIDE and pos[2] == 0:
                ret.append(box)
            elif side == LEFT_SIDE and pos[0] == 0:
                ret.append(box)
            elif side == RIGHT_SIDE and pos[0] == 2:
                ret.append(box)
        return ret

    def resetMoves(self):
        """Empty moves."""
        self.move = ""

    def updateFaceColors(self):
        FaceColor.update(
            {"front": self.boxAt(1, 0, 1).xz, "left": self.boxAt(0, 1, 1).yz,
             "top": self.boxAt(1, 1, 2).xy})

    def registerGraphicsHandler(self, g):
        self.gui = g

    def pauseAction(self):
        self.calledForPause = True

    def unpauseAction(self):
        self.calledForPause = False

    def isActionPaused(self):
        return self.calledForPause

    def action(self, word):
        """Apply algorithm to the cube."""
        keys = utilities.split_word(word)

        for key in keys:
            if len(key) > 1:
                key = key[0].upper() + key[1:]
            else:
                key = key.upper()
            if key == "": continue

            if key == 'F':
                rotation.rotateFrontSide(self)
                self.gui.rotateBoxes(
                    self.getSide(FRONT_SIDE), (0, 0, 1))
            elif key == 'B':
                rotation.rotateBackSide(self)
                self.gui.rotateBoxes(
                    self.getSide(BACK_SIDE), (0, 0, 1),
                    reverse=True)
            elif key == 'L':
                rotation.rotateLeftSide(self)
                self.gui.rotateBoxes(
                    self.getSide(LEFT_SIDE), (1, 0, 0),
                    reverse=True)
            elif key == 'R':
                rotation.rotateRightSide(self)
                self.gui.rotateBoxes(self.getSide(
                    RIGHT_SIDE), (1, 0, 0))
            elif key == 'U':
                rotation.rotateTopSide(self)
                self.gui.rotateBoxes(
                    self.getSide(TOP_SIDE), (0, 1, 0))
            elif key == 'D':
                rotation.rotateBottomSide(self)
                self.gui.rotateBoxes(self.getSide(
                    BOTTOM_SIDE), (0, 1, 0),
                    reverse=True)
            elif key == 'Fi':
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                self.gui.rotateBoxes(self.getSide(
                    FRONT_SIDE), (0, 0, 1),
                    reverse=True)
            elif key == 'Bi':
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                self.gui.rotateBoxes(
                    self.getSide(BACK_SIDE), (0, 0, 1))
            elif key == 'Li':
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                self.gui.rotateBoxes(
                    self.getSide(LEFT_SIDE), (1, 0, 0))
            elif key == 'Ri':
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                self.gui.rotateBoxes(
                    self.getSide(RIGHT_SIDE), (1, 0, 0),
                    reverse=True)
            elif key == 'Ui':
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                self.gui.rotateBoxes(
                    self.getSide(TOP_SIDE), (0, 1, 0),
                    reverse=True)
            elif key == 'Di':
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                self.gui.rotateBoxes(
                    self.getSide(BOTTOM_SIDE), (0, 1, 0))
            elif key == 'F2':
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                self.gui.rotateBoxes(
                    self.getSide(FRONT_SIDE), (0, 0, 1),
                    angle=pi)
            elif key == 'B2':
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                self.gui.rotateBoxes(
                    self.getSide(BACK_SIDE), (0, 0, 1),
                    reverse=True, angle=pi)
            elif key == 'L2':
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                self.gui.rotateBoxes(
                    self.getSide(LEFT_SIDE), (1, 0, 0),
                    reverse=True, angle=pi)
            elif key == 'R2':
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                self.gui.rotateBoxes(
                    self.getSide(RIGHT_SIDE), (1, 0, 0),
                    angle=pi)
            elif key == 'U2':
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                self.gui.rotateBoxes(
                    self.getSide(TOP_SIDE), (0, 1, 0),
                    angle=pi)
            elif key == 'D2':
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                self.gui.rotateBoxes(
                    self.getSide(BOTTOM_SIDE), (0, 1, 0),
                    reverse=True, angle=pi)
            elif key == "M":
                rotation.rotateM(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[0] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (1, 0, 0), reverse=True)
            elif key == "E":
                rotation.rotateE(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[2] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 1, 0), reverse=True)
            elif key == "S":
                rotation.rotateS(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[1] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 0, 1))
            elif key == "M2":
                rotation.rotateM(self)
                rotation.rotateM(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[0] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (1, 0, 0), reverse=True, angle=pi)
            elif key == "E2":
                rotation.rotateE(self)
                rotation.rotateE(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[2] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 1, 0), reverse=True, angle=pi)
            elif key == "S2":
                rotation.rotateS(self)
                rotation.rotateS(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[1] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 0, 1), angle=pi)
            elif key == "Mi":
                rotation.rotateM(self)
                rotation.rotateM(self)
                rotation.rotateM(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[0] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (1, 0, 0))
            elif key == "Ei":
                rotation.rotateE(self)
                rotation.rotateE(self)
                rotation.rotateE(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[2] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 1, 0))
            elif key == "Si":
                rotation.rotateS(self)
                rotation.rotateS(self)
                rotation.rotateS(self)
                boxes = []
                for box in self.boxes:
                    if box.pos[1] == 1:
                        boxes.append(box)
                self.gui.rotateBoxes(boxes, (0, 0, 1), reverse=True)
            elif key == "X":
                rotation.rotateRightSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateM(self)
                rotation.rotateM(self)
                rotation.rotateM(self)
                self.gui.rotateBoxes(self.boxes, (1, 0, 0))
            elif key == "Xi":
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateM(self)
                self.gui.rotateBoxes(self.boxes, (1, 0, 0), reverse=True)
            elif key == "X2":
                rotation.rotateM(self)
                rotation.rotateM(self)
                rotation.rotateRightSide(self)
                rotation.rotateRightSide(self)
                rotation.rotateLeftSide(self)
                rotation.rotateLeftSide(self)
                self.gui.rotateBoxes(self.boxes, (1, 0, 0), angle=pi)
            elif key == "Y":
                rotation.rotateTopSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateE(self)
                rotation.rotateE(self)
                rotation.rotateE(self)
                self.gui.rotateBoxes(self.boxes, (0, 1, 0))
            elif key == "Yi":
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateE(self)
                self.gui.rotateBoxes(self.boxes, (0, 1, 0), reverse=True)
            elif key == "Y2":
                rotation.rotateTopSide(self)
                rotation.rotateTopSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateBottomSide(self)
                rotation.rotateE(self)
                rotation.rotateE(self)
                self.gui.rotateBoxes(self.boxes, (0, 1, 0), angle=pi)
            elif key == "Z":
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateS(self)
                rotation.rotateS(self)
                rotation.rotateS(self)
                self.gui.rotateBoxes(self.boxes, (0, 0, 1), reverse=True)
            elif key == "Zi":
                rotation.rotateFrontSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateS(self)
                self.gui.rotateBoxes(self.boxes, (0, 0, 1))
            elif key == "Z2":
                rotation.rotateFrontSide(self)
                rotation.rotateFrontSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateBackSide(self)
                rotation.rotateS(self)
                rotation.rotateS(self)
                self.gui.rotateBoxes(
                    self.boxes, (0, 0, 1), reverse=True,
                    angle=pi)
            else:
                print("unknown character : " + key)
                raise SystemError
            self.move += " " + key + " "

    def OLLsolved(self):
        self.updateFaceColors()
        boxes = self.getSide(TOP_SIDE)
        for box in boxes:
            if box.xy.color is not FaceColor.top.color:
                return False
        return True

    def findAll(self, array, color):
        """Returns all box with color from the array."""
        ret = []
        for box in self.boxes:
            if box.pos in array:
                if box.hasColor(color):
                    ret.append(box)
        return ret

    def actionRealTime(self, word):
        """Solves real time for the user. For each next move, the user presses the space key."""
        # if self.isActionPaused():
        # self.gui.waitForUnpause();
        keys = word.split(" ")
        for key in keys:
            try:
                self.action(key)
                self.gui.waitForUnpause()
            except:
                continue

    def findAllWithout(self, array, color):
        """Returns all box without color from the array."""
        ret = []
        for box in self.boxes:
            if box.pos in array:
                if not box.hasColor(color):
                    ret.append(box)
        return ret

    def f2lSecondPhaseComplete(self):
        """Checks if f2l is complete."""
        C1 = self.boxAt(0, 0, 1).xz.color == \
             FaceColor.front.color and self.boxAt(2, 0, 1).xz.color == \
             FaceColor.front.color

        C2 = self.boxAt(0, 0, 1).yz.color == FaceColor.left.color and \
             self.boxAt(0, 2, 1).yz.color == FaceColor.left.color
        C3 = self.boxAt(0, 2, 1).xz.color == FaceColor.back.color and \
             self.boxAt(2, 2, 1).xz.color == FaceColor.back.color
        C4 = self.boxAt(2, 2, 1).yz.color == FaceColor.right.color and \
             self.boxAt(2, 0, 1).yz.color == FaceColor.right.color
        return C1 and C2 and C3 and C4

    def boxAt(self, x, y, z):
        for box in self.boxes:
            if box.pos == (x, y, z):
                return box

    def solve(self):
        return solveTheCube(self)


print("Welcome to the Rubik's Cube!")


def fun():
    """This function is launched after the graphics has been initialized."""

    print('Generating random algorithm')
    algo = utilities.randomAlgorithm(20)
    print(algo)

    print('Applying random algorithm to the cube')
    c.action(algo)

    print('Getting the solution algorithm')
    answer = c.solve()
    print(answer)

    print('Applying the solution to the cube')
    c.action(answer)

    print('Is rubiks cube solved? {}'.format(c.isSolved()))

    print("End of Program")


c = Cube()
# c.updateFaceColors();
graphics = GUI(c)
c.registerGraphicsHandler(graphics)
c.startRecording()
c.setFunction(fun)

graphics.begin()

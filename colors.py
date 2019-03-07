import visual


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


RED = ColorItem("red");
BLUE = ColorItem("blue");
GREEN = ColorItem("green");
ORANGE = ColorItem("orange");
WHITE = ColorItem("white");
YELLOW = ColorItem("yellow");

RED.setColor(visual.color.red)
GREEN.setColor(visual.color.green)
YELLOW.setColor(visual.color.yellow)
BLUE.setColor(visual.color.blue)
WHITE.setColor(visual.color.white)
ORANGE.setColor(visual.color.orange)

RED.setOpposite(ORANGE)
BLUE.setOpposite(GREEN)
WHITE.setOpposite(YELLOW)


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

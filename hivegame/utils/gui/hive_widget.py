import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from hivegame.utils import hexutil
from hivegame.utils.game_state import GameState
from hivegame.pieces import piece_factory


class GameWidget(QtWidgets.QWidget):
    """The Qt Widget which shows the game."""

    _kind_to_text = {
        "A": "Ant",
        "B": "Beetle",
        "G": "Grasshopper",
        "S": "Spider",
        "Q": "Queen"
    }
    _text_to_piece = {
        "Ant": "A",
        "Beetle": "B",
        "Grasshopper": "G",
        "Spider": "S",
        "Queen": "Q"
    }

    hexagon_under_cursor = None
    selected_hexagon = None

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.setMouseTracking(True) # we want to receive mouseMoveEvents

        self.level = GameState()
        self.hexgrid = hexutil.HexGrid(24)

        # initialize GUI objects needed for painting
        self.font = QtGui.QFont("Helvetica", 20)
        self.font.setStyleHint(QtGui.QFont.SansSerif)
        self.pen = QtGui.QPen()
        self.pen.setWidth(2)
        self.select_brush = QtGui.QBrush(QtGui.QColor(127, 127, 255, 127))
        self.unseen_brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 127))

        # set center position
        self.center = QtCore.QPoint(0, 0)

        # Related to mouse events
        self.last_pos = QtCore.QPoint()
        self.is_mouse_pressed = False

        # mouse timer helps to distinguish click from press-and-hold
        self.mouse_timer = QtCore.QTimer()
        self.mouse_timer.setInterval(250)
        self.mouse_timer.setSingleShot(True)

    def hexagon_of_pos(self, pos):
        """Compute the hexagon at the screen position."""
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        return self.hexgrid.hex_at_coordinate(pos.x() - xc, pos.y() - yc)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            # Check if it is a border hex
            game_pos = event.pos() + self.center
            hexagon = self.hexagon_of_pos(game_pos)
            if hexagon not in self.level.get_border_tiles():
                return

            # Show dropdown menu
            menu = QtWidgets.QMenu()
            # TODO color
            color = "w"
            available_kinds = self.level.available_kinds_to_place(color)
            for kind in available_kinds:
                action_to_add = menu.addAction(self._kind_to_text.get(kind))

            # select executed item
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if not action:
                return  # user clicked elsewhere, or no more pieces available
            # TODO clean up text to kind
            self.level.move_or_append_to(piece_factory.create_piece(color, self._text_to_piece[action.text()],
                                                                    available_kinds[action.text()[0]]), hexagon)
            self.repaint()
            return
        elif event.button() == QtCore.Qt.LeftButton:
            self.is_mouse_pressed = True
            self.last_pos = event.pos()
            if not self.mouse_timer.isActive():
                self.mouse_timer.start()
            return

    def mouseReleaseEvent(self, event):
        self.is_mouse_pressed = False
        if self.mouse_timer.isActive():
            self.mouse_timer.stop()
            # perform selection
            game_pos = event.pos() + self.center
            hexagon = self.hexagon_of_pos(game_pos)
            self.selected_hexagon = hexagon
            self.repaint()

    def mouseMoveEvent(self, event):
        if self.is_mouse_pressed and not self.mouse_timer.isActive():
            pos_change = event.pos() - self.last_pos
            self.center -= pos_change
            self.last_pos = event.pos()
        self.select_hexagon(event.pos())

    def select_hexagon(self, pos):
        """Select hexagon and path to hexagon at position."""
        game_pos = pos + self.center
        hexagon = self.hexagon_of_pos(game_pos)
        self.hexagon_under_cursor = hexagon
        self.repaint()
 
    def paintEvent(self, event):
        # compute center of window
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        # bounding box when we translate the origin to be at the center
        bbox = hexutil.Rectangle(self.center.x() - xc, self.center.y() -yc, size.width(), size.height())
        hexgrid = self.hexgrid
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            # paint background black
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor())
            painter.drawRect(0, 0, size.width(), size.height())
            painter.restore()

            # set up drawing state
            painter.setPen(self.pen)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            painter.setFont(self.font)
            painter.translate(xc, yc)
            # draw each hexagon which is in the window
            
            for hexagon in hexgrid.hexes_in_rectangle(bbox):
                selectable = False
                polygon = QtGui.QPolygon([QtCore.QPoint(*corner) - self.center for corner in hexgrid.corners(hexagon)])
                # if it is a placed hexagon
                if self.level.get_tile_content(hexagon):
                    selectable = True
                    if hexagon == self.selected_hexagon:
                        painter.setBrush(QtGui.QColor("yellow"))
                    else:
                        painter.setBrush(QtGui.QColor("lightGray"))
                    painter.drawPolygon(polygon)

                    # draw bug (which is currently represented with a letter)
                    rect = hexgrid.bounding_box(hexagon)
                    relative_rect = hexutil.Rectangle(x=rect.x - self.center.x(), y=rect.y - self.center.y(),
                                                      width=rect.width, height=rect.height)
                    relative_rect = QtCore.QRectF(*relative_rect) # convert to Qt RectF and add relative position
                    painter.drawText(relative_rect, QtCore.Qt.AlignCenter, self.level.get_tile_content(hexagon)[-1].kind)
                # if it is a border hexagon
                elif self.level.is_border(hexagon):
                    selectable = True
                    painter.setBrush(QtGui.QColor(10, 20, 20))
                    painter.drawPolygon(polygon)

                # highlight hex under cursor
                if selectable:
                    if hexagon == self.hexagon_under_cursor:
                        painter.setBrush(QtGui.QColor(255, 255, 0, 150))
                        painter.drawPolygon(polygon)
        finally:
            painter.end()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = GameWidget()
    window.show()
    app.exec_()


main()

#   Copyright Alexander Baranin 2016

from sfml.graphics import *
from sfml.system import Vector2
import weakref


# 2D hash intended for GUI and overlay mouse lick handling
# works with static Rectangles. References objects weakly.
class Fixed2DHash:
    def __init__(self, global_size, cell_count, origin = Vector2(0.0, 0.0)):
        self._size = global_size
        self._cell_size = (global_size[0] / cell_count[0], 
                           global_size[1] / cell_count[1])
        self._cell_count = cell_count
        self._origin = origin
        self._cells = [None] * (self._cell_count[0] * self._cell_count[1])

    def clampx(self, index):
        return int(max(0, min(index, self._cell_count[0] - 1)))

    def clampy(self, index):
        return int(max(0, min(index, self._cell_count[1] - 1)))

    def register(self, rect, obj):
        x_min = self.clampx((rect.left - self._origin.x) // self._cell_size[0])
        x_max = self.clampx((rect.right - self._origin.x) // self._cell_size[0])
        y_min = self.clampy((rect.top - self._origin.y) // self._cell_size[1])
        y_max = self.clampy((rect.bottom - self._origin.y) // self._cell_size[1])
        indexes = []
        for ix in range(x_min, x_max + 1):
            for iy in range(y_min, y_max + 1):
                index = iy * self._cell_count[0] + ix
                indexes.append(index)
                if self._cells[index] is not None:
                    self._cells[index].add(obj)
                else:
                    new_set = weakref.WeakSet()
                    new_set.add(obj)
                    self._cells[index] = new_set
        return indexes

    def unregister(self, obj, indexes):
        for i in indexes:
            if self._cells[i] is not None:
                try:
                    self._cells[i].remove(obj)
                except KeyError:
                    pass

    def cell(self, point):
        """Get objects in the same cell as the point"""
        x = self.clampx((point[0] - self._origin.x) // self._cell_size[0])
        y = self.clampy((point[1] - self._origin.y) // self._cell_size[1])
        index = y * self._cell_count[0] + x
        cell = self._cells[index]
        if cell is None:
            return None
        else:
            return list(cell)

    def under_rect(self, rect):
        """Get all cells under the rect"""
        x_min = self.clampx((rect.left - self._origin.x) // self._cell_size[0])
        x_max = self.clampx((rect.right - self._origin.x) // self._cell_size[0])
        y_min = self.clampy((rect.top - self._origin.y) // self._cell_size[1])
        y_max = self.clampy((rect.bottom - self._origin.y) // self._cell_size[1])
        cells = []
        for ix in range(x_min, x_max + 1):
            for iy in range(y_min, y_max + 1):
                index = iy * self._cell_count[0] + ix
                cells.append(self._cells[index])
        return cells

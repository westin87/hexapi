import math


class Object2D:
    def __init__(self, x=0, y=0):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __add__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x + other.x,
                    self.y + other.y)
        else:
            x, y = (self.x + other,
                    self.y + other)

        return self.__class__(x, y)
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x - other.x,
                    self.y - other.y)
        else:
            x, y = (self.x - other,
                    self.y - other)

        return self.__class__(x, y)
    __rsub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x * other.x,
                    self.y * other.y)
        else:
            x, y = (self.x * other,
                    self.y * other)

        return self.__class__(x, y)
    __rmul__ = __mul__

    def __pow__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x ** other.x,
                    self.y ** other.y)
        else:
            x, y = (self.x ** other,
                    self.y ** other)

        return self.__class__(x, y)
    __rpow__ = __pow__

    def __truediv__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x / other.x,
                    self.y / other.y)
        else:
            x, y = (self.x / other,
                    self.y / other)

        return self.__class__(x, y)

    def __rtruediv__(self, other):
        if isinstance(other, Object2D):
            x, y = (other.x / self.x,
                    other.y / self.y)
        else:
            x, y = (other / self.x,
                    other / self.y)

        return self.__class__(x, y)

    # Python 2 support:
    __div__ = __truediv__
    __rdiv__ = __rtruediv__

    def __floordiv__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x // other.x,
                    self.y // other.y)
        else:
            x, y = (self.x // other,
                    self.y // other)

        return self.__class__(x, y)

    def __rfloordiv__(self, other):
        if isinstance(other, Object2D):
            x, y = (other.x // self.x,
                    other.y // self.y)
        else:
            x, y = (other // self.x,
                    other // self.y)

        return self.__class__(x, y)

    def __iadd__(self, other):
        if isinstance(other, Object2D):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other
            self.y += other

        return self

    def __idiv__(self, other):
        if isinstance(other, Object2D):
            self.x /= other.x
            self.y /= other.y
        else:
            self.x /= other
            self.y /= other

        return self

    def __imul__(self, other):
        if isinstance(other, Object2D):
            self.x *= other.x
            self.y *= other.y
        else:
            self.x *= other
            self.y *= other

        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Object2D):
            self.x //= other.x
            self.y //= other.y
        else:
            self.x //= other
            self.y //= other

        return self

    def __isub__(self, other):
        if isinstance(other, Object2D):
            self.x -= other.x
            self.y -= other.y
        else:
            self.x -= other
            self.y -= other

        return self

    def __eq__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x == other.x
            y_equal = self.y == other.y
        else:
            x_equal = self.x == other
            y_equal = self.y == other

        return x_equal and y_equal

    def __lt__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x < other.x
            y_equal = self.y < other.y
        else:
            x_equal = self.x < other
            y_equal = self.y < other

        return x_equal and y_equal

    def __le__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x <= other.x
            y_equal = self.y <= other.y
        else:
            x_equal = self.x <= other
            y_equal = self.y <= other

        return x_equal and y_equal

    def __gt__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x > other.x
            y_equal = self.y > other.y
        else:
            x_equal = self.x > other
            y_equal = self.y > other

        return x_equal and y_equal

    def __ge__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x >= other.x
            y_equal = self.y >= other.y
        else:
            x_equal = self.x >= other
            y_equal = self.y >= other

        return x_equal and y_equal

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __len__(self):
        return 3

    def __iter__(self):
        return iter([self.x, self.y])

    @staticmethod
    def dot(first, second):
        if isinstance(first, Object2D) and isinstance(second, Object2D):
            return (first.x * second.x) + (first.y * second.y)
        else:
            raise TypeError("Incorrect types of input: {} vs {}".format(
                type(first), type(second)))


class Vector2D(Object2D):
    def __str__(self):
        return "x: {:.02F}, y: {:.02F}".format(self.x, self.y)

    def __repr__(self):
        return "Vector2D(x={}, y={})".format(self.x, self.y)

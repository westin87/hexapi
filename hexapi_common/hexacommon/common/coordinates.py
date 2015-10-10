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
    __rtruediv__ = __truediv__

    # Python 2 support:
    __div__ = __truediv__
    __rdiv__ = __div__

    def __floordiv__(self, other):
        if isinstance(other, Object2D):
            x, y = (self.x // other.x,
                    self.y // other.y)
        else:
            x, y = (self.x // other,
                    self.y // other)

        return self.__class__(x, y)
    __rfloordiv__ = __floordiv__

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


class Object3D:
    def __init__(self, z=0, y=0, x=0):
        if isinstance(z, tuple):
            self.z = z[0]
            self.y = z[1]
            self.x = z[2]
        else:
            self.z = z
            self.y = y
            self.x = x

    def __add__(self, other):
        if isinstance(other, Object3D):
            x, y, z = (self.x + other.x,
                       self.y + other.y,
                       self.z + other.z)
        else:
            x, y, z = (self.x + other,
                       self.y + other,
                       self.z + other)

        return self.__class__(z, y, x)
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Object3D):
            x, y, z = (self.x - other.x,
                       self.y - other.y,
                       self.z - other.z)
        else:
            x, y, z = (self.x - other,
                       self.y - other,
                       self.z - other)

        return self.__class__(z, y, x)
    __rsub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Object3D):
            x, y, z = (self.x * other.x,
                       self.y * other.y,
                       self.z * other.z)
        else:
            x, y, z = (self.x * other,
                       self.y * other,
                       self.z * other)

        return self.__class__(z, y, x)
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Object3D):
            x, y, z = (self.x / other.x,
                       self.y / other.y,
                       self.z / other.z)
        else:
            x, y, z = (self.x / other,
                       self.y / other,
                       self.z / other)

        return self.__class__(z, y, x)
    __rtruediv__ = __truediv__

    def __floordiv__(self, other):
        if isinstance(other, Object3D):
            x, y, z = (self.x // other.x,
                       self.y // other.y,
                       self.z // other.z)
        else:
            x, y, z = (self.x // other,
                       self.y // other,
                       self.z // other)

        return self.__class__(z, y, x)
    __rfloordiv__ = __floordiv__

    def __iadd__(self, other):
        if isinstance(other, Object3D):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other
            self.y += other
            self.z += other
        return self

    def __idiv__(self, other):
        if isinstance(other, Object3D):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        else:
            self.x /= other
            self.y /= other
            self.z /= other

        return self

    def __imul__(self, other):
        if isinstance(other, Object3D):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            self.x *= other
            self.y *= other
            self.z *= other

        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Object3D):
            self.x //= other.x
            self.y //= other.y
            self.z //= other.z
        else:
            self.x //= other
            self.y //= other
            self.z //= other

        return self

    def __isub__(self, other):
        if isinstance(other, Object3D):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        else:
            self.x -= other
            self.y -= other
            self.z -= other

        return self

    def __eq__(self, other):
        if isinstance(other, Object3D):
            x_equal = self.x == other.x
            y_equal = self.y == other.y
            z_equal = self.z == other.z
        else:
            x_equal = self.x == other
            y_equal = self.y == other
            z_equal = self.z == other

        return x_equal and y_equal and z_equal

    def __lt__(self, other):
        if isinstance(other, Object3D):
            x_equal = self.x < other.x
            y_equal = self.y < other.y
            z_equal = self.z < other.z
        else:
            x_equal = self.x < other
            y_equal = self.y < other
            z_equal = self.z < other

        return x_equal and y_equal and z_equal

    def __le__(self, other):
        if isinstance(other, Object3D):
            x_equal = self.x <= other.x
            y_equal = self.y <= other.y
            z_equal = self.z <= other.z
        else:
            x_equal = self.x <= other
            y_equal = self.y <= other
            z_equal = self.z <= other

        return x_equal and y_equal and z_equal

    def __gt__(self, other):
        if isinstance(other, Object3D):
            x_equal = self.x > other.x
            y_equal = self.y > other.y
            z_equal = self.z > other.z
        else:
            x_equal = self.x > other
            y_equal = self.y > other
            z_equal = self.z > other

        return x_equal and y_equal and z_equal

    def __ge__(self, other):
        if isinstance(other, Object2D):
            x_equal = self.x >= other.x
            y_equal = self.y >= other.y
            z_equal = self.z >= other.z
        else:
            x_equal = self.x >= other
            y_equal = self.y >= other
            z_equal = self.z >= other

        return x_equal and y_equal and z_equal

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __len__(self):
        return 3

    def __iter__(self):
        return iter([self.z, self.y, self.x])


class Point2D(Object2D):
    def __str__(self):
        return "Point at x: {}, y: {}".format(self.x, self.y)

    def __repr__(self):
        return "Point2D(x={}, y={})".format(self.x, self.y)


class Point3D(Object3D):
    def __str__(self):
        return "Point at z: {}, y: {} and x: {}".format(self.z, self.y, self.x)

    def __repr__(self):
        return "Point3D(z={}, y={}, x={})".format(self.z, self.y, self.x)


class Value2D(Object2D):
    def __str__(self):
        return "Value x: {}, y: {}".format(self.x, self.y)


class Value3D(Object3D):
    def __str__(self):
        return "Value z: {}, y: {} and x: {}".format(self.z, self.y, self.x)

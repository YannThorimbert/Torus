from thorpy.elements.element import Element
from thorpy.painting.painters.imageframe import ImageFrame
from thorpy.painting.painters.basicframe import BasicFrame
from thorpy.miscgui import style, functions


class Image(Element):
    """Image element."""

    @staticmethod
    def make(path=None, color=None, colorkey=None):
        """Image element.
        <path>: the path to the image.
        <color>: if path is None, use this color instead of image.
        """
        print("type2",path)
        img = Image(path, color, colorkey=colorkey)
        img.finish()
        return img

    def __init__(self, path=None, color=None, elements=None, normal_params=None,
                    colorkey=None):
        """Image element.
        <path>: the path to the image.
        <color>: if path is None, use this color instead of image.
        """
        super(Image, self).__init__("", elements, normal_params)
        if path:
            painter = ImageFrame(path, mode=None, colorkey=colorkey)
        else:
            if color:
                painter = BasicFrame(style.SIZE, color)
            else:
                raise Exception("You must specify either a path or a color")
        self.set_painter(painter)

    def set_alpha(self, alpha):
        img = self.get_image()
        img.set_alpha(alpha)
        self.set_image(img)

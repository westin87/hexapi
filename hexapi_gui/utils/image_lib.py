#!/usr/bin/env python3

from PIL import Image


def merge_images(image_list):
    """ Merges a list of four images, all images has to be of equal size.
    """
    if len(image_list) != 4:
        raise ValueError("Incorrect number of images")
    image_sizes = [image.size for image in image_list]
    if len(set(image_sizes)) != 1:
        raise ValueError("Images must be of equal size.")

    image_size = image_sizes[0]
    new_image = Image.new("RGB", tuple([2*element for element in image_size]))

    for i, image in enumerate(image_list):
        if i == 0:
            box = (0, 0, image_size[0], image_size[1])
        elif i == 1:
            box = (image_size[0], 0, 2*image_size[0], image_size[1])
        elif i == 2:
            box = (0, image_size[1], image_size[0], 2*image_size[1])
        else:
            box = (image_size[0], image_size[1],
                   2*image_size[0], 2*image_size[1])

        new_image.paste(image, box)
    return new_image

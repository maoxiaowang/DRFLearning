# import itertools
# import math
import os
from io import BytesIO

# import imageio
from PIL import Image, ImageFont, ImageDraw
from django.core.files.uploadedfile import InMemoryUploadedFile

from common import BASE_DIR
# from scipy.sparse import dok_matrix
# from scipy.sparse.csgraph import dijkstra
# from matplotlib import pyplot as plt
from common.utils.text import get_filename_extension as fe

__all__ = [
    'resize_image',
    'ImageGenerator',
    # 'ShortestPathAlgorithm'
]


def resize_image(image, width=200, height=200) -> InMemoryUploadedFile:
    """
    Process InMemoryUploadedFile
    return size: 200x200
    """

    img = Image.open(image)
    assert img.format.upper() in ('PNG', 'JPG', 'JPEG')
    img_format = img.format

    mode = img.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            alpha = img.split()[3]
            bgmask = alpha.point(lambda x: 255 - x)
            img = img.convert('RGB')
            # paste(color, box, mask)
            img.paste((255, 255, 255), None, bgmask)
        else:
            img = img.convert('RGB')

    # width, height = img.size
    img_width, img_height = img.size
    # 调整比例
    img_wh_ratio = img_width / img_height
    target_wh_ratio = width / height

    # box：(left, upper, right, lower)
    if target_wh_ratio > img_wh_ratio:
        # 原图宽度不变
        target_height = img_width / target_wh_ratio  # 目标高度（小于原高）
        delta = (img_height - target_height) / 2
        box = (0, delta, img_width, delta + target_height)
        region = img.crop(box)
    elif target_wh_ratio < img_wh_ratio:
        target_width = img_width / target_wh_ratio
        delta = (img_width - target_width) / 2
        box = (delta, 0, delta + target_width, img_height)
        region = img.crop(box)
    else:
        # 比例相同，原图
        region = img

    a = region.resize((width, height), Image.ANTIALIAS)  # anti-aliasing

    img_io = BytesIO()
    a.save(img_io, img_format)

    try:
        content_type = image.content_type
    except AttributeError:
        suffix = fe(image.name).lstrip('.')
        content_type = f'image/{suffix}'

    img_file = InMemoryUploadedFile(
        file=img_io,
        field_name=None,
        name=image.name,
        content_type=content_type,
        size=img_io.tell(),
        charset=None
    )
    return img_file


class ImageGenerator(object):
    class Colors:
        white = '#FFFFFF'
        black = '#000000'
        grey = '#AEAEAE'
        dark = '#2C353E'

    images_dir = os.path.join(BASE_DIR, 'static/images')
    fonts_dir = os.path.join(BASE_DIR, 'static/fonts')

    def get_font(self, font_name, size=24):
        return ImageFont.truetype(os.path.join(self.fonts_dir, font_name), size=size)

    def get_image(self, image_name, convert='RGBA', **kwargs):
        return Image.open(os.path.join(self.images_dir, image_name), **kwargs).convert(convert)

    @staticmethod
    def get_draw(image):
        return ImageDraw.Draw(image)

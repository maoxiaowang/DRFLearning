from pathlib import Path


class PathMixin:
    _BASE_DIR = 'static/default'

    def __getattribute__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        value = object.__getattribute__(self, item)
        return str(Path(PathMixin._BASE_DIR).joinpath(value))

    @property
    def _all_files(self):
        return [getattr(self, item) for item in self.__dir__() if not item.startswith('_')]


class DefaultFilePath(PathMixin):
    """
    修改完成后，运行
    python manage.py init_default_images
    上传图片
    """
    default_image = 'default.jpg'


DEFAULT_FILES = DefaultFilePath()

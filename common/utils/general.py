class ClsHelper(object):

    def _list_properties(self, exclude_private=True, include_annotations=False):
        """
        去掉所有内置（非对象）属性，获取用户自定的属性和值

        exclude_private：去掉私有属性
        """
        result = dict()
        for key, value in self.__class__.__dict__.items():
            if not callable(value):
                satisfied = not key.startswith('_') if exclude_private else not key.startswith('__')
                if satisfied:
                    result[key] = value
        if include_annotations:
            for key, value in self.__annotations__.items():
                result[key] = getattr(self, key)
        return result

    def _list_values(self, exclude_private=True):
        d = self._list_properties(exclude_private=exclude_private)
        values = list()
        for k, v in d.items():
            values.append(v)
        return values

    def _list_keys(self, exclude_private=True):
        d = self._list_properties(exclude_private=exclude_private)
        values = list()
        for k, v in d.items():
            values.append(k)
        return values

    def _list_methods(self, exclude_private=True):
        result = dict()
        for key, value in self.__class__.__dict__.items():
            if callable(value):
                satisfied = not key.startswith('_') if exclude_private else not key.startswith('__')
                if satisfied:
                    result[key] = value
        return result


def enum_to_choices(enum_class, split_name=True, reverse=False):
    if reverse:
        return tuple(
            (item[0], item[1].value) for item in enum_class.__members__.items()
        )
    return tuple(
        (item[1].value, ' '.join(item[0].split('_')) if split_name else item[0])
        for item in enum_class.__members__.items()
    )


class EnumMixin:
    @classmethod
    def all_values(cls):
        return [item.value for item in getattr(cls, '__members__').values()]

    @classmethod
    def all_keys(cls):
        return [item for item in getattr(cls, '__members__').keys()]

    @classmethod
    def all_items(cls):
        return dict(zip(cls.all_keys(), cls.all_values()))


BLANK = ' '
PERIOD = '.'
STRIKE = '-'
EMPTY = ''


class PrintHandler(object):
    """
    e.g.
    ph = PrintHandler()
    ph.print('Started to write ... ')
    time.sleep(1)
    ph.print('phase 2 ... ', add=True, end=False)
    time.sleep(1)
    ph.print('[OK]', add=True)

    ph.print('Started to sing ... ')
    time.sleep(1)
    ph.print('[OK]', add=True)

    > Started to write ...
    > Started to write ... phase 2 ...
    > Started to write ... phase 2 ... [OK]
    > Started to sing ...
    > Started to sing ... [OK]
    """
    print_def = None

    def __init__(self, print_def=None, end_arg_name=None):
        self._init_str = None
        self._total_len = 0
        self._post_parts = list()
        self.print_def = print_def or print
        self.end_arg_name = end_arg_name or 'end'

    @staticmethod
    def padding(message: str, max_length=None, filling=PERIOD, start=BLANK, end=BLANK,
                layer: int = None, layer_icon=STRIKE, layer_width=2) -> str:
        if not isinstance(message, str):
            message = str(message)
        if not filling:
            filling = EMPTY
        # add layer
        if layer:
            if layer_icon:
                if not isinstance(layer_icon, str):
                    layer_icon = str(layer_icon)
                layer_icon += BLANK
            else:
                layer_icon = EMPTY
            assert isinstance(layer, int) and layer > 0, 'The layer must be a positive integer.'
            assert isinstance(layer_width, int) and layer_width > 0
            layer_blanks = BLANK * (layer * layer_width)
            message = layer_blanks + layer_icon + message

        max_len = max_length or 100
        message_len = len(message)
        start_len = len(start)
        end_len = len(end)
        # 缩略
        eps_len = 3
        if message_len > max_len:
            max_len -= (start_len + end_len + eps_len)
            message = message[:max_len] + start + filling * eps_len + end
        else:
            diff_len = eps_len - (max_len - message_len)
            max_len -= (start_len + end_len)
            message = message[:(message_len - diff_len)]
            message_len = len(message) - (start_len + end_len)
            message = message + start + filling * (max_len - message_len) + end
        return message

    def print(self, string, add=False, end=None, end_arg_name=None, str_len=None, **kwargs):
        end_arg_name = end_arg_name or self.end_arg_name
        str_len = str_len or len(string)
        self._total_len += str_len
        if add:
            self._post_parts.append(string)
            # p_string = self._init_str + EMPTY.join(self._post_parts)
            if end is None:
                # add模式下，end默认为True
                end = True
            if not end:
                end = f'\r\033[{self._total_len}C'
            else:
                end = '\r\n'
                self._clean()
            kwargs.update({end_arg_name: end})
            self.print_def.__call__(string, **kwargs)
        else:
            if end is None:
                end = False
            if not end:
                self._init_str = string
                kwargs.update({end_arg_name: f'\r\033[{str_len}C'})
            self.print_def(string, **kwargs)

    def _clean(self):
        self._init_str = None
        self._total_len = 0
        self._post_parts = list()

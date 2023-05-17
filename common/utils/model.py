import os
import time
import typing
from pathlib import Path

from django.apps import apps
from django.db.models import Model, QuerySet

from common.utils.text import obj2iter


def trans_obj_to_pk(obj: typing.Union[int, Model], model_cls):
    if isinstance(model_cls, str):
        assert len(model_cls.split('.')) == 2, 'Model class string must be like "app_label.model_class".'
        model_cls = apps.get_model(model_cls)
    assert isinstance(obj, (int, model_cls))
    if isinstance(obj, int):
        return obj
    return getattr(obj, 'pk')


def trans_objs_to_pks(objs: typing.Union[int, Model, list, QuerySet], model_cls, exclude_nonexists=False) -> list:
    """
    将instance/pk/列表（包含instance/pk）转为pk列表
    """
    # get model class
    if isinstance(model_cls, str):
        assert len(model_cls.split('.')) == 2, 'Model class string must be like "app_label.model_class".'
        model_cls = apps.get_model(model_cls)

    # queryset
    if isinstance(objs, QuerySet):
        return [item.pk for item in objs]

    # other types
    assert isinstance(objs, (int, model_cls, list))
    # to be iterable
    if isinstance(objs, (int, model_cls)):
        objs = obj2iter(objs)

    pk_list = list()
    for item in objs:
        if isinstance(item, int):
            pk_list.append(item)
        elif isinstance(item, model_cls):
            pk_list.append(getattr(item, 'pk'))
        else:
            raise ValueError('Unknown object %s in list' % type(item))

    if exclude_nonexists:
        return list(model_cls.objects.filter(pk__in=pk_list).values_list('pk', flat=True))

    return pk_list


def auto_id_upload_to(dir_path, instance, filename, replace=True):
    time_string = str(time.time())
    extension = Path(filename).suffix
    model_name = getattr(instance, '_meta').model_name
    if replace and getattr(instance, 'id'):
        filename = f'{model_name}_{instance.id}{extension}'
    else:
        filename = f'{model_name}_{time_string}{extension}'
    return os.path.join(dir_path, filename)

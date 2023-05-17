"""
Usage:
        pt = PeriodicTaskHandler()
        pt.make_crontab_schedule(
            month_of_year=match_time.month, day_of_month=match_time.day,
            hour=match_time.hour, minute=match_time.minute
        )
        pt.create_task(
            unique_name, 'TASK.PATH',
            one_off=True, expire_seconds=3600 * 10, task_args=[match_id]
        )

"""

import json
from datetime import datetime

from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask


CURRENT_TIMEZONE = timezone.get_current_timezone()
SCHEDULE_TYPES = {
    'interval': IntervalSchedule,
    'crontab': CrontabSchedule
}


class PeriodicTaskHandler(object):
    schedule = None
    task = None
    task_model = PeriodicTask

    @staticmethod
    def _validate_task_name(task_name):
        assert len(task_name.split('.')) > 1, 'Valid task name is required, example "proj.tasks.import_contacts"'

    @property
    def _schedule_args(self) -> dict:
        assert isinstance(self.schedule, tuple(SCHEDULE_TYPES.values())), 'A schedule should be created first'
        arg = dict()
        for name, cls in SCHEDULE_TYPES.items():
            if isinstance(self.schedule, cls):
                arg.update({name: self.schedule})
        if not arg:
            raise ValueError('Unsupported schedule type: %s' % type(self.schedule))
        return arg

    def get_task(self, unique_name):
        return self.task or self.task_model.objects.filter(name=unique_name).first()

    def disable_task(self, unique_name):
        task = self.get_task(unique_name)
        print('disable_task: %s' % task)
        if task and task.enabled:
            task.enabled = False
            task.save()

    def create_task(self, unique_name: str,
                    task_name: str,
                    start_time: datetime = None,
                    expire_seconds: int = None,
                    expires: datetime = None,
                    one_off: bool = False,
                    priority: int = None,
                    task_args='[]', task_kwargs='{}', **kwargs):
        """
        expires_seconds: 多少秒之后执行任务
        expires: 之后哪个时间点执行任务
        """
        self._validate_task_name(task_name)
        if isinstance(task_args, list):
            task_args = json.dumps(task_args)
        if isinstance(task_kwargs, dict):
            task_kwargs = json.dumps(task_kwargs)
        defaults = {
            'task': task_name,
            'start_time': start_time,
            'expires': expires,
            'expire_seconds': expire_seconds,
            'one_off': one_off,
            'priority': priority,
            'args': task_args,
            'kwargs': task_kwargs
        }
        defaults.update(self._schedule_args)
        defaults.update(**kwargs)
        self.task = self.task_model.objects.update_or_create(defaults, name=unique_name)

    def make_interval_schedule(self, every, period: str = IntervalSchedule.SECONDS):
        """
        every: 每几个period执行一次
        period: days, hours, minutes, seconds, microseconds
        """
        defaults = {'every': every, 'period': period}
        self.schedule, _ = IntervalSchedule.objects.get_or_create(defaults, **defaults)

    def make_crontab_schedule(self, month_of_year='*', day_of_month='*', day_of_week='*', hour='*', minute='*',
                              tz=CURRENT_TIMEZONE):
        defaults = {
            'minute': minute,
            'hour': hour,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month_of_year': month_of_year,
            'timezone': tz
        }
        self.schedule, _ = CrontabSchedule.objects.get_or_create(defaults, **defaults)

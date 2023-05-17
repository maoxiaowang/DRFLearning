import sys

from django.core.management.base import BaseCommand, OutputWrapper

from common.filters.backends import QuerySetFilter
from common.logging import loggers
from common.utils.text import query_str2dict


class QuerySetCommand(BaseCommand):
    filter_backend = QuerySetFilter(strict=True)

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-by', type=str, default=None,
            help='Queryset order argument'
        )
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Queryset sliced by, a positive integer requires.'
        )
        parser.add_argument(
            '--filter', type=query_str2dict, default=None,
            help='Queryset filter queries. see document for help.'
        )
        parser.add_argument(
            '--exclude', type=query_str2dict, default=None,
            help='Queryset exclude queries, similar to filter.'
        )

    def handle(self, *args, **options):
        if options.get('filter'):
            self.filter_backend.filter_kwargs.update(**options['filter'])
        if options.get('exclude'):
            self.filter_backend.exclude_kwargs.update(**options['exclude'])


class GracefulCommand(BaseCommand):
    graceful_message = 'Bye'

    def __init__(self, stdout=None, **kwargs):
        self.stdout_line = OutputWrapper(stdout or sys.stdout, ending='')
        super(GracefulCommand, self).__init__(stdout=stdout, **kwargs)

    def graceful_handle(self, *args, **options):
        raise NotImplementedError

    def handle(self, *args, **options):
        try:
            self.graceful_handle(*args, **options)
        except KeyboardInterrupt:
            self.stdout.write('\n' + self.graceful_message)


class FakeCommand(object):
    class Stdout:
        def __init__(self, logger):
            self.logger = logger

        def write(self, message):
            if self.logger:
                self.logger.info(message)

    class Style:
        def __getattribute__(self, item):
            return type('Bar', (object,), {'__call__': lambda s, x: x})()

    def __init__(self, logger=None):
        self.stdout = self.Stdout(logger=logger or loggers.django)
        self.stdout_line = self.Stdout(logger=logger or loggers.django)
        self.style = self.Style()

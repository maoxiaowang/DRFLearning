class SignalAction(object):
    is_created = False
    is_updated = False
    is_deleted = False

    def __init__(self, kwargs):
        self.kwargs = kwargs
        if 'created' in self.kwargs:
            if self.kwargs['created']:
                self.is_created = True
            else:
                self.is_updated = True
        else:
            self.is_deleted = True

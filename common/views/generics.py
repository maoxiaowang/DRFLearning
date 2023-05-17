from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView as _APIView

from common.permissions import login_required
from common.views import mixins


class APIView(_APIView):
    _ignore_model_permissions = True


class CreateAPIView(mixins.CreateModelMixin,
                    GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    @login_required
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    @login_required
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    @login_required
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @login_required
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @login_required
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @login_required
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @login_required
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @login_required
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @login_required
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @login_required
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @login_required
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ListAddRemoveAPIView(mixins.M2MListModelMixin,
                           mixins.M2MAddModelMixin,
                           mixins.M2MRemoveModelMixin,
                           GenericAPIView):
    """
    列出反查询集（多对多），或从反查询集中添加/删除条目
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @login_required
    def post(self, request, *args, **kwargs):
        return self.add(request, *args, **kwargs)

    @login_required
    def delete(self, request, *args, **kwargs):
        return self.remove(request, *args, **kwargs)


class SetListAPIView(mixins.SetListModelMixin,
                     GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

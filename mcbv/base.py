from __future__ import unicode_literals

import logging
from functools import update_wrapper

from django import http
from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.utils.decorators import classonlymethod
from django.utils import six


logger = logging.getLogger('django.request')'')

class ContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """
    def add_context(self):
        """Convenience method; may be overridden to add context by returning a dictionary."""
        return {}

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        kwargs.update(self.add_context())
        return kwargs

class TemplateResponseMixin(object):
    """
    A mixin that can be used to render a template.
    """
    template_name = None
    response_class = TemplateResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        return self.response_class(
           request = self.request,
            template = self.get_template_names(),
           context = context,
            **response_kwargs
        )

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
               "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]

    def get(self, request, *args, **kwargs):
        from detail import DetailView
        from edit import FormView, FormSetView, ModelFormSetView, CreateView, UpdateView
        from list import ListView

        args    = [request] + list(args)
        context = dict()
        update  = context.update

        if isinstance(self, DetailView)                      : update( self.detail_get(*args, **kwargs) )
        if isinstance(self, FormView)                        : update( self.form_get(*args, **kwargs) )
        if isinstance(self, (FormSetView, ModelFormSetView)) : update( self.formset_get(*args, **kwargs) )
        if isinstance(self, CreateView)                      : update( self.create_get(*args, **kwargs) )
        if isinstance(self, UpdateView)                      : update( self.update_get(*args, **kwargs) )
        if isinstance(self, ListView)                        : update( self.list_get(*args, **kwargs) )

        update(self.get_context_data(**kwargs))
        return self.render_to_response(context)

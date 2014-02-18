from base import ContextMixin, TemplateResponseMixin

class MultipleObjectMixin(ContextMixin):
    """
    A mixin for views manipulating multiple objects.
    """
    allow_empty              = True
    list_queryset            = None
    list_model               = None
    paginate_by              = None
    list_context_object_name = None
    paginate_orphans         = 0
    paginator_class          = Paginator
    page_kwarg               = 'page'

    def get_list_queryset(self):
        """
        Get the list of items for this view. This must be an iterable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.list_queryset is not None:
            queryset = self.list_queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.list_model is not None:
            queryset = self.list_model._default_manager.all()
        else:
            raise ImproperlyConfigured("'%s' must define 'list_queryset' or 'list_model'"
                                       % self.__class__.__name__)
        return queryset

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                               'page_number': page_number,
                                'message': str(e)
            })

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_paginator(self, queryset, per_page, orphans=0,
                     allow_empty_first_page=True, **kwargs):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(
           queryset, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page, **kwargs)

    def get_paginate_orphans(self):
        """
        Returns the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.paginate_orphans

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_list_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.list_context_object_name:
            return self.list_context_object_name
        elif hasattr(object_list, 'model'):
            return '%s_list' % object_list.model._meta.object_name.lower()
        else:
            return None

    def get_list_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        if "object_list" not in kwargs:
            kwargs["object_list"] = self.get_queryset()

        queryset            = kwargs.pop('object_list')
        page_size           = self.get_paginate_by(queryset)
        context_object_name = self.get_list_context_object_name(queryset)
        page                = None

        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
               'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': page.object_list
            }
        else:
            context = {
               'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }

        if context_object_name is not None:
            context[context_object_name] = context["object_list"]
        context.update(kwargs)
        return context

class ListView(MultipleObjectTemplateResponseMixin, BaseListView):
    pass

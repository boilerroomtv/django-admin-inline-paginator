from django.contrib.admin import TabularInline
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator


class InlineChangeList(object):
    """
        Used by template to construct the paginator
    """
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__['get_query_string']

    def __init__(self, request, page_num, paginator):
        self.show_all = 'all' in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class PaginationFormSetBase(object):
    queryset = None
    request = None
    per_page = 20
    pagination_key = 'page'

    def get_page_num(self) -> int:
        page = self.request.GET.get(self.pagination_key, '1')
        if page.isnumeric() and page > '0':
            return int(page)

        return 1

    def get_page(self, paginator: Paginator, page: int):
        if page <= paginator.num_pages:
            return paginator.page(page)

        return paginator.page(1)

    def mount_paginator(self, page_num: int = None):
        page_num = self.get_page_num() if not page_num else page_num
        self.paginator = Paginator(self.queryset, self.per_page)
        self.page = self.get_page(self.paginator, page_num)
        self.cl = InlineChangeList(self.request, page_num, self.paginator)

    def mount_queryset(self):
        if self.cl.show_all:
            self._queryset = self.queryset

        self._queryset = self.page.object_list

    def __init__(self, *args, **kwargs):
        super(PaginationFormSetBase, self).__init__(*args, **kwargs)
        self.mount_paginator()
        self.mount_queryset()


class TabularInlinePaginated(TabularInline):
    pagination_key = 'page'
    template = 'admin/tabular_paginated.html'
    per_page = 20
    extra = 0
    can_delete = False
    redirect_suffix = ''

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        class PaginationFormSet(PaginationFormSetBase, formset_class):
            pagination_key = self.pagination_key
            redirect_suffix = self.redirect_suffix

        PaginationFormSet.request = request
        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet

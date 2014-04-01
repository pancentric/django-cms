# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap


def from_iterable(iterables):
    """
    Backport of itertools.chain.from_iterable
    """
    for it in iterables:
        for element in it:
            yield element


class CMSSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        """Django-cms has a wee bug in that pages that are just placeholders
        for a redirect are included in the sitemap.xml - this is the cure.
        (Unfortunately there's no point in wrapping up this code and sending in
        a pull request, as it's been substantially rewritten - but still has
        the same bug!)
        """
        from cms.utils.page_resolver import get_page_queryset
        page_queryset = get_page_queryset(None)
        all_pages = page_queryset.published().filter(login_required=False)
        return [page
                for page in all_pages
                if not page.get_redirect()]

    def lastmod(self, page):
        modification_dates = [page.changed_date, page.publication_date]
        plugins_for_placeholder = lambda placeholder: placeholder.get_plugins()
        plugins = from_iterable(map(plugins_for_placeholder, page.placeholders.all()))
        plugin_modification_dates = map(lambda plugin: plugin.changed_date, plugins)
        modification_dates.extend(plugin_modification_dates)
        return max(modification_dates)

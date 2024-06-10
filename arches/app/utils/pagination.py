from django.core.paginator import Paginator


def get_paginator(request, results, total_count, page, count_per_page):
    paginator = Paginator(list(range(total_count)), count_per_page)
    pages = [page]
    if paginator.num_pages > 1:
        before = list(range(1, page))
        after = list(range(page + 1, paginator.num_pages + 1))
        default_ct = 2
        ct_before = (
            default_ct if len(after) > default_ct else default_ct * 2 - len(after)
        )
        ct_after = (
            default_ct if len(before) > default_ct else default_ct * 2 - len(before)
        )
        if len(before) > ct_before:
            before = [1, None] + before[-1 * (ct_before - 1) :]
        if len(after) > ct_after:
            after = after[0 : ct_after - 1] + [None, paginator.num_pages]
        pages = before + pages + after
    return paginator, pages

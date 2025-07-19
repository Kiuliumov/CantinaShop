from django import template

register = template.Library()


@register.simple_tag
def page_range(paginator, current_page, radius=2):
    total_pages = paginator.num_pages
    current = current_page
    start = max(current - radius, 1)
    end = min(current + radius, total_pages)

    if start == 1:
        end = min(start + 2 * radius, total_pages)
    if end == total_pages:
        start = max(end - 2 * radius, 1)

    return range(start, end + 1)

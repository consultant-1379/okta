from django import template
from ..models import Post


register=template.Library()


@register.simple_tag
def total_posts():
    posts=Post.objects.filter(status='published')
    return posts.count()
import bleach
from markdown import markdown

def get_html(s:str):
    allow_tags = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
    'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img'
    ]
    return bleach.linkify(
        bleach.clean(
            markdown(s, output_form='html'),
            tags=allow_tags,
            strip=True,
            attributes={
                '*': ['class'],
                'a': ['href', 'rel'],
                'img': ['src', 'alt'],  #支持<img src …>标签和属性
            }))

#!/usr/bin/env python3

from greshunkel.build import main, POSTS_DIR, WIKI_DIR
from greshunkel.context import BASE_CONTEXT, build_blog_context

if __name__ == '__main__':
    context = build_blog_context(BASE_CONTEXT, POSTS_DIR, 'posts/', 'POSTS')
    context = build_blog_context(BASE_CONTEXT, WIKI_DIR, 'wiki/', 'WIKI_POSTS')
    main(context)

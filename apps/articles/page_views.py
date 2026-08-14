# Django modules
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def article_list_page(request):
    '''Frontend page for listing all articles with search/filter.'''
    return render(request, 'articles/article_list.html')

@login_required
def article_create_page(request):
    '''Frontend page for creating a new article.'''
    return render(request, 'articles/article_form.html', {'is_edit': False})

@login_required
def article_edit_page(request, slug):
    '''Frontend page for editing an existing article.'''
    return render(request, 'articles/article_form.html', {'is_edit': True, 'slug': slug})

def article_test_page(request, slug):
    '''Frontend for testing the article API.'''
    context = {
        'slug': slug,
        'current_user': request.user.username if request.user.is_authenticated else ''
    }
    return render(request, 'articles/article_test.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CopingTool
from .seed_data import DEFAULT_COPING_TOOLS

def ensure_seed_tools():
    """Seeds default coping exercises if database is empty."""
    for tool_data in DEFAULT_COPING_TOOLS:
        CopingTool.objects.get_or_create(
            slug=tool_data['slug'],
            defaults=tool_data
        )

def coping_list_view(request):
    ensure_seed_tools()
    tools = CopingTool.objects.filter(is_active=True).order_by('order')
    category_filter = request.GET.get('category')
    if category_filter:
        tools = tools.filter(category=category_filter)

    categories = CopingTool.CATEGORY_CHOICES

    return render(request, 'coping/list.html', {
        'tools': tools,
        'categories': categories,
        'current_category': category_filter,
    })


def coping_detail_view(request, slug):
    ensure_seed_tools()
    tool = get_object_or_404(CopingTool, slug=slug, is_active=True)

    return render(request, 'coping/detail.html', {
        'tool': tool,
        'steps_json': tool.steps,
    })

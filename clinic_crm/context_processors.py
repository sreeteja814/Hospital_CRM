from branches.models import Branch


def branch_list(request):
    if request.user.is_authenticated:
        return {'all_branches': Branch.objects.filter(is_active=True)}
    return {}

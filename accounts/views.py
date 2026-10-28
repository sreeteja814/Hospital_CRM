from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .permissions import role_required
from .models import User
from .forms import StaffCreateForm, StaffUpdateForm, StaffSetPasswordForm


@role_required(User.Role.ADMIN)
def staff_list(request):
    staff = User.objects.all().select_related('branch').order_by('username')
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@role_required(User.Role.ADMIN)
def staff_create(request):
    if request.method == 'POST':
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff account created.')
            return redirect('accounts:staff_list')
    else:
        form = StaffCreateForm()
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Add Staff'})


@role_required(User.Role.ADMIN)
def staff_update(request, pk):
    staff_member = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffUpdateForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff account updated.')
            return redirect('accounts:staff_list')
    else:
        form = StaffUpdateForm(instance=staff_member)
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': f'Edit Staff - {staff_member.username}'})


@role_required(User.Role.ADMIN)
def staff_set_password(request, pk):
    staff_member = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffSetPasswordForm(request.POST)
        if form.is_valid():
            staff_member.set_password(form.cleaned_data['new_password1'])
            staff_member.save()
            messages.success(request, f"Password updated for {staff_member.username}.")
            return redirect('accounts:staff_list')
    else:
        form = StaffSetPasswordForm()
    return render(request, 'accounts/staff_password_form.html', {'form': form, 'staff_member': staff_member})

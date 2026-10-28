from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'phone', 'opening_time', 'closing_time', 'is_active')
    search_fields = ('code', 'name', 'city')
    list_filter = ('is_active', 'city')

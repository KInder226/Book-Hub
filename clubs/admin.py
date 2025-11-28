from django.contrib import admin
from .models import Club, ClubMembership, ClubInvitation


class ClubMembershipInline(admin.TabularInline):
    model = ClubMembership
    extra = 1


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_private', 'current_book', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ()
    readonly_fields = ('invitation_code', 'created_at', 'updated_at')
    inlines = [ClubMembershipInline]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('club', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('club__name', 'user__username')
    readonly_fields = ('joined_at',)


@admin.register(ClubInvitation)
class ClubInvitationAdmin(admin.ModelAdmin):
    list_display = ('club', 'email', 'invited_by', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('club__name', 'email', 'invited_by__username')
    readonly_fields = ('created_at', 'accepted_at')


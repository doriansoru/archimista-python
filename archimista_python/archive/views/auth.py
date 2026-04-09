"""Authentication views: login, logout, forced password change."""

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from archimista_python.archive.models import UserProfile


class ArchimistaLoginView(LoginView):
    """Custom login view with Italian labels."""
    template_name = 'archive/login.html'

    def get_success_url(self):
        """Redirect to password change if must_change_password is True."""
        user = self.request.user
        if hasattr(user, 'archive_profile') and user.archive_profile.must_change_password:
            return reverse_lazy('archive:password_change')
        return reverse_lazy('archive:fond_list')


def archimista_logout(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'Disconnesso con successo.')
    return redirect('archive:login')


@login_required
def password_change_view(request):
    """Password change view — forces change if must_change_password is True."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    must_change = profile.must_change_password

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Update session hash so user stays logged in after password change
            update_session_auth_hash(request, user)
            # Remove forced password flag
            profile.must_change_password = False
            profile.save()
            if must_change:
                messages.success(request, 'Password cambiata con successo. Ora puoi utilizzare il sistema.')
            else:
                messages.success(request, 'Password cambiata con successo.')
            return redirect('archive:fond_list')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'archive/password_change.html', {
        'form': form,
        'must_change': must_change,
    })

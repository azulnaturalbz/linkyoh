from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from .email_utils import send_password_reset_confirmation_email

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    Custom view that extends Django's PasswordResetCompleteView to send a confirmation email.
    """
    def get(self, request, *args, **kwargs):
        # Get the user from the session if available
        user_id = request.session.get('password_reset_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Send confirmation email
                send_password_reset_confirmation_email(user, request)
                # Remove the user ID from the session
                del request.session['password_reset_user_id']
            except User.DoesNotExist:
                pass  # User not found, continue without sending email
        
        # Call the parent class's get method to render the template
        return super().get(request, *args, **kwargs)

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Custom view that extends Django's PasswordResetConfirmView to store the user ID in the session.
    """
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        # Store the user ID in the session for the complete view to use
        if self.user:
            self.request.session['password_reset_user_id'] = self.user.id
        
        # Call the parent class's form_valid method to reset the password
        return super().form_valid(form)
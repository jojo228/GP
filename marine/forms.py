from django import forms
from django.contrib.auth import authenticate


# --------------------------------- Authentication form ------------------------------------------------------#
class AuthenticationFormWithContact(forms.Form):
    contact = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        contact = self.cleaned_data.get("contact")
        password = self.cleaned_data.get("password")

        if contact and password:
            self.user_cache = authenticate(
                self.request, contact=contact, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Contact ou mot de passe invalide")
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.
        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError("inactive user")

    def get_user(self):
        return self.user_cache

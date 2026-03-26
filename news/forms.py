# news/forms.py
"""
Forms for the news app.

This module defines the forms used for:

*   User registration (:class:`RegistrationForm`).
*   Article creation and updates (:class:`ArticleForm`).
*   Newsletter creation and updates (:class:`NewsletterForm`).
*   Publisher creation (:class:`PublisherForm`).
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Newsletter, Publisher


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user with a specific role.

    This form extends the default UserCreationForm to include email and role fields.
    It also applies Bootstrap classes to form fields for styling.
    """

    class Meta(UserCreationForm.Meta):
        """
        Meta options for the RegistrationForm.

        Specifies the model (`CustomUser`) and the fields to be displayed.
        """
        model = CustomUser
        # UserCreationForm automatically handles the password fields.
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.

        Sets the email field as required and applies CSS classes to widgets.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

        # Automatically apply Bootstrap classes to all fields for clean UI styling.
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class ArticleForm(forms.ModelForm):
    """
    Form for Journalists to draft new articles.

    This form allows creating an Article instance with a title and content.
    The author and publisher are handled in the view.
    """

    class Meta:
        """
        Meta options for the ArticleForm.

        Specifies the model and fields, and customizes widgets for a better UI.
        """
        model = Article
        # We only need title, content, and publisher.
        # Author and is_approved are handled securely in the view logic.
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter article title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Write your article here...",
                }
            ),
            "publisher": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class NewsletterForm(forms.ModelForm):
    """
    Form for Journalists to draft new newsletters.

    This form allows creating a Newsletter instance with a title and content.
    """

    class Meta:
        """
        Meta options for the NewsletterForm.

        Specifies the model and fields, and customizes widgets for a better UI.
        """
        model = Newsletter
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter newsletter subject",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Draft your newsletter here...",
                }
            ),
            "publisher": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class PublisherForm(forms.ModelForm):
    """
    Form for Editors to add new Publishers to the platform.
    """

    class Meta:
        """
        Meta options for the PublisherForm.

        Specifies the model and fields, and customizes widgets for a better UI.
        """
        model = Publisher
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., The Daily Tech",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Brief description of the publication...",
                }
            ),
        }

# news/views.py
"""
Views for the news app.

This module defines the views that handle HTTP requests for the news application.
It includes views for:
- User registration and subscription management.
- Article listing and details (public).
- Journalist article creation.
- Editor dashboard and article approval.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied

from .models import Article, Publisher, CustomUser, Newsletter
from .forms import ArticleForm, RegistrationForm, NewsletterForm, PublisherForm
from .decorators import editor_required, journalist_required


def register(request):
    """
    Handle user registration.

    Processes the registration form. If valid, saves the new user,
    logs them in, and redirects to the article list.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response (rendered template or redirect).
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after they register
            login(request, user)
            messages.success(
                request, f"Registration successful! Welcome, {user.username}."
            )
            return redirect("article_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def publisher_list(request):
    """
    Display a list of all publishers.

    This view retrieves all Publisher objects from the database, ordered by name,
    and renders them in a list for users to browse and subscribe.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response with the rendered publisher list.
    :rtype: django.http.HttpResponse
    """
    # Retrieve all publishers, ordered alphabetically by name.
    publishers = Publisher.objects.all().order_by("name")
    return render(
        request,
        "news/publisher_list.html",
        {"publishers": publishers},
    )


def article_list(request):
    """
    Display a list of all approved articles.

    Fetches all articles marked as approved, ordered by creation date (newest first).

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response with the rendered article list.
    :rtype: django.http.HttpResponse
    """
    articles = Article.objects.filter(is_approved=True).order_by("-created_at")
    return render(request, "news/article_list.html", {"articles": articles})


def article_detail(request, pk):
    """
    Display the details of a single article.

    Retrieves an article by its primary key. The article must be approved.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the article.
    :type pk: int
    :return: An HTTP response with the rendered article detail.
    :rtype: django.http.HttpResponse
    """
    article = get_object_or_404(Article, pk=pk, is_approved=True)
    return render(request, "news/article_detail.html", {"article": article})


def newsletter_list(request):
    """
    Display a list of all approved newsletters.

    Fetches all newsletters marked as approved, ordered by creation date (newest first).

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response with the rendered newsletter list.
    :rtype: django.http.HttpResponse
    """
    # Retrieve all approved newsletters, ordered by most recent.
    newsletters = Newsletter.objects.filter(is_approved=True).order_by(
        "-created_at"
    )
    return render(
        request, "news/newsletter_list.html", {"newsletters": newsletters}
    )


def newsletter_detail(request, pk):
    """
    Display the details of a single, approved newsletter.

    Retrieves a newsletter by its primary key. The newsletter must be approved
    to be viewed by the public.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int
    :return: An HTTP response with the rendered newsletter detail.
    :rtype: django.http.HttpResponse
    """
    # Retrieve the specific newsletter, ensuring it is approved.
    newsletter = get_object_or_404(Newsletter, pk=pk, is_approved=True)
    return render(
        request, "news/newsletter_detail.html", {"newsletter": newsletter}
    )


@login_required
@journalist_required
def journalist_dashboard(request):
    """
    Display a dashboard for a journalist.

    Shows lists of articles and newsletters authored by the currently logged-in
    journalist, allowing them to manage their content.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response with the rendered journalist dashboard.
    :rtype: django.http.HttpResponse
    """
    # Fetch all articles authored by the current user.
    articles = Article.objects.filter(author=request.user).order_by(
        "-created_at"
    )
    # Fetch all newsletters authored by the current user.
    newsletters = Newsletter.objects.filter(author=request.user).order_by(
        "-created_at"
    )

    return render(
        request,
        "news/journalist_dashboard.html",
        {"articles": articles, "newsletters": newsletters},
    )


@login_required
@journalist_required
def create_article(request):
    """
    Allow a Journalist to create a new article.

    Displays a form for creating an article. Upon valid submission,
    assigns the current user as the author and their affiliated publisher
    (if any) to the article. The article is created as unapproved.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response (rendered form or redirect).
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article submitted for editor approval.")
            return redirect("article_list")
    else:
        form = ArticleForm()

    return render(request, "news/create_article.html", {"form": form})


@login_required
@journalist_required
def update_article(request, pk):
    """
    Allow a Journalist to update their own article.

    Fetches an existing article and presents a form to edit it.
    Only the original author can update their article. Upon submission,
    the article's approval status is reset to False, requiring re-approval.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the article to update.
    :type pk: int
    :return: An HTTP response (rendered form or redirect).
    :rtype: django.http.HttpResponse
    :raises PermissionDenied: If the user is not the author of the article.
    """
    article = get_object_or_404(Article, pk=pk)

    # Security check: Ensure the user is the author of the article.
    if article.author != request.user:
        raise PermissionDenied("You can only edit your own articles.")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            # Any update requires re-approval from an editor.
            updated_article.is_approved = False
            updated_article.save()
            messages.success(request, "Article updated and sent for review.")
            return redirect("journalist_dashboard")
    else:
        # Pre-populate the form with the existing article's data.
        form = ArticleForm(instance=article)

    return render(
        request, "news/create_article.html", {"form": form, "is_update": True}
    )


@login_required
@journalist_required
def delete_article(request, pk):
    """
    Allow a Journalist to delete their own article.

    Presents a confirmation page before deleting an article. Only the
    original author can perform this action.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the article to delete.
    :type pk: int
    :return: An HTTP response (confirmation page or redirect).
    :rtype: django.http.HttpResponse
    :raises PermissionDenied: If the user is not the author of the article.
    """
    article = get_object_or_404(Article, pk=pk)

    # Security check: Ensure the user is the author of the article.
    if article.author != request.user:
        raise PermissionDenied("You can only delete your own articles.")

    # On confirmation, delete the object.
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect("journalist_dashboard")

    # Display the confirmation page.
    return render(
        request,
        "news/confirm_delete.html",
        {"object": article, "type": "Article"},
    )


@login_required
@journalist_required
def create_newsletter(request):
    """
    Allow a Journalist to create a new newsletter.

    Displays a form for creating a newsletter. Upon valid submission,
    assigns the current user as the author. The newsletter is created as
    unapproved by default.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response (rendered form or redirect).
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            messages.success(
                request,
                "Newsletter drafted and submitted for editor approval.",
            )
            return redirect("article_list")
    else:
        form = NewsletterForm()

    return render(request, "news/create_newsletter.html", {"form": form})


@login_required
@journalist_required
def update_newsletter(request, pk):
    """
    Allow a Journalist to update their own newsletter.

    Fetches an existing newsletter and presents a form to edit it.
    Only the original author can perform this action. Upon submission,
    the newsletter's approval status is reset to False.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the newsletter to update.
    :type pk: int
    :return: An HTTP response (rendered form or redirect).
    :rtype: django.http.HttpResponse
    :raises PermissionDenied: If the user is not the author of the newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Security check: Ensure the user is the author of the newsletter.
    if newsletter.author != request.user:
        raise PermissionDenied("You can only edit your own newsletters.")

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            updated_nl = form.save(commit=False)
            # Any update requires re-approval.
            updated_nl.is_approved = False
            updated_nl.save()
            messages.success(
                request, "Newsletter updated and sent for review."
            )
            return redirect("journalist_dashboard")
    else:
        # Pre-populate the form with the existing newsletter's data.
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "news/create_newsletter.html",
        {"form": form, "is_update": True},
    )


@login_required
@journalist_required
def delete_newsletter(request, pk):
    """
    Allow a Journalist to delete their own newsletter.

    Presents a confirmation page before deleting a newsletter. Only the
    original author can perform this action.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the newsletter to delete.
    :type pk: int
    :return: An HTTP response (confirmation page or redirect).
    :rtype: django.http.HttpResponse
    :raises PermissionDenied: If the user is not the author of the newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Security check: Ensure the user is the author of the newsletter.
    if newsletter.author != request.user:
        raise PermissionDenied("You can only delete your own newsletters.")

    # On confirmation, delete the object.
    if request.method == "POST":
        newsletter.delete()
        messages.success(request, "Newsletter deleted successfully.")
        return redirect("journalist_dashboard")

    # Display the confirmation page.
    return render(
        request,
        "news/confirm_delete.html",
        {"object": newsletter, "type": "Newsletter"},
    )


@login_required
@editor_required
def create_publisher(request):
    """
    Allow an Editor to create a new Publisher entity.

    Presents a form for an editor to add a new publisher to the platform.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response (rendered form or redirect).
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            messages.success(
                request, f"Publisher '{publisher.name}' successfully created!"
            )
            # Redirect back to the main editor dashboard after creation.
            return redirect("unapproved_articles")
    else:
        form = PublisherForm()

    return render(request, "news/create_publisher.html", {"form": form})


@login_required
@editor_required
def unapproved_articles(request):
    """
    Display a dashboard for Editors to manage unapproved content.

    Fetches all unapproved articles and newsletters. If the editor is affiliated
    with a publisher, it only shows content for that publisher. Otherwise, it
    shows all unapproved content on the platform.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: An HTTP response with the rendered editor dashboard.
    :rtype: django.http.HttpResponse
    """
    # If the editor is tied to a specific publisher, filter content for them.
    if request.user.publisher_affiliation:
        articles = Article.objects.filter(
            is_approved=False, publisher=request.user.publisher_affiliation
        )
        newsletters = Newsletter.objects.filter(
            is_approved=False, publisher=request.user.publisher_affiliation
        )
    # Otherwise, show all unapproved content (e.g., for a super-editor).
    else:
        articles = Article.objects.filter(is_approved=False)
        newsletters = Newsletter.objects.filter(is_approved=False)

    return render(
        request,
        "news/editor_dashboard.html",
        {
            "articles": articles,
            "newsletters": newsletters,
        },
    )


@login_required
@editor_required
def approve_newsletter(request, pk):
    """
    Approve a newsletter and notify subscribers via HTML/Text email.

    Sets the newsletter's `is_approved` status to True. Sends email
    notifications to all users subscribed to the newsletter's publisher and/or
    author.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the newsletter to approve.
    :type pk: int
    :return: An HTTP response (confirmation page or redirect).
    :rtype: django.http.HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk, is_approved=False)

    # Security check: Ensure editor can only approve for their affiliated publisher.
    if (
        request.user.publisher_affiliation
        and newsletter.publisher != request.user.publisher_affiliation
    ):
        messages.error(
            request,
            "You are not authorized to approve newsletters for this publisher.",
        )
        return redirect("unapproved_articles")

    if request.method == "POST":
        newsletter.is_approved = True
        newsletter.save()

        # --- Email Notification Logic ---

        # 1. Gather all subscribers for the Publisher, if one is associated.
        publisher_emails = []
        if newsletter.publisher:
            pub_subs = newsletter.publisher.reader_subscribers.all()
            publisher_emails = [user.email for user in pub_subs if user.email]

        # 2. Gather all subscribers for the specific Journalist author.
        journalist_emails = []
        if newsletter.author:
            journo_subs = newsletter.author.reader_subscribers.all()
            journalist_emails = [
                user.email for user in journo_subs if user.email
            ]

        # 3. Combine and remove duplicates using a set for efficiency.
        recipient_list = list(set(publisher_emails + journalist_emails))

        # 4. Dispatch the email if there are any subscribers to notify.
        if recipient_list:
            subject = f"New Newsletter: {newsletter.title}"
            # Get the base URL (e.g., http://127.0.0.1:8000) for email links.
            domain = request.build_absolute_uri("/")[:-1]

            # Context for rendering the HTML email template.
            context = {
                "newsletter": newsletter,
                "domain": domain,
            }

            # Render both HTML and plain-text versions of the email.
            html_content = render_to_string(
                "emails/newsletter_alert.html", context
            )
            text_content = (
                f"A new newsletter from {newsletter.author.username} is out!\n\n"
                f"Subject: {newsletter.title}\n\n"
                f"Read it now on our platform: {domain}/newsletter/{newsletter.pk}/"
            )

            try:
                # Use EmailMultiAlternatives to send a multipart email (HTML with a text fallback).
                msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)

                messages.success(
                    request,
                    f"Newsletter '{newsletter.title}' approved and {len(recipient_list)} subscribers notified.",
                )
            except Exception as e:
                # If email sending fails, inform the editor but don't crash.
                messages.warning(
                    request,
                    f"Newsletter approved, but failed to send emails: {str(e)}",
                )
        else:
            # Inform the editor that the newsletter was approved but no one was notified.
            messages.success(
                request,
                f"Newsletter '{newsletter.title}' approved. No active subscribers to notify.",
            )

        return redirect("unapproved_articles")

    # If it's a GET request, show the confirmation page before approving.
    return render(
        request,
        "news/approve_newsletter_confirm.html",
        {"newsletter": newsletter},
    )


@login_required
@editor_required
def approve_article(request, pk):
    """
    Approve an article and notify subscribers.

    Sets the article's `is_approved` status to True. Sends email notifications
    to subscribers of the publisher and the journalist.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key of the article to approve.
    :type pk: int
    :return: An HTTP response (confirmation page or redirect).
    :rtype: django.http.HttpResponse
    """
    article = get_object_or_404(Article, pk=pk, is_approved=False)

    # Security check: Ensure editor can only approve articles from their affiliated publisher.
    if request.user.publisher_affiliation and article.publisher != request.user.publisher_affiliation:
        messages.error(request, "You are not authorized to approve articles for this publisher.")
        return redirect("unapproved_articles")

    if request.method == "POST":
        article.is_approved = True
        article.save()

        # --- Email Notification Logic ---

        # 1. Gather all subscribers for the Publisher, if one is associated.
        publisher_emails = []
        if article.publisher:
            pub_subs = article.publisher.reader_subscribers.all()
            publisher_emails = [user.email for user in pub_subs if user.email]

        # 2. Gather all subscribers for the specific Journalist author.
        journalist_emails = []
        if article.author:
            journo_subs = article.author.reader_subscribers.all()
            journalist_emails = [
                user.email for user in journo_subs if user.email
            ]

        # 3. Combine and remove duplicates using a set for efficiency.
        recipient_list = list(set(publisher_emails + journalist_emails))

        # 4. Dispatch the email if there are any subscribers to notify.
        if recipient_list:
            subject = f"New Article Published: {article.title}"

            # Get the base URL (e.g., http://127.0.0.1:8000) for email links.
            domain = request.build_absolute_uri("/")[:-1]

            # Context for rendering the HTML email template.
            context = {
                "article": article,
                "domain": domain,
            }

            # Render both HTML and plain-text versions of the email.
            html_content = render_to_string(
                "emails/article_alert.html", context
            )

            # Create a plain-text fallback for email clients that block HTML.
            text_content = f"An article you might be interested in has just been published by {article.author.username}.\n\nTitle: {article.title}\n\nRead it now on our platform: {domain}/article/{article.pk}/"

            try:
                # Use EmailMultiAlternatives to send a multipart email (HTML with a text fallback).
                msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)

                messages.success(
                    request,
                    f"Article '{article.title}' approved and {len(recipient_list)} subscribers notified via email.",
                )
            except Exception as e:
                # If email sending fails, inform the editor but don't crash.
                messages.warning(
                    request,
                    f"Article approved, but failed to send emails: {str(e)}",
                )
        else:
            # Inform the editor that the article was approved but no one was notified.
            messages.success(
                request,
                f"Article '{article.title}' approved. No active subscribers to notify.",
            )

        return redirect("unapproved_articles")

    # If it's a GET request, show the confirmation page before approving.
    return render(
        request, "news/approve_article_confirm.html", {"article": article}
    )


@login_required
def toggle_subscription(request, target_type, target_id):
    """
    Toggle a user's subscription to a publisher or journalist.

    Allows a Reader to subscribe or unsubscribe from a specific publisher or
    journalist. Handles validation of roles.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param target_type: The type of entity to subscribe to ('publisher' or 'journalist').
    :type target_type: str
    :param target_id: The primary key of the target entity.
    :type target_id: int
    :return: An HTTP redirect response.
    :rtype: django.http.HttpResponseRedirect
    """
    user = request.user
    # Ensure only Readers can subscribe
    if user.role != CustomUser.Role.READER:
        messages.error(request, "Only readers can subscribe to updates.")
        return redirect("article_list")

    if target_type == "publisher":
        target = get_object_or_404(Publisher, id=target_id)
        if target in user.subscribed_publishers.all():
            user.subscribed_publishers.remove(target)
            messages.info(request, f"Unsubscribed from {target.name}")
        else:
            user.subscribed_publishers.add(target)
            messages.success(request, f"Subscribed to {target.name}!")

    elif target_type == "journalist":
        target = get_object_or_404(CustomUser, id=target_id)
        # Ensure the target user is actually a journalist
        if target.role != CustomUser.Role.JOURNALIST:
            messages.error(request, "You can only subscribe to journalists.")
            return redirect("article_list")

        if target in user.subscribed_journalists.all():
            user.subscribed_journalists.remove(target)
            messages.info(request, f"Unsubscribed from {target.username}")
        else:
            user.subscribed_journalists.add(target)
            messages.success(request, f"Subscribed to {target.username}!")

    return redirect("article_list")

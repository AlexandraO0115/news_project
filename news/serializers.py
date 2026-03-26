# news/serializers.py
"""
Serializers for the news app.

This module defines the serializers used to convert model instances into JSON
format for the API.
"""
from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializes Article models into JSON format for API consumption.

    This serializer handles the conversion of Article objects to JSON,
    including read-only string representations for related author and
    publisher fields.

    :ivar author: The string representation of the article's author.
    :vartype author: rest_framework.serializers.StringRelatedField
    :ivar publisher: The string representation of the article's publisher.
    :vartype publisher: rest_framework.serializers.StringRelatedField
    """

    # Using StringRelatedField so the API returns the actual names
    # instead of just the database ID numbers for authors and publishers.
    author = serializers.StringRelatedField(read_only=True)
    publisher = serializers.StringRelatedField(read_only=True)

    class Meta:
        """
        Meta options for ArticleSerializer.

        :ivar model: The model associated with this serializer.
        :ivar fields: The list of fields to include in the serialization.
        """
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "publisher",
            "created_at",
            "updated_at",
        ]

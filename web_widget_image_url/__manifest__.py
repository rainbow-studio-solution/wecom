
{
    "name": "Web Image URL",
    "summary": "This module provides web widget for displaying image from URL",
    "category": "Web",
    "version": "12.0.0.1",

    'author': "RStudio",

    "depends": ["web"],
    "data": [
        "views/web_widget_image_url.xml",
    ],
    "qweb": ["static/src/xml/*.xml"],
    "installable": True,
}

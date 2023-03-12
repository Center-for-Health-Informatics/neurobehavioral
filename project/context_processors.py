from django.conf import settings

def settings_context_processor(request):
    my_dict = {
        'SITE_TITLE': getattr(settings, 'SITE_TITLE', 'My Website'),
        'SITE_CONTACT_EMAIL': getattr(settings, 'SITE_CONTACT_EMAIL', 'combmichi@uc.edu'),
        "INCLUDE_INFOBAR": settings.INCLUDE_INFOBAR,
        "INCLUDE_INFOBAR_TYPE": settings.INCLUDE_INFOBAR_TYPE,
    }

    return my_dict
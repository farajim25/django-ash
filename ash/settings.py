from django.conf import settings

ASH_SITE_HEADER =  getattr(settings, 'ASH_SITE_HEADER', 'Django Ash')
ASH_SITE_LOGO_ICON = getattr(settings, 'ASH_SITE_LOGO_ICON', 'icon-trending-up')
ASH_APPS_DEFAULT_ICON = getattr(settings, 'ASH_APPS_DEFAULT_ICON', 'icon-box')

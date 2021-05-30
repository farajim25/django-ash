'use strict';
{
    window.addEventListener('load', function () {
        django.jQuery("[autocomplete-filter]").on('change', function (e) {
            django.jQuery(this).parents('form').first().submit()
        });
    });
}

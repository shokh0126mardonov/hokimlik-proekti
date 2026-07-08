import django_filters

from .models import Application


class ApplicationFilter(django_filters.FilterSet):
    age_filter = django_filters.ChoiceFilter(
        field_name="age_medium",
        choices=Application.AgeAverage.choices
    )

    class Meta:
        model = Application
        fields = []
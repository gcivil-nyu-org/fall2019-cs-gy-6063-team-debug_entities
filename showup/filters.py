import django_filters
from showup.models import Concert


class ConcertFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(
        field_name="datetime",
        label="Date range",
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    )
    borough = django_filters.MultipleChoiceFilter(choices=Concert.BOROUGH_CHOICES)
    performers = django_filters.AllValuesMultipleFilter(field_name="performer_names")
    venues = django_filters.AllValuesMultipleFilter(field_name="venue_name")
    genres = django_filters.CharFilter(
        field_name="genres",
        lookup_expr="contains",
        label="Enter genres separated by commas",
    )

    class Meta:
        model = Concert
        fields = []

import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'  # точное совпадение без учёта регистра
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='iexact'  # точное совпадение без учёта регистра
    )
    year = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='exact'  # точное совпадение с учётом регистра
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'  # частичное совпадение без учёта регистра
    )

    class Meta:
        model = Title
        fields = ['category', 'genre', 'year', 'name']

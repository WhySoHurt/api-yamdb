from rest_framework.pagination import PageNumberPagination


class ReviewCommentPagination(PageNumberPagination):
    """Пагинация для отзывов и комментариев."""
    
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 30
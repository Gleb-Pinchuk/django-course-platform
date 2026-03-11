from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Course
from .serializers import CourseSerializer
from .tasks import send_course_update_notifications


@extend_schema(
    tags=['courses'],
    summary='Получить список курсов',
    description='Возвращает пагинированный список доступных курсов',
)
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра курсов.
    """
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema(
    tags=['courses'],
    summary='Обновить курс',
    description='Обновляет курс и отправляет уведомления подписчикам (не чаще 4 часов)',
    request=CourseSerializer,
    responses={
        200: CourseSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    }
)
class CourseUpdateView(generics.UpdateAPIView):
    """
    View для обновления курса с отправкой уведомлений подписчикам.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        course = serializer.save()

        if course.can_send_notification():
            send_course_update_notifications.delay(course_id=course.id)
            course.mark_notified()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

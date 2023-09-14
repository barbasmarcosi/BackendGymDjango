from django.contrib import admin
from django.urls import path, include
from exercises import views
from exercises import serializers
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Jaseci API",
        default_version='v1',
        description="Welcome to the world of Jaseci",
        terms_of_service="https://www.jaseci.org",
        contact=openapi.Contact(email="jason@jaseci.org"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),  # <-- Here
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),  # <-- Here
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),  # <-- Here
    path('admin/', admin.site.urls),
    path('', include('exercises.urls')),
    path('api/exercises_with_muscular_groups/<int:pk>',
         views.get_exercise_with_muscular_group),
    path('api/muscular_groups/<int:exercise_id>',
         views.get_muscular_groups_by_exercise),
    path('api/persons/<int:active>',
         views.get_persons),
    # path('api/exercise_with_muscular_groups',
    #      views.get_exercises_with_muscular_group),
    path('api/person_plannings_complete/<int:person_id>&<int:all_plannings>',
         views.get_exercises_with_muscular_group),
    path('api/person_plannings_complete_2/<int:person_id>&<int:all_plannings>',
         views.get_person_plannings_2),
    # path('api/muscular_group_with_exercises',
    #      views.muscular_group_with_exercises_list),
    # path('api/exercises_with_muscular_groups',
    #      views.exercises_with_muscular_groups_list),
    # path(r'^api/tutorials/(?P<pk>[0-9]+)$', views.tutorial_detail)
]

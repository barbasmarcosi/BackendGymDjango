from rest_framework import routers
from .api import ExerciseViewSet
from .api import MuscularGroupViewSet
# from .api import ReadMuscularGroupExercisesViewSet
# from .api import WriteMuscularGroupExercisesViewSet
# from .api import ExerciseWithMuscularGroupsViewSet
from .api import PaymentViewSet
from .api import PersonViewSet
from .api import PersonPlanningViewSet
from .api import PlanningViewSet
from .api import RoutineViewSet
from .api import RoutineExerciseViewSet
from .api import ExercisesWithMuscularGroupViewSet
from .api import PlanViewSet

router = routers.DefaultRouter()
# urlpatterns = [
#     url(r'^api/tutorials$', views.tutorial_list),
#     url(r'^api/tutorials/(?P<pk>[0-9]+)$', views.tutorial_detail),
#     url(r'^api/tutorials/published$', views.tutorial_list_published)
# ]

router.register('api/muscular_groups', MuscularGroupViewSet, 'muscular_groups')
# router.register('api/exercise_with_muscular_groups',
#                 ExerciseWithMuscularGroupsViewSet, 'exercise_with_muscular_groups')
# router.register('api/muscular_groups/:id',
#                 MuscularGroupViewSet, 'muscular_group')
# router.register(
#     r'^api/muscular_group/(?P<pk>[0-9]+)$', tutorial_detail, 'muscular_group')
router.register('api/exercises', ExerciseViewSet, 'exercise')
router.register('api/exercises_with_muscular_groups', ExercisesWithMuscularGroupViewSet, 'exercises_with_muscular_groups')
# router.register('api/muscular_groups_exercises',
#                 WriteMuscularGroupExercisesViewSet, 'muscular_groups_exercises'),
# router.register('api/muscular_groups_exercises',
#                 ReadMuscularGroupExercisesViewSet, 'muscular_groups_exercises'),
router.register('api/payments', PaymentViewSet, 'payment')
router.register('api/persons', PersonViewSet, 'person')
router.register('api/person_plannings',
                PersonPlanningViewSet, 'person_planning')
router.register('api/routines', RoutineViewSet, 'routine')
router.register('api/routine_exercises',
                RoutineExerciseViewSet, 'routine_exercise')
router.register('api/plannings', PlanningViewSet, 'planning')
router.register('api/plans', PlanViewSet, 'plan')

urlpatterns = router.urls

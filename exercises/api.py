from .models import Exercise
from .models import MuscularGroup
# from .models import MuscularGroupExercises
from .models import Payment
from .models import Person
from .models import PersonPlanning
from .models import Planning
from .models import Routine
from .models import RoutineExercise
from .models import Plan
from .views import get_exercises_with_muscular_group
from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView
from .serializers import ExerciseSerializer
from .serializers import MuscularGroupSerializer
from .serializers import MuscularGroupWithExercisesSerializer
from .serializers import ExerciseWithMuscularGroupsSerializer
# from .serializers import MuscularGroupExercisesSerializer
# from .serializers import ExplicitMuscularGroupExercisesSerializer
# from .serializers import ExerciseWithMuscularGroupSerializer
from .serializers import PaymentSerializer
from .serializers import PersonSerializer
from .serializers import PersonPlanningSerializer
from .serializers import PlanningSerializer
from .serializers import RoutineSerializer
from .serializers import RoutineExerciseSerializer
from .serializers import PlanSerializer
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import models, connection
from rest_framework.generics import RetrieveAPIView
# from rest_framework.generics import APIV
import numpy as np


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class MuscularGroupViewSet(viewsets.ModelViewSet):
    queryset = MuscularGroup.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = MuscularGroupWithExercisesSerializer


class ExercisesWithMuscularGroupViewSet(viewsets.GenericViewSet):
    # queryset = Exercise.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ExerciseWithMuscularGroupsSerializer

    def create(self, request):

        exercise_data = JSONParser().parse(request)
        exercise_serializer = ExerciseWithMuscularGroupsSerializer(
            data=exercise_data)
        if exercise_serializer.is_valid():
            exercise_serializer.save()
            exercise_id = exercise_serializer.data["id"]
            for el in exercise_data["muscular_groups"]:
                raw = f'INSERT INTO exercises_musculargroup_exercises (musculargroup_id, exercise_id) VALUES ({el}, {exercise_id})'
                with connection.cursor() as cursor:
                    cursor.execute(raw)
            return JsonResponse(exercise_serializer.data, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        delete_raw = f'DELETE FROM exercises_musculargroup_exercises WHERE exercise_id = {pk}'
        with connection.cursor() as cursor:
            cursor.execute(delete_raw)
        exercise_data = JSONParser().parse(request)
        # print(f'\n\n{exercise_data}\n\n')
        exercise_serializer = ExerciseWithMuscularGroupsSerializer(data=exercise_data)
        if exercise_serializer.is_valid():
            for el in exercise_data["muscular_groups"]:
                raw = f'INSERT INTO exercises_musculargroup_exercises (musculargroup_id, exercise_id) VALUES ({el}, {pk})'
                with connection.cursor() as cursor:
                    cursor.execute(raw)
            return JsonResponse(exercise_serializer.data, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        raw = f"select A.id AS exercise_id, A.name AS exercise_name, a.url as exercise_url, C.id as musuclar_group_id, C.name AS musuclar_group_name, C.url as musuclar_group_url from exercises_exercise a left join exercises_musculargroup_exercises b on a.id = b.exercise_id join exercises_musculargroup c on c.id = b.musculargroup_id"

        with connection.cursor() as cursor:
            cursor.execute(raw)
            res = dict_fetchall(cursor)
        ids = np.unique(np.array([el['exercise_id'] for el in res]))
        final_data = []
        for id in ids:
            new_data = []
            for el in res:
                if el['exercise_id'] == id:
                    new_data.append(el)
            final_data.append({"id": new_data[0]['exercise_id'], "name": new_data[0]['exercise_name'],
                               "url": new_data[0]['exercise_url'], "muscular_groups": [{'id': el['musuclar_group_id'], "name": el['musuclar_group_name'], 'url': el['musuclar_group_url']} for el in new_data]})

        return JsonResponse(data=final_data, safe=False)

# class MuscularEditGroupViewSet(viewsets.ViewSet):
#     def create(self, request):
#         if request.method == 'POST':
#             muscular_group_data = JSONParser().parse(request)
#             muscular_group_serializer = MuscularGroupSerializer(
#                 data=muscular_group_data)
#             if muscular_group_serializer.is_valid():
#                 muscular_group_serializer.save()
#                 return JsonResponse(muscular_group_serializer.data, status=status.HTTP_201_CREATED)
#             return JsonResponse(muscular_group_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # queryset = MuscularGroup.objects.all()
    # # delete = MuscularGroup.objects.all().filter(3).delete()
    # permission_classes = [permissions.AllowAny]
    # serializer_class = MuscularGroupSerializer

# viewsets.


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    permission_classes = [permissions.AllowAny]
    # serializer_class = ExerciseWithMuscularGroupsSerializer
    serializer_class = ExerciseWithMuscularGroupsSerializer
    # lookup_field = 'id'

    # def list(self, request):
    #     serializer = ExerciseWithMuscularGroupsSerializer(
    #         self.queryset, many=True)
    #     return JsonResponse(serializer.data, safe=False)

    # def list(self, request):
    #     consulta_sql = f"SELECT * FROM exercises_exercise A JOIN exercises_musculargroupexercises B ON A.ID = B.EXERCISE_ID JOIN exercises_musculargroup C ON B.MUSCULAR_GROUP_ID = C.ID"

    #     # Ejecuta la consulta y obtén los resultados
    #     with connection.cursor() as cursor:
    #         cursor.execute(consulta_sql)
    #         resultados = dict_fetchall(cursor)

    #     return RawQuerySet(Producto, consulta_sql, [])
    # serializer = ExerciseSerializer(self.queryset, many=True)
    # return JsonResponse(serializer.data, safe=False)
# class ExerciseViewSet(viewsets.ModelViewSet):
#     queryset = Exercise.objects.all()
#     permission_classes = [permissions.AllowAny]
#     serializer_class = ExerciseSerializer


# class ReadMuscularGroupExercisesViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = MuscularGroupExercises.objects.all()
#     permission_classes = [permissions.AllowAny]
#     serializer_class = ExplicitMuscularGroupExercisesSerializer


# class WriteMuscularGroupExercisesViewSet(viewsets.GenericViewSet):
#     queryset = MuscularGroupExercises.objects.all()
#     permission_classes = [permissions.AllowAny]
#     serializer_class = MuscularGroupExercisesSerializer

#     def list(self, request):
#         serializer = ExplicitMuscularGroupExercisesSerializer(
#             self.queryset, many=True)
#         return JsonResponse(serializer.data, safe=False)

#     def get(self, request, pk=None):
#         item = get_object_or_404(self.queryset, pk=pk)
#         serializer = ExplicitMuscularGroupExercisesSerializer(item)
#         return JsonResponse(serializer.data, safe=False)

#     def create(self, request):
#         muscular_group_exercises_data = JSONParser().parse(request)
#         muscular_group_exercises_serializer = MuscularGroupExercisesSerializer(
#             data=muscular_group_exercises_data)
#         if muscular_group_exercises_serializer.is_valid():
#             muscular_group_exercises_serializer.save()
#             return JsonResponse(muscular_group_exercises_serializer.data, status=status.HTTP_201_CREATED)
#         return JsonResponse(muscular_group_exercises_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PaymentSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonSerializer


class PersonPlanningViewSet(viewsets.ModelViewSet):
    queryset = PersonPlanning.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonPlanningSerializer


class PersonPlanningGenericAPIView(GenericAPIView):
    queryset = PersonPlanning.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonPlanningSerializer

    def retrieve(self, request, person_id=None, ):
        item = get_object_or_404(self.queryset, person_id=person_id)
        serializer = PersonPlanningSerializer(item)
        return JsonResponse(serializer.data, safe=False)


class PlanningViewSet(viewsets.ModelViewSet):
    queryset = Planning.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PlanningSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RoutineSerializer


class RoutineExerciseViewSet(viewsets.ModelViewSet):
    queryset = RoutineExercise.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RoutineExerciseSerializer


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PlanSerializer

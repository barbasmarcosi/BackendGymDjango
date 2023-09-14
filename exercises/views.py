from django.shortcuts import render
from django.core.serializers import serialize
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.core.serializers.json import DjangoJSONEncoder
from .models import RoutineExercise
from .models import Routine
from .models import Planning
from .models import PersonPlanning
from .models import Person
from .models import MuscularGroup
from .models import Exercise
from .serializers import RoutineExerciseSerializer
from .serializers import RoutineSerializer
from .serializers import PlanningSerializer
from .serializers import PersonPlanningSerializer
from .serializers import PersonSerializer
from .serializers import MuscularGroupSerializer
from .serializers import ExerciseWithMuscularGroupsSerializer
from .serializers import ExerciseSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.db import models, connection
import numpy as np
# class LazyEncoder(DjangoJSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, YourCustomType):
#             return str(obj)
#         return super().default(obj)


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        tutorials = MuscularGroup.objects.all()

        title = request.query_params.get('title', None)
        if title is not None:
            tutorials = tutorials.filter(title__icontains=title)

        tutorials_serializer = MuscularGroupSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = MuscularGroupSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = MuscularGroup.objects.all().delete()
        return JsonResponse({'message': '{} MuscularGroups were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_persons(request, active):
    persons = Person.objects.filter(active=True if active else False)
    persons_serializer = PersonSerializer(persons, many=True)
    return JsonResponse(persons_serializer.data, safe=False)


@api_view(['GET'])
def get_muscular_groups_by_exercise(request, exercise_id):
    raw = f'select * from exercises_musculargroup A JOIN exercises_musculargroup_exercises B ON A.id = B.musculargroup_id WHERE B.exercise_id = {exercise_id}'
    # muscular_groups = MuscularGroup.objects.filter(exercise_id=exercise_id)
    # muscular_groups_serializer = MuscularGroupSerializer(
    #     muscular_groups, many=True)
    with connection.cursor() as cursor:
        cursor.execute(raw)
        res = dict_fetchall(cursor)
    return JsonResponse(res, safe=False)


@api_view(['GET'])
def get_person_plannings_2(request, person_id, all_plannings):
    person_planning_raw = f"select * from exercises_personplanning where person_id = {person_id} {f'and state = {all_plannings}'  if not all_plannings else ''}"

    with connection.cursor() as cursor:
        cursor.execute(person_planning_raw)
        res = dict_fetchall(cursor)
    ids = np.unique(np.array([el['Planning_id'] for el in res]))
    final_res = []
    for id in ids:
        routine_exercise_raw = f'select A.id, A.series, A.day,B.id AS routine_exercise_id, B.repetitions, B.unity, B.weight, C.name AS exercise from exercises_routine A left join exercises_routineexercise B ON A.id = B.routine_id LEFT JOIN exercises_exercise C ON C.id = B.exercise_id WHERE A.id = {id}'
        with connection.cursor() as cursor:
            cursor.execute(routine_exercise_raw)
            second_res = dict_fetchall(cursor)
        print(f'\n\n{second_res}\n\n')
        partial_res = {'id': second_res[0]['id'], 'series': second_res[0]
                       ['series'], 'day': second_res[0]['day'], 'routines': []}
        for el in second_res:
            partial_res['routines'].append({'id': el['routine_exercise_id'], 'repetitions': el['repetitions'],
                                           'unity': el['unity'], 'weight': el['weight'], 'exercise': el['exercise']})
        final_res.append(partial_res)
        # res = Planning.objects.filter(pk=id)
        # res = PlanningSerializer(res, many=True)
        # partial_res = []
        # for i, el in enumerate(res.data, start=0):
        #     if el["routines"]:
        #         routine_id = el["routines"][i]["id"]
        #         query_1 = RoutineExercise.objects.filter(routine=routine_id)
        #         query_2 = RoutineExerciseSerializer(query_1, many=True)
        #         new_el = {**el, "routines": query_2.data}
        #     else:
        #         new_el = {**el, "routines": []}
        #     partial_res.append(new_el)
        # final_res.append(partial_res[0])
    return JsonResponse(data=final_res, safe=False)


@api_view(['GET'])
def get_person_plannings(request, person_id, all_plannings):
    raw = f"select * from exercises_personplanning where person_id = {person_id} {f'and state = {all_plannings}'  if all_plannings else ''}"

    with connection.cursor() as cursor:
        cursor.execute(raw)
        res = dict_fetchall(cursor)
    ids = np.unique(np.array([el['id'] for el in res]))
    final_res = []
    for id in ids:
        res = Planning.objects.filter(pk=id)
        res = PlanningSerializer(res, many=True)
        partial_res = []
        for i, el in enumerate(res.data, start=0):
            if el["routines"]:
                routine_id = el["routines"][i]["id"]
                query_1 = RoutineExercise.objects.filter(routine=routine_id)
                query_2 = RoutineExerciseSerializer(query_1, many=True)
                new_el = {**el, "routines": query_2.data}
            else:
                new_el = {**el, "routines": []}
            partial_res.append(new_el)
        final_res.append(partial_res[0])
    return JsonResponse(data=final_res, safe=False)


@api_view(['GET'])
def get_exercise_with_muscular_group(request, pk):
    if request.method == 'GET':
        raw = f"select A.id AS exercise_id, A.name AS exercise_name, a.url as exercise_url, C.id as musuclar_group_id, C.name AS musuclar_group_name, C.url as musuclar_group_url from exercises_exercise a left join exercises_musculargroup_exercises b on a.id = b.exercise_id join exercises_musculargroup c on c.id = b.musculargroup_id where A.id = {pk}"

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


@api_view(['GET', 'POST'])
def get_exercises_with_muscular_group(request):
    if request.method == 'GET':
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

    elif request.method == 'POST':
        exercise_data = JSONParser().parse(request)
        exercise_serializer = ExerciseWithMuscularGroupsSerializer(
            data=exercise_data)
        if exercise_serializer.is_valid():
            exercise_serializer.save()
            return JsonResponse(exercise_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def tutorial_list_published(request):
    tutorials = MuscularGroup.objects.filter(published=True)

    if request.method == 'GET':
        tutorials_serializer = MuscularGroupSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)

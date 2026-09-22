from rest_framework import serializers
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
from django.db import models


class MuscularGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = MuscularGroup
        fields = ['id', 'name', 'url']


class IdMuscularGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = MuscularGroup
        fields = ['id']



# class MuscularGroupExercisesSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = MuscularGroupExercises
#         fields = '__all__'


class ExerciseSerializer(serializers.ModelSerializer):
    muscular_groups = MuscularGroupSerializer(
        many=True, read_only=True)

    class Meta:
        model = Exercise
        fields = '__all__'


class MuscularGroupWithExercisesSerializer(serializers.ModelSerializer):
    exercises = IdMuscularGroupSerializer(
        many=True, read_only=True)

    class Meta:
        model = MuscularGroup
        fields = '__all__'


class ExerciseWithMuscularGroupsSerializer(serializers.ModelSerializer):
    muscular_groups = IdMuscularGroupSerializer(
        many=True, read_only=True)

    class Meta:
        model = Exercise
        fields = '__all__'
# class MuscularGroup(models.Model):
#     name = models.CharField(max_length=100)
#     url = models.TextField(null=True)

#     def __str__(self):
#         return self.name


# class ExerciseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MuscularGroup
#         fields = '__all__'
    # exercises = models.ManyToManyField(Exercise)


# class ExplicitMuscularGroupExercisesSerializer(serializers.ModelSerializer):
#     exercise = ExerciseSerializer(read_only=True)
#     muscular_group = MuscularGroupSerializer(read_only=True)

#     class Meta:
#         model = MuscularGroupExercises
#         fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class PersonPlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonPlanning
        fields = '__all__'

    # exercises = Routine.objects.prefetch_related('routineexercise_set')
    # exercises = RoutineExerciseSerializer(many=True, read_only=True)

    # class Meta:
    #     model = Routine
    #     fields = '__all__'
#   series = models.IntegerField()
#     day = models.IntegerField()


class RoutineSerializer(serializers.ModelSerializer):
    # series = serializers.IntegerField()
    # day = serializers.IntegerField()
    # exercise = RoutineExerciseSerializer()

    class Meta:
        model = Routine
        fields = '__all__'


class RoutineExerciseSerializer(serializers.ModelSerializer):
    # exercise = ExerciseSerializer()
    # routine = RoutineSerializer()

    class Meta:
        model = RoutineExercise
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class PlanningSerializer(serializers.ModelSerializer):
    # routines = RoutineSerializer(many=True, read_only=True)

    class Meta:
        model = Planning
        fields = '__all__'

from django.db import models


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    url = models.TextField(null=True)

    def __str__(self):
        return self.name


class MuscularGroup(models.Model):
    name = models.CharField(max_length=100)
    url = models.TextField(null=True)
    exercises = models.ManyToManyField(Exercise)

    def __str__(self):
        return self.name


# class MuscularGroupExercises(models.Model):
#     exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
#     muscular_group = models.ForeignKey(
#         'MuscularGroup', on_delete=models.CASCADE)
    # name = models.CharField(max_length=100)
    # url = models.TextField(null=True)
    # exercises = models.ManyToManyField(Exercise)

    # def __str__(self):
    #     return self.name
    # def __str__(self):
    #     return self.muscular_group


class Plan(models.Model):
    name = models.CharField(max_length=50)
    amount = models.FloatField()
    plan_type = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    born_date = models.DateField(null=True)
    register_date = models.DateField(auto_now=True)
    resubscription_date = models.DateField(null=True)
    unsubscribe_date = models.DateField(null=True)
    new_payment_date = models.DateField(null=True, default=None)
    payment_advice_date = models.DateField(null=True, default=None)
    last_activity = models.DateField(null=True, default=None)
    dni = models.BigIntegerField(unique=True, null=True)
    phone = models.CharField(max_length=20, null=True)
    comments = models.TextField(null=True)
    condition = models.IntegerField(default=1)
    plan = models.ForeignKey('Plan', on_delete=models.PROTECT)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['last_activity']

    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now=True)
    payment_type = models.CharField(max_length=50)
    bonus = models.IntegerField(default=0)
    person = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return self.amount


class Routine(models.Model):
    series = models.IntegerField()
    day = models.IntegerField()
    # exercise = models.ManyToOneRel(to='RoutineExercise', field='exercise', field_name='exercise')

    # def __str__(self):
    #     return self.str(self.day)


class RoutineExercise(models.Model):
    # name = models.CharField(max_length=50)
    repetitions = models.IntegerField()
    unity = models.CharField(max_length=20)
    weight = models.IntegerField()
    exercise = models.ForeignKey('Exercise', on_delete=models.PROTECT)
    routine = models.ForeignKey('Routine', on_delete=models.PROTECT)

    # def __str__(self):
    #     return self.name


class Planning(models.Model):
    name = models.CharField(max_length=50)
    duration = models.IntegerField()
    routines = models.ManyToManyField(Routine)

    def __str__(self):
        return self.name


class PersonPlanning(models.Model):
    state = models.BooleanField()
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    Planning = models.ForeignKey('Planning', on_delete=models.CASCADE)


# class Payment(models.Model):

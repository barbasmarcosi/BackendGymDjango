from django.test import TestCase

from .models import (
    Exercise, MuscularGroup, Person, PersonPlanning, Plan, Planning, Routine,
    RoutineExercise,
)


class GetPersonPlannings2Tests(TestCase):
    """Characterization of GET /api/person_plannings_complete_2/<person_id>&<all_plannings>.

    Two quirks are pinned on purpose. The state filter is applied only when
    all_plannings is falsy, and routines are looked up by planning id rather
    than through any relation. Both are easy to "correct" while rewriting, and
    both change the response.
    """

    def setUp(self):
        self.plan = Plan.objects.create(
            name="Monthly", amount=1000.0, plan_type="full")
        self.person = Person.objects.create(name="Ana", dni=1, plan=self.plan)
        self.other = Person.objects.create(name="Beto", dni=2, plan=self.plan)

        self.squat = Exercise.objects.create(name="Squat", url=None)
        self.routine = Routine.objects.create(series=3, day=1)
        self.planning = Planning.objects.create(name="Base", duration=4)
        self.planning.routines.add(self.routine)
        RoutineExercise.objects.create(
            repetitions=10, unity="reps", weight=50,
            exercise=self.squat, routine=self.routine)

    def get(self, person_id, all_plannings):
        return self.client.get(
            f"/api/person_plannings_complete_2/{person_id}&{all_plannings}")

    def test_returns_each_planning_with_its_routines_nested(self):
        PersonPlanning.objects.create(
            state=True, person=self.person, Planning=self.planning)

        body = self.get(self.person.pk, 1).json()

        self.assertEqual(len(body), 1)
        entry = body[0]
        self.assertEqual(sorted(entry.keys()), ["day", "id", "routines", "series"])
        self.assertEqual(entry["series"], 3)
        self.assertEqual(entry["day"], 1)
        self.assertEqual(len(entry["routines"]), 1)
        self.assertEqual(
            sorted(entry["routines"][0].keys()),
            ["exercise", "id", "repetitions", "unity", "weight"])
        self.assertEqual(entry["routines"][0]["exercise"], "Squat")
        self.assertEqual(entry["routines"][0]["repetitions"], 10)

    def make_second_planning(self):
        """A planning whose id matches a routine id, as the endpoint requires."""
        routine = Routine.objects.create(series=5, day=2)
        planning = Planning.objects.create(name="Second", duration=8)
        planning.routines.add(routine)
        RoutineExercise.objects.create(
            repetitions=8, unity="reps", weight=60,
            exercise=self.squat, routine=routine)
        self.assertEqual(planning.pk, routine.pk)
        return planning

    def test_all_plannings_1_returns_rows_of_both_states(self):
        second = self.make_second_planning()
        PersonPlanning.objects.create(
            state=True, person=self.person, Planning=self.planning)
        PersonPlanning.objects.create(
            state=False, person=self.person, Planning=second)

        self.assertEqual(len(self.get(self.person.pk, 1).json()), 2)

    def test_all_plannings_0_keeps_only_the_state_false_row(self):
        second = self.make_second_planning()
        PersonPlanning.objects.create(
            state=True, person=self.person, Planning=self.planning)
        PersonPlanning.objects.create(
            state=False, person=self.person, Planning=second)

        body = self.get(self.person.pk, 0).json()

        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["series"], 5)

    def test_a_person_without_plannings_returns_an_empty_list(self):
        response = self.get(self.other.pk, 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_one_person_does_not_see_another_persons_plannings(self):
        PersonPlanning.objects.create(
            state=True, person=self.other, Planning=self.planning)

        self.assertEqual(self.get(self.person.pk, 1).json(), [])

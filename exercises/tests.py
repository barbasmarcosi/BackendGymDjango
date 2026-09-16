from django.test import TestCase

from .models import Exercise, MuscularGroup


class GetExerciseWithMuscularGroupTests(TestCase):
    """Characterization of GET /api/exercises_with_muscular_groups/<int:pk>.

    These tests pin the behaviour the endpoint has today, so that a refactor of
    its implementation can be shown to preserve it. They describe the response
    contract only, never how the data is fetched.
    """

    def setUp(self):
        self.bench_press = Exercise.objects.create(
            name="Bench press", url="https://example.invalid/bench")
        self.plank = Exercise.objects.create(name="Plank", url=None)

        self.chest = MuscularGroup.objects.create(
            name="Chest", url="https://example.invalid/chest")
        self.triceps = MuscularGroup.objects.create(name="Triceps", url=None)

        self.chest.exercises.add(self.bench_press)
        self.triceps.exercises.add(self.bench_press)

    def get(self, pk):
        return self.client.get(f"/api/exercises_with_muscular_groups/{pk}")

    def test_returns_the_exercise_with_each_of_its_muscular_groups(self):
        response = self.get(self.bench_press.pk)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)

        entry = body[0]
        self.assertEqual(entry["id"], self.bench_press.pk)
        self.assertEqual(entry["name"], "Bench press")
        self.assertEqual(entry["url"], "https://example.invalid/bench")

        # Group order is not part of the contract; membership and fields are.
        groups = sorted(entry["muscular_groups"], key=lambda g: g["id"])
        self.assertEqual(groups, [
            {"id": self.chest.pk, "name": "Chest",
             "url": "https://example.invalid/chest"},
            {"id": self.triceps.pk, "name": "Triceps", "url": None},
        ])

    def test_exposes_exactly_the_documented_keys(self):
        entry = self.get(self.bench_press.pk).json()[0]

        self.assertEqual(sorted(entry.keys()),
                         ["id", "muscular_groups", "name", "url"])
        for group in entry["muscular_groups"]:
            self.assertEqual(sorted(group.keys()), ["id", "name", "url"])

    def test_an_exercise_without_muscular_groups_returns_an_empty_list(self):
        response = self.get(self.plank.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_an_unknown_exercise_returns_an_empty_list(self):
        response = self.get(self.bench_press.pk + self.plank.pk + 1000)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_one_exercise_does_not_leak_another_exercises_groups(self):
        back = MuscularGroup.objects.create(name="Back", url=None)
        pull_up = Exercise.objects.create(name="Pull up", url=None)
        back.exercises.add(pull_up)

        entry = self.get(self.bench_press.pk).json()[0]
        names = {group["name"] for group in entry["muscular_groups"]}

        self.assertEqual(names, {"Chest", "Triceps"})

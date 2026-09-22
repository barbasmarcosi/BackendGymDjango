import json

from django.test import TestCase

from exercises.models import Exercise, MuscularGroup


COLLECTION_URL = "/api/exercises_with_muscular_groups/"


def detail_url(exercise_id):
    return f"/api/exercises_with_muscular_groups/{exercise_id}"


def update_url(exercise_id):
    return f"/api/exercises_with_muscular_groups/{exercise_id}/"


class Midas038ExerciseMuscularGroupContractTests(TestCase):
    def setUp(self):
        # Burn a few primary keys so a solution that assumes IDs start at 1 is invalid.
        for i in range(3):
            Exercise.objects.create(name=f"sentinel-exercise-{i}", url=None)
            MuscularGroup.objects.create(name=f"sentinel-group-{i}", url=None)

        self.chest = MuscularGroup.objects.create(
            name="M038 Chest", url="https://example.invalid/m038/chest"
        )
        self.triceps = MuscularGroup.objects.create(
            name="M038 Triceps", url=None
        )
        self.shoulders = MuscularGroup.objects.create(
            name="M038 Shoulders", url="https://example.invalid/m038/shoulders"
        )
        self.back = MuscularGroup.objects.create(
            name="M038 Back", url="https://example.invalid/m038/back"
        )

        self.press = Exercise.objects.create(
            name="M038 Press", url="https://example.invalid/m038/press"
        )
        self.row = Exercise.objects.create(name="M038 Row", url=None)
        self.groupless = Exercise.objects.create(
            name="M038 Groupless", url="https://example.invalid/m038/groupless"
        )

        self.chest.exercises.add(self.press)
        self.triceps.exercises.add(self.press)
        self.shoulders.exercises.add(self.press)
        self.back.exercises.add(self.row)

    def get_collection(self):
        response = self.client.get(COLLECTION_URL)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsInstance(body, list)
        return body

    def get_detail(self, exercise_id):
        response = self.client.get(detail_url(exercise_id))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsInstance(body, list)
        return body

    def assert_entry_shape(self, entry):
        self.assertEqual(
            sorted(entry.keys()),
            ["id", "muscular_groups", "name", "url"],
        )
        self.assertIsInstance(entry["muscular_groups"], list)
        for group in entry["muscular_groups"]:
            self.assertEqual(sorted(group.keys()), ["id", "name", "url"])

    def assert_group_ids(self, entry, expected_ids):
        self.assertEqual(
            {group["id"] for group in entry["muscular_groups"]},
            set(expected_ids),
        )

    def test_collection_contract_is_grouped_isolated_and_omits_groupless(self):
        body = self.get_collection()
        ids = [entry["id"] for entry in body]

        self.assertEqual(ids.count(self.press.pk), 1)
        self.assertEqual(ids.count(self.row.pk), 1)
        self.assertNotIn(self.groupless.pk, ids)

        by_id = {entry["id"]: entry for entry in body}
        self.assertEqual(set(by_id), {self.press.pk, self.row.pk})

        press = by_id[self.press.pk]
        row = by_id[self.row.pk]
        self.assert_entry_shape(press)
        self.assert_entry_shape(row)

        self.assertEqual(press["name"], self.press.name)
        self.assertEqual(press["url"], self.press.url)
        self.assert_group_ids(
            press,
            [self.chest.pk, self.triceps.pk, self.shoulders.pk],
        )

        self.assertEqual(row["name"], self.row.name)
        self.assertIsNone(row["url"])
        self.assert_group_ids(row, [self.back.pk])

        self.assertNotIn(
            self.back.pk,
            {group["id"] for group in press["muscular_groups"]},
        )

    def test_detail_contract_unknown_and_groupless_behavior(self):
        body = self.get_detail(self.press.pk)
        self.assertEqual(len(body), 1)

        entry = body[0]
        self.assert_entry_shape(entry)
        self.assertEqual(entry["id"], self.press.pk)
        self.assertEqual(entry["name"], self.press.name)
        self.assertEqual(entry["url"], self.press.url)
        self.assert_group_ids(
            entry,
            [self.chest.pk, self.triceps.pk, self.shoulders.pk],
        )

        self.assertEqual(self.get_detail(self.groupless.pk), [])
        self.assertEqual(self.get_detail(self.groupless.pk + 100000), [])

    def test_post_creates_exact_associations_and_preserves_null_url(self):
        alpha = MuscularGroup.objects.create(name="M038 Alpha", url=None)
        beta = MuscularGroup.objects.create(
            name="M038 Beta", url="https://example.invalid/m038/beta"
        )
        payload = {
            "name": "M038 Created",
            "url": None,
            "muscular_groups": [alpha.pk, beta.pk],
        }

        response = self.client.post(
            COLLECTION_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        created = Exercise.objects.get(name="M038 Created")
        self.assertIsNone(created.url)
        self.assertEqual(
            set(
                MuscularGroup.objects.filter(exercises=created)
                .values_list("id", flat=True)
            ),
            {alpha.pk, beta.pk},
        )

        detail = self.get_detail(created.pk)
        self.assertEqual(len(detail), 1)
        self.assert_entry_shape(detail[0])
        self.assert_group_ids(detail[0], [alpha.pk, beta.pk])

        collection = {entry["id"]: entry for entry in self.get_collection()}
        self.assertIn(created.pk, collection)
        self.assert_group_ids(collection[created.pk], [alpha.pk, beta.pk])

    def test_post_with_empty_groups_creates_but_grouped_reads_hide_it(self):
        payload = {
            "name": "M038 Empty Created",
            "url": "https://example.invalid/m038/empty-created",
            "muscular_groups": [],
        }
        response = self.client.post(
            COLLECTION_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        created = Exercise.objects.get(name="M038 Empty Created")
        self.assertFalse(MuscularGroup.objects.filter(exercises=created).exists())
        self.assertEqual(self.get_detail(created.pk), [])
        self.assertNotIn(
            created.pk,
            {entry["id"] for entry in self.get_collection()},
        )

    def test_put_replaces_associations_without_touching_another_exercise(self):
        other_group = MuscularGroup.objects.create(
            name="M038 Other Group", url=None
        )
        other = Exercise.objects.create(name="M038 Other Exercise", url=None)
        other_group.exercises.add(other)

        payload = {
            "name": self.press.name,
            "url": self.press.url,
            "muscular_groups": [self.back.pk],
        }
        response = self.client.put(
            update_url(self.press.pk),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            set(
                MuscularGroup.objects.filter(exercises=self.press)
                .values_list("id", flat=True)
            ),
            {self.back.pk},
        )
        self.assertEqual(
            set(
                MuscularGroup.objects.filter(exercises=other)
                .values_list("id", flat=True)
            ),
            {other_group.pk},
        )

        detail = self.get_detail(self.press.pk)
        self.assertEqual(len(detail), 1)
        self.assert_group_ids(detail[0], [self.back.pk])

    def test_put_empty_groups_removes_all_associations(self):
        payload = {
            "name": self.row.name,
            "url": self.row.url,
            "muscular_groups": [],
        }
        response = self.client.put(
            update_url(self.row.pk),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        self.assertFalse(
            MuscularGroup.objects.filter(exercises=self.row).exists()
        )
        self.assertEqual(self.get_detail(self.row.pk), [])
        self.assertNotIn(
            self.row.pk,
            {entry["id"] for entry in self.get_collection()},
        )

from django.test import TestCase
from .scoring import compute_scores, detect_circular_dependencies

class ScoringTests(TestCase):
    def test_basic_scoring(self):
        tasks = [
            {"id":"1","title":"A","due_date":"2025-12-01","estimated_hours":2,"importance":8,"dependencies":[]},
            {"id":"2","title":"B","due_date":"2025-11-25","estimated_hours":6,"importance":6,"dependencies":["1"]},
            {"id":"3","title":"C","due_date":None,"estimated_hours":1,"importance":5,"dependencies":[]}
        ]
        res = compute_scores(tasks, strategy="smart", today=None)
        self.assertIn("tasks", res)
        self.assertEqual(len(res["tasks"]),3)
        top = res["tasks"][0]
        self.assertTrue("score" in top)

    def test_circular_detection(self):
        tasks = {
            "1": {"dependencies":["2"]},
            "2": {"dependencies":["3"]},
            "3": {"dependencies":["1"]}
        }
        cycles = detect_circular_dependencies(tasks)
        self.assertTrue(len(cycles) >= 1)

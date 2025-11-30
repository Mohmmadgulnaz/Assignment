from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from .scoring import compute_scores

class AnalyzeTasks(APIView):
    def post(self, request):
        payload = request.data
        tasks = payload.get("tasks") if isinstance(payload, dict) and payload.get("tasks") else (payload if isinstance(payload, list) else [])
        if not isinstance(tasks, list):
            return Response({"error": "Provide a list of tasks or {\"tasks\": [...]}"}, status=status.HTTP_400_BAD_REQUEST)
        validated = []
        errors = []
        for i, t in enumerate(tasks):
            serializer = TaskInputSerializer(data=t)
            if serializer.is_valid():
                validated.append(serializer.validated_data)
            else:
                errors.append({"index": i, "errors": serializer.errors})
        if errors:
            return Response({"error": "Some tasks invalid", "details": errors}, status=status.HTTP_400_BAD_REQUEST)
        strategy = request.query_params.get("strategy", "smart")
        result = compute_scores(validated, strategy=strategy)
        return Response(result)

class SuggestTasks(APIView):
    def post(self, request):
        payload = request.data
        tasks = payload.get("tasks") if isinstance(payload, dict) and payload.get("tasks") else (payload if isinstance(payload, list) else [])
        if not isinstance(tasks, list) or len(tasks) == 0:
            return Response({"error":"Provide tasks list in body"}, status=status.HTTP_400_BAD_REQUEST)
        strategy = request.query_params.get("strategy", "smart")
        result = compute_scores(tasks, strategy=strategy)
        top3 = result["tasks"][:3]
        suggestions = []
        for t in top3:
            suggestions.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "score": t.get("score"),
                "explanation": t.get("explanation"),
                "why": f"Selected because score {t.get('score')} (priority {t.get('priority_level')})."
            })
        return Response({"suggestions": suggestions, "cycles": result["cycles"]})

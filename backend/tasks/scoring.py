from datetime import date
import math

DEFAULT_WEIGHTS = {
    "urgency": 0.35,
    "importance": 0.35,
    "effort": 0.15,
    "dependency": 0.15
}

def detect_circular_dependencies(tasks):
    visited = {}
    stack = []
    cycles = []

    def dfs(node):
        visited[node] = 1
        stack.append(node)
        for dep in tasks.get(node, {}).get("dependencies", []):
            dep = str(dep)
            if dep not in tasks:
                continue
            if visited.get(dep, 0) == 0:
                dfs(dep)
            elif visited.get(dep) == 1:
                try:
                    idx = stack.index(dep)
                    cycle = stack[idx:] + [dep]
                except ValueError:
                    cycle = [dep, node, dep]
                cycles.append(cycle)
        stack.pop()
        visited[node] = 2

    for node in tasks:
        if visited.get(node, 0) == 0:
            dfs(node)
    return cycles

def normalize(value, min_v, max_v):
    if min_v == max_v:
        return 0.5
    return (value - min_v) / (max_v - min_v)

def compute_scores(task_list, weights=None, today=None, strategy="smart"):
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    if strategy == "fastest":
        weights = {**weights, "effort": 0.5, "importance": 0.2, "urgency": 0.2, "dependency": 0.1}
    elif strategy == "impact":
        weights = {**weights, "importance": 0.6, "urgency": 0.2, "effort": 0.1, "dependency": 0.1}
    elif strategy == "deadline":
        weights = {**weights, "urgency": 0.7, "importance": 0.15, "effort": 0.05, "dependency": 0.1}

    today = today or date.today()

    id_map = {}
    for i, t in enumerate(task_list):
        t_id = str(t.get("id", i))
        id_map[t_id] = {**t, "id": t_id}
        if not isinstance(id_map[t_id].get("dependencies"), list):
            id_map[t_id]["dependencies"] = []

    cycles = detect_circular_dependencies(id_map)
    cyc_set = set()
    for c in cycles:
        cyc_set.update(c)

    urgencies = {}
    importances = {}
    efforts = {}
    for tid, t in id_map.items():
        dd = t.get("due_date")
        if dd:
            try:
                y, m, d = map(int, dd.split("-"))
                due = date(y, m, d)
                days = (due - today).days
            except Exception:
                days = 365
        else:
            days = 365
        days = max(-365, min(365, days))
        urgencies[tid] = -days
        imp = t.get("importance") or 5
        importances[tid] = max(1, min(10, int(imp)))
        est = t.get("estimated_hours") or 1.0
        try:
            est = float(est)
        except Exception:
            est = 1.0
        efforts[tid] = max(0.25, est)

    dependents_count = {tid: 0 for tid in id_map}
    for tid, t in id_map.items():
        for dep in t.get("dependencies", []):
            dep = str(dep)
            if dep in dependents_count:
                dependents_count[dep] += 1

    min_urg = min(urgencies.values()) if urgencies else 0
    max_urg = max(urgencies.values()) if urgencies else 1
    min_imp = min(importances.values()) if importances else 1
    max_imp = max(importances.values()) if importances else 10
    min_eff = min(efforts.values()) if efforts else 0.25
    max_eff = max(efforts.values()) if efforts else 10
    min_dep = min(dependents_count.values()) if dependents_count else 0
    max_dep = max(dependents_count.values()) if dependents_count else 1

    results = []
    for tid, t in id_map.items():
        u = normalize(urgencies[tid], min_urg, max_urg)
        imp = normalize(importances[tid], min_imp, max_imp)
        eff_norm = normalize(efforts[tid], min_eff, max_eff)
        eff = 1.0 - eff_norm
        dep = normalize(dependents_count[tid], min_dep, max_dep)

        score = (
            weights.get("urgency", 0) * u +
            weights.get("importance", 0) * imp +
            weights.get("effort", 0) * eff +
            weights.get("dependency", 0) * dep
        )

        explanation_parts = []
        if t.get("due_date"):
            try:
                days_to_due = (date.fromisoformat(t["due_date"]) - today).days
            except Exception:
                days_to_due = "invalid"
            explanation_parts.append(f"Urgency: {round(u,3)} (days to due: {days_to_due})")
        else:
            explanation_parts.append(f"Urgency: {round(u,3)} (no due date)")
        explanation_parts.append(f"Importance: {round(imp,3)}")
        explanation_parts.append(f"Effort advantage: {round(eff,3)}")
        explanation_parts.append(f"Dep impact: {round(dep,3)}")
        if tid in cyc_set:
            explanation_parts.append("Circular-dependency detected")

        if score >= 0.75:
            level = "High"
        elif score >= 0.45:
            level = "Medium"
        else:
            level = "Low"

        results.append({
            **t,
            "score": round(score, 4),
            "priority_level": level,
            "explanation": "; ".join(explanation_parts)
        })

    def sort_key(r):
        pdays = 0
        if r.get("due_date"):
            try:
                pdays = (date.fromisoformat(r["due_date"]) - today).days
            except Exception:
                pdays = 365
        past_due_boost = 0.05 if pdays < 0 else 0.0
        return (r["score"] + past_due_boost, - (r.get("estimated_hours") or 0))

    results_sorted = sorted(results, key=sort_key, reverse=True)
    return {"tasks": results_sorted, "cycles": cycles}

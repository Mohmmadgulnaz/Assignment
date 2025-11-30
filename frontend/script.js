const API_BASE = "/api/tasks/";
let localTasks = [];

function showResults(tasks) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";
  if (!tasks || tasks.length===0) {
    resultsDiv.textContent = "No tasks to display.";
    return;
  }
  tasks.forEach(t => {
    const el = document.createElement("div");
    el.className = `task priority-${t.priority_level}`;
    el.innerHTML = `<strong>${t.title}</strong> <span class="small">(${t.priority_level}) score: ${t.score}</span>
                    <div class="small">Due: ${t.due_date || '—'} | Est: ${t.estimated_hours}h | Importance: ${t.importance}</div>
                    <div class="small">Why: ${t.explanation}</div>`;
    resultsDiv.appendChild(el);
  });
}

function showSuggestions(suggestions) {
  const sdiv = document.getElementById("suggestions");
  sdiv.innerHTML = "";
  if (!suggestions || suggestions.length===0) {
    sdiv.textContent = "No suggestions.";
    return;
  }
  suggestions.forEach(s => {
    const el = document.createElement("div");
    el.className = "task";
    el.innerHTML = `<strong>${s.title}</strong> <div class="small">score: ${s.score}</div>
                    <div class="small">why: ${s.why}</div>`;
    sdiv.appendChild(el);
  });
}

document.getElementById("task-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const t = {
    id: (localTasks.length+1).toString(),
    title: document.getElementById("title").value,
    due_date: document.getElementById("due_date").value || null,
    estimated_hours: parseFloat(document.getElementById("estimated_hours").value) || 1,
    importance: parseInt(document.getElementById("importance").value) || 5,
    dependencies: (document.getElementById("dependencies").value || "").split(",").map(s=>s.trim()).filter(Boolean)
  };
  localTasks.push(t);
  document.getElementById("task-form").reset();
  alert("Task added locally. Click Analyze Tasks to send to API.");
});

document.getElementById("analyze-btn").addEventListener("click", async () => {
  let tasks = [...localTasks];
  const bulk = document.getElementById("bulk").value;
  if (bulk.trim()) {
    try {
      const arr = JSON.parse(bulk);
      if (Array.isArray(arr)) tasks = arr.concat(tasks);
    } catch (err) {
      alert("Bulk JSON invalid: " + err.message);
      return;
    }
  }
  if (tasks.length===0) {
    alert("No tasks provided.");
    return;
  }
  const strategy = document.getElementById("strategy").value || "smart";
  try {
    const res = await fetch(API_BASE + "analyze/?strategy=" + strategy, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({tasks})
    });
    if(!res.ok) {
      const err = await res.json();
      alert("API error: " + JSON.stringify(err));
      return;
    }
    const data = await res.json();
    showResults(data.tasks);
    const sres = await fetch(API_BASE + "suggest/?strategy=" + strategy, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({tasks})
    });
    const sdata = await sres.json();
    showSuggestions(sdata.suggestions || []);
  } catch (err) {
    alert("Network error: " + err.message);
  }
});

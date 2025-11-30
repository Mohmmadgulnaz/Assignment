Clone the Repository
type-->git clone <your-repo-url>
type-->cd task-analyzer

Backend Setup
type-->cd backend
type-->python -m venv venv

Windows:venv\Scripts\activate
Mac/Linux:source venv/bin/activate

Install dependencies:pip install -r requirements.txt

Apply migrations:python manage.py migrate

Run server:python manage.py runserver
Backend will be available at:http://127.0.0.1:8000

Frontend Setup
Option A — Open directly
frontend/index.html
Option B — Serve via static server (recommended)
cd frontend
python -m http.server 5500
Open:http://localhost:5500

Algorithm Explanation 

The Smart Task Analyzer uses a multi-factor scoring algorithm to determine which tasks should be prioritized first. Each task is evaluated using four major components: urgency, importance, effort, and dependency impact, all of which are normalized to ensure fairness and consistency regardless of scale.

1. Urgency is calculated from the number of days remaining until a task’s due date. A task that is due soon receives a higher urgency score, while a task that is past due receives an even stronger emphasis since it requires immediate attention. Tasks without a valid or missing due date are treated as tasks far in the future to avoid inflating urgency.

2. Importance is a user-provided rating on a 1–10 scale indicating how essential the task is. Prioritizing tasks that users deem important helps align the algorithm with real work priorities and human judgment. Higher importance yields a higher normalized score.

3. Effort represents the estimated number of hours required to complete a task. To promote productivity, effort is inverted in scoring (i.e., low-effort tasks score higher), enabling “quick wins.” Tasks with higher effort still receive some weight but are deprioritized compared to smaller tasks of equal importance and urgency.

4. Dependency Impact measures how many other tasks rely on the current one. If multiple tasks depend on Task A, then completing Task A unblocks future progress—making dependency impact vital in prioritization.

All these components are normalized (scaled between 0 and 1) to prevent any one factor from dominating. They are then combined using weighted formulas. Default weights are used for Smart Balance, but alternative strategies allow different behavior:

Fastest Wins → heavily weights low effort

High Impact → heavily weights importance

Deadline Driven → heavily weights urgency

Smart Balance → blends all factors proportionally

To detect circular dependencies (e.g., A depends on B, and B depends on A), the system uses a Depth-First Search (DFS) graph traversal. Any such cycles are returned and highlighted in the results, allowing the user to correct invalid structures.

The final score is calculated by combining all weighted factors, and tasks are sorted in descending order of priority. The system also provides explanations per task to make the results transparent and understandable.

Design Decisions
 Normalization
Ensures all scoring factors are comparable and fair.
 Inverted Effort
Promotes quick wins while still considering heavy tasks when strongly important or urgent.
 Weighted Strategy System
Allows multiple priority styles depending on user preference.
 Circular Dependency Detection
Implemented using DFS to meet assignment requirements.
 Simple JSON-based Task Input
Easy to test and easy for frontend and backend to communicate.
Clear API Separation
/analyze/ → full scoring and sorting
/suggest/ → top 3 recommended tasks

 

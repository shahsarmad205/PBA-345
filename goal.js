const token = localStorage.getItem("token");

// === TAB SWITCHING ===
const uncompletedTab = document.getElementById("uncompletedTab");
const completedTab = document.getElementById("completedTab");
const uncompletedGoals = document.getElementById("uncompletedGoals");
const completedGoals = document.getElementById("completedGoals");

uncompletedTab.addEventListener("click", () => {
  uncompletedTab.classList.add("active");
  completedTab.classList.remove("active");
  uncompletedGoals.style.display = "block";
  completedGoals.style.display = "none";
});

completedTab.addEventListener("click", () => {
  completedTab.classList.add("active");
  uncompletedTab.classList.remove("active");
  uncompletedGoals.style.display = "none";
  completedGoals.style.display = "block";
});

// === OPEN & CLOSE GOAL MODAL ===
function openGoalModal() {
  document.getElementById('goalModal').style.display = 'flex';
}

function closeGoalModal() {
  document.getElementById('goalModal').style.display = 'none';
}

// === FETCH GOALS ===
async function fetchGoals() {
  try {
    const response = await fetch("http://127.0.0.1:5001/api/goal/", {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!response.ok) throw new Error("Failed to fetch goals");

    const goals = await response.json();
    renderGoals(goals);
  } catch (error) {
    console.error("Fetch Goals Error:", error);
  }
}

// === RENDER GOALS ===
function renderGoals(goals) {
  const completedBody = document.getElementById("completed-goal-body");
  const uncompletedBody = document.getElementById("uncompleted-goal-body");

  completedBody.innerHTML = "";
  uncompletedBody.innerHTML = "";

  goals.forEach(goal => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${goal.name}</td>
      <td>${goal.deadline || 'N/A'}</td>
      <td>
        ${!goal.completed ? `
          <button onclick="markGoalComplete(${goal.id})">Mark Complete</button>
          <button onclick="editGoal(${goal.id})">Edit</button>` : ''}
        <button onclick="deleteGoal(${goal.id})">Delete</button>
      </td>
    `;
    (goal.completed ? completedBody : uncompletedBody).appendChild(row);
  });
}

// === SUBMIT NEW GOAL ===
document.getElementById('goalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const name = document.getElementById('goalName').value.trim();
  const targetAmount = parseFloat(document.getElementById('goalAmount').value);
  const deadline = document.getElementById('goalDate').value;
  const priority = document.getElementById('goalPriority').value;

  if (!name || isNaN(targetAmount) || !deadline || !priority) {
    alert("Please fill all fields correctly.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5001/api/goal/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        name,
        target_amount: targetAmount,
        current_amount: 0,
        deadline,
        priority,
        completed: false
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Failed to add goal");
    }

    alert("Goal added successfully!");
    closeGoalModal();
    e.target.reset();
    fetchGoals();
  } catch (err) {
    alert(`Add Goal Error: ${err.message}`);
  }
});

// === EDIT GOAL ===
async function editGoal(id) {
  const newName = prompt("Enter new goal name:");
  const newDeadline = prompt("Enter new deadline (YYYY-MM-DD):");

  if (!newName || !newDeadline) {
    alert("Invalid input.");
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:5001/api/goal/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ name: newName, deadline: newDeadline })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Failed to update goal");
    }

    alert("Goal updated successfully!");
    fetchGoals();
  } catch (error) {
    alert(`Edit Goal Error: ${error.message}`);
  }
}

// === DELETE GOAL ===
async function deleteGoal(id) {
  if (!confirm("Are you sure you want to delete this goal?")) return;

  try {
    const response = await fetch(`http://127.0.0.1:5001/api/goal/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Failed to delete goal");
    }

    alert("Goal deleted successfully!");
    fetchGoals();
  } catch (error) {
    alert(`Delete Goal Error: ${error.message}`);
  }
}

// === MARK GOAL COMPLETE ===
async function markGoalComplete(id) {
  try {
    const response = await fetch(`http://127.0.0.1:5001/api/goal/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ completed: true })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Failed to mark goal complete");
    }

    alert("Goal marked as complete!");
    fetchGoals();
  } catch (error) {
    alert(`Mark Complete Error: ${error.message}`);
  }
}

// === LOAD PAGE ===
fetchGoals();

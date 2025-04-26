document.addEventListener('DOMContentLoaded', () => {

  // === INCOME TABLE SETUP ===
  const existingIncomeRows = document.querySelectorAll(".income-table tbody tr");
  existingIncomeRows.forEach(row => attachRowActions(row));
  
  // === GOAL HANDLING ===
  const addGoalBtn = document.querySelector('.add-goal-btn');
  if (addGoalBtn) {
    addGoalBtn.addEventListener('click', addGoal);
  }

  const goalTitles = document.querySelectorAll('.goal-title');
  if (goalTitles.length > 0) updateGoalTitles();

  function updateGoalTitles() {
    goalTitles.forEach((title, index) => {
      title.textContent = `Goal ${index + 1}`;
    });
  }

  function addGoal() {
    const form = document.getElementById('goalForm');
    if (!form) return;

    const firstGroup = document.querySelector('.goal-group');
    if (!firstGroup) return;

    const newGroup = firstGroup.cloneNode(true);
    newGroup.querySelectorAll('input, select').forEach(field => {
      if (field.tagName === 'SELECT') field.selectedIndex = 0;
      else field.value = '';
    });

    const removeBtn = newGroup.querySelector('.remove-goal-btn');
    if (removeBtn) {
      removeBtn.style.display = 'inline-block';
      removeBtn.onclick = () => removeGoal(removeBtn);
    }

    form.insertBefore(newGroup, document.querySelector('.form-nav'));
    updateGoalTitles();
  }

  function removeGoal(button) {
    const group = button.closest('.goal-group');
    const allGroups = document.querySelectorAll('.goal-group');
    if (group && allGroups.length > 1) {
      group.remove();
      updateGoalTitles();
    }
  }

  // === SIGNUP ===
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const firstName = document.getElementById('firstName')?.value.trim();
      const lastName = document.getElementById('lastName')?.value.trim();
      const email = document.getElementById('email')?.value.trim();
      const password = document.getElementById('password')?.value;
      const confirmPassword = document.getElementById('confirmPassword')?.value;

      if (!/^(?=.*\d).{8,}$/.test(password)) {
        alert('Password must be at least 8 characters long and contain at least one number.');
        return;
      }

      if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
      }

      const formData = { first_name: firstName, last_name: lastName, email, password };

      try {
        const response = await fetch('http://127.0.0.1:5001/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Signup failed');
        }

        const result = await response.json();
        localStorage.setItem("token", result.token);
        await saveInitialExpenses(result.token);
        window.location.href = 'signup-income.html';
      } catch (error) {
        alert(`Signup Error: ${error.message}`);
      }
    });
  }
  async function saveInitialExpenses(token) {
    const today = new Date().toISOString().split("T")[0];
  
    const categories = document.querySelectorAll('.signup-expense-category');
    const amounts = document.querySelectorAll('.signup-expense-amount');
    const recurrings = document.querySelectorAll('.signup-expense-recurring');
  
    for (let i = 0; i < categories.length; i++) {
      const category = categories[i].value.trim();
      const amount = parseFloat(amounts[i].value);
      const recurring = recurrings[i].value === "true";
  
      if (!category || isNaN(amount)) continue; // Skip invalid entries
  
      await fetch("http://127.0.0.1:5001/api/expense/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ category, amount, recurring, date: today }),
      });
    }
  }
  

  // === LOGIN ===
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const email = document.getElementById('login-email')?.value.trim();
      const password = document.getElementById('login-password')?.value;

      try {
        const response = await fetch('http://127.0.0.1:5001/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Login failed');
        }

        const result = await response.json();
        localStorage.setItem("token", result.token);
        window.location.href = 'dashboard.html';
      } catch (error) {
        alert(`Login Error: ${error.message}`);
      }
    });
  }

  // === PROFILE EDIT & SAVE ===
const editIcons = document.querySelectorAll(".edit-icon");
editIcons.forEach((icon) => {
  icon.addEventListener("click", async () => {
    const section = icon.closest(".section");
    const isEditing = icon.classList.contains("editing");
    const rows = section.querySelectorAll(".field-row");

    if (isEditing) {
      // === SAVE MODE ===
      const updatedData = {};

      rows.forEach((row) => {
        const label = row.children[0].textContent.trim().toLowerCase().replace(/\s+/g, "_");
        const input = row.querySelector("input");
        if (input) {
          const value = input.value;
          const span = document.createElement("span");
          span.textContent = value;
          row.replaceChild(span, input);
          updatedData[label] = value;
        }
      });

      // Normalize field naming for backend
      if (updatedData.zip) {
        updatedData.zip_code = updatedData.zip;
        delete updatedData.zip;
      }

      try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:5001/api/profile/", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(updatedData),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || "Failed to save profile");
        }

        alert("Profile updated successfully!");
      } catch (error) {
        alert(`Save failed: ${error.message}`);
      }

      icon.textContent = "✏️";
      icon.classList.remove("editing");
    } else {
      // === EDIT MODE ===
      rows.forEach((row) => {
        const valueSpan = row.children[1];
        if (valueSpan && !valueSpan.querySelector("input")) {
          const input = document.createElement("input");
          input.type = "text";
          input.value = valueSpan.textContent.replace("$", "").replace(",", "");
          input.classList.add("editable-input");
          row.replaceChild(input, valueSpan);
        }
      });

      icon.textContent = "💾";
      icon.classList.add("editing");
    }
  });
});


  // === GUARD PROTECTED ROUTES ===
  const isProtected = document.body.classList.contains("auth-required");
  if (isProtected && !localStorage.getItem("token")) {
    alert("Please log in first.");
    window.location.href = "signin.html";
  }

  // === LOAD PROFILE DATA ===
  const isProfilePage = document.body.classList.contains("profile-page");
  if (isProfilePage) {
    const token = localStorage.getItem("token");
    fetch("http://127.0.0.1:5001/api/profile/", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch profile data");
        return res.json();
      })
      .then((data) => {
        document.getElementById("email-field").textContent = data.email || '';
        document.getElementById("address-field").textContent = data.address || '';
        document.getElementById("state-field").textContent = data.state || '';
        document.getElementById("zip-field").textContent = data.zip || '';
        document.getElementById("salary-field").textContent = data.salary != null ? `$${data.salary.toLocaleString()}` : '';
        document.getElementById("monthly-income-field").textContent = data.monthly_income != null ? `$${data.monthly_income.toLocaleString()}` : '';
        document.getElementById("password-field").textContent = "********";
      })
      .catch((error) => {
        console.error("Error fetching profile data:", error);
        alert("Failed to load profile data. Please try again later.");
      });
  }
});

// === EXPENSE TAB HANDLING ===
const recurringTab = document.getElementById("recurringTab");
const nonRecurringTab = document.getElementById("nonRecurringTab");

const recurringExpenses = document.getElementById("recurringExpenses");
const nonRecurringExpenses = document.getElementById("nonRecurringExpenses");

if (recurringTab && nonRecurringTab && recurringExpenses && nonRecurringExpenses) {
  recurringTab.addEventListener("click", () => {
    recurringTab.classList.add("active");
    nonRecurringTab.classList.remove("active");
    recurringExpenses.style.display = "block";
    nonRecurringExpenses.style.display = "none";
  });

  nonRecurringTab.addEventListener("click", () => {
    nonRecurringTab.classList.add("active");
    recurringTab.classList.remove("active");
    recurringExpenses.style.display = "none";
    nonRecurringExpenses.style.display = "block";
  });
}

// === EXPENSE BACKEND LOGIC ===
const token = localStorage.getItem("token");
const recurringBody = document.getElementById("recurring-expense-body");
const nonRecurringBody = document.getElementById("nonrecurring-expense-body");
const addCategoryBtn = document.getElementById("add-category-btn");

if (token && recurringBody && nonRecurringBody) {
  fetchExpenses();
}

function fetchExpenses() {
  fetch("http://127.0.0.1:5001/api/expense/?recurring=true", {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((res) => res.json())
    .then((data) => renderExpenseTable(data, recurringBody));

  fetch("http://127.0.0.1:5001/api/expense/?recurring=false", {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((res) => res.json())
    .then((data) => renderExpenseTable(data, nonRecurringBody));
}

function renderExpenseTable(data, tableBody) {
  tableBody.innerHTML = "";
  data.forEach((exp) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${exp.category}</td>
      <td>$${parseFloat(exp.amount).toLocaleString()}</td>
      <td>
        <button class="edit-expense-btn" data-id="${exp.id}" data-recurring="${exp.recurring}">Edit</button>
        <button class="delete-expense-btn" data-id="${exp.id}">Delete</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
  setupExpenseButtons();
}

let isEditing = false;
let editingId = null;

if (addCategoryBtn) {
  addCategoryBtn.addEventListener("click", () => {
    isEditing = false;
    editingId = null;
    document.getElementById("modal-category").value = "";
    document.getElementById("modal-amount").value = "";
    document.getElementById("modal-recurring").value = "true";
    document.getElementById("expense-modal").style.display = "flex";
  });
}

function setupExpenseButtons() {
  document.querySelectorAll(".edit-expense-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;
      const row = button.closest("tr");
      const category = row.children[0].textContent;
      const amount = row.children[1].textContent.replace(/\$|,/g, "");
      const isRecurring = button.dataset.recurring === "true";

      isEditing = true;
      editingId = id;

      document.getElementById("modal-category").value = category;
      document.getElementById("modal-amount").value = amount;
      document.getElementById("modal-recurring").value = isRecurring.toString();
      document.getElementById("expense-modal").style.display = "flex";
    });
  });

  document.querySelectorAll(".delete-expense-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;
      fetch(`http://127.0.0.1:5001/api/expense/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(() => fetchExpenses())
        .catch((err) => alert("Failed to delete expense"));
    });
  });
}

function submitModal() {
  const category = document.getElementById("modal-category").value.trim();
  const amount = document.getElementById("modal-amount").value.trim();
  const isRecurring = document.getElementById("modal-recurring").value === "true";

  if (!category || !amount || isNaN(amount)) {
    alert("Please enter a valid category and numeric amount.");
    return;
  }

  const today = new Date().toISOString().split("T")[0];
  const url = isEditing
    ? `http://127.0.0.1:5001/api/expense/${editingId}`
    : "http://127.0.0.1:5001/api/expense/";

  const method = isEditing ? "PUT" : "POST";

  fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      category,
      amount,
      recurring: isRecurring,
      date: today,
    }),
  })
    .then((res) => res.ok ? res.json() : res.json().then(err => { throw err }))
    .then(() => {
      closeModal();
      fetchExpenses();
    })
    .catch((err) => alert("Error: " + (err.error || "Request failed")));
}

function closeModal() {
  document.getElementById("expense-modal").style.display = "none";
}


// === GOAL TABS HANDLING ===
const uncompletedTab = document.getElementById("uncompletedTab");
const completedTab = document.getElementById("completedTab");
const uncompletedGoals = document.getElementById("uncompletedGoals");
const completedGoals = document.getElementById("completedGoals");

if (uncompletedTab && completedTab && uncompletedGoals && completedGoals) {
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

  fetchGoals();
}

function fetchGoals() {
  const token = localStorage.getItem("token");
  if (!token) return;

  fetch("http://127.0.0.1:5001/api/goal", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then((goals) => {
      const completedBody = document.getElementById("completed-goal-body");
      const uncompletedBody = document.getElementById("uncompleted-goal-body");
      completedBody.innerHTML = "";
      uncompletedBody.innerHTML = "";

      goals.forEach((goal) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${goal.name}</td>
          <td>$${goal.current_amount} / $${goal.target_amount}</td>
          <td>${goal.priority}</td>
          <td>${goal.deadline}</td>
        `;

        if (goal.completed) {
          completedBody.appendChild(row);
        } else {
          uncompletedBody.appendChild(row);
        }
      });
    })
    .catch((err) => console.error("Failed to fetch goals:", err));
}

 
 // === INCOME PAGE HANDLING ===

 function enableEdit(fieldId) {
  const inputField = document.getElementById(fieldId);
  if (inputField) {
    inputField.removeAttribute("readonly");
    inputField.focus();
    const saveBtn = document.getElementById("save-btn");
    if (saveBtn) saveBtn.style.display = "block";
  }
}

async function saveChanges() {
  const salaryInput = document.getElementById("salary");
  const monthlyIncomeInput = document.getElementById("monthlyIncome");
  const saveBtn = document.getElementById("save-btn");

  if (!salaryInput || !monthlyIncomeInput || !token) {
    alert("Missing inputs or token.");
    return;
  }

  const salary = parseFloat(salaryInput.value.replace(/\$|,/g, ""));
  const monthlyIncome = parseFloat(monthlyIncomeInput.value.replace(/\$|,/g, ""));

  if (isNaN(salary) || isNaN(monthlyIncome)) {
    alert("Please enter valid numeric values.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5001/api/profile/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ salary, monthly_income: monthlyIncome }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.message || "Failed to save income.");
    }

    salaryInput.setAttribute("readonly", true);
    monthlyIncomeInput.setAttribute("readonly", true);
    if (saveBtn) saveBtn.style.display = "none";
    alert("Income details saved successfully!");
  } catch (err) {
    alert("Error saving income: " + err.message);
  }
}

function addIncome() {
  const tableBody = document.querySelector(".income-table tbody");

  const newRow = document.createElement("tr");

  newRow.innerHTML = `
    <td><input type="text" placeholder="Source" class="source-input" /></td>
    <td><input type="number" placeholder="Amount" class="amount-input" /></td>
    <td>
      <button class="save-btn">Save</button>
      <button class="delete-btn">Delete</button>
    </td>
  `;

  // Save button behavior
  newRow.querySelector(".save-btn").addEventListener("click", () => {
    const source = newRow.querySelector(".source-input").value.trim();
    const amount = newRow.querySelector(".amount-input").value.trim();

    if (!source || isNaN(amount) || amount <= 0) {
      alert("Please enter a valid source and numeric amount.");
      return;
    }

    newRow.innerHTML = `
      <td>${source}</td>
      <td>$${parseFloat(amount).toLocaleString()}</td>
      <td>
        <button class="edit-btn">Edit</button>
        <button class="delete-btn">Delete</button>
      </td>
    `;

    attachRowActions(newRow); // Reattach Edit/Delete
  });

  // Delete button behavior
  newRow.querySelector(".delete-btn").addEventListener("click", () => {
    newRow.remove();
  });

  tableBody.appendChild(newRow);
}
function attachRowActions(row) {
  const editBtn = row.querySelector(".edit-btn");
  const deleteBtn = row.querySelector(".delete-btn");

  if (editBtn) {
    editBtn.addEventListener("click", () => {
      const source = row.children[0].textContent;
      const amount = row.children[1].textContent.replace(/\$|,/g, "");

      row.innerHTML = `
        <td><input type="text" value="${source}" class="source-input" /></td>
        <td><input type="number" value="${amount}" class="amount-input" /></td>
        <td>
          <button class="save-btn">Save</button>
          <button class="delete-btn">Delete</button>
        </td>
      `;

      row.querySelector(".save-btn").addEventListener("click", () => {
        const newSource = row.querySelector(".source-input").value.trim();
        const newAmount = row.querySelector(".amount-input").value.trim();

        if (!newSource || isNaN(newAmount) || newAmount <= 0) {
          alert("Please enter a valid source and amount.");
          return;
        }

        row.innerHTML = `
          <td>${newSource}</td>
          <td>$${parseFloat(newAmount).toLocaleString()}</td>
          <td>
            <button class="edit-btn">Edit</button>
            <button class="delete-btn">Delete</button>
          </td>
        `;

        attachRowActions(row); // rebind buttons after saving
      });

      row.querySelector(".delete-btn").addEventListener("click", () => {
        row.remove();
      });
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      row.remove();
    });
  }
}

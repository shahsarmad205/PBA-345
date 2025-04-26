// script.js - Handles dynamic behavior for BudgetMate signup steps

// === STEP 4: Financial Goals (Add / Remove) ===
function updateGoalTitles() {
    const goalTitles = document.querySelectorAll('.goal-title');
    goalTitles.forEach((title, index) => {
      title.textContent = `Goal ${index + 1}`;
    });
  }
  
  function addGoal() {
    const form = document.getElementById('goalForm');
    const firstGroup = document.querySelector('.goal-group');
    const newGroup = firstGroup.cloneNode(true);
  
    // Clear all inputs in the cloned group
    newGroup.querySelectorAll('input, select').forEach(field => {
      if (field.tagName === 'SELECT') {
        field.selectedIndex = 0;
      } else {
        field.value = '';
      }
    });
  
    // Show and attach remove button
    const removeBtn = newGroup.querySelector('.remove-goal-btn');
    removeBtn.style.display = 'inline-block';
    removeBtn.onclick = function () {
      removeGoal(this);
    };
  
    form.insertBefore(newGroup, document.querySelector('.form-nav'));
    updateGoalTitles(); // 👈 update numbers
  }
  
  function removeGoal(button) {
    const group = button.closest('.goal-group');
    const allGroups = document.querySelectorAll('.goal-group');
    if (allGroups.length > 1) {
      group.remove();
      updateGoalTitles(); // 👈 update numbers
    }
  }
  
  
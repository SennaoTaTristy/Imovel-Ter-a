document.getElementById('task-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/add', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(task => {
        const taskList = document.getElementById('task-list');
        const taskDiv = document.createElement('div');
        taskDiv.className = 'task';
        taskDiv.dataset.id = task.id;
        taskDiv.innerHTML = `
            <h2>${task.title}</h2>
            <p>${task.notes}</p>
            <input type="range" min="0" max="100" value="${task.progress}" class="progress-bar">
            <span>${task.progress}%</span>
        `;
        taskList.appendChild(taskDiv);
    });
});

document.getElementById('task-list').addEventListener('input', function(e) {
    if (e.target.classList.contains('progress-bar')) {
        const taskDiv = e.target.closest('.task');
        const taskId = taskDiv.dataset.id;
        const progress = e.target.value;
        fetch('/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `id=${taskId}&progress=${progress}`
        })
        .then(response => response.json())
        .then(task => {
            taskDiv.querySelector('span').textContent = `${task.progress}%`;
            if (task.completed) {
                const completedSpan = document.createElement('span');
                completedSpan.className = 'completed';
                completedSpan.textContent = 'Completado!';
                taskDiv.appendChild(completedSpan);
            }
        });
    }
});

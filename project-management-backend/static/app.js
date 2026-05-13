const API_URL = 'http://localhost:5000/api/v1';

let token = localStorage.getItem('access_token');
let currentUser = null;
let currentProjectId = null;
let projectData = null;

function showMsg(text, type) {
    const msg = document.getElementById('msg') || document.getElementById('msg-auth');
    msg.textContent = text;
    msg.className = `msg ${type}`;
    setTimeout(() => msg.className = 'msg', 4000);
}

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Auth
async function doLogin() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        showMsg('Заполните все поля', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.error || 'Ошибка входа');

        token = data.access_token;
        localStorage.setItem('access_token', token);
        currentUser = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));

        showView('projects');
        loadProjects();
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function doRegister() {
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;

    if (!username || username.length < 3) {
        showMsg('Имя пользователя: минимум 3 символа', 'error');
        return;
    }
    if (!email || !validateEmail(email)) {
        showMsg('Введите корректный email', 'error');
        return;
    }
    if (!password || password.length < 6) {
        showMsg('Пароль: минимум 6 символов', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, role: 'user' })
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.error || 'Ошибка регистрации');

        showMsg('Регистрация успешна! Войдите.', 'success');
        document.getElementById('tab-login').click();
        document.getElementById('login-username').value = username;
        document.getElementById('login-password').value = '';
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

function doLogout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    showView('auth');
}

function showView(view) {
    document.getElementById('auth-view').classList.add('hidden');
    document.getElementById('projects-view').classList.add('hidden');
    document.getElementById('project-detail-view').classList.add('hidden');
    document.getElementById('user-badge').classList.add('hidden');
    document.getElementById('user-badge').classList.remove('flex');

    if (view === 'auth') {
        document.getElementById('auth-view').classList.remove('hidden');
    } else if (view === 'projects') {
        document.getElementById('projects-view').classList.remove('hidden');
        document.getElementById('user-badge').classList.remove('hidden');
        document.getElementById('user-badge').classList.add('flex');
    } else if (view === 'detail') {
        document.getElementById('project-detail-view').classList.remove('hidden');
        document.getElementById('user-badge').classList.remove('hidden');
        document.getElementById('user-badge').classList.add('flex');
    }
}

async function apiRequest(endpoint, method, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_URL}${endpoint}`, options);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || 'Ошибка запроса');
    return data;
}

// Projects
async function loadProjects() {
    try {
        const data = await apiRequest('/projects', 'GET');
        renderProjects(data.projects);
        document.getElementById('user-name').textContent = currentUser.username;
        document.getElementById('projects-count').textContent = `${data.projects.length} проектов`;
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

function renderProjects(projects) {
    const container = document.getElementById('projects-list');

    if (projects.length === 0) {
        container.innerHTML = `
            <div class="card p-12 text-center col-span-2">
                <svg class="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
                <p class="text-lg text-[var(--text-secondary)] mb-2">Проектов пока нет</p>
                <p class="text-sm text-[var(--text-tertiary)]">Создайте первый проект выше</p>
            </div>
        `;
        return;
    }

    container.innerHTML = projects.map(p => `
        <div class="card p-5 cursor-pointer" onclick="openProject(${p.id}, '${escapeHtml(p.name)}')">
            <div class="flex items-start justify-between mb-3">
                <h3 class="font-semibold text-lg">${escapeHtml(p.name)}</h3>
                <div class="flex gap-2">
                    <button onclick="event.stopPropagation(); deleteProject(${p.id})" class="btn-ghost p-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                    </button>
                </div>
            </div>
            <p class="text-sm text-[var(--text-secondary)] mb-3">${escapeHtml(p.description) || 'Без описания'}</p>
            <div class="text-xs text-[var(--text-tertiary)] flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                ${p.created_at ? new Date(p.created_at).toLocaleDateString('ru-RU') : ''}
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

async function createProject() {
    const name = document.getElementById('new-project-name').value.trim();
    const description = document.getElementById('new-project-desc').value.trim();

    if (!name) {
        showMsg('Введите название проекта', 'error');
        return;
    }

    try {
        await apiRequest('/projects', 'POST', { name, description });
        document.getElementById('new-project-name').value = '';
        document.getElementById('new-project-desc').value = '';
        loadProjects();
        showMsg('Проект создан!', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function deleteProject(id) {
    if (!confirm('Удалить проект и все задачи?')) return;

    try {
        await apiRequest(`/projects/${id}`, 'DELETE');
        loadProjects();
        showMsg('Проект удалён', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

// Project Detail
async function openProject(projectId, projectName) {
    currentProjectId = projectId;

    try {
        const projectRes = await apiRequest(`/projects/${projectId}`, 'GET');
        projectData = projectRes.project;

        document.getElementById('project-title').value = projectData.name || '';
        document.getElementById('project-description').value = projectData.description || '';

        const tasksRes = await apiRequest(`/tasks/project/${projectId}`, 'GET');
        renderTasks(tasksRes.tasks);

        showView('detail');
        initSortable();
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

function backToProjects() {
    showView('projects');
    loadProjects();
}

async function saveProject() {
    const name = document.getElementById('project-title').value.trim();
    const description = document.getElementById('project-description').value.trim();

    if (!name) {
        showMsg('Введите название проекта', 'error');
        return;
    }

    try {
        await apiRequest(`/projects/${currentProjectId}`, 'PUT', { name, description });
        showMsg('Проект сохранён!', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

function reloadTasks() {
    apiRequest(`/tasks/project/${currentProjectId}`, 'GET')
        .then(data => renderTasks(data.tasks))
        .then(() => initSortable())
        .catch(e => showMsg(e.message, 'error'));
}

function renderTasks(tasks) {
    const container = document.getElementById('tasks-list');

    if (!tasks || tasks.length === 0) {
        container.innerHTML = `
            <div class="text-center py-16">
                <svg class="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                </svg>
                <p class="text-lg text-[var(--text-secondary)] mb-2">Задач пока нет</p>
                <p class="text-sm text-[var(--text-tertiary)]">Добавьте первую задачу выше</p>
            </div>
        `;
        return;
    }

    container.innerHTML = tasks.map(t => renderTaskCard(t, false)).join('');
}

function getStatusHtml(status, taskId) {
    const statusLabels = {
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'done': 'Done'
    };
    const currentLabel = statusLabels[status] || 'To Do';

    return `
        <div class="status-dropdown-wrapper relative">
            <button onclick="toggleStatusDropdown(${taskId})" class="status-badge status-${status}">
                ${currentLabel}
                <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
            </button>
            <div id="status-dropdown-${taskId}" class="status-dropdown">
                <div class="status-option" onclick="updateTaskStatus(${taskId}, 'todo')">
                    <span class="w-2 h-2 rounded-full bg-[var(--todo-color)]"></span>
                    To Do
                </div>
                <div class="status-option" onclick="updateTaskStatus(${taskId}, 'in_progress')">
                    <span class="w-2 h-2 rounded-full bg-[var(--in-progress-color)]"></span>
                    In Progress
                </div>
                <div class="status-option" onclick="updateTaskStatus(${taskId}, 'done')">
                    <span class="w-2 h-2 rounded-full bg-[var(--done-color)]"></span>
                    Done
                </div>
            </div>
        </div>
    `;
}

function toggleStatusDropdown(taskId) {
    document.querySelectorAll('.status-dropdown').forEach(d => {
        if (d.id !== `status-dropdown-${taskId}`) d.classList.remove('show');
    });
    const dropdown = document.getElementById(`status-dropdown-${taskId}`);
    dropdown.classList.toggle('show');
}

function renderTaskCard(task, isSubtask) {
    const statusClass = task.status === 'in_progress' ? 'in_progress' : (task.status === 'done' ? 'done' : '');
    const indentClass = isSubtask ? 'subtask-container' : '';

    let subtasksHtml = '';
    if (task.subtasks && task.subtasks.length > 0) {
        subtasksHtml = `<div class="subtasks-list mt-3 space-y-2">${task.subtasks.map(st => renderTaskCard(st, true)).join('')}</div>`;
    }

    return `
        <div class="task-card ${statusClass} ${indentClass}" data-id="${task.id}">
            <div class="flex items-start gap-3">
                <div class="sortable-handle pt-1 text-[var(--text-tertiary)]">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"/>
                    </svg>
                </div>

                <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex-1">
                            <input type="text" class="inline-edit text-base font-medium task-title w-full"
                                value="${escapeHtml(task.title)}"
                                onblur="updateTaskTitle(${task.id}, this.value)"
                                onclick="this.select()">
                            ${task.description ? `<p class="text-sm text-[var(--text-secondary)] mt-1 task-desc">${escapeHtml(task.description)}</p>` : ''}
                        </div>

                        <div class="flex items-center gap-2 flex-shrink-0">
                            ${getStatusHtml(task.status, task.id)}

                            <button onclick="toggleSubtaskForm(${task.id})" class="btn-ghost p-1.5" title="Добавить подзадачу">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                            </button>

                            <button onclick="deleteTask(${task.id})" class="btn-ghost p-1.5 text-[var(--danger)]" title="Удалить">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Subtask Form -->
                    <div id="subtask-form-${task.id}" class="subtask-form mt-3">
                        <div class="flex gap-2">
                            <input type="text" id="subtask-input-${task.id}" class="input flex-1 text-sm"
                                placeholder="Название подзадачи..."
                                onkeydown="if(event.key==='Enter') addSubtask(${task.id})">
                            <button onclick="addSubtask(${task.id})" class="btn-primary text-sm py-2">Добавить</button>
                            <button onclick="toggleSubtaskForm(${task.id})" class="btn-secondary text-sm py-2">Отмена</button>
                        </div>
                    </div>

                    ${subtasksHtml}
                </div>
            </div>
        </div>
    `;
}

function toggleSubtaskForm(taskId) {
    const form = document.getElementById(`subtask-form-${taskId}`);
    form.classList.toggle('show');
    if (form.classList.contains('show')) {
        document.getElementById(`subtask-input-${taskId}`).focus();
    }
}

// Tasks Actions
async function createTask() {
    const title = document.getElementById('new-task-title').value.trim();

    if (!title) {
        showMsg('Введите название задачи', 'error');
        return;
    }

    try {
        await apiRequest('/tasks', 'POST', {
            title,
            description: '',
            project_id: currentProjectId
        });
        document.getElementById('new-task-title').value = '';
        reloadTasks();
        showMsg('Задача добавлена!', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function addSubtask(parentId) {
    const input = document.getElementById(`subtask-input-${parentId}`);
    const title = input.value.trim();

    if (!title) return;

    try {
        await apiRequest('/tasks', 'POST', {
            title,
            description: '',
            project_id: currentProjectId,
            parent_id: parentId
        });
        reloadTasks();
        showMsg('Подзадача добавлена!', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function updateTaskTitle(taskId, title) {
    if (!title.trim()) {
        reloadTasks();
        return;
    }

    try {
        await apiRequest(`/tasks/${taskId}`, 'PUT', { title: title.trim() });
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function updateTaskStatus(taskId, status) {
    try {
        await apiRequest(`/tasks/${taskId}`, 'PUT', { status });
        reloadTasks();
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Удалить задачу?')) return;

    try {
        await apiRequest(`/tasks/${taskId}`, 'DELETE');
        reloadTasks();
        showMsg('Задача удалена', 'success');
    } catch (e) {
        showMsg(e.message, 'error');
    }
}

// Drag & Drop with SortableJS
function initSortable() {
    if (window.Sortable) {
        const tasksList = document.getElementById('tasks-list');
        new Sortable(tasksList, {
            animation: 150,
            handle: '.sortable-handle',
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onEnd: function(evt) {
                // Reorder logic would go here
                console.log('Moved task from', evt.oldIndex, 'to', evt.newIndex);
            }
        });

        // Also make subtasks sortable
        document.querySelectorAll('.subtasks-list').forEach(list => {
            new Sortable(list, {
                animation: 150,
                handle: '.sortable-handle',
                ghostClass: 'sortable-ghost',
            });
        });
    }
}

// Init
const savedUser = localStorage.getItem('user');
if (token && savedUser) {
    currentUser = JSON.parse(savedUser);
    showView('projects');
    loadProjects();
}
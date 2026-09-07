const API_BASE = '/api';

// --- НАВИГАЦИЯ ---
document.querySelectorAll('nav ul li').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('nav ul li').forEach(el => el.classList.remove('active'));
        this.classList.add('active');
        const tabId = this.dataset.tab;
        document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');
        if (tabId === 'dashboard') loadDashboard();
        if (tabId === 'product') loadProduct();
        if (tabId === 'intents') loadIntents();
        if (tabId === 'goals') loadGoals();
        if (tabId === 'sources') loadSources();
        if (tabId === 'settings') { loadSettings(); loadClientList(); }
        if (tabId === 'leads') loadLeads();
        if (tabId === 'modules') loadModules();
        if (tabId === 'logs') loadLogs();
    });
});

// --- ЧАСЫ ---
function updateClock() {
    document.getElementById('time').textContent = new Date().toLocaleString();
}
setInterval(updateClock, 1000);
updateClock();

// --- ДАШБОРД ---
async function loadDashboard() {
    try {
        const resp = await fetch(`${API_BASE}/leads?limit=1`);
        const data = await resp.json();
        document.getElementById('total-leads').textContent = data.total || 0;
        const stats = await fetch(`${API_BASE}/leads/status-stats`).then(r => r.json());
        document.getElementById('converted-leads').textContent = stats.converted || 0;
        const rate = data.total > 0 ? Math.round((stats.converted / data.total) * 100) : 0;
        document.getElementById('conversion-rate').textContent = rate + '%';
        const funnel = await fetch(`${API_BASE}/leads/funnel`).then(r => r.json());
        document.getElementById('stage-new').textContent = funnel.new || 0;
        document.getElementById('stage-contacted').textContent = funnel.contacted || 0;
        document.getElementById('stage-in_progress').textContent = funnel.in_progress || 0;
        document.getElementById('stage-closing').textContent = funnel.closing || 0;
        document.getElementById('stage-converted').textContent = funnel.converted || 0;
    } catch(e) { console.error(e); }
}

// --- ТОВАР ---
async function loadProduct() {
    try {
        const resp = await fetch(`${API_BASE}/product`);
        const data = await resp.json();
        if (data) {
            document.getElementById('product-name').value = data.name || '';
            document.getElementById('product-category').value = data.category || '';
            document.getElementById('product-attributes').value = (data.attributes || []).join(', ');
            document.getElementById('product-keywords').value = (data.keywords || []).join(', ');
            document.getElementById('product-industries').value = (data.industries || []).join(', ');
            document.getElementById('product-regions').value = (data.regions || []).join(', ');
        }
    } catch(e) { console.error(e); }
}
document.getElementById('product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('product-name').value,
        category: document.getElementById('product-category').value,
        attributes: document.getElementById('product-attributes').value.split(',').map(s => s.trim()).filter(Boolean),
        keywords: document.getElementById('product-keywords').value.split(',').map(s => s.trim()).filter(Boolean),
        industries: document.getElementById('product-industries').value.split(',').map(s => s.trim()).filter(Boolean),
        regions: document.getElementById('product-regions').value.split(',').map(s => s.trim()).filter(Boolean),
    };
    await fetch(`${API_BASE}/product`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    alert('Сохранено!');
});

// --- ИНТЕНТЫ ---
async function loadIntents() {
    try {
        const resp = await fetch(`${API_BASE}/intents`);
        const data = await resp.json();
        document.getElementById('intent-buying').value = (data.buying || []).join(', ');
        document.getElementById('intent-problem').value = (data.problem || []).join(', ');
        document.getElementById('intent-seeking').value = (data.seeking || []).join(', ');
        document.getElementById('intent-urgency').value = (data.urgency || []).join(', ');
    } catch(e) { console.error(e); }
}
document.getElementById('intents-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        buying: document.getElementById('intent-buying').value.split(',').map(s => s.trim()).filter(Boolean),
        problem: document.getElementById('intent-problem').value.split(',').map(s => s.trim()).filter(Boolean),
        seeking: document.getElementById('intent-seeking').value.split(',').map(s => s.trim()).filter(Boolean),
        urgency: document.getElementById('intent-urgency').value.split(',').map(s => s.trim()).filter(Boolean),
    };
    await fetch(`${API_BASE}/intents`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    alert('Сохранено!');
});

// --- ЦЕЛИ ---
async function loadGoals() {
    try {
        const resp = await fetch(`${API_BASE}/goals`);
        const data = await resp.json();
        let html = '';
        data.goals.forEach(g => {
            const triggerLabels = { 'link': '🔗 Ссылка', 'keyword': '📝 Ключевая фраза', 'action': '⚡ Действие', 'button': '🔘 Кнопка' };
            html += `<div class="goal-card">
                <div class="goal-info">
                    <span class="goal-name">🏆 ${g.name}</span>
                    <span class="goal-details">Триггер: ${triggerLabels[g.trigger_type] || g.trigger_type} → "${g.trigger_value}"</span>
                    <span class="goal-details" style="color: #888; font-size: 12px;">${g.description || ''}</span>
                </div>
                <div class="goal-actions">
                    <button class="btn-delete" data-id="${g.id}">🗑 Удалить</button>
                </div>
            </div>`;
        });
        document.getElementById('goals-list').innerHTML = html || '<p>Нет целей</p>';
        document.querySelectorAll('.goal-card .btn-delete').forEach(btn => {
            btn.addEventListener('click', async function() {
                if (confirm('Удалить цель?')) {
                    const id = this.dataset.id;
                    await fetch(`${API_BASE}/goals/${id}`, { method: 'DELETE' });
                    loadGoals();
                }
            });
        });
    } catch(e) { console.error(e); }
}
document.getElementById('add-goal-btn').addEventListener('click', async function() {
    const name = document.getElementById('goal-name').value.trim();
    const trigger_type = document.getElementById('goal-trigger-type').value;
    const trigger_value = document.getElementById('goal-trigger-value').value.trim();
    const priority = parseInt(document.getElementById('goal-priority').value) || 1;
    const indicators = document.getElementById('goal-indicators').value.split(',').map(s => s.trim()).filter(Boolean);
    const description = document.getElementById('goal-description').value.trim();
    if (!name || !trigger_value) { alert('Заполните название и значение триггера'); return; }
    await fetch(`${API_BASE}/goals`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description, trigger_type, trigger_value, success_indicators: indicators, priority }) });
    document.getElementById('goal-name').value = '';
    document.getElementById('goal-trigger-value').value = '';
    document.getElementById('goal-indicators').value = '';
    document.getElementById('goal-description').value = '';
    loadGoals();
});

// --- ИСТОЧНИКИ ---
async function loadSources() {
    try {
        const resp = await fetch(`${API_BASE}/sources`);
        const data = await resp.json();
        let html = '<div class="sources-grid">';
        data.sources.forEach(s => {
            html += `<div class="source-card">
                <span class="source-name">${s.platform === 'telegram' ? '✈️' : s.platform === 'reddit' ? '🔴' : '📱'} ${s.name}</span>
                <span class="source-platform">${s.platform}</span>
                <span class="source-status ${s.enabled ? 'enabled' : 'disabled'}">${s.enabled ? '✅ Включен' : '❌ Отключен'}</span>
                <div class="source-actions">
                    <button class="btn-toggle" data-id="${s.id}" data-enabled="${s.enabled}">${s.enabled ? '⏹ Выключить' : '▶ Включить'}</button>
                    <button class="btn-delete" data-id="${s.id}">🗑 Удалить</button>
                </div>
            </div>`;
        });
        html += '</div>';
        document.getElementById('sources-list').innerHTML = html || '<p>Нет источников</p>';
        document.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', async function() {
                const id = this.dataset.id;
                const enabled = this.dataset.enabled === 'true';
                await fetch(`${API_BASE}/sources/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: !enabled })
                });
                loadSources();
            });
        });
        document.querySelectorAll('.source-card .btn-delete').forEach(btn => {
            btn.addEventListener('click', async function() {
                if (confirm('Удалить источник?')) {
                    const id = this.dataset.id;
                    await fetch(`${API_BASE}/sources/${id}`, { method: 'DELETE' });
                    loadSources();
                }
            });
        });
    } catch(e) { console.error(e); }
}
document.getElementById('add-source-btn').addEventListener('click', async () => {
    const platform = document.getElementById('source-platform').value;
    const name = document.getElementById('source-name').value.trim();
    if (!name) { alert('Введите название чата'); return; }
    await fetch(`${API_BASE}/sources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, name, enabled: true })
    });
    document.getElementById('source-name').value = '';
    loadSources();
});

// --- НАСТРОЙКИ (ОБЩИЕ) ---
async function loadSettings() {
    try {
        const resp = await fetch(`${API_BASE}/settings/proactive`);
        const data = await resp.json();
        document.getElementById('proactive-enabled').checked = data.enabled;
        updateProactiveLabel(data.enabled);
        document.getElementById('min-score').value = data.min_intent_score || 40;
        document.getElementById('min-score-value').textContent = (data.min_intent_score || 40) + '%';
        document.getElementById('greeting-template').value = data.greeting_template || '';
        const blacklistResp = await fetch(`${API_BASE}/settings/blacklist`);
        const blacklistData = await blacklistResp.json();
        renderBlacklist(blacklistData.blacklist || []);
    } catch(e) { console.error(e); }
}

function updateProactiveLabel(enabled) {
    const label = document.getElementById('proactive-status-label');
    if (enabled) {
        label.textContent = 'Отправка активных сообщений ВКЛЮЧЕНА';
        label.style.color = '#4ade80';
    } else {
        label.textContent = 'Отправка активных сообщений ОТКЛЮЧЕНА';
        label.style.color = '#f87171';
    }
}

document.getElementById('proactive-enabled').addEventListener('change', function() {
    updateProactiveLabel(this.checked);
});

document.getElementById('min-score').addEventListener('input', function() {
    document.getElementById('min-score-value').textContent = this.value + '%';
});

document.getElementById('settings-save-btn').addEventListener('click', async function() {
    const data = {
        enabled: document.getElementById('proactive-enabled').checked,
        min_intent_score: parseInt(document.getElementById('min-score').value),
        max_messages_per_day: 10,
        cooldown_minutes: 60,
        greeting_template: document.getElementById('greeting-template').value,
        timezone: 'Europe/Moscow',
        working_hours_start: '09:00',
        working_hours_end: '21:00'
    };
    try {
        await fetch(`${API_BASE}/settings/proactive`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        alert('✅ Настройки сохранены!');
    } catch(e) {
        alert('❌ Ошибка сохранения');
        console.error(e);
    }
});

// --- ЧЕРНЫЙ СПИСОК ---
async function renderBlacklist(blacklist) {
    const container = document.getElementById('blacklist-list');
    if (!blacklist || blacklist.length === 0) {
        container.innerHTML = '<p>Нет пользователей в черном списке</p>';
        return;
    }
    let html = '';
    blacklist.forEach(userId => {
        html += `<div class="blacklist-item">
            <span>🛑 ${userId}</span>
            <button class="remove-btn" data-user="${userId}">✕</button>
        </div>`;
    });
    container.innerHTML = html;
    document.querySelectorAll('.blacklist-item .remove-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const userId = this.dataset.user;
            await fetch(`${API_BASE}/settings/blacklist/${userId}`, { method: 'DELETE' });
            loadSettings();
        });
    });
}

document.getElementById('blacklist-add-btn').addEventListener('click', async function() {
    const input = document.getElementById('blacklist-input');
    const userId = input.value.trim();
    if (!userId) { alert('Введите ID пользователя'); return; }
    await fetch(`${API_BASE}/settings/blacklist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    input.value = '';
    loadSettings();
});

// --- НАСТРОЙКИ ДЛЯ КЛИЕНТА ---
async function loadClientList() {
    try {
        const resp = await fetch(`${API_BASE}/leads?limit=100`);
        const data = await resp.json();
        const select = document.getElementById('ai-client-select');
        select.innerHTML = '<option value="">-- Выберите клиента --</option>';
        data.leads.forEach(lead => {
            const option = document.createElement('option');
            option.value = lead.user_id;
            option.textContent = `${lead.user_id || 'Без ID'} (${lead.intent_score || 0}%)`;
            select.appendChild(option);
        });
    } catch(e) { console.error(e); }
}

document.getElementById('ai-client-load-btn').addEventListener('click', async function() {
    const userId = document.getElementById('ai-client-select').value;
    if (!userId) { alert('Выберите клиента'); return; }
    await loadClientSettings(userId);
});

async function loadClientSettings(userId) {
    try {
        const resp = await fetch(`${API_BASE}/settings/client/${userId}`);
        const data = await resp.json();
        const settings = data.settings || {};
        
        document.getElementById('ai-client-settings').style.display = 'block';
        
        // Профиль
        document.getElementById('ai-visual').textContent = (settings.profile?.visual || 0) + '%';
        document.getElementById('ai-audial').textContent = (settings.profile?.audial || 0) + '%';
        document.getElementById('ai-logical').textContent = (settings.profile?.logical || 0) + '%';
        document.getElementById('ai-kinesthetic').textContent = (settings.profile?.kinesthetic || 0) + '%';
        document.getElementById('ai-intent').textContent = settings.intent || '-';
        document.getElementById('ai-region').textContent = settings.region || '-';
        document.getElementById('ai-product').textContent = settings.product || '-';
        document.getElementById('ai-status').textContent = settings.status || '-';
        
        // Последнее сообщение
        document.getElementById('ai-last-message').textContent = settings.last_message || 'Нет сообщений';
        document.getElementById('ai-message-time').textContent = settings.last_message_time || '';
        
        // Роль
        document.getElementById('ai-role').value = settings.role || 'Консультант';
        
        // Стратегия
        document.getElementById('ai-strategy').value = settings.strategy || 'classic';
        updateStrategyDescription(settings.strategy || 'classic');
        
        // Этапы
        const stages = settings.stages || getDefaultStages(settings.strategy || 'classic');
        renderStages(stages);
        
        // Параметры
        document.getElementById('ai-max-chars').value = settings.max_chars || 500;
        document.getElementById('ai-temperature').value = settings.temperature || 0.7;
        document.getElementById('ai-temperature-value').textContent = settings.temperature || 0.7;
        
        // Режим общения
        const mode = settings.communication_mode || 'wait';
        document.querySelector(`input[name="communication-mode"][value="${mode}"]`).checked = true;
        
        // Сохраняем userId для сохранения
        document.getElementById('ai-client-settings').dataset.userId = userId;
        
    } catch(e) {
        console.error(e);
        alert('Ошибка загрузки настроек клиента');
    }
}

function updateStrategyDescription(strategy) {
    const descriptions = {
        'classic': 'Приветствие → Потребности → Презентация → Возражения → Закрытие',
        'problem_solution': 'Проблема → Причина → Решение → Действие',
        'emotional': 'Эмоция → Проблема → Решение → Выгода → Возражения → Закрытие',
        'rational': 'Факты → Сравнение → Выгода → Действие',
        'custom': 'Свой набор этапов'
    };
    document.getElementById('ai-strategy-description').textContent = descriptions[strategy] || '';
}

function getDefaultStages(strategy) {
    const stages = {
        'classic': [
            { id: '1', name: 'Приветствие', instruction: 'Коротко представиться, узнать имя клиента' },
            { id: '2', name: 'Выяснение потребностей', instruction: 'Спросить про бюджет, объем, сроки' },
            { id: '3', name: 'Презентация товара', instruction: 'Акцент на выгодах для клиента' },
            { id: '4', name: 'Работа с возражениями', instruction: 'Сравнить с конкурентами, дать гарантии' },
            { id: '5', name: 'Закрытие сделки', instruction: 'Четкое предложение + ограничение по времени' }
        ],
        'problem_solution': [
            { id: '1', name: 'Выявление проблемы', instruction: 'Узнать, что не устраивает клиента сейчас' },
            { id: '2', name: 'Анализ причины', instruction: 'Понять, почему это проблема' },
            { id: '3', name: 'Предложение решения', instruction: 'Показать, как товар решает проблему' },
            { id: '4', name: 'Призыв к действию', instruction: 'Предложить купить прямо сейчас' }
        ],
        'emotional': [
            { id: '1', name: 'Эмоциональный контакт', instruction: 'Создать доверие и комфорт' },
            { id: '2', name: 'Выявление боли', instruction: 'Узнать, что беспокоит клиента' },
            { id: '3', name: 'Предложение решения', instruction: 'Показать, как товар меняет жизнь' },
            { id: '4', name: 'Демонстрация выгоды', instruction: 'Показать, что получит клиент' },
            { id: '5', name: 'Работа с возражениями', instruction: 'Убрать сомнения' },
            { id: '6', name: 'Закрытие', instruction: 'Предложить купить с эмоциональным акцентом' }
        ],
        'rational': [
            { id: '1', name: 'Факты', instruction: 'Дать четкие характеристики товара' },
            { id: '2', name: 'Сравнение', instruction: 'Сравнить с конкурентами по цифрам' },
            { id: '3', name: 'Выгода', instruction: 'Показать экономию или преимущества' },
            { id: '4', name: 'Действие', instruction: 'Предложить купить с гарантией' }
        ],
        'custom': []
    };
    return stages[strategy] || stages['classic'];
}

function renderStages(stages) {
    const container = document.getElementById('stages-container');
    if (!stages || stages.length === 0) {
        container.innerHTML = '<p style="color: #888;">Нет этапов. Добавьте первый этап.</p>';
        return;
    }
    let html = '';
    stages.forEach((stage, index) => {
        html += `<div class="stage-item" style="background: #f8f9fa; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #60a5fa;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span style="font-weight: 600; min-width: 30px;">${index + 1}.</span>
                <input type="text" value="${stage.name || ''}" placeholder="Название этапа" style="flex: 1; min-width: 150px; padding: 5px 10px; border: 1px solid #ddd; border-radius: 4px;" class="stage-name">
                <input type="text" value="${stage.instruction || ''}" placeholder="Инструкция" style="flex: 2; min-width: 200px; padding: 5px 10px; border: 1px solid #ddd; border-radius: 4px;" class="stage-instruction">
                <button class="btn-remove-stage" style="background: #f87171; color: white; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer;">✕</button>
            </div>
        </div>`;
    });
    container.innerHTML = html;
    
    document.querySelectorAll('.btn-remove-stage').forEach((btn, index) => {
        btn.addEventListener('click', function() {
            const items = container.querySelectorAll('.stage-item');
            if (items.length <= 1) {
                alert('Нельзя удалить последний этап');
                return;
            }
            this.closest('.stage-item').remove();
        });
    });
}

document.getElementById('add-stage-btn').addEventListener('click', function() {
    const container = document.getElementById('stages-container');
    const newStage = document.createElement('div');
    newStage.className = 'stage-item';
    newStage.style.cssText = 'background: #f8f9fa; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #60a5fa;';
    const count = container.querySelectorAll('.stage-item').length + 1;
    newStage.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span style="font-weight: 600; min-width: 30px;">${count}.</span>
            <input type="text" placeholder="Название этапа" style="flex: 1; min-width: 150px; padding: 5px 10px; border: 1px solid #ddd; border-radius: 4px;" class="stage-name">
            <input type="text" placeholder="Инструкция" style="flex: 2; min-width: 200px; padding: 5px 10px; border: 1px solid #ddd; border-radius: 4px;" class="stage-instruction">
            <button class="btn-remove-stage" style="background: #f87171; color: white; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer;">✕</button>
        </div>
    `;
    container.appendChild(newStage);
    newStage.querySelector('.btn-remove-stage').addEventListener('click', function() {
        const items = container.querySelectorAll('.stage-item');
        if (items.length <= 1) {
            alert('Нельзя удалить последний этап');
            return;
        }
        this.closest('.stage-item').remove();
    });
});

document.getElementById('ai-strategy').addEventListener('change', function() {
    const strategy = this.value;
    updateStrategyDescription(strategy);
    const stages = getDefaultStages(strategy);
    renderStages(stages);
});

document.getElementById('ai-temperature').addEventListener('input', function() {
    document.getElementById('ai-temperature-value').textContent = this.value;
});

document.getElementById('ai-client-save-btn').addEventListener('click', async function() {
    const userId = document.getElementById('ai-client-settings').dataset.userId;
    if (!userId) { alert('Выберите клиента'); return; }
    
    const stages = [];
    document.querySelectorAll('#stages-container .stage-item').forEach(item => {
        const name = item.querySelector('.stage-name').value;
        const instruction = item.querySelector('.stage-instruction').value;
        if (name || instruction) {
            stages.push({ id: String(stages.length + 1), name: name || 'Этап', instruction: instruction || '' });
        }
    });
    
    const mode = document.querySelector('input[name="communication-mode"]:checked').value;
    const role = document.getElementById('ai-role').value;
    const customRole = document.getElementById('ai-custom-role').value;
    
    const data = {
        role: role === 'Свой вариант' ? customRole : role,
        stages: stages,
        strategy: document.getElementById('ai-strategy').value,
        communication_mode: mode,
        max_chars: parseInt(document.getElementById('ai-max-chars').value) || 500,
        temperature: parseFloat(document.getElementById('ai-temperature').value) || 0.7
    };
    
    try {
        await fetch(`${API_BASE}/settings/client/${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        alert('✅ Настройки для клиента сохранены!');
    } catch(e) {
        alert('❌ Ошибка сохранения');
        console.error(e);
    }
});

// --- КЛИЕНТЫ ---
async function loadLeads() {
    const status = document.getElementById('lead-filter-status').value;
    const score = document.getElementById('lead-filter-score').value;
    let url = `${API_BASE}/leads?limit=50`;
    if (status) url += `&status=${status}`;
    if (score) url += `&min_score=${score}`;
    try {
        const resp = await fetch(url);
        const data = await resp.json();
        let html = '<table><thead><tr><th>ID</th><th>Пользователь</th><th>Сообщение</th><th>Источник</th><th>Интент</th><th>Score</th><th>Статус</th></tr></thead><tbody>';
        data.leads.forEach(l => {
            html += `<tr>
                <td>${l.id}</td>
                <td>${l.username || l.user_id}</td>
                <td>${l.message || ''}</td>
                <td>${l.source || ''}</td>
                <td>${l.intent || ''}</td>
                <td>${l.intent_score || 0}</td>
                <td><span class="status-badge ${l.status || 'new'}">${l.status || 'new'}</span></td>
            </tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('leads-table-container').innerHTML = html || '<p>Нет клиентов</p>';
    } catch(e) { console.error(e); }
}
document.getElementById('lead-filter-btn').addEventListener('click', loadLeads);

// --- МОДУЛИ ---
async function loadModules() {
    try {
        const resp = await fetch(`${API_BASE}/modules`);
        const data = await resp.json();
        let html = '';
        for (const [name, status] of Object.entries(data)) {
            const running = status.running;
            html += `<div class="module-card">
                <span class="module-name">${name}</span>
                <span class="module-status ${running ? 'running' : 'stopped'}">${running ? '● Запущен' : '○ Остановлен'}</span>
                <div class="module-controls">
                    <button class="btn-start" data-module="${name}" data-action="start">▶ Старт</button>
                    <button class="btn-stop" data-module="${name}" data-action="stop">⏹ Стоп</button>
                    <button class="btn-restart" data-module="${name}" data-action="restart">⟳ Рестарт</button>
                </div>
            </div>`;
        }
        document.getElementById('modules-container').innerHTML = html;
        document.querySelectorAll('.module-controls button').forEach(btn => {
            btn.addEventListener('click', async function() {
                const module = this.dataset.module;
                const action = this.dataset.action;
                await fetch(`${API_BASE}/modules/${module}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action }) });
                loadModules();
            });
        });
    } catch(e) { console.error(e); }
}

// --- ЛОГИ ---
async function loadLogs() {
    const module = document.getElementById('log-module').value;
    try {
        const resp = await fetch(`${API_BASE}/logs?module=${module}&lines=100`);
        const text = await resp.text();
        document.getElementById('log-content').textContent = text;
    } catch(e) { console.error(e); }
}
document.getElementById('log-refresh-btn').addEventListener('click', loadLogs);

// --- ЗАГРУЗКА ПРИ СТАРТЕ ---
loadDashboard();

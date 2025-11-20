/**
 * Settings Page JavaScript
 * Handles system configuration and logo management
 */

let currentLogoId = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    // Require authentication
    if (!Auth.requireAuth()) {
        return;
    }

    // Load user info
    loadUserInfo();

    // Load current configuration
    loadConfig();

    // Load active logo
    loadActiveLogo();

    // Setup form submissions
    setupFormHandlers();

    // Setup drag and drop for logo upload
    setupDragAndDrop();

    // Load theme from localStorage
    loadTheme();
});

/**
 * Load user information into sidebar
 */
function loadUserInfo() {
    const user = Auth.getCurrentUser();
    if (user) {
        document.getElementById('user-name').textContent = user.full_name || 'Usuario';
        document.getElementById('user-username').textContent = `@${user.username}`;

        // Display roles
        const rolesContainer = document.getElementById('user-roles');
        rolesContainer.innerHTML = '';
        if (user.roles && user.roles.length > 0) {
            user.roles.forEach(role => {
                const badge = document.createElement('span');
                badge.className = 'px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs';
                badge.textContent = role;
                rolesContainer.appendChild(badge);
            });
        }
    }
}

/**
 * Load system configuration from API
 */
async function loadConfig() {
    try {
        const response = await axios.get('/api/config/system', {
            headers: {
                'Authorization': `Bearer ${Auth.getAccessToken()}`
            }
        });

        const config = response.data;

        // Populate form fields
        document.getElementById('company_name').value = config.company_name || '';
        document.getElementById('company_email').value = config.company_email || '';
        document.getElementById('company_address').value = config.company_address || '';
        document.getElementById('company_phone').value = config.company_phone || '';
        document.getElementById('timezone').value = config.timezone || 'America/Santo_Domingo';
        document.getElementById('language').value = config.language || 'es';
        document.getElementById('reports_email').value = config.reports_email || '';

        // Set theme radio button
        const themeRadios = document.querySelectorAll('input[name="theme"]');
        themeRadios.forEach(radio => {
            if (radio.value === config.theme) {
                radio.checked = true;
            }
        });

    } catch (error) {
        console.error('Error loading configuration:', error);
        if (error.response && error.response.status === 401) {
            Auth.logout();
        } else {
            showNotification('Error al cargar la configuración', 'error');
        }
    }
}

/**
 * Load active logo
 */
async function loadActiveLogo() {
    try {
        const response = await axios.get('/api/config/logo/active', {
            headers: {
                'Authorization': `Bearer ${Auth.getAccessToken()}`
            }
        });

        if (response.data && response.data.id) {
            currentLogoId = response.data.id;
            displayLogo(response.data);
        } else {
            // No logo active
            currentLogoId = null;
            displayNoLogo();
        }

    } catch (error) {
        console.error('Error loading logo:', error);
        if (error.response && error.response.status === 404) {
            // No logo found, this is okay
            displayNoLogo();
        } else if (error.response && error.response.status === 401) {
            Auth.logout();
        }
    }
}

/**
 * Display logo in preview area
 */
function displayLogo(logoData) {
    const preview = document.getElementById('logo-preview');
    preview.innerHTML = `<img src="/api/config/logo/file/${logoData.id}" alt="Logo" />`;

    // Show delete button
    const deleteBtn = document.getElementById('delete-logo-btn');
    if (deleteBtn) {
        deleteBtn.style.display = 'flex';
    }
}

/**
 * Display "no logo" placeholder
 */
function displayNoLogo() {
    const preview = document.getElementById('logo-preview');
    preview.innerHTML = `
        <div class="text-center" style="color: var(--text-secondary);">
            <i class="fas fa-image text-4xl mb-2"></i>
            <p class="text-sm">No hay logo activo</p>
        </div>
    `;

    // Hide delete button
    const deleteBtn = document.getElementById('delete-logo-btn');
    if (deleteBtn) {
        deleteBtn.style.display = 'none';
    }
}

/**
 * Setup form submission handlers
 */
function setupFormHandlers() {
    // Company form submission
    document.getElementById('company-form').addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            company_name: document.getElementById('company_name').value,
            company_email: document.getElementById('company_email').value || null,
            company_address: document.getElementById('company_address').value || null,
            company_phone: document.getElementById('company_phone').value || null,
            timezone: document.getElementById('timezone').value,
            language: document.getElementById('language').value,
            reports_email: document.getElementById('reports_email').value || null
        };

        try {
            const response = await axios.put('/api/config/system', formData, {
                headers: {
                    'Authorization': `Bearer ${Auth.getAccessToken()}`,
                    'Content-Type': 'application/json'
                }
            });

            showNotification('Configuración guardada exitosamente', 'success');
        } catch (error) {
            console.error('Error saving configuration:', error);
            if (error.response && error.response.status === 401) {
                Auth.logout();
            } else if (error.response && error.response.status === 403) {
                showNotification('No tienes permisos para modificar la configuración', 'error');
            } else {
                showNotification('Error al guardar la configuración', 'error');
            }
        }
    });
}

/**
 * Handle logo file upload
 */
async function handleLogoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('El archivo es demasiado grande. Máximo 5MB', 'error');
        return;
    }

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml'];
    if (!validTypes.includes(file.type)) {
        showNotification('Tipo de archivo no válido. Use PNG, JPG, GIF o SVG', 'error');
        return;
    }

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        showNotification('Subiendo logo...', 'success');

        const response = await axios.post('/api/config/logo/upload', formData, {
            headers: {
                'Authorization': `Bearer ${Auth.getAccessToken()}`,
                'Content-Type': 'multipart/form-data'
            }
        });

        if (response.data.success) {
            currentLogoId = response.data.logo.id;
            displayLogo(response.data.logo);
            showNotification('Logo subido exitosamente', 'success');
        }

    } catch (error) {
        console.error('Error uploading logo:', error);
        if (error.response && error.response.status === 401) {
            Auth.logout();
        } else if (error.response && error.response.status === 403) {
            showNotification('No tienes permisos para subir logos', 'error');
        } else if (error.response && error.response.data && error.response.data.detail) {
            showNotification(error.response.data.detail, 'error');
        } else {
            showNotification('Error al subir el logo', 'error');
        }
    } finally {
        // Reset file input
        event.target.value = '';
    }
}

/**
 * Setup drag and drop for logo upload
 */
function setupDragAndDrop() {
    const uploadZone = document.getElementById('upload-zone');

    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('logo-file');
            fileInput.files = files;

            // Trigger the onchange event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    });
}

/**
 * Delete current logo
 */
async function deleteLogo() {
    if (!currentLogoId) {
        showNotification('No hay logo para eliminar', 'error');
        return;
    }

    if (!confirm('¿Estás seguro de que quieres eliminar el logo actual? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const response = await axios.delete(`/api/config/logo/${currentLogoId}`, {
            headers: {
                'Authorization': `Bearer ${Auth.getAccessToken()}`
            }
        });

        if (response.data.success) {
            currentLogoId = null;
            displayNoLogo();
            showNotification('Logo eliminado exitosamente', 'success');
        }

    } catch (error) {
        console.error('Error deleting logo:', error);
        if (error.response && error.response.status === 401) {
            Auth.logout();
        } else if (error.response && error.response.status === 403) {
            showNotification('No tienes permisos para eliminar logos', 'error');
        } else {
            showNotification('Error al eliminar el logo', 'error');
        }
    }
}

/**
 * Save theme preference
 */
async function saveThemePreference() {
    const selectedTheme = document.querySelector('input[name="theme"]:checked');
    if (!selectedTheme) {
        showNotification('Por favor selecciona un tema', 'error');
        return;
    }

    const theme = selectedTheme.value;

    try {
        const response = await axios.put('/api/config/system', {
            theme: theme
        }, {
            headers: {
                'Authorization': `Bearer ${Auth.getAccessToken()}`,
                'Content-Type': 'application/json'
            }
        });

        // Update current theme
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateThemeIcon(theme);

        showNotification('Preferencia de tema guardada', 'success');

    } catch (error) {
        console.error('Error saving theme preference:', error);
        if (error.response && error.response.status === 401) {
            Auth.logout();
        } else if (error.response && error.response.status === 403) {
            showNotification('No tienes permisos para modificar el tema', 'error');
        } else {
            showNotification('Error al guardar la preferencia de tema', 'error');
        }
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(el => el.remove());

    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="flex items-center gap-2">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

/**
 * Load theme from localStorage
 */
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

/**
 * Toggle theme (light/dark)
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

/**
 * Update theme icon
 */
function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

/**
 * Logout user
 */
function logout() {
    Auth.logout();
}

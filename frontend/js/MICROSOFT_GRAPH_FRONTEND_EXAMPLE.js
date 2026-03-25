"""
Ejemplo de cómo usar Microsoft Graph API desde el frontend
"""

// ==================== LOGIN DE MICROSOFT ====================

async function loginWithMicrosoft() {
    try {
        // 1. Obtener URL de autenticación
        const response = await fetch('/api/auth/microsoft/login');
        const { auth_url } = await response.json();
        
        // 2. Redirigir al usuario a Microsoft
        window.location.href = auth_url;
        // El callback se maneja automáticamente
    } catch (error) {
        console.error('Error en login de Microsoft:', error);
        alert('Error al iniciar sesión con Microsoft');
    }
}

// ==================== VERIFICAR AUTENTICACIÓN ====================

async function checkMicrosoftAuthStatus() {
    try {
        const token = localStorage.getItem('access_token'); // Tu JWT token
        const response = await fetch('/api/auth/microsoft/status', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        return {
            is_authenticated: data.is_microsoft_authenticated,
            email: data.microsoft_email,
            expires_at: data.token_expires_at
        };
    } catch (error) {
        console.error('Error verificando estado:', error);
        return { is_authenticated: false };
    }
}

// ==================== SINCRONIZAR CORREOS ENVIADOS ====================

async function syncSentEmails() {
    try {
        const token = localStorage.getItem('access_token');
        
        // Mostrar loading
        showLoading('Sincronizando correos enviados...');
        
        const response = await fetch('/api/sync/microsoft/sent?limit=50', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Sincronización completada:', {
            guardados: data.count,
            total: data.total,
            mensaje: data.message
        });
        
        // Mostrar resultados
        return {
            success: true,
            saved: data.count,
            total: data.total,
            emails: data.emails,
            errors: data.errors
        };
        
    } catch (error) {
        console.error('Error sincronizando correos enviados:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// ==================== SINCRONIZAR CORREOS DE ENTRADA ====================

async function syncInboxEmails() {
    try {
        const token = localStorage.getItem('access_token');
        
        showLoading('Sincronizando correos de entrada...');
        
        const response = await fetch('/api/sync/microsoft/inbox?limit=50', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        return {
            success: true,
            saved: data.count,
            total: data.total,
            emails: data.emails,
            errors: data.errors
        };
        
    } catch (error) {
        console.error('Error sincronizando entrada:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// ==================== DESCONECTAR MICROSOFT ====================

async function disconnectMicrosoft() {
    try {
        const token = localStorage.getItem('access_token');
        
        if (!confirm('¿Desconectar la cuenta de Microsoft?')) {
            return;
        }
        
        const response = await fetch('/api/auth/microsoft/disconnect', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            alert('Cuenta de Microsoft desconectada');
            // Redirigir al login
            window.location.href = '/login.html';
        } else {
            throw new Error('Error desconectando');
        }
        
    } catch (error) {
        console.error('Error desconectando:', error);
        alert('Error al desconectar');
    }
}

// ==================== OBTENER ESTADO ====================

async function getSyncStatus() {
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch('/api/sync/microsoft/status', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        return {
            authenticated: data.is_authenticated,
            email: data.microsoft_email,
            email_count: data.email_count,
            token_expires: data.token_expires_at,
            last_sync: data.last_sync
        };
        
    } catch (error) {
        console.error('Error obteniendo estado:', error);
        return null;
    }
}

// ==================== EJEMPLO DE INTERFAZ ====================

async function initMicrosoftUI() {
    // Verificar si el usuario está conectado a Microsoft
    const status = await checkMicrosoftAuthStatus();
    
    const microsoftButtonContainer = document.getElementById('microsoft-auth');
    
    if (status.is_authenticated) {
        // Usuario conectado - mostrar opciones de sincronización
        microsoftButtonContainer.innerHTML = `
            <div class="microsoft-connected">
                <p><strong>Conectado con:</strong> ${status.email}</p>
                <p><small>Token expira: ${new Date(status.expires_at).toLocaleString()}</small></p>
                
                <button onclick="syncSentEmails()" class="btn btn-primary">
                    💌 Sincronizar Enviados
                </button>
                
                <button onclick="syncInboxEmails()" class="btn btn-primary">
                    📬 Sincronizar Entrada
                </button>
                
                <button onclick="disconnectMicrosoft()" class="btn btn-danger">
                    🔓 Desconectar
                </button>
            </div>
        `;
    } else {
        // Usuario no conectado - mostrar botón de login
        microsoftButtonContainer.innerHTML = `
            <button onclick="loginWithMicrosoft()" class="btn btn-success">
                🔐 Conectar con Microsoft
            </button>
        `;
    }
}

// Llamar cuando carga la página
document.addEventListener('DOMContentLoaded', initMicrosoftUI);

// ==================== UTILIDADES ====================

function showLoading(message) {
    const loader = document.createElement('div');
    loader.className = 'loading-spinner';
    loader.innerHTML = `
        <div class="spinner"></div>
        <p>${message}</p>
    `;
    document.body.appendChild(loader);
    return loader;
}

function hideLoading(loader) {
    if (loader && loader.parentNode) {
        loader.parentNode.removeChild(loader);
    }
}

// ==================== MANEJO DE CALLBACK ====================
// Este se ejecuta automáticamente después de que Microsoft redirige

window.addEventListener('load', async () => {
    // Si hay usuarios conectados, actualizar UI
    const status = await getSyncStatus();
    if (status) {
        console.log('Estado actual:', status);
    }
});

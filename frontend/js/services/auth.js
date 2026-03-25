/**
 * Servicio de Autenticación - Maneja login, logout y tokens
 */
const AuthService = {
    /**
     * Inicia sesión
     */
    async login(username, password) {
        try {
            const response = await axios.post('/api/auth/login', {
                username: username,
                password: password
            });
            
            if (response.data.tokens) {
                localStorage.setItem('access_token', response.data.tokens.access_token);
                localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }
            
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error de conexión' };
        }
    },
    
    /**
     * Registra un nuevo usuario
     */
    async register(username, email, password, full_name) {
        try {
            const response = await axios.post('/api/auth/register', {
                username,
                email,
                password,
                full_name
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error de conexión' };
        }
    },
    
    /**
     * Cierra sesión
     */
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
    
    /**
     * Obtiene el usuario actual
     */
    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    
    /**
     * Obtiene el token de acceso
     */
    getAccessToken() {
        return localStorage.getItem('access_token');
    },
    
    /**
     * Verifica si el usuario está autenticado
     */
    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },
    
    /**
     * Refresca el token
     */
    async refreshToken() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await axios.post('/api/auth/refresh', {
                refresh_token: refreshToken
            });
            
            localStorage.setItem('access_token', response.data.tokens.access_token);
            return response.data.tokens;
        } catch (error) {
            this.logout();
            throw error;
        }
    }
};

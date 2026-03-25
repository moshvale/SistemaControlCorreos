/**
 * Servicio de API - Maneja todas las peticiones HTTP
 */
const APIService = {
    /**
     * Configurar axios con token de autorización
     */
    setupAxios() {
        axios.interceptors.request.use(config => {
            const token = localStorage.getItem('access_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        
        // Manejar respuesta 401 (token expirado)
        axios.interceptors.response.use(
            response => response,
            async error => {
                const original = error.config;
                
                // No reintentar refresh token request si ya falló
                if (original.url?.includes('/api/auth/refresh')) {
                    AuthService.logout();
                    window.location.href = '/';
                    return Promise.reject(error);
                }
                
                // Intentar refrescar token solo una vez
                if (error.response?.status === 401 && !original._retry) {
                    original._retry = true;
                    try {
                        const tokens = await AuthService.refreshToken();
                        axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
                        original.headers.Authorization = `Bearer ${tokens.access_token}`;
                        return axios(original);
                    } catch (err) {
                        AuthService.logout();
                        window.location.href = '/';
                        return Promise.reject(err);
                    }
                }
                return Promise.reject(error);
            }
        );
    },
    
    /**
     * Obtiene los correos del usuario
     */
    async getEmails(page = 1, filters = {}) {
        try {
            let url = `/api/emails?page=${page}`;
            if (filters.subject) url += `&subject=${filters.subject}`;
            if (filters.sender) url += `&sender=${filters.sender}`;
            if (filters.recipient) url += `&recipient=${filters.recipient}`;
            if (filters.date_from) url += `&date_from=${filters.date_from}`;
            if (filters.date_to) url += `&date_to=${filters.date_to}`;
            if (filters.has_attachments !== undefined) url += `&has_attachments=${filters.has_attachments}`;
            
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando correos' };
        }
    },
    
    /**
     * Obtiene TODOS los correos compartidos (de todos los usuarios)
     */
    async getSharedEmails(page = 1, filters = {}) {
        try {
            let url = `/api/emails/shared/all?page=${page}`;
            if (filters.subject) url += `&subject=${filters.subject}`;
            if (filters.sender) url += `&sender=${filters.sender}`;
            if (filters.recipient) url += `&recipient=${filters.recipient}`;
            if (filters.date_from) url += `&date_from=${filters.date_from}`;
            if (filters.date_to) url += `&date_to=${filters.date_to}`;
            if (filters.has_attachments !== undefined) url += `&has_attachments=${filters.has_attachments}`;
            
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando correos compartidos' };
        }
    },
    
    /**
     * Obtiene un correo específico
     */
    async getEmail(emailId) {
        try {
            const response = await axios.get(`/api/emails/${emailId}`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando correo' };
        }
    },
    
    /**
     * Crea un nuevo correo
     */
    async createEmail(emailData) {
        try {
            // Asegurar que la fecha esté en formato ISO válido
            if (emailData.sent_date) {
                const dateObj = new Date(emailData.sent_date);
                emailData.sent_date = dateObj.toISOString();
            }
            
            const response = await axios.post('/api/emails', emailData);
            return response.data;
        } catch (error) {
            console.error('Error creando correo:', error.response?.data);
            throw error.response?.data || { error: error.message || 'Error creando correo' };
        }
    },
    
    /**
     * Actualiza un correo
     */
    async updateEmail(emailId, updates) {
        try {
            const response = await axios.put(`/api/emails/${emailId}`, updates);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error actualizando correo' };
        }
    },
    
    /**
     * Elimina un correo
     */
    async deleteEmail(emailId) {
        try {
            const response = await axios.delete(`/api/emails/${emailId}`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error eliminando correo' };
        }
    },
    
    /**
     * Busca correos (solo del usuario)
     */
    async searchEmails(searchTerm, page = 1) {
        try {
            const response = await axios.post('/api/emails/search', {
                search_term: searchTerm,
                page: page
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error buscando correos' };
        }
    },
    
    /**
     * Busca en TODOS los correos compartidos
     */
    async searchSharedEmails(searchTerm, page = 1) {
        try {
            const response = await axios.post('/api/emails/shared/search', {
                search_term: searchTerm,
                page: page
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error buscando correos compartidos' };
        }
    },
    
    /**
     * Sincroniza con Outlook
     */
    async syncOutlook() {
        try {
            const response = await axios.post('/api/emails/sync/outlook');
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error sincronizando con Outlook' };
        }
    },
    
    /**
     * Exporta correos a CSV
     */
    async exportToCSV(emailIds = []) {
        try {
            const response = await axios.post('/api/emails/export/csv', {
                email_ids: emailIds
            }, { responseType: 'blob' });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `correos_${new Date().getTime()}.csv`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            throw error.response?.data || { error: 'Error exportando a CSV' };
        }
    },
    
    /**
     * Exporta correos a PDF
     */
    async exportToPDF(emailIds = []) {
        try {
            const response = await axios.post('/api/emails/export/pdf', {
                email_ids: emailIds
            }, { responseType: 'blob' });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `correos_${new Date().getTime()}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            throw error.response?.data || { error: 'Error exportando a PDF' };
        }
    },
    
    /**
     * Exporta correos a Excel con filtros de fechas
     */
    async exportToExcel(dateFrom, dateTo, emailIds = [], includeAudit = true) {
        try {
            const response = await axios.post('/api/emails/export/excel', {
                date_from: dateFrom,
                date_to: dateTo,
                email_ids: emailIds,
                include_audit: includeAudit
            }, { responseType: 'blob' });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `reporte_correos_${new Date().getTime()}.xlsx`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            throw error.response?.data || { error: 'Error exportando a Excel' };
        }
    },
    
    /**
     * Obtiene estadísticas del dashboard
     */
    async getDashboardStats() {
        try {
            const response = await axios.get('/api/emails/dashboard/stats');
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando estadísticas' };
        }
    },
    
    /**
     * Admin: Obtiene lista de usuarios
     */
    async getUsers(page = 1) {
        try {
            const response = await axios.get(`/api/admin/users?page=${page}`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando usuarios' };
        }
    },
    
    /**
     * Admin: Obtiene logs de auditoría
     */
    async getAuditLogs(page = 1, filters = {}) {
        try {
            let url = `/api/admin/audit-logs?page=${page}`;
            if (filters.user_id) url += `&user_id=${filters.user_id}`;
            if (filters.action) url += `&action=${filters.action}`;
            
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando logs' };
        }
    },
    
    /**
     * Admin: Obtiene estadísticas del sistema
     */
    async getAdminStats() {
        try {
            const response = await axios.get('/api/admin/stats');
            return response.data;
        } catch (error) {
            throw error.response?.data || { error: 'Error cargando estadísticas' };
        }
    }
};

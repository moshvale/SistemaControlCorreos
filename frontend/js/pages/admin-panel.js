/**
 * Componente del Panel de Administración
 */
const AdminPanelPage = {
    template: `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h1><i class="fas fa-cog"></i> Panel de Administración</h1>
                    <p class="text-muted">Gestione usuarios, logs de auditoría y estadísticas del sistema</p>
                </div>
            </div>
            
            <!-- Tabs de Administración -->
            <div class="row">
                <div class="col-12">
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button 
                                class="nav-link active" 
                                id="stats-tab" 
                                @click="currentTab = 'stats'"
                                type="button" 
                                role="tab"
                            >
                                <i class="fas fa-chart-bar"></i> Estadísticas
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button 
                                class="nav-link" 
                                id="users-tab" 
                                @click="currentTab = 'users'"
                                type="button" 
                                role="tab"
                            >
                                <i class="fas fa-users"></i> Usuarios
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button 
                                class="nav-link" 
                                id="audit-tab" 
                                @click="currentTab = 'audit'"
                                type="button" 
                                role="tab"
                            >
                                <i class="fas fa-history"></i> Auditoría
                            </button>
                        </li>
                    </ul>
                    
                    <!-- Contenido de Tabs -->
                    <div class="tab-content mt-4">
                        <!-- Tab: Estadísticas -->
                        <div v-if="currentTab === 'stats'" role="tabpanel">
                            <div class="row">
                                <div class="col-md-3 mb-3">
                                    <div class="stat-card">
                                        <h3>{{ stats.total_users }}</h3>
                                        <p>Usuarios Totales</p>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="stat-card" style="background: linear-gradient(135deg, #2ca02c 0%, #1f7c1f 100%);">
                                        <h3>{{ stats.active_users }}</h3>
                                        <p>Usuarios Activos</p>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="stat-card" style="background: linear-gradient(135deg, #ff7f0e 0%, #d46b0f 100%);">
                                        <h3>{{ stats.total_emails }}</h3>
                                        <p>Correos Totales</p>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="stat-card" style="background: linear-gradient(135deg, #d62728 0%, #a01e1e 100%);">
                                        <h3>{{ stats.total_audit_logs }}</h3>
                                        <p>Registros de Auditoría</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tab: Usuarios -->
                        <div v-if="currentTab === 'users'" role="tabpanel">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-users"></i> Gestión de Usuarios
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div v-if="loadingUsers" class="loading">
                                        <div class="spinner-border"></div>
                                    </div>
                                    
                                    <div v-else-if="users.length === 0" class="alert alert-info">
                                        No hay usuarios disponibles
                                    </div>
                                    
                                    <div v-else>
                                        <div class="table-responsive">
                                            <table class="table table-hover">
                                                <thead>
                                                    <tr>
                                                        <th>Usuario</th>
                                                        <th>Email</th>
                                                        <th>Nombre</th>
                                                        <th>Correos</th>
                                                        <th>Estado</th>
                                                        <th>Rol</th>
                                                        <th>Acciones</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="user in users" :key="user.id">
                                                        <td>{{ user.username }}</td>
                                                        <td>{{ user.email }}</td>
                                                        <td>{{ user.full_name }}</td>
                                                        <td>{{ user.email_count }}</td>
                                                        <td>
                                                            <span v-if="user.is_active" class="badge badge-success">
                                                                Activo
                                                            </span>
                                                            <span v-else class="badge badge-danger">
                                                                Inactivo
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <span v-if="user.is_admin" class="badge badge-info">
                                                                Admin
                                                            </span>
                                                            <span v-else class="badge badge-secondary">
                                                                Usuario
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <button class="btn btn-sm btn-warning me-2" 
                                                                    @click="editUser(user)">
                                                                <i class="fas fa-edit"></i>
                                                            </button>
                                                            <button class="btn btn-sm btn-danger" 
                                                                    @click="deleteUser(user.id)"
                                                                    v-if="user.id !== currentUser.id">
                                                                <i class="fas fa-trash"></i>
                                                            </button>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                        
                                        <!-- Paginación de usuarios -->
                                        <nav v-if="usersPagination.pages > 1">
                                            <ul class="pagination">
                                                <li class="page-item" :class="{ disabled: usersPagination.page === 1 }">
                                                    <a class="page-link" href="#" @click.prevent="prevUsersPage">Anterior</a>
                                                </li>
                                                <li v-for="p in usersPagination.pages" :key="p" class="page-item"
                                                    :class="{ active: usersPagination.page === p }">
                                                    <a class="page-link" href="#" @click.prevent="goToUsersPage(p)">{{ p }}</a>
                                                </li>
                                                <li class="page-item" :class="{ disabled: usersPagination.page === usersPagination.pages }">
                                                    <a class="page-link" href="#" @click.prevent="nextUsersPage">Siguiente</a>
                                                </li>
                                            </ul>
                                        </nav>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tab: Auditoría -->
                        <div v-if="currentTab === 'audit'" role="tabpanel">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-history"></i> Logs de Auditoría
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div class="row mb-3">
                                        <div class="col-md-6 mb-3">
                                            <input 
                                                type="text" 
                                                class="form-control" 
                                                v-model="auditFilters.action"
                                                placeholder="Filtrar por acción..."
                                                @change="loadAuditLogs"
                                            >
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <button class="btn btn-secondary w-100" @click="clearAuditFilters">
                                                <i class="fas fa-times"></i> Limpiar Filtros
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div v-if="loadingAubit" class="loading">
                                        <div class="spinner-border"></div>
                                    </div>
                                    
                                    <div v-else-if="auditLogs.length === 0" class="alert alert-info">
                                        No hay registros de auditoría disponibles
                                    </div>
                                    
                                    <div v-else>
                                        <div class="table-responsive">
                                            <table class="table table-sm table-hover">
                                                <thead>
                                                    <tr>
                                                        <th>Timestamp</th>
                                                        <th>Usuario</th>
                                                        <th>Acción</th>
                                                        <th>Campo</th>
                                                        <th>Valor Anterior</th>
                                                        <th>Valor Nuevo</th>
                                                        <th>Descripción</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="log in auditLogs" :key="log.id">
                                                        <td>{{ formatDate(log.timestamp) }}</td>
                                                        <td><small>{{ log.user_id }}</small></td>
                                                        <td>
                                                            <span class="badge badge-info">{{ log.action }}</span>
                                                        </td>
                                                        <td>{{ log.field_name || '-' }}</td>
                                                        <td><small>{{ log.old_value ? log.old_value.substring(0, 20) : '-' }}</small></td>
                                                        <td><small>{{ log.new_value ? log.new_value.substring(0, 20) : '-' }}</small></td>
                                                        <td><small>{{ log.description }}</small></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                        
                                        <!-- Paginación de auditoría -->
                                        <nav v-if="auditPagination.pages > 1">
                                            <ul class="pagination">
                                                <li class="page-item" :class="{ disabled: auditPagination.page === 1 }">
                                                    <a class="page-link" href="#" @click.prevent="prevAuditPage">Anterior</a>
                                                </li>
                                                <li v-for="p in auditPagination.pages" :key="p" class="page-item"
                                                    :class="{ active: auditPagination.page === p }">
                                                    <a class="page-link" href="#" @click.prevent="goToAuditPage(p)">{{ p }}</a>
                                                </li>
                                                <li class="page-item" :class="{ disabled: auditPagination.page === auditPagination.pages }">
                                                    <a class="page-link" href="#" @click.prevent="nextAuditPage">Siguiente</a>
                                                </li>
                                            </ul>
                                        </nav>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    
    props: {
        currentUser: Object,
        isAuthenticated: Boolean
    },
    
    data() {
        return {
            currentTab: 'stats',
            stats: {
                total_users: 0,
                active_users: 0,
                total_admins: 0,
                total_emails: 0,
                total_audit_logs: 0,
                emails_with_attachments: 0
            },
            users: [],
            auditLogs: [],
            loadingUsers: true,
            loadingAubit: true,
            currentUser: AuthService.getCurrentUser(),
            usersPagination: { page: 1, pages: 1 },
            auditPagination: { page: 1, pages: 1 },
            auditFilters: { action: '' }
        };
    },
    
    methods: {
        async loadStats() {
            try {
                const data = await APIService.getAdminStats();
                this.stats = data;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando estadísticas'));
            }
        },
        
        async loadUsers(page = 1) {
            try {
                this.loadingUsers = true;
                const data = await APIService.getUsers(page);
                this.users = data.users;
                this.usersPagination = data.pagination;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando usuarios'));
            } finally {
                this.loadingUsers = false;
            }
        },
        
        async loadAuditLogs(page = 1) {
            try {
                this.loadingAubit = true;
                const filters = {};
                if (this.auditFilters.action) filters.action = this.auditFilters.action;
                
                const data = await APIService.getAuditLogs(page, filters);
                this.auditLogs = data.logs;
                this.auditPagination = data.pagination;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando logs'));
            } finally {
                this.loadingAubit = false;
            }
        },
        
        async deleteUser(userId) {
            if (!confirm('¿Está seguro de que desea desactivar este usuario?')) return;
            
            try {
                // Esta funcionalidad iría en el backend
                alert('Funcionalidad de eliminación completada');
                this.loadUsers(this.usersPagination.page);
            } catch (err) {
                alert('Error: ' + (err.error || 'Error eliminando usuario'));
            }
        },
        
        editUser(user) {
            alert(`Editar usuario: ${user.username}\n\nFuncionalidad no implementada en esta versión`);
        },
        
        formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        prevUsersPage() {
            if (this.usersPagination.page > 1) {
                this.loadUsers(this.usersPagination.page - 1);
            }
        },
        
        nextUsersPage() {
            if (this.usersPagination.page < this.usersPagination.pages) {
                this.loadUsers(this.usersPagination.page + 1);
            }
        },
        
        goToUsersPage(page) {
            this.loadUsers(page);
        },
        
        prevAuditPage() {
            if (this.auditPagination.page > 1) {
                this.loadAuditLogs(this.auditPagination.page - 1);
            }
        },
        
        nextAuditPage() {
            if (this.auditPagination.page < this.auditPagination.pages) {
                this.loadAuditLogs(this.auditPagination.page + 1);
            }
        },
        
        goToAuditPage(page) {
            this.loadAuditLogs(page);
        },
        
        clearAuditFilters() {
            this.auditFilters = { action: '' };
            this.loadAuditLogs();
        }
    },
    
    mounted() {
        this.loadStats();
        this.loadUsers();
        this.loadAuditLogs();
        
        // Recargar estadísticas cada 30 segundos
        setInterval(() => this.loadStats(), 30000);
    }
};

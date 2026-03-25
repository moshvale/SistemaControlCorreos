/**
 * Aplicación Principal Vue.js
 */
const { createApp } = Vue;

const App = {
    template: `
        <div id="app" class="d-flex flex-column">
            <!-- Navbar -->
            <nav class="navbar navbar-expand-lg">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#/">
                        <i class="fas fa-envelope"></i> Gestor de Correos
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item" v-if="isAuthenticated">
                                <a class="nav-link" href="#/dashboard">
                                    <i class="fas fa-chart-line"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item" v-if="isAuthenticated">
                                <a class="nav-link" href="#/emails">
                                    <i class="fas fa-inbox"></i> Correos
                                </a>
                            </li>
                            <li class="nav-item" v-if="isAuthenticated && currentUser?.is_admin">
                                <a class="nav-link" href="#/admin">
                                    <i class="fas fa-cog"></i> Administración
                                </a>
                            </li>
                            <li class="nav-item" v-if="isAuthenticated">
                                <div class="user-badge">
                                    <i class="fas fa-user-circle"></i>
                                    {{ currentUser?.username }}
                                    <button @click="logout" class="btn btn-sm btn-outline-light ms-2">
                                        Salir
                                    </button>
                                </div>
                            </li>
                            <li class="nav-item" v-if="!isAuthenticated">
                                <a class="nav-link" href="#/">Login</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <!-- Contenido Principal -->
            <div class="main-content">
                <component 
                    :is="currentComponent" 
                    :key="currentPage"
                    :currentUser="currentUser"
                    :isAuthenticated="isAuthenticated"
                ></component>
            </div>
            
            <!-- Footer -->
            <footer>
                <p>&copy; 2026 Sistema de Gestión de Correos. INE Todos los derechos reservados.</p>
            </footer>
        </div>
    `,
    
    data() {
        return {
            isAuthenticated: false,
            currentUser: null,
            currentPage: 'login'
        };
    },
    
    computed: {
        currentComponent() {
            if (!this.isAuthenticated && this.currentPage === 'login') {
                return LoginPage;
            }
            if (this.isAuthenticated && this.currentPage === 'dashboard') {
                return DashboardPage;
            }
            if (this.isAuthenticated && this.currentPage === 'emails') {
                return EmailsListPage;
            }
            if (this.isAuthenticated && this.currentPage === 'email-form') {
                return EmailFormPage;
            }
            if (this.isAuthenticated && this.currentUser?.is_admin && this.currentPage === 'admin') {
                return AdminPanelPage;
            }
            return LoginPage;
        }
    },
    
    methods: {
        logout() {
            if (confirm('¿Desea cerrar sesión?')) {
                AuthService.logout();
                this.isAuthenticated = false;
                this.currentPage = 'login';
                window.location.hash = '#/';
            }
        },
        
        checkAuth() {
            const user = AuthService.getCurrentUser();
            const token = AuthService.getAccessToken();
            
            if (user && token) {
                this.isAuthenticated = true;
                this.currentUser = user;
            } else {
                this.isAuthenticated = false;
                this.currentPage = 'login';
            }
        },
        
        handleRoute(page) {
            if (!this.isAuthenticated && page !== 'login') {
                window.location.hash = '#/';
                return;
            }
            this.currentPage = page;
        },
        
        updateRoute() {
            // Verificar autenticación nuevamente
            this.checkAuth();
            
            // Parsear el hash correctamente: "#/dashboard" -> "dashboard"
            const fullHash = window.location.hash.slice(1); // Quitar el "#"
            const hash = fullHash.split('/').filter(x => x)[0]; // Obtener el primer segmento
            
            if (!hash || hash === '') {
                if (this.isAuthenticated) {
                    window.location.hash = '#/dashboard';
                } else {
                    this.currentPage = 'login';
                }
            } else if (hash === 'dashboard') {
                this.handleRoute('dashboard');
            } else if (hash === 'emails') {
                this.handleRoute('emails');
            } else if (hash === 'email-form') {
                this.handleRoute('email-form');
            } else if (hash === 'admin') {
                this.handleRoute('admin');
            } else {
                // Ruta no reconocida, volver a la raíz
                if (this.isAuthenticated) {
                    window.location.hash = '#/dashboard';
                } else {
                    window.location.hash = '#/';
                }
            }
        }
    },
    
    mounted() {
        // Configurar Axios
        APIService.setupAxios();
        
        // Verificar autenticación
        this.checkAuth();
        
        // Procesar ruta inicial
        this.updateRoute();
        
        // Escuchar cambios en hash
        window.addEventListener('hashchange', () => {
            this.updateRoute();
        });
    }
};

// Crear y montar la aplicación
const app = createApp(App);
app.mount('#app');

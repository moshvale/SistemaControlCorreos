/**
 * Componente de Login
 */
const LoginPage = {
    template: `
        <div class="container" style="max-width: 500px; margin-top: 50px;">
            <div class="card">
                <div class="card-header">
                    <h3 class="mb-0">
                        <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                    </h3>
                </div>
                <div class="card-body">
                    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                        {{ error }}
                        <button type="button" class="btn-close" @click="error = ''"></button>
                    </div>
                    
                    <form @submit.prevent="handleLogin">
                        <div class="mb-3">
                            <label for="username" class="form-label">Usuario</label>
                            <input 
                                type="text" 
                                class="form-control" 
                                id="username"
                                v-model="form.username"
                                required
                                :disabled="loading"
                            >
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Contraseña</label>
                            <input 
                                type="password" 
                                class="form-control" 
                                id="password"
                                v-model="form.password"
                                required
                                :disabled="loading"
                            >
                        </div>
                        
                        <div class="d-grid gap-2 mb-3">
                            <button 
                                type="submit" 
                                class="btn btn-primary btn-lg"
                                :disabled="loading"
                            >
                                <span v-if="loading">
                                    <span class="spinner-border spinner-border-sm me-2"></span>
                                    Iniciando sesión...
                                </span>
                                <span v-else>
                                    <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                                </span>
                            </button>
                        </div>
                        
                        <p class="text-center">
                            ¿No tiene cuenta? 
                            <a href="#" @click="toggleRegister">Registrarse</a>
                        </p>
                    </form>
                    
                    <hr>
                    
                    <div v-if="showRegister">
                        <h5>Crear Nueva Cuenta</h5>
                        
                        <form @submit.prevent="handleRegister">
                            <div class="mb-3">
                                <label for="reg-username" class="form-label">Usuario</label>
                                <input 
                                    type="text" 
                                    class="form-control" 
                                    id="reg-username"
                                    v-model="registerForm.username"
                                    required
                                    :disabled="loading"
                                >
                            </div>
                            
                            <div class="mb-3">
                                <label for="reg-email" class="form-label">Correo Electrónico</label>
                                <input 
                                    type="email" 
                                    class="form-control" 
                                    id="reg-email"
                                    v-model="registerForm.email"
                                    required
                                    :disabled="loading"
                                >
                            </div>
                            
                            <div class="mb-3">
                                <label for="reg-full-name" class="form-label">Nombre Completo</label>
                                <input 
                                    type="text" 
                                    class="form-control" 
                                    id="reg-full-name"
                                    v-model="registerForm.full_name"
                                    :disabled="loading"
                                >
                            </div>
                            
                            <div class="mb-3">
                                <label for="reg-password" class="form-label">Contraseña</label>
                                <input 
                                    type="password" 
                                    class="form-control" 
                                    id="reg-password"
                                    v-model="registerForm.password"
                                    minlength="8"
                                    required
                                    :disabled="loading"
                                >
                                <small class="form-text">Mínimo 8 caracteres</small>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button 
                                    type="submit" 
                                    class="btn btn-success btn-lg"
                                    :disabled="loading"
                                >
                                    <span v-if="loading">
                                        <span class="spinner-border spinner-border-sm me-2"></span>
                                        Registrando...
                                    </span>
                                    <span v-else>
                                        <i class="fas fa-user-plus"></i> Registrarse
                                    </span>
                                </button>
                                <button 
                                    type="button" 
                                    class="btn btn-secondary"
                                    @click="toggleRegister"
                                    :disabled="loading"
                                >
                                    Cancelar
                                </button>
                            </div>
                        </form>
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
            form: {
                username: '',
                password: ''
            },
            registerForm: {
                username: '',
                email: '',
                password: '',
                full_name: ''
            },
            error: '',
            loading: false,
            showRegister: false
        };
    },
    
    methods: {
        async handleLogin() {
            this.error = '';
            this.loading = true;
            
            try {
                const response = await AuthService.login(
                    this.form.username,
                    this.form.password
                );
                
                // Esperar un poco para asegurar que los datos se guardaron en localStorage
                // y luego cambiar la navegación
                setTimeout(() => {
                    // Verificar que el token está en localStorage antes de navegar
                    const token = localStorage.getItem('access_token');
                    if (token) {
                        window.location.hash = '#/dashboard';
                    } else {
                        this.error = 'Error guardando sesión. Intente nuevamente.';
                        this.loading = false;
                    }
                }, 150);
            } catch (err) {
                this.error = err.error || 'Error en login. Intente nuevamente.';
                this.loading = false;
            }
        },
        
        async handleRegister() {
            this.error = '';
            this.loading = true;
            
            try {
                const response = await AuthService.register(
                    this.registerForm.username,
                    this.registerForm.email,
                    this.registerForm.password,
                    this.registerForm.full_name
                );
                
                this.error = '';
                alert('Usuario registrado exitosamente. Por favor, inicie sesión.');
                this.showRegister = false;
                
                this.form.username = this.registerForm.username;
                this.registerForm = {
                    username: '',
                    email: '',
                    password: '',
                    full_name: ''
                };
            } catch (err) {
                this.error = err.error || 'Error en registro. Intente nuevamente.';
            } finally {
                this.loading = false;
            }
        },
        
        toggleRegister() {
            this.showRegister = !this.showRegister;
            this.error = '';
        }
    }
};

/**
 * Componente de Dashboard
 */
const DashboardPage = {
    template: `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h1><i class="fas fa-chart-line"></i> Dashboard</h1>
                            <p class="text-muted">Bienvenido, {{ currentUser?.username }}!</p>
                        </div>
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; border-radius: 8px; text-align: center;">
                            <i class="fas fa-share-alt" style="font-size: 24px; margin-bottom: 8px;"></i>
                            <div style="font-weight: bold;">Dashboard Compartido</div>
                            <div style="font-size: 12px; opacity: 0.9;">Datos de todos los usuarios</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div v-if="loading" class="loading">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
            
            <div v-else>
                <!-- Banner informativo -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="alert alert-info alert-dismissible fade show" role="alert">
                            <i class="fas fa-info-circle"></i>
                            <strong>Información Compartida:</strong> Este dashboard muestra estadísticas y correos sincronizados de todos los usuarios del sistema. Todos los usuarios registrados pueden ver los mismos datos.
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    </div>
                </div>
                
                <!-- Tarjetas de Estadísticas -->
                <div class="row mb-4">
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="stat-card">
                            <h3>{{ stats.total_emails }}</h3>
                            <p>Correos Totales</p>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #2ca02c 0%, #1f7c1f 100%);">
                            <h3>{{ stats.emails_with_attachments }}</h3>
                            <p>Con Archivos Adjuntos</p>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #ff7f0e 0%, #d46b0f 100%);">
                            <h3>{{ emailsThisMonth }}</h3>
                            <p>Este Mes</p>
                        </div>
                    </div>
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="stat-card" style="background: linear-gradient(135deg, #d62728 0%, #a01e1e 100%);">
                            <h3>{{ topSender?.sender || '-' }}</h3>
                            <p>Remitente Principal</p>
                        </div>
                    </div>
                </div>
                
                <!-- Panel de Sincronización -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card" style="border-left: 4px solid #28a745;">
                            <div class="card-header" style="background: #f0fff4;">
                                <h5 class="mb-0">
                                    <i class="fas fa-sync text-success"></i>
                                    Sincronización de Correos
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-success">
                                    <i class="fas fa-check-circle"></i>
                                    <strong>Outlook de Escritorio Disponible:</strong> Tienes instalado Outlook de escritorio en este equipo, lo que te permite sincronizar correos automáticamente.
                                </div>
                                <p class="text-muted mb-3">
                                    <i class="fas fa-info-circle"></i> 
                                    Asegúrate de tener Outlook abierto antes de sincronizar. Se sincronizará el último correo enviado desde tu bandeja de elementos enviados.
                                </p>
                                <button class="btn btn-success" @click="syncOutlook" :disabled="syncing">
                                    <span v-if="syncing">
                                        <span class="spinner-border spinner-border-sm me-2"></span>
                                        Sincronizando...
                                    </span>
                                    <span v-else>
                                        <i class="fas fa-sync"></i> Sincronizar Outlook
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Acciones Rápidas -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="fas fa-bolt"></i> Acciones Rápidas</h5>
                            </div>
                            <div class="card-body">
                                <button class="btn btn-primary me-2" @click="goToEmails">
                                    <i class="fas fa-inbox"></i> Ver Correos
                                </button>
                                <button class="btn btn-info me-2" @click="goToNewEmail">
                                    <i class="fas fa-plus"></i> Nuevo Correo
                                </button>
                                <button class="btn btn-warning" @click="showExcelModal">
                                    <i class="fas fa-file-excel"></i> Descargar Excel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Modal de Exportación a Excel -->
                <div v-if="showingExcelModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title"><i class="fas fa-file-excel"></i> Exportar a Excel</h5>
                                <button type="button" class="btn-close" @click="showingExcelModal = false"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-4">Descarga un reporte en Excel con los correos filtrados por rango de fechas. El reporte incluye información de auditoría mostrando qué usuario registró cada correo.</p>
                                
                                <form @submit.prevent="exportExcel">
                                    <div class="mb-3">
                                        <label for="dateFrom" class="form-label">
                                            <i class="fas fa-calendar"></i> Desde (Fecha de envío)
                                        </label>
                                        <input 
                                            type="date" 
                                            class="form-control" 
                                            id="dateFrom"
                                            v-model="excelForm.dateFrom"
                                            required
                                        >
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="dateTo" class="form-label">
                                            <i class="fas fa-calendar"></i> Hasta (Fecha de envío)
                                        </label>
                                        <input 
                                            type="date" 
                                            class="form-control" 
                                            id="dateTo"
                                            v-model="excelForm.dateTo"
                                            required
                                        >
                                    </div>
                                    
                                    <div class="mb-3 form-check">
                                        <input 
                                            type="checkbox" 
                                            class="form-check-input" 
                                            id="includeAudit"
                                            v-model="excelForm.includeAudit"
                                        >
                                        <label class="form-check-label" for="includeAudit">
                                            Incluir información de auditoría (usuario que registró, fecha de modificación, etc.)
                                        </label>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" @click="showingExcelModal = false">
                                    Cancelar
                                </button>
                                <button type="button" class="btn btn-success" @click="exportExcel" :disabled="exporting">
                                    <span v-if="exporting">
                                        <span class="spinner-border spinner-border-sm me-2"></span>
                                        Generando...
                                    </span>
                                    <span v-else>
                                        <i class="fas fa-download"></i> Descargar Excel
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Gráficos de Información -->
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="fas fa-bar-chart"></i> Correos por Importancia</h5>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm">
                                    <tr v-for="item in stats.by_importance" :key="item.importance">
                                        <td>{{ item.importance }}</td>
                                        <td>
                                            <span class="badge" :class="getImportanceBadge(item.importance)">
                                                {{ item.count }} correos
                                            </span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="fas fa-user"></i> Top 5 Remitentes</h5>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm">
                                    <tr v-for="(sender, idx) in stats.top_senders.slice(0, 5)" :key="idx">
                                        <td>{{ sender.sender }}</td>
                                        <td>
                                            <span class="badge badge-info">
                                                {{ sender.count }} correos
                                            </span>
                                        </td>
                                    </tr>
                                    <tr v-if="stats.top_senders.length === 0">
                                        <td colspan="2" class="text-center text-muted">No hay datos</td>
                                    </tr>
                                </table>
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
            stats: {
                total_emails: 0,
                emails_with_attachments: 0,
                emails_by_month: [],
                top_senders: [],
                by_importance: []
            },
            loading: true,
            syncing: false,
            showingExcelModal: false,
            exporting: false,
            authenticating: false,
            microsoftAuthenticated: false,
            microsoftEmail: null,
            excelForm: {
                dateFrom: this.getDefaultDateFrom(),
                dateTo: this.getDefaultDateTo(),
                includeAudit: true
            }
        };
    },
    
    computed: {
        emailsThisMonth() {
            const now = new Date();
            const currentMonth = now.getMonth() + 1;
            const currentYear = now.getFullYear();
            
            const item = this.stats.emails_by_month.find(m => 
                m.month === currentMonth && m.year === currentYear
            );
            
            return item ? item.count : 0;
        },
        
        topSender() {
            return this.stats.top_senders[0] || null;
        }
    },
    
    methods: {
        getDefaultDateFrom() {
            // 30 días atrás
            const date = new Date();
            date.setDate(date.getDate() - 30);
            return date.toISOString().split('T')[0];
        },
        
        getDefaultDateTo() {
            // Hoy
            return new Date().toISOString().split('T')[0];
        },
        
        async loadStats() {
            try {
                this.loading = true;
                const data = await APIService.getDashboardStats();
                this.stats = data;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando estadísticas'));
            } finally {
                this.loading = false;
            }
        },
        
        async syncOutlook() {
            if (!confirm('¿Sincronizar correos desde Outlook?')) return;
            
            try {
                this.syncing = true;
                const result = await APIService.syncOutlook();
                alert(`Sincronización completada:\n- Creados: ${result.stats.created}\n- Duplicados: ${result.stats.duplicates}`);
                await this.loadStats();
            } catch (err) {
                alert('Error sincronizando: ' + (err.error || 'Error desconocido'));
            } finally {
                this.syncing = false;
            }
        },
        
        showExcelModal() {
            this.excelForm.dateFrom = this.getDefaultDateFrom();
            this.excelForm.dateTo = this.getDefaultDateTo();
            this.showingExcelModal = true;
        },
        
        async exportExcel() {
            // Validar que dateFrom no sea mayor a dateTo
            if (this.excelForm.dateFrom > this.excelForm.dateTo) {
                alert('La fecha "Desde" no puede ser posterior a la fecha "Hasta"');
                return;
            }
            
            try {
                this.exporting = true;
                await APIService.exportToExcel(
                    this.excelForm.dateFrom,
                    this.excelForm.dateTo,
                    [],
                    this.excelForm.includeAudit
                );
                this.showingExcelModal = false;
                alert('Reporte descargado exitosamente');
            } catch (err) {
                alert('Error exportando a Excel: ' + (err.error || 'Error desconocido'));
            } finally {
                this.exporting = false;
            }
        },
        
        async exportData() {
            const format = prompt('¿En qué formato desea exportar? (csv/pdf):', 'csv');
            if (!format) return;
            
            try {
                if (format.toLowerCase() === 'csv') {
                    await APIService.exportToCSV();
                } else if (format.toLowerCase() === 'pdf') {
                    await APIService.exportToPDF();
                } else {
                    alert('Formato no válido. Use csv o pdf');
                }
            } catch (err) {
                alert('Error: ' + (err.error || 'Error exportando'));
            }
        },
        
        goToEmails() {
            window.location.hash = '#/emails';
        },
        
        goToNewEmail() {
            window.location.hash = '#/email-form';
        },
        
        getImportanceBadge(importance) {
            const map = {
                'High': 'badge-danger',
                'Normal': 'badge-info',
                'Low': 'badge-success'
            };
            return map[importance] || 'badge-secondary';
        },
        
        async checkMicrosoftStatus() {
            try {
                const response = await axios.get('/api/auth/microsoft/status', {
                    headers: {
                        'Authorization': `Bearer ${AuthService.getAccessToken()}`
                    }
                });
                
                const { is_microsoft_authenticated, microsoft_email } = response.data;
                this.microsoftAuthenticated = is_microsoft_authenticated;
                this.microsoftEmail = microsoft_email;
            } catch (error) {
                // Silenciosamente fallar si no está autenticado
                this.microsoftAuthenticated = false;
                this.microsoftEmail = null;
            }
        },
        
        async authenticateMicrosoft() {
            try {
                this.authenticating = true;
                
                // Obtener URL de autenticación de Microsoft
                const response = await axios.get('/api/auth/microsoft/login');
                const authUrl = response.data.auth_url;
                
                if (!authUrl) {
                    alert('Error: No se pudo obtener URL de autenticación');
                    return;
                }
                
                // Abrir en ventana emergente
                const width = 600;
                const height = 700;
                const left = window.screenX + (window.outerWidth - width) / 2;
                const top = window.screenY + (window.outerHeight - height) / 2;
                
                const popup = window.open(authUrl, 'microsoft_auth', 
                    `width=${width},height=${height},left=${left},top=${top}`);
                
                // Verificar periódicamente si la popup se cerró
                const checkPopup = setInterval(() => {
                    if (popup.closed) {
                        clearInterval(checkPopup);
                        this.authenticating = false;
                        
                        // Verificar el estado después de que se cierre la popup
                        setTimeout(() => {
                            this.checkMicrosoftStatus();
                        }, 1000);
                    }
                }, 1000);
                
            } catch (error) {
                alert('Error: ' + (error.response?.data?.error || error.message));
                this.authenticating = false;
            }
        },
        
        async disconnectMicrosoft() {
            if (!confirm('¿Estás seguro de que quieres desconectar tu cuenta de Microsoft?\n\nSiguirás usando Outlook local como fallback si está disponible.')) {
                return;
            }
            
            try {
                this.authenticating = true;
                
                await axios.post('/api/auth/microsoft/disconnect', {}, {
                    headers: {
                        'Authorization': `Bearer ${AuthService.getAccessToken()}`
                    }
                });
                
                this.microsoftAuthenticated = false;
                this.microsoftEmail = null;
                alert('Cuenta de Microsoft desconectada');
                
            } catch (error) {
                alert('Error desconectando: ' + (error.response?.data?.error || error.message));
            } finally {
                this.authenticating = false;
            }
        }
    },
    
    mounted() {
        this.loadStats();
        this.checkMicrosoftStatus();
    }
};

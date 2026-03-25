/**
 * Componente de Lista de Correos
 */
const EmailsListPage = {
    template: `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h1><i class="fas fa-inbox"></i> Correos Compartidos</h1>
                            <p class="text-muted">Vista compartida de todos los correos sincronizados del sistema</p>
                        </div>
                        <button class="btn btn-primary" @click="goToNewEmail">
                            <i class="fas fa-plus"></i> Nuevo Correo
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Filtros y Búsqueda -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-filter"></i> Filtros y Búsqueda</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Buscar</label>
                                    <div class="search-box">
                                        <i class="fas fa-search"></i>
                                        <input 
                                            type="text" 
                                            class="form-control" 
                                            v-model="searchTerm"
                                            placeholder="Asunto, remitente, destinatario..."
                                            @keyup.enter="search"
                                        >
                                    </div>
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Remitente</label>
                                    <input 
                                        type="text" 
                                        class="form-control" 
                                        v-model="filters.sender"
                                        placeholder="Filtrar por remitente"
                                        @change="loadEmails"
                                    >
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Desde</label>
                                    <input 
                                        type="date" 
                                        class="form-control" 
                                        v-model="filters.date_from"
                                        @change="loadEmails"
                                    >
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Hasta</label>
                                    <input 
                                        type="date" 
                                        class="form-control" 
                                        v-model="filters.date_to"
                                        @change="loadEmails"
                                    >
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Con Archivos Adjuntos</label>
                                    <select class="form-select" v-model="filters.has_attachments" @change="loadEmails">
                                        <option value="">Todos</option>
                                        <option value="true">Sí</option>
                                        <option value="false">No</option>
                                    </select>
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">&nbsp;</label>
                                    <button class="btn btn-secondary w-100" @click="clearFilters">
                                        <i class="fas fa-times"></i> Limpiar Filtros
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Acciones en lote -->
            <div v-if="selectedEmails.length > 0" class="row mb-4">
                <div class="col-12">
                    <div class="alert alert-warning">
                        <div class="d-flex justify-content-between align-items-center">
                            <span><strong>{{ selectedEmails.length }} correos seleccionados</strong></span>
                            <div>
                                <button class="btn btn-sm btn-primary ms-2" @click="exportSelectedCSV">
                                    <i class="fas fa-file-csv"></i> Exportar CSV
                                </button>
                                <button class="btn btn-sm btn-primary ms-2" @click="exportSelectedPDF">
                                    <i class="fas fa-file-pdf"></i> Exportar PDF
                                </button>
                                <button class="btn btn-sm btn-danger ms-2" @click="deleteSelectedEmails" :disabled="deleting">
                                    <span v-if="deleting">
                                        <span class="spinner-border spinner-border-sm me-2"></span>
                                        Eliminando...
                                    </span>
                                    <span v-else>
                                        <i class="fas fa-trash"></i> Eliminar Seleccionados
                                    </span>
                                </button>
                                <button class="btn btn-sm btn-secondary ms-2" @click="clearSelection">
                                    Limpiar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tabla de Correos -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-list"></i> 
                                Correos ({{ pagination.total }})
                            </h5>
                        </div>
                        <div class="card-body">
                            <div v-if="loading" class="loading">
                                <div class="spinner-border"></div>
                            </div>
                            
                            <div v-else-if="emails.length === 0" class="alert alert-info">
                                No hay correos disponibles
                            </div>
                            
                            <div v-else>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th style="width: 40px;">
                                                    <input 
                                                        type="checkbox" 
                                                        @change="toggleSelectAll"
                                                        :checked="selectedEmails.length === emails.length && emails.length > 0"
                                                    >
                                                </th>
                                                <th>Fecha</th>
                                                <th>Asunto</th>
                                                <th>Remitente</th>
                                                <th>Destinatarios</th>
                                                <th>Adjuntos</th>
                                                <th>Importancia</th>
                                                <th>Acciones</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="email in emails" :key="email.id">
                                                <td>
                                                    <input 
                                                        type="checkbox" 
                                                        :checked="selectedEmails.includes(email.id)"
                                                        @change="toggleSelect(email.id)"
                                                    >
                                                </td>
                                                <td>{{ formatDate(email.sent_date) }}</td>
                                                <td>
                                                    <a href="#" @click.prevent="viewEmail(email.id)" style="text-decoration: none;">
                                                        {{ email.subject.substring(0, 50) }}{{ email.subject.length > 50 ? '...' : '' }}
                                                    </a>
                                                </td>
                                                <td>{{ email.sender.substring(0, 30) }}</td>
                                                <td>
                                                    <small>{{ email.recipients.length }} destinatarios</small>
                                                </td>
                                                <td>
                                                    <i v-if="email.has_attachments" class="fas fa-paperclip text-warning" title="Tiene adjuntos"></i>
                                                    <span v-else class="text-muted">-</span>
                                                </td>
                                                <td>
                                                    <span class="badge" :class="getImportanceBadge(email.importance)">
                                                        {{ email.importance }}
                                                    </span>
                                                </td>
                                                <td>
                                                    <button class="btn btn-sm btn-info me-2" @click="viewEmail(email.id)" title="Ver">
                                                        <i class="fas fa-eye"></i>
                                                    </button>
                                                    <button class="btn btn-sm btn-warning me-2" @click="editEmail(email.id)" title="Editar">
                                                        <i class="fas fa-edit"></i>
                                                    </button>
                                                    <button class="btn btn-sm btn-danger" @click="deleteEmail(email.id)" title="Eliminar">
                                                        <i class="fas fa-trash"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                
                                <!-- Paginación -->
                                <nav v-if="pagination.pages > 1">
                                    <ul class="pagination">
                                        <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                                            <a class="page-link" href="#" @click.prevent="previousPage">Anterior</a>
                                        </li>
                                        <li v-for="p in pagination.pages" :key="p" class="page-item" 
                                            :class="{ active: pagination.page === p }">
                                            <a class="page-link" href="#" @click.prevent="goToPage(p)">{{ p }}</a>
                                        </li>
                                        <li class="page-item" :class="{ disabled: pagination.page === pagination.pages }">
                                            <a class="page-link" href="#" @click.prevent="nextPage">Siguiente</a>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Detalles -->
            <div v-if="selectedEmail" class="modal d-block" style="display: block; background: rgba(0,0,0,0.5);">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Detalles del Correo</h5>
                            <button type="button" class="btn-close" @click="selectedEmail = null"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>Fecha:</strong> {{ formatDate(selectedEmail.sent_date) }}</p>
                            <p><strong>Asunto:</strong> {{ selectedEmail.subject }}</p>
                            <p><strong>Remitente:</strong> {{ selectedEmail.sender }}</p>
                            <p><strong>Destinatarios:</strong></p>
                            <ul>
                                <li v-for="(recipient, idx) in selectedEmail.recipients" :key="idx">
                                    {{ recipient.name || recipient.email }} ({{ recipient.email }})
                                </li>
                            </ul>
                            <p><strong>Contenido:</strong></p>
                            <div class="alert alert-light">
                                {{ selectedEmail.body_snippet || 'Sin contenido' }}
                            </div>
                            <p v-if="selectedEmail.has_attachments">
                                <strong><i class="fas fa-paperclip"></i> Archivos Adjuntos:</strong> 
                                {{ selectedEmail.attachment_count }} archivo(s)
                            </p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="selectedEmail = null">Cerrar</button>
                            <button type="button" class="btn btn-warning" @click="editEmail(selectedEmail.id); selectedEmail = null;">
                                <i class="fas fa-edit"></i> Editar
                            </button>
                            <button type="button" class="btn btn-danger" @click="deleteEmail(selectedEmail.id); selectedEmail = null;">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
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
            emails: [],
            selectedEmails: [],
            selectedEmail: null,
            deleting: false,
            loading: true,
            searchTerm: '',
            filters: {
                subject: '',
                sender: '',
                recipient: '',
                date_from: '',
                date_to: '',
                has_attachments: ''
            },
            pagination: {
                page: 1,
                per_page: 20,
                total: 0,
                pages: 1
            }
        };
    },
    
    methods: {
        async loadEmails() {
            try {
                this.loading = true;
                const filters = {};
                if (this.filters.sender) filters.sender = this.filters.sender;
                if (this.filters.date_from) filters.date_from = this.filters.date_from;
                if (this.filters.date_to) filters.date_to = this.filters.date_to;
                if (this.filters.has_attachments) filters.has_attachments = this.filters.has_attachments === 'true';
                
                // Obtener TODOS los correos compartidos (no solo del usuario)
                const data = await APIService.getSharedEmails(this.pagination.page, filters);
                this.emails = data.emails;
                this.pagination = data.pagination;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando correos'));
            } finally {
                this.loading = false;
            }
        },
        
        async search() {
            if (!this.searchTerm) {
                this.loadEmails();
                return;
            }
            
            try {
                this.loading = true;
                // Buscar en TODOS los correos compartidos
                const data = await APIService.searchSharedEmails(this.searchTerm, this.pagination.page);
                this.emails = data.emails;
                this.pagination = data.pagination;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error buscando'));
            } finally {
                this.loading = false;
            }
        },
        
        async viewEmail(emailId) {
            try {
                const data = await APIService.getEmail(emailId);
                this.selectedEmail = data.email;
            } catch (err) {
                alert('Error: ' + (err.error || 'Error cargando correo'));
            }
        },
        
        async deleteEmail(emailId) {
            if (!confirm('¿Está seguro de que desea eliminar este correo?')) return;
            
            try {
                await APIService.deleteEmail(emailId);
                this.selectedEmail = null;
                this.loadEmails();
                alert('Correo eliminado exitosamente');
            } catch (err) {
                alert('Error: ' + (err.error || 'Error eliminando'));
            }
        },
        
        async deleteSelectedEmails() {
            if (this.selectedEmails.length === 0) {
                alert('Selecciona al menos un correo para eliminar');
                return;
            }
            
            const count = this.selectedEmails.length;
            if (!confirm(`¿Está seguro de que desea eliminar ${count} correo(s)?`)) return;
            
            this.deleting = true;
            try {
                // Eliminar cada correo seleccionado
                for (const emailId of this.selectedEmails) {
                    try {
                        await APIService.deleteEmail(emailId);
                    } catch (err) {
                        console.error(`Error eliminando correo ${emailId}:`, err);
                    }
                }
                
                // Limpiar la selección y recargar
                this.selectedEmails = [];
                this.selectedEmail = null;
                await this.loadEmails();
                alert(`${count} correo(s) eliminado(s) exitosamente`);
            } catch (err) {
                alert('Error: ' + (err.error || 'Error eliminando'));
            } finally {
                this.deleting = false;
            }
        },
        
        editEmail(emailId) {
            window.location.hash = '#/email-form?id=' + emailId;
        },
        
        goToNewEmail() {
            window.location.hash = '#/email-form';
        },
        
        clearFilters() {
            this.filters = {
                subject: '',
                sender: '',
                recipient: '',
                date_from: '',
                date_to: '',
                has_attachments: ''
            };
            this.searchTerm = '';
            this.pagination.page = 1;
            this.loadEmails();
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
        
        toggleSelect(emailId) {
            const idx = this.selectedEmails.indexOf(emailId);
            if (idx > -1) {
                this.selectedEmails.splice(idx, 1);
            } else {
                this.selectedEmails.push(emailId);
            }
        },
        
        toggleSelectAll() {
            if (this.selectedEmails.length === this.emails.length) {
                this.selectedEmails = [];
            } else {
                this.selectedEmails = this.emails.map(e => e.id);
            }
        },
        
        clearSelection() {
            this.selectedEmails = [];
        },
        
        async exportSelectedCSV() {
            try {
                await APIService.exportToCSV(this.selectedEmails);
                this.clearSelection();
            } catch (err) {
                alert('Error: ' + (err.error || 'Error exportando'));
            }
        },
        
        async exportSelectedPDF() {
            try {
                await APIService.exportToPDF(this.selectedEmails);
                this.clearSelection();
            } catch (err) {
                alert('Error: ' + (err.error || 'Error exportando'));
            }
        },
        
        goToPage(page) {
            this.pagination.page = page;
            this.loadEmails();
        },
        
        previousPage() {
            if (this.pagination.page > 1) {
                this.pagination.page--;
                this.loadEmails();
            }
        },
        
        nextPage() {
            if (this.pagination.page < this.pagination.pages) {
                this.pagination.page++;
                this.loadEmails();
            }
        },
        
        getImportanceBadge(importance) {
            const map = {
                'High': 'badge-danger',
                'Normal': 'badge-info',
                'Low': 'badge-success'
            };
            return map[importance] || 'badge-secondary';
        }
    },
    
    mounted() {
        this.loadEmails();
    }
};

/**
 * Componente de Formulario de Correo
 */
const EmailFormPage = {
    template: `
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h1><i class="fas fa-envelope"></i> {{ isEdit ? 'Editar Correo' : 'Nuevo Correo' }}</h1>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-8 offset-md-2">
                    <div class="card">
                        <div class="card-body">
                            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                                {{ error }}
                                <button type="button" class="btn-close" @click="error = ''"></button>
                            </div>
                            
                            <form @submit.prevent="handleSubmit">
                                <div class="mb-3">
                                    <label for="subject" class="form-label">Asunto *</label>
                                    <input 
                                        type="text" 
                                        class="form-control" 
                                        id="subject"
                                        v-model="form.subject"
                                        required
                                        :disabled="loading"
                                    >
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="sender" class="form-label">Remitente *</label>
                                        <input 
                                            type="email" 
                                            class="form-control" 
                                            id="sender"
                                            v-model="form.sender"
                                            required
                                            :disabled="loading"
                                        >
                                    </div>
                                    
                                    <div class="col-md-6 mb-3">
                                        <label for="sent_date" class="form-label">Fecha de Envío *</label>
                                        <input 
                                            type="datetime-local" 
                                            class="form-control" 
                                            id="sent_date"
                                            v-model="form.sent_date"
                                            required
                                            :disabled="loading"
                                        >
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="recipients" class="form-label">Destinatarios *</label>
                                    <div v-for="(recipient, idx) in form.recipients" :key="idx" class="input-group mb-2">
                                        <input 
                                            type="email" 
                                            class="form-control" 
                                            v-model="recipient.email"
                                            placeholder="correo@example.com"
                                            :disabled="loading"
                                        >
                                        <input 
                                            type="text" 
                                            class="form-control" 
                                            v-model="recipient.name"
                                            placeholder="Nombre (opcional)"
                                            :disabled="loading"
                                        >
                                        <button 
                                            type="button" 
                                            class="btn btn-danger" 
                                            @click="removeRecipient(idx)"
                                            :disabled="loading || form.recipients.length === 1"
                                        >
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                    <button 
                                        type="button" 
                                        class="btn btn-secondary btn-sm mt-2"
                                        @click="addRecipient"
                                        :disabled="loading"
                                    >
                                        <i class="fas fa-plus"></i> Agregar Destinatario
                                    </button>
                                    <div class="mt-3">
                                        <label for="bulkRecipients" class="form-label">Agregar destinatarios masivos</label>
                                        <textarea
                                            id="bulkRecipients"
                                            class="form-control"
                                            v-model="bulkRecipients"
                                            rows="2"
                                            placeholder="Pega aquí correos separados por coma o punto y coma"
                                            :disabled="loading"
                                        ></textarea>
                                        <button
                                            type="button"
                                            class="btn btn-info btn-sm mt-2"
                                            @click="addBulkRecipients"
                                            :disabled="loading || !bulkRecipients.trim()"
                                        >
                                            <i class="fas fa-user-plus"></i> Agregar Correos Masivos
                                        </button>
                                        <small class="form-text text-muted">Ejemplo: correo1@dom.com, correo2@dom.com; correo3@dom.com</small>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="body_snippet" class="form-label">Fragmento de Contenido</label>
                                    <textarea 
                                        class="form-control" 
                                        id="body_snippet"
                                        v-model="form.body_snippet"
                                        rows="4"
                                        placeholder="Primeras líneas del contenido del correo..."
                                        :disabled="loading"
                                    ></textarea>
                                    <small class="form-text">Se guardarán los primeros 200 caracteres</small>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="importance" class="form-label">Importancia</label>
                                        <select class="form-select" id="importance" v-model="form.importance" :disabled="loading">
                                            <option value="Low">Baja</option>
                                            <option value="Normal">Normal</option>
                                            <option value="High">Alta</option>
                                        </select>
                                    </div>
                                    
                                    <div class="col-md-6 mb-3">
                                        <label for="has_attachments" class="form-label">Archivos Adjuntos</label>
                                        <div class="form-check mt-2">
                                            <input 
                                                class="form-check-input" 
                                                type="checkbox" 
                                                id="has_attachments"
                                                v-model="form.has_attachments"
                                                :disabled="loading"
                                            >
                                            <label class="form-check-label" for="has_attachments">
                                                ¿Tiene archivos adjuntos?
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                
                                <div v-if="form.has_attachments" class="mb-3">
                                    <label for="attachment_count" class="form-label">Cantidad de Adjuntos</label>
                                    <input 
                                        type="number" 
                                        class="form-control" 
                                        id="attachment_count"
                                        v-model.number="form.attachment_count"
                                        min="0"
                                        :disabled="loading"
                                    >
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button 
                                        type="submit" 
                                        class="btn btn-primary btn-lg"
                                        :disabled="loading"
                                    >
                                        <span v-if="loading">
                                            <span class="spinner-border spinner-border-sm me-2"></span>
                                            Guardando...
                                        </span>
                                        <span v-else>
                                            <i class="fas fa-save"></i> {{ isEdit ? 'Actualizar' : 'Crear' }} Correo
                                        </span>
                                    </button>
                                    
                                    <button 
                                        type="button" 
                                        class="btn btn-secondary btn-lg"
                                        @click="goBack"
                                        :disabled="loading"
                                    >
                                        <i class="fas fa-arrow-left"></i> Volver
                                    </button>
                                </div>
                            </form>
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
            isEdit: false,
            emailId: null,
            loading: false,
            error: '',
            bulkRecipients: '', // Para capturar correos masivos
            form: {
                subject: '',
                sender: '',
                recipients: [{ email: '', name: '' }],
                sent_date: new Date().toISOString().slice(0, 16),
                body_snippet: '',
                importance: 'Normal',
                has_attachments: false,
                attachment_count: 0
            }
        };
    },
    
    methods: {
        async loadEmail(emailId) {
            try {
                this.loading = true;
                const data = await APIService.getEmail(emailId);
                const email = data.email;
                
                this.form = {
                    subject: email.subject,
                    sender: email.sender,
                    recipients: email.recipients.length > 0 ? email.recipients : [{ email: '', name: '' }],
                    sent_date: email.sent_date.slice(0, 16),
                    body_snippet: email.body_snippet || '',
                    importance: email.importance,
                    has_attachments: email.has_attachments,
                    attachment_count: email.attachment_count
                };
            } catch (err) {
                this.error = err.error || 'Error cargando correo';
            } finally {
                this.loading = false;
            }
        },
        
        async handleSubmit() {
            // Validaciones
            // Si no hay destinatarios válidos, mostrar error
            if (!this.form.subject || !this.form.sender) {
                this.error = 'Por favor complete los campos requeridos';
                return;
            }
            // Permitir que la lista de destinatarios esté vacía solo si hay destinatarios masivos pendientes
            const validRecipients = this.form.recipients.filter(r => r.email).length;
            if (validRecipients === 0 && (!this.bulkRecipients || !this.bulkRecipients.trim())) {
                this.error = 'Debe agregar al menos un destinatario (individual o masivo)';
                return;
            }
            // Si hay destinatarios masivos pendientes, agrégalos antes de enviar
            if (this.bulkRecipients && this.bulkRecipients.trim()) {
                this.addBulkRecipients();
            }
            
            try {
                this.loading = true;
                this.error = '';
                
                const payload = {
                    ...this.form,
                    recipients: this.form.recipients.filter(r => r.email)
                };
                
                console.log('Payload a enviar:', payload);
                
                // TEST: Usar endpoint de debug primero
                const debugResponse = await axios.post('/api/emails/debug/create', payload, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                console.log('Debug response:', debugResponse.data);
                
                if (this.isEdit) {
                    await APIService.updateEmail(this.emailId, payload);
                    alert('Correo actualizado exitosamente');
                } else {
                    await APIService.createEmail(payload);
                    alert('Correo creado exitosamente');
                }
                
                window.location.hash = '#/emails';
            } catch (err) {
                console.error('Error en handleSubmit:', err.response?.data || err);
                this.error = err.response?.data?.error || err.error || 'Error guardando correo';
            } finally {
                this.loading = false;
            }
        },
        
        addRecipient() {
            this.form.recipients.push({ email: '', name: '' });
        },
        
        removeRecipient(idx) {
            this.form.recipients.splice(idx, 1);
        },
        
        goBack() {
            window.location.hash = '#/emails';
        },
        addBulkRecipients() {
            // Separar por coma o punto y coma
            if (!this.bulkRecipients.trim()) return;
            const emails = this.bulkRecipients.split(/[;,]+/)
                .map(e => e.trim())
                .filter(e => e.length > 0);
            // Agregar solo los que no estén ya en la lista
            emails.forEach(email => {
                if (email && !this.form.recipients.some(r => r.email === email)) {
                    this.form.recipients.push({ email, name: '' });
                }
            });
            this.bulkRecipients = '';
        }
    },
    
    mounted() {
        // Obtener ID de la URL si es edición
        const params = new URLSearchParams(window.location.hash.split('?')[1]);
        const id = params.get('id');
        
        if (id) {
            this.isEdit = true;
            this.emailId = parseInt(id);
            this.loadEmail(this.emailId);
        }
    }
};

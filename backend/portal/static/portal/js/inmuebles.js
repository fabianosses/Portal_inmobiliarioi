// portal/static/portal/js/inmuebles.js

class InmuebleManager {
    constructor() {
        this.initEventListeners();
        this.setupFormValidation();
        this.setupFormSubmission();
    }

    initEventListeners() {
        // Cargar comunas cuando cambia la región
        const regionSelect = document.getElementById('id_region_codigo');
        if (regionSelect) {
            regionSelect.addEventListener('change', () => this.cargarComunas());
        }

        // Validación de imagen en tiempo real
        const imagenInput = document.querySelector('input[type="file"]');
        if (imagenInput) {
            imagenInput.addEventListener('change', (e) => this.validarImagen(e));
        }

        // Validación de formulario antes de enviar
        const form = document.getElementById('inmuebleForm');
        if (form) {
            form.addEventListener('submit', (e) => this.validarFormulario(e));
        }
    }

    setupFormSubmission() {
        const form = document.getElementById('inmuebleForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                // Habilitar el campo de comuna antes de enviar el formulario
                const comunaSelect = document.getElementById('id_comuna_codigo');
                if (comunaSelect && comunaSelect.disabled) {
                    comunaSelect.disabled = false;
                }
                
                // También asegurarse de que tenga un valor seleccionado
                if (comunaSelect && !comunaSelect.value) {
                    e.preventDefault();
                    this.mostrarError('Por favor, selecciona una comuna');
                    comunaSelect.focus();
                }
            });
        }
    }

    setupFormValidation() {
        // Agregar validación personalizada a campos numéricos
        const numericFields = document.querySelectorAll('input[type="number"]');
        numericFields.forEach(field => {
            field.addEventListener('blur', () => this.validarCampoNumerico(field));
        });
    }

    async cargarComunas() {
        const regionSelect = document.getElementById('id_region_codigo');
        const comunaSelect = document.getElementById('id_comuna_codigo');
        const loadingDiv = document.getElementById('comuna-loading');
        
        if (!regionSelect || !comunaSelect) return;
        
        const regionCode = regionSelect.value;
        
        // Resetear comuna
        comunaSelect.disabled = true;
        comunaSelect.innerHTML = '<option value="">Cargando...</option>';
        
        if (!regionCode) {
            comunaSelect.innerHTML = '<option value="">Selecciona una región primero</option>';
            return;
        }
        
        // Mostrar loading
        if (loadingDiv) loadingDiv.style.display = 'block';
        
        try {
            const response = await fetch(`/cargar-comunas/?region=${encodeURIComponent(regionCode)}`);
            
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (Array.isArray(data)) {
                comunaSelect.innerHTML = '<option value="">Selecciona una comuna</option>';
                data.forEach(comuna => {
                    const option = document.createElement('option');
                    option.value = comuna.codigo;
                    option.textContent = comuna.nombre;
                    comunaSelect.appendChild(option);
                });
                comunaSelect.disabled = false;
            } else {
                throw new Error('Formato de respuesta inválido');
            }
        } catch (error) {
            console.error('Error cargando comunas:', error);
            this.mostrarError('Error al cargar las comunas. Por favor, intenta nuevamente.');
            comunaSelect.innerHTML = '<option value="">Error cargando comunas</option>';
        } finally {
            if (loadingDiv) loadingDiv.style.display = 'none';
        }
    }

    validarImagen(e) {
        const file = e.target.files[0];
        if (!file) return;

        const maxSize = 5 * 1024 * 1024; // 5MB
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

        // Validar tamaño
        if (file.size > maxSize) {
            this.mostrarError('La imagen es demasiado grande. Máximo 5MB permitido.');
            e.target.value = '';
            return;
        }

        // Validar tipo
        if (!validTypes.includes(file.type)) {
            this.mostrarError('Solo se permiten imágenes JPG, PNG o WebP.');
            e.target.value = '';
            return;
        }

        // Mostrar preview
        this.mostrarPreviewImagen(file);
    }

    mostrarPreviewImagen(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            let preview = document.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('img');
                preview.className = 'image-preview img-thumbnail mt-2';
                preview.style.maxWidth = '200px';
                document.querySelector('input[type="file"]').parentNode.appendChild(preview);
            }
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    validarCampoNumerico(field) {
        const value = parseFloat(field.value);
        const min = parseFloat(field.min) || 0;

        if (field.value && value < min) {
            this.mostrarErrorCampo(field, `El valor debe ser mayor o igual a ${min}`);
        } else {
            this.limpiarErrorCampo(field);
        }

        // Validación específica para metros cuadrados
        if (field.name === 'm2_construidos' || field.name === 'm2_totales') {
            this.validarMetrosCuadrados();
        }
    }

    validarMetrosCuadrados() {
        const m2Construidos = document.querySelector('[name="m2_construidos"]');
        const m2Totales = document.querySelector('[name="m2_totales"]');
        
        if (m2Construidos && m2Totales && m2Construidos.value && m2Totales.value) {
            const construidos = parseFloat(m2Construidos.value);
            const totales = parseFloat(m2Totales.value);
            
            if (construidos > totales) {
                this.mostrarErrorCampo(m2Construidos, 'Los m² construidos no pueden ser mayores a los m² totales');
            } else {
                this.limpiarErrorCampo(m2Construidos);
            }
        }
    }

    validarFormulario(e) {
        let esValido = true;
        const camposRequeridos = document.querySelectorAll('[required]');
        
        // Limpiar errores previos
        this.limpiarErrores();
        
        // Validar campos requeridos
        camposRequeridos.forEach(campo => {
            if (!campo.value.trim()) {
                this.mostrarErrorCampo(campo, 'Este campo es obligatorio');
                esValido = false;
            }
        });

        // Validaciones específicas
        const precio = document.querySelector('[name="precio_mensual"]');
        if (precio && precio.value && parseFloat(precio.value) <= 0) {
            this.mostrarErrorCampo(precio, 'El precio debe ser mayor a 0');
            esValido = false;
        }

        if (!esValido) {
            e.preventDefault();
            this.mostrarError('Por favor, completa todos los campos obligatorios y corrige los errores.');
            // Scroll al primer error
            const primerError = document.querySelector('.is-invalid');
            if (primerError) {
                primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    mostrarErrorCampo(campo, mensaje) {
        campo.classList.add('is-invalid');
        
        let errorDiv = campo.parentNode.querySelector('.field-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            campo.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = mensaje;
    }

    limpiarErrorCampo(campo) {
        campo.classList.remove('is-invalid');
        const errorDiv = campo.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    limpiarErrores() {
        document.querySelectorAll('.is-invalid').forEach(campo => {
            campo.classList.remove('is-invalid');
        });
        document.querySelectorAll('.field-error').forEach(error => {
            error.remove();
        });
    }

    mostrarError(mensaje) {
        this.mostrarMensaje(mensaje, 'danger');
    }

    mostrarExito(mensaje) {
        this.mostrarMensaje(mensaje, 'success');
    }

    mostrarMensaje(mensaje, tipo) {
        // Crear o reutilizar contenedor de mensajes
        let container = document.getElementById('mensajes-flotantes');
        if (!container) {
            container = document.createElement('div');
            container.id = 'mensajes-flotantes';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }

        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
        mensajeDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(mensajeDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (mensajeDiv.parentNode) {
                mensajeDiv.remove();
            }
        }, 5000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new InmuebleManager();
    
    // Verificar mensajes del servidor
    const mensajesServidor = document.querySelectorAll('.alert');
    mensajesServidor.forEach(alert => {
        if (alert.textContent.includes('INMUEBLE_CREADO_EXITOSAMENTE')) {
            setTimeout(() => {
                alert.remove();
            }, 3000);
        }
    });
});
/**
 * Displays a Bootstrap toast notification.
 * @param {string} message The message to display.
 * @param {string} type The type of toast ('info', 'success', 'warning', 'error').
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    const toastId = 'toast-' + Date.now();
    
    const toastTypeClasses = {
        error: 'bg-danger',
        success: 'bg-success',
        warning: 'bg-warning',
        info: 'bg-info'
    };

    const toastIconClasses = {
        error: 'bi-exclamation-triangle',
        success: 'bi-check-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };

    const toastHtml = `
        <div class="toast align-items-center text-white ${toastTypeClasses[type] || 'bg-info'} border-0" 
             role="alert" aria-live="assertive" aria-atomic="true" id="${toastId}">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${toastIconClasses[type] || 'bi-info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
    
    document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055'; // Ensure it's above modals
    document.body.appendChild(container);
    return container;
}
// Funciones para el carrito de compras
function addToCart(productId) {
    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Producto agregado al carrito', 'success');
            updateCartCount(data.cartCount);
        } else {
            showAlert('Error al agregar el producto', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al agregar el producto', 'danger');
    });
}

function updateQuantity(productId, change) {
    fetch(`/cart/update/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ change: change })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showAlert('Error al actualizar la cantidad', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al actualizar la cantidad', 'danger');
    });
}

function removeFromCart(productId) {
    fetch(`/cart/remove/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showAlert('Error al eliminar el producto', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al eliminar el producto', 'danger');
    });
}

function updateCartCount(count) {
    const cartCountElement = document.getElementById('cartCount');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

function checkout() {
    window.location.href = '/checkout';
}

// Funciones para el panel de administración
function editProduct(productId) {
    fetch(`/admin/product/${productId}`)
        .then(response => response.json())
        .then(product => {
            document.getElementById('edit_product_id').value = product.id;
            document.getElementById('edit_name').value = product.name;
            document.getElementById('edit_description').value = product.description;
            document.getElementById('edit_price').value = product.price;
            document.getElementById('edit_stock').value = product.stock;
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar los datos del producto', 'danger');
        });
}

function deleteProduct(productId) {
    if (confirm('¿Estás seguro de que deseas eliminar este producto?')) {
        fetch(`/admin/product/${productId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Producto eliminado correctamente', 'success');
                location.reload();
            } else {
                showAlert('Error al eliminar el producto', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al eliminar el producto', 'danger');
        });
    }
}

// Función para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-cerrar la alerta después de 3 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}); 
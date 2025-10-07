/**
 * Script principal pour l'application de gestion d'inventaire
 * Gère les interactions utilisateur, les animations et les fonctionnalités communes
 */

// Variables globales
let isScanning = false;
let scanHistory = [];

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialise l'application
 */
function initializeApp() {
    // Initialiser les tooltips Bootstrap
    initializeTooltips();
    
    // Initialiser les animations
    initializeAnimations();
    
    // Initialiser les gestionnaires d'événements
    initializeEventHandlers();
    
    // Charger les préférences utilisateur
    loadUserPreferences();
    
    console.log('Application initialisée avec succès');
}

/**
 * Initialise les tooltips Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialise les animations d'entrée
 */
function initializeAnimations() {
    // Ajouter la classe fade-in aux cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

/**
 * Initialise les gestionnaires d'événements globaux
 */
function initializeEventHandlers() {
    // Gestionnaire pour les formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Gestionnaire pour les boutons de suppression
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', handleDeleteConfirmation);
    });
    
    // Gestionnaire pour les champs de recherche
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', handleSearch);
    });
    
    // Gestionnaire pour les raccourcis clavier
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

/**
 * Gère la soumission des formulaires
 */
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        // Ajouter un spinner de chargement
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Traitement...';
        submitButton.disabled = true;
        
        // Restaurer le bouton après 3 secondes (au cas où)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    }
}

/**
 * Gère les confirmations de suppression
 */
function handleDeleteConfirmation(event) {
    event.preventDefault();
    
    const button = event.target.closest('a, button');
    const itemName = button.dataset.itemName || 'cet élément';
    
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${itemName} ?\n\nCette action est irréversible.`)) {
        window.location.href = button.href;
    }
}

/**
 * Gère la recherche en temps réel
 */
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const targetSelector = event.target.dataset.search;
    const items = document.querySelectorAll(targetSelector);
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = '';
            item.classList.remove('d-none');
        } else {
            item.style.display = 'none';
            item.classList.add('d-none');
        }
    });
}

/**
 * Gère les raccourcis clavier
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K : Focus sur la recherche
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[data-search]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Échap : Fermer les modals et scanners
    if (event.key === 'Escape') {
        closeAllModals();
        stopAllScanners();
    }
    
    // Ctrl/Cmd + S : Scanner (si on est sur la page scanner)
    if ((event.ctrlKey || event.metaKey) && event.key === 's' && window.location.pathname.includes('scanner')) {
        event.preventDefault();
        const startButton = document.getElementById('startCamera');
        if (startButton && startButton.style.display !== 'none') {
            startButton.click();
        }
    }
}

/**
 * Ferme tous les modals ouverts
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

/**
 * Arrête tous les scanners actifs
 */
function stopAllScanners() {
    if (typeof Quagga !== 'undefined' && isScanning) {
        Quagga.stop();
        isScanning = false;
        
        const stopButton = document.getElementById('stopCamera');
        const startButton = document.getElementById('startCamera');
        
        if (stopButton) stopButton.style.display = 'none';
        if (startButton) startButton.style.display = 'inline-block';
    }
}

/**
 * Charge les préférences utilisateur depuis le localStorage
 */
function loadUserPreferences() {
    const preferences = localStorage.getItem('inventaire_preferences');
    if (preferences) {
        try {
            const prefs = JSON.parse(preferences);
            applyUserPreferences(prefs);
        } catch (error) {
            console.warn('Erreur lors du chargement des préférences:', error);
        }
    }
}

/**
 * Applique les préférences utilisateur
 */
function applyUserPreferences(preferences) {
    // Thème sombre/clair
    if (preferences.theme === 'dark') {
        document.body.classList.add('dark-theme');
    }
    
    // Taille de police
    if (preferences.fontSize) {
        document.body.style.fontSize = preferences.fontSize;
    }
    
    // Autres préférences...
}

/**
 * Sauvegarde les préférences utilisateur
 */
function saveUserPreferences(preferences) {
    localStorage.setItem('inventaire_preferences', JSON.stringify(preferences));
}

/**
 * Utilitaires pour les notifications
 */
const Notifications = {
    /**
     * Affiche une notification de succès
     */
    success: function(message, duration = 5000) {
        this.show(message, 'success', duration);
    },
    
    /**
     * Affiche une notification d'erreur
     */
    error: function(message, duration = 7000) {
        this.show(message, 'danger', duration);
    },
    
    /**
     * Affiche une notification d'information
     */
    info: function(message, duration = 5000) {
        this.show(message, 'info', duration);
    },
    
    /**
     * Affiche une notification d'avertissement
     */
    warning: function(message, duration = 6000) {
        this.show(message, 'warning', duration);
    },
    
    /**
     * Affiche une notification
     */
    show: function(message, type = 'info', duration = 5000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
        `;
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-suppression
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
};

/**
 * Utilitaires pour les requêtes API
 */
const API = {
    /**
     * Effectue une requête GET
     */
    get: async function(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Erreur API GET:', error);
            Notifications.error('Erreur de communication avec le serveur');
            throw error;
        }
    },
    
    /**
     * Effectue une requête POST
     */
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erreur API POST:', error);
            Notifications.error('Erreur de communication avec le serveur');
            throw error;
        }
    }
};

/**
 * Utilitaires pour le formatage
 */
const Format = {
    /**
     * Formate un prix en euros
     */
    price: function(price) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(price);
    },
    
    /**
     * Formate une date
     */
    date: function(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    /**
     * Formate un nombre
     */
    number: function(number) {
        return new Intl.NumberFormat('fr-FR').format(number);
    }
};

/**
 * Utilitaires pour la validation
 */
const Validation = {
    /**
     * Valide un code-barres
     */
    barcode: function(barcode) {
        // Vérifier que c'est un nombre et qu'il a une longueur appropriée
        const cleaned = barcode.replace(/\D/g, '');
        return cleaned.length >= 8 && cleaned.length <= 18;
    },
    
    /**
     * Valide un prix
     */
    price: function(price) {
        const num = parseFloat(price);
        return !isNaN(num) && num >= 0;
    },
    
    /**
     * Valide un stock
     */
    stock: function(stock) {
        const num = parseInt(stock);
        return !isNaN(num) && num >= 0;
    },
    
    /**
     * Valide un nom de produit
     */
    productName: function(name) {
        return typeof name === 'string' && name.trim().length >= 2;
    }
};

/**
 * Utilitaires pour le stockage local
 */
const Storage = {
    /**
     * Sauvegarde des données dans le localStorage
     */
    save: function(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Erreur de sauvegarde:', error);
            return false;
        }
    },
    
    /**
     * Charge des données depuis le localStorage
     */
    load: function(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Erreur de chargement:', error);
            return defaultValue;
        }
    },
    
    /**
     * Supprime des données du localStorage
     */
    remove: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Erreur de suppression:', error);
            return false;
        }
    }
};

/**
 * Gestionnaire d'événements pour les erreurs globales
 */
window.addEventListener('error', function(event) {
    console.error('Erreur JavaScript:', event.error);
    Notifications.error('Une erreur inattendue s\'est produite. Veuillez recharger la page.');
});

/**
 * Gestionnaire pour les erreurs de promesses non gérées
 */
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesse rejetée non gérée:', event.reason);
    Notifications.error('Une erreur de communication s\'est produite.');
});

/**
 * Fonction pour déboguer (à supprimer en production)
 */
function debug(message, data = null) {
    if (console && console.log) {
        console.log(`[DEBUG] ${message}`, data || '');
    }
}

// Exposer les utilitaires globalement pour faciliter l'utilisation
window.Notifications = Notifications;
window.API = API;
window.Format = Format;
window.Validation = Validation;
window.Storage = Storage;
window.debug = debug;

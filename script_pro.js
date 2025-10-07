/**
 * Script professionnel avec animations avancées pour l'application de gestion d'inventaire
 * Inclut des effets visuels, des animations fluides et une expérience utilisateur premium
 */

// Variables globales
let isScanning = false;
let scanHistory = [];
let particleSystem = null;
let animationQueue = [];

// Configuration des animations
const ANIMATION_CONFIG = {
    duration: 600,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    stagger: 100
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    createParticleSystem();
    initializeScrollAnimations();
    initializeCounterAnimations();
    initializeTypewriterEffect();
});

/**
 * Initialise l'application avec des animations d'entrée
 */
function initializeApp() {
    showLoadingScreen();
    
    setTimeout(() => {
        hideLoadingScreen();
        initializeTooltips();
        initializeAnimations();
        initializeEventHandlers();
        loadUserPreferences();
        initializeProgressBars();
        console.log('🚀 Application initialisée avec succès');
    }, 1500);
}

/**
 * Affiche un écran de chargement animé
 */
function showLoadingScreen() {
    const loadingHTML = `
        <div id="loadingScreen" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
             style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); z-index: 9999;">
            <div class="text-center text-white">
                <div class="spinner-custom mb-4"></div>
                <h3 class="mb-2">Gestion d'Inventaire</h3>
                <p class="mb-0">Chargement en cours...</p>
                <div class="progress mt-3" style="width: 200px; height: 4px;">
                    <div class="progress-bar" id="loadingProgress" style="width: 0%"></div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('afterbegin', loadingHTML);
    
    // Animation de la barre de progression
    let progress = 0;
    const progressBar = document.getElementById('loadingProgress');
    const interval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressBar.style.width = progress + '%';
    }, 200);
}

/**
 * Cache l'écran de chargement avec animation
 */
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        loadingScreen.style.transform = 'scale(0.9)';
        loadingScreen.style.transition = 'all 0.5s ease-out';
        
        setTimeout(() => {
            loadingScreen.remove();
        }, 500);
    }
}

/**
 * Crée un système de particules en arrière-plan
 */
function createParticleSystem() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);
    
    for (let i = 0; i < 50; i++) {
        createParticle(particlesContainer);
    }
}

/**
 * Crée une particule individuelle
 */
function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Position aléatoire
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    // Animation aléatoire
    particle.style.animationDelay = Math.random() * 6 + 's';
    particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
    
    container.appendChild(particle);
    
    // Supprimer et recréer la particule après animation
    setTimeout(() => {
        if (particle.parentNode) {
            particle.remove();
            createParticle(container);
        }
    }, 6000);
}

/**
 * Initialise les animations au scroll
 */
function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                animateElement(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observer tous les éléments avec la classe animate-on-scroll
    document.querySelectorAll('.card, .table, .btn-group').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
}

/**
 * Anime un élément avec des effets personnalisés
 */
function animateElement(element) {
    element.style.transform = 'translateY(0)';
    element.style.opacity = '1';
    
    // Ajouter un effet de brillance
    const shine = document.createElement('div');
    shine.style.cssText = `
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        pointer-events: none;
        transition: left 0.6s ease;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(shine);
    
    setTimeout(() => {
        shine.style.left = '100%';
    }, 100);
    
    setTimeout(() => {
        shine.remove();
    }, 700);
}

/**
 * Initialise les animations de compteur pour les statistiques
 */
function initializeCounterAnimations() {
    const counters = document.querySelectorAll('.card h3, .card h4, .card h5');
    
    counters.forEach(counter => {
        const text = counter.textContent;
        const number = parseInt(text.replace(/[^\d]/g, ''));
        
        if (!isNaN(number) && number > 0) {
            animateCounter(counter, 0, number, 2000);
        }
    });
}

/**
 * Anime un compteur de 0 à la valeur cible
 */
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const originalText = element.textContent;
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Fonction d'easing
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * easeOutCubic);
        
        element.textContent = originalText.replace(end.toString(), current.toString());
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = originalText;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Initialise l'effet de machine à écrire pour les titres
 */
function initializeTypewriterEffect() {
    const titles = document.querySelectorAll('h1, .navbar-brand');
    
    titles.forEach(title => {
        const text = title.textContent;
        title.textContent = '';
        title.style.borderRight = '2px solid';
        title.style.animation = 'blink 1s infinite';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                title.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                title.style.borderRight = 'none';
                title.style.animation = 'none';
            }
        };
        
        setTimeout(typeWriter, 500);
    });
}

/**
 * Initialise les barres de progression animées
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 1000);
    });
}

/**
 * Initialise les tooltips Bootstrap avec animations
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { show: 300, hide: 100 }
        });
    });
}

/**
 * Initialise les animations d'entrée avec décalage
 */
function initializeAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all ${ANIMATION_CONFIG.duration}ms ${ANIMATION_CONFIG.easing}`;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
            card.classList.add('fade-in');
        }, index * ANIMATION_CONFIG.stagger);
    });
}

/**
 * Initialise les gestionnaires d'événements avec animations
 */
function initializeEventHandlers() {
    // Gestionnaire pour les formulaires avec animation de soumission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmitWithAnimation);
    });
    
    // Gestionnaire pour les boutons avec effet ripple
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
    });
    
    // Gestionnaire pour les champs de recherche avec animation
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', handleSearchWithAnimation);
    });
    
    // Gestionnaire pour les raccourcis clavier
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Gestionnaire pour le scroll fluide
    initializeSmoothScroll();
}

/**
 * Crée un effet ripple sur les boutons
 */
function createRippleEffect(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Gère la soumission des formulaires avec animations
 */
function handleFormSubmitWithAnimation(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        // Animation de chargement
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Traitement...';
        submitButton.disabled = true;
        
        // Animation de pulsation
        submitButton.style.animation = 'pulse 1s infinite';
        
        // Restaurer après 3 secondes
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
            submitButton.style.animation = 'none';
        }, 3000);
    }
    
    // Animation du formulaire
    form.style.transform = 'scale(0.98)';
    form.style.opacity = '0.8';
    
    setTimeout(() => {
        form.style.transform = 'scale(1)';
        form.style.opacity = '1';
    }, 200);
}

/**
 * Gère la recherche avec animations
 */
function handleSearchWithAnimation(event) {
    const searchTerm = event.target.value.toLowerCase();
    const targetSelector = event.target.dataset.search;
    const items = document.querySelectorAll(targetSelector);
    
    items.forEach((item, index) => {
        const text = item.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        
        setTimeout(() => {
            if (shouldShow) {
                item.style.display = '';
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, 50);
            } else {
                item.style.opacity = '0';
                item.style.transform = 'translateX(20px)';
                
                setTimeout(() => {
                    item.style.display = 'none';
                }, 300);
            }
        }, index * 50);
    });
}

/**
 * Initialise le scroll fluide
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Gère les raccourcis clavier avec feedback visuel
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K : Focus sur la recherche
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[data-search]');
        if (searchInput) {
            searchInput.focus();
            searchInput.style.transform = 'scale(1.05)';
            setTimeout(() => {
                searchInput.style.transform = 'scale(1)';
            }, 200);
        }
        showKeyboardShortcutFeedback('Recherche activée');
    }
    
    // Échap : Fermer les modals et scanners
    if (event.key === 'Escape') {
        closeAllModals();
        stopAllScanners();
        showKeyboardShortcutFeedback('Éléments fermés');
    }
    
    // Ctrl/Cmd + S : Scanner
    if ((event.ctrlKey || event.metaKey) && event.key === 's' && window.location.pathname.includes('scanner')) {
        event.preventDefault();
        const startButton = document.getElementById('startCamera');
        if (startButton && startButton.style.display !== 'none') {
            startButton.click();
            showKeyboardShortcutFeedback('Scanner démarré');
        }
    }
}

/**
 * Affiche un feedback visuel pour les raccourcis clavier
 */
function showKeyboardShortcutFeedback(message) {
    const feedback = document.createElement('div');
    feedback.className = 'position-fixed top-50 start-50 translate-middle bg-dark text-white px-3 py-2 rounded';
    feedback.style.zIndex = '9999';
    feedback.textContent = message;
    
    document.body.appendChild(feedback);
    
    // Animation d'apparition
    feedback.style.opacity = '0';
    feedback.style.transform = 'translate(-50%, -50%) scale(0.8)';
    feedback.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        feedback.style.opacity = '1';
        feedback.style.transform = 'translate(-50%, -50%) scale(1)';
    }, 10);
    
    // Suppression automatique
    setTimeout(() => {
        feedback.style.opacity = '0';
        feedback.style.transform = 'translate(-50%, -50%) scale(0.8)';
        setTimeout(() => feedback.remove(), 300);
    }, 2000);
}

/**
 * Ferme tous les modals avec animation
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
 * Arrête tous les scanners avec animation
 */
function stopAllScanners() {
    if (typeof Quagga !== 'undefined' && isScanning) {
        Quagga.stop();
        isScanning = false;
        
        const viewport = document.querySelector('.viewport');
        if (viewport) {
            viewport.classList.remove('scanning');
        }
        
        const stopButton = document.getElementById('stopCamera');
        const startButton = document.getElementById('startCamera');
        
        if (stopButton) {
            stopButton.style.display = 'none';
            stopButton.style.animation = 'fadeOut 0.3s ease';
        }
        if (startButton) {
            startButton.style.display = 'inline-block';
            startButton.style.animation = 'fadeIn 0.3s ease';
        }
    }
}

/**
 * Utilitaires pour les notifications avec animations avancées
 */
const NotificationsPro = {
    container: null,
    
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'info', duration = 5000) {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 mb-2`;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${this.getIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        this.container.appendChild(toast);
        
        // Animation d'entrée
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
        
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Initialiser le toast Bootstrap
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        // Suppression automatique avec animation
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 500);
        }, duration);
    },
    
    getIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'x-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    success(message, duration = 5000) {
        this.show(message, 'success', duration);
    },
    
    error(message, duration = 7000) {
        this.show(message, 'danger', duration);
    },
    
    warning(message, duration = 6000) {
        this.show(message, 'warning', duration);
    },
    
    info(message, duration = 5000) {
        this.show(message, 'info', duration);
    }
};

/**
 * Gestionnaire d'événements pour les erreurs globales avec notifications
 */
window.addEventListener('error', function(event) {
    console.error('Erreur JavaScript:', event.error);
    NotificationsPro.error('Une erreur inattendue s\'est produite. Veuillez recharger la page.');
});

/**
 * Gestionnaire pour les erreurs de promesses non gérées
 */
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesse rejetée non gérée:', event.reason);
    NotificationsPro.error('Une erreur de communication s\'est produite.');
});

/**
 * Ajouter des styles CSS pour les animations personnalisées
 */
const additionalStyles = `
    <style>
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes blink {
            0%, 50% { border-color: transparent; }
            51%, 100% { border-color: currentColor; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-10px); }
        }
        
        .toast {
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', additionalStyles);

// Exposer les utilitaires globalement
window.NotificationsPro = NotificationsPro;
window.animateElement = animateElement;
window.createRippleEffect = createRippleEffect;

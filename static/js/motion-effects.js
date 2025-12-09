// ANU LMS Motion Effects JavaScript
// Enhanced interactive features for mouse movement and animations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all motion effects
    initMouseTracking();
    initScrollAnimations();
    initHoverEffects();
    initParallaxEffects();
    initMagneticElements();
    initRippleEffects();
});

// Mouse Tracking and Highlighting (Reduced Motion)
function initMouseTracking() {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 12px;
        height: 12px;
        background: var(--anu-blue);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        transition: all 0.3s ease;
        opacity: 0.6;
        transform: translate(-50%, -50%);
    `;
    document.body.appendChild(cursor);

    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    document.addEventListener('mouseleave', () => {
        cursor.style.opacity = '0';
    });

    // Slower cursor following for reduced motion
    function updateCursor() {
        cursorX += (mouseX - cursorX) * 0.05; // Reduced from 0.1
        cursorY += (mouseY - cursorY) * 0.05;

        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';

        requestAnimationFrame(updateCursor);
    }
    updateCursor();

    // Subtle cursor changes on interactive elements
    const interactiveElements = document.querySelectorAll('button, a, .card, .book-card, .btn');

    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1.2)'; // Reduced from 1.5
            cursor.style.opacity = '0.8';
        });

        el.addEventListener('mouseleave', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.opacity = '0.6';
        });
    });
}

// Scroll-based Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for scroll animations
    const animateElements = document.querySelectorAll('.card, .book-card, .hero-card, .section-heading, .eresources-card');
    animateElements.forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });

    // Stagger animations for book cards
    const bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

// Enhanced Hover Effects (Reduced Motion)
function initHoverEffects() {
    // Subtle book card tilt effect (reduced intensity)
    const bookCards = document.querySelectorAll('.book-card');

    bookCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // Reduced rotation intensity from /10 to /20
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
    });

    // Subtle hero card glow effect
    const heroCards = document.querySelectorAll('.hero-card');

    heroCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('glow');
        });

        card.addEventListener('mouseleave', () => {
            card.classList.remove('glow');
        });
    });

    // Gentle button hover effect (removed pulse)
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-1px)'; // Reduced from -2px
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0px)';
        });
    });
}

// Parallax Effects
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.parallax');

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;

        parallaxElements.forEach(el => {
            const rate = el.dataset.parallax || 0.5;
            el.style.transform = `translateY(${scrolled * rate}px)`;
        });
    });

    // Add parallax to hero section
    const heroSection = document.querySelector('.hero-wrapper');
    if (heroSection) {
        heroSection.classList.add('parallax');
        heroSection.dataset.parallax = '0.3';
    }
}

// Magnetic Elements (Reduced Motion)
function initMagneticElements() {
    const magneticElements = document.querySelectorAll('.magnetic, .btn');

    magneticElements.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            // Reduced magnetic effect from 0.3 to 0.1
            el.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = 'translate(0px, 0px)';
        });
    });
}

// Ripple Effects
function initRippleEffects() {
    const rippleElements = document.querySelectorAll('.ripple, .btn, .card');

    rippleElements.forEach(el => {
        el.addEventListener('click', (e) => {
            const ripple = document.createElement('div');
            ripple.className = 'ripple-effect';

            const rect = el.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
            `;

            el.style.position = 'relative';
            el.style.overflow = 'hidden';
            el.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add ripple CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Floating Elements Animation
function initFloatingElements() {
    const floatingElements = document.querySelectorAll('.floating');

    floatingElements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.5}s`;
    });
}

// Mouse Follow Effects
function initMouseFollowEffects() {
    const followElements = document.querySelectorAll('.mouse-follow');

    document.addEventListener('mousemove', (e) => {
        followElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            el.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
        });
    });
}

// Scroll Progress Indicator
function initScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, var(--anu-blue), var(--anu-dark));
        z-index: 1000;
        transition: width 0.3s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;

        progressBar.style.width = scrollPercent + '%';
    });
}

// Typing Effect for Text
function initTypingEffect() {
    const typingElements = document.querySelectorAll('.typing-effect');

    typingElements.forEach(el => {
        const text = el.textContent;
        el.textContent = '';
        el.style.borderRight = '2px solid var(--anu-blue)';

        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                el.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                el.style.borderRight = 'none';
            }
        }, 100);
    });
}

// Particle Effects
function initParticleEffects() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    `;
    document.body.appendChild(particleContainer);

    // Create particles on mouse move
    let particleCount = 0;
    document.addEventListener('mousemove', (e) => {
        if (particleCount < 50) { // Limit particles
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: var(--anu-blue);
                border-radius: 50%;
                left: ${e.clientX}px;
                top: ${e.clientY}px;
                animation: particle-float 2s ease-out forwards;
                opacity: 0.7;
            `;

            particleContainer.appendChild(particle);
            particleCount++;

            setTimeout(() => {
                particle.remove();
                particleCount--;
            }, 2000);
        }
    });

    // Add particle animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes particle-float {
            0% {
                transform: translateY(0px) scale(1);
                opacity: 0.7;
            }
            100% {
                transform: translateY(-100px) scale(0);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize additional effects
initFloatingElements();
initMouseFollowEffects();
initScrollProgress();
initTypingEffect();
// initParticleEffects(); // Removed for reduced motion

// Performance optimization - throttle scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Add smooth scrolling to anchor links
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

// Add loading animations
window.addEventListener('load', () => {
    document.body.classList.add('loaded');

    // Add fade-in effect to body
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});

// Keyboard navigation enhancements
document.addEventListener('keydown', (e) => {
    // Add focus effects for keyboard navigation
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
});

// Add focus styles for keyboard navigation
const focusStyle = document.createElement('style');
focusStyle.textContent = `
    .keyboard-navigation *:focus {
        outline: 2px solid var(--anu-blue) !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 4px rgba(0,123,255,0.25) !important;
    }
`;
document.head.appendChild(focusStyle);

// Error handling
window.addEventListener('error', (e) => {
    console.warn('Motion effects error:', e.error);
    // Gracefully disable effects if there's an error
    document.body.classList.add('motion-disabled');
});

// Performance monitoring
if ('performance' in window && 'mark' in window.performance) {
    performance.mark('motion-effects-start');
    // Mark end when all effects are loaded
    setTimeout(() => {
        performance.mark('motion-effects-end');
        performance.measure('motion-effects-load', 'motion-effects-start', 'motion-effects-end');
        console.log('Motion effects loaded in:', performance.getEntriesByName('motion-effects-load')[0].duration, 'ms');
    }, 1000);
}

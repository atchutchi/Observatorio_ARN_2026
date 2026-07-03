document.addEventListener('DOMContentLoaded', function() {
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;
    
    // Create particles container
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'hero-particles';
    heroSection.appendChild(particlesContainer);
    
    // Create particles
    for (let i = 0; i < 30; i++) {
        createParticle(particlesContainer);
    }
    
    // Initialize card animations
    initCardsAnimation();
    
    // Add data-text attributes to section titles
    initSectionTitles();
});

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random size between 3px and 8px
    const size = Math.random() * 5 + 3;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Random position
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.top = `${Math.random() * 100}%`;
    
    // Random opacity
    particle.style.opacity = Math.random() * 0.5 + 0.1;
    
    // Random animation duration (5-15s)
    const duration = Math.random() * 10 + 5;
    particle.style.animationDuration = `${duration}s`;
    
    // Random delay
    const delay = Math.random() * 5;
    particle.style.animationDelay = `${delay}s`;
    
    container.appendChild(particle);
}

function initCardsAnimation() {
    const cards = document.querySelectorAll('.custom-card');
    
    // Add staggered animation to cards
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        card.style.transitionDelay = `${0.1 * index}s`;
    });
    
    // Initialize Intersection Observer for cards
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                cardObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observe each card
    cards.forEach(card => {
        cardObserver.observe(card);
    });
}

function initSectionTitles() {
    const sectionTitles = document.querySelectorAll('.section-title');
    
    sectionTitles.forEach(title => {
        // Use the title text as the data-text attribute
        const titleText = title.textContent.trim();
        title.setAttribute('data-text', titleText);
    });
} 
// FreeRide Documentation Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
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

    // Add subtle animation to feature cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.6s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                observer.unobserve(entry.target);
            }
        });
    });

    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });

    // Add copy button to code blocks
    document.querySelectorAll('div.highlight').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            padding: 4px 12px;
            background: #3498DB;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
        `;
        
        block.style.position = 'relative';
        block.appendChild(button);
        
        block.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });
        
        block.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });
        
        button.addEventListener('click', () => {
            const code = block.querySelector('pre').textContent;
            navigator.clipboard.writeText(code).then(() => {
                button.textContent = 'Copied!';
                button.style.background = '#27AE60';
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.background = '#3498DB';
                }, 2000);
            });
        });
    });

    // Add "Economics Tip" tooltips
    const economicTerms = {
        'equilibrium': 'The point where supply and demand curves intersect',
        'elasticity': 'A measure of responsiveness to price changes',
        'surplus': 'The area between a curve and the market price',
        'demand': 'The relationship between price and quantity demanded',
        'supply': 'The relationship between price and quantity supplied'
    };

    // Highlight economic terms in content
    const content = document.querySelector('.bd-content');
    if (content) {
        Object.keys(economicTerms).forEach(term => {
            const regex = new RegExp(`\\b${term}\\b`, 'gi');
            // This is a simplified version - in production you'd want to avoid replacing inside code blocks
        });
    }
});
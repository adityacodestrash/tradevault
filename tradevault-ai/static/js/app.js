/**
 * =============================================================================
 * TRADEVAULT AI — Frontend JavaScript
 * =============================================================================
 * Handles:
 * - Mobile menu toggle
 * - Flash message auto-dismiss
 * - Password visibility toggle
 * - Smooth scrolling
 * - Table sorting helpers
 * - Form validation enhancements
 * =============================================================================
 */

document.addEventListener('DOMContentLoaded', function() {

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================
    window.toggleMobileMenu = function() {
        const menu = document.getElementById('mobileMenu');
        menu.classList.toggle('active');
    };

    // Close mobile menu when clicking a link
    document.querySelectorAll('.mobile-menu a').forEach(link => {
        link.addEventListener('click', () => {
            document.getElementById('mobileMenu').classList.remove('active');
        });
    });

    // ============================================
    // FLASH MESSAGE AUTO-DISMISS
    // ============================================
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach((flash, index) => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(20px)';
            setTimeout(() => flash.remove(), 300);
        }, 5000 + (index * 500)); // Stagger dismissals
    });

    // ============================================
    // PASSWORD VISIBILITY TOGGLE
    // ============================================
    window.togglePassword = function(inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('i');

        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    };

    // ============================================
    // SMOOTH SCROLLING FOR ANCHOR LINKS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // ============================================
    // SIDEBAR ACTIVE STATE HIGHLIGHTING
    // ============================================
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ============================================
    // FORM INPUT ENHANCEMENTS
    // ============================================
    // Auto-capitalize pair inputs
    document.querySelectorAll('input[name="pair"]').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });

    // Set default date to today for trade date inputs
    document.querySelectorAll('input[name="trade_date"]').forEach(input => {
        if (!input.value) {
            input.valueAsDate = new Date();
        }
    });

    // ============================================
    // TABLE SORTING (Client-side)
    // ============================================
    document.querySelectorAll('.data-table th').forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const index = Array.from(this.parentElement.children).indexOf(this);
            const isNumeric = !isNaN(parseFloat(rows[0]?.children[index]?.textContent));

            // Toggle sort direction
            const currentDir = this.dataset.sortDir || 'asc';
            const newDir = currentDir === 'asc' ? 'desc' : 'asc';

            // Clear other headers
            table.querySelectorAll('th').forEach(th => {
                th.dataset.sortDir = '';
                th.innerHTML = th.textContent.replace(' ↑', '').replace(' ↓', '');
            });

            this.dataset.sortDir = newDir;
            this.innerHTML = this.textContent + (newDir === 'asc' ? ' ↑' : ' ↓');

            rows.sort((a, b) => {
                const aVal = a.children[index].textContent.trim();
                const bVal = b.children[index].textContent.trim();

                if (isNumeric) {
                    return newDir === 'asc' 
                        ? parseFloat(aVal) - parseFloat(bVal)
                        : parseFloat(bVal) - parseFloat(aVal);
                }

                return newDir === 'asc'
                    ? aVal.localeCompare(bVal)
                    : bVal.localeCompare(aVal);
            });

            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // ============================================
    // CONFIRM DIALOGS FOR DESTRUCTIVE ACTIONS
    // ============================================
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ============================================
    // NAVBAR SCROLL EFFECT
    // ============================================
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.style.background = 'rgba(10, 14, 26, 0.95)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(10, 14, 26, 0.85)';
            navbar.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    });

    // ============================================
    // LOADING STATE FOR BUTTONS
    // ============================================
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            if (btn && !btn.dataset.noLoading) {
                const originalText = btn.innerHTML;
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                btn.dataset.originalText = originalText;
            }
        });
    });

    // ============================================
    // TOOLTIP SYSTEM (Simple CSS-based)
    // ============================================
    document.querySelectorAll('[title]').forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.dataset.title = this.title;
            this.title = '';
        });
        el.addEventListener('mouseleave', function() {
            this.title = this.dataset.title;
        });
    });

    // ============================================
    // GOAL PROGRESS ANIMATION
    // ============================================
    document.querySelectorAll('.goal-progress-fill').forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 300);
    });

    // ============================================
    // PRINT STYLES (for journal export)
    // ============================================
    if (window.location.pathname.includes('/journal')) {
        const printBtn = document.createElement('button');
        printBtn.className = 'btn btn-ghost btn-sm';
        printBtn.innerHTML = '<i class="fas fa-print"></i> Print';
        printBtn.style.marginLeft = 'auto';
        printBtn.addEventListener('click', () => window.print());

        const header = document.querySelector('.page-header');
        if (header) {
            header.appendChild(printBtn);
        }
    }

    console.log('%c TradeVault AI ', 'background: linear-gradient(135deg, #00d4aa, #3b82f6); color: #0a0e1a; font-size: 20px; font-weight: bold; padding: 10px 20px; border-radius: 8px;');
    console.log('%c Built for serious traders. ', 'color: #00d4aa; font-size: 14px;');
});

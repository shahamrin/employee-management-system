/* =============================================================
   Smart Employee Management System – Client-Side JavaScript
   Handles sidebar toggle, flash dismiss, delete modals, and
   client-side form validation.
   ============================================================= */

document.addEventListener('DOMContentLoaded', () => {

    // ── Sidebar mobile toggle ──
    const sidebar    = document.getElementById('sidebar');
    const toggleBtn  = document.getElementById('sidebarToggle');
    const overlay    = document.getElementById('sidebarOverlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }


    // ── Auto-dismiss flash alerts ──
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Close button
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(-12px)';
                setTimeout(() => alert.remove(), 300);
            });
        }
        // Auto-dismiss after 6 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(-12px)';
                setTimeout(() => alert.remove(), 300);
            }
        }, 6000);
    });


    // ── Delete confirmation modal ──
    const deleteModal   = document.getElementById('deleteModal');
    const deleteForm    = document.getElementById('deleteForm');
    const deleteEmpName = document.getElementById('deleteEmpName');

    document.querySelectorAll('.btn-delete-trigger').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const empId   = btn.dataset.empId;
            const empName = btn.dataset.empName;

            if (deleteForm) {
                deleteForm.action = `/employees/delete/${empId}`;
            }
            if (deleteEmpName) {
                deleteEmpName.textContent = empName;
            }
            if (deleteModal) {
                deleteModal.classList.add('active');
            }
        });
    });

    // Cancel modal
    document.querySelectorAll('.modal-cancel').forEach(btn => {
        btn.addEventListener('click', () => {
            if (deleteModal) deleteModal.classList.remove('active');
        });
    });

    // Close modal on overlay click
    if (deleteModal) {
        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) {
                deleteModal.classList.remove('active');
            }
        });
    }

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && deleteModal && deleteModal.classList.contains('active')) {
            deleteModal.classList.remove('active');
        }
    });


    // ── Client-side form validation ──
    const empForm = document.getElementById('employeeForm');
    if (empForm) {
        empForm.addEventListener('submit', (e) => {
            const errors = [];
            const firstName  = empForm.querySelector('[name="first_name"]');
            const lastName   = empForm.querySelector('[name="last_name"]');
            const email      = empForm.querySelector('[name="email"]');
            const department = empForm.querySelector('[name="department"]');
            const designation= empForm.querySelector('[name="designation"]');
            const salary     = empForm.querySelector('[name="salary"]');

            if (firstName && !firstName.value.trim()) errors.push('First name is required');
            if (lastName  && !lastName.value.trim())  errors.push('Last name is required');
            if (email && (!email.value.trim() || !email.value.includes('@')))
                errors.push('Valid email is required');
            if (department && !department.value.trim()) errors.push('Department is required');
            if (designation && !designation.value.trim()) errors.push('Designation is required');
            if (salary) {
                const val = parseFloat(salary.value);
                if (isNaN(val) || val < 0) errors.push('Salary must be a valid non-negative number');
            }

            if (errors.length > 0) {
                e.preventDefault();
                // Show errors
                let alertBox = document.getElementById('clientAlert');
                if (!alertBox) {
                    alertBox = document.createElement('div');
                    alertBox.id = 'clientAlert';
                    alertBox.className = 'alert alert-error';
                    alertBox.style.marginBottom = '16px';
                    empForm.parentElement.insertBefore(alertBox, empForm);
                }
                alertBox.innerHTML = `
                    <span>⚠️</span>
                    <span>${errors.join('. ')}.</span>
                    <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
                `;
            }
        });
    }


    // ── Salary formatting in inputs ──
    const salaryInput = document.querySelector('input[name="salary"]');
    if (salaryInput) {
        salaryInput.addEventListener('blur', () => {
            const val = parseFloat(salaryInput.value);
            if (!isNaN(val) && val >= 0) {
                salaryInput.value = val.toFixed(2);
            }
        });
    }


    // ── Animate stat cards on scroll (Intersection Observer) ──
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    entry.target.style.animationDelay = `${index * 80}ms`;
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        statCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            observer.observe(card);
        });
    }

    // Add fade-in animation styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        .fade-in {
            animation: fadeInUp 0.5s ease-out forwards;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);

});

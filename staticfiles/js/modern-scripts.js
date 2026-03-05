// Modern School Management System - Advanced JavaScript

// Global Variables
let currentUser = null;
let notifications = [];
let dashboardData = {};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeAnimations();
    loadDashboardData();
    initializeNotifications();
});

// Application Initialization
function initializeApp() {
    // Set current user from template context
    currentUser = window.currentUser || null;
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Setup form validation
    setupFormValidation();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
}

// Setup Event Listeners
function setupEventListeners() {
    // Navigation active state
    setupNavigationActiveState();
    
    // Form submissions
    setupFormSubmissions();
    
    // Dynamic content loading
    setupDynamicContent();
    
    // Search functionality
    setupSearchFunctionality();
    
    // File uploads
    setupFileUploads();
    
    // Print functionality
    setupPrintFunctionality();
}

// Initialize Animations
function initializeAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe dashboard cards and other elements
    document.querySelectorAll('.dashboard-card, .stat-card, .card').forEach(el => {
        observer.observe(el);
    });
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Simulate API call for dashboard data
        dashboardData = await fetchDashboardData();
        updateDashboardUI();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Fetch Dashboard Data (Mock API)
async function fetchDashboardData() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                totalStudents: 1250,
                totalFaculty: 85,
                totalCourses: 142,
                averageAttendance: 87.5,
                recentActivities: [
                    { type: 'enrollment', message: 'New student enrolled', time: '2 mins ago' },
                    { type: 'grade', message: 'Grades submitted for CS101', time: '15 mins ago' },
                    { type: 'attendance', message: 'Attendance marked for Math201', time: '1 hour ago' }
                ],
                notifications: [
                    { type: 'info', message: 'System maintenance scheduled', time: 'Tomorrow' },
                    { type: 'warning', message: 'Fee payment due soon', time: '3 days' }
                ]
            });
        }, 1000);
    });
}

// Update Dashboard UI
function updateDashboardUI() {
    // Update statistics with animation
    animateNumber('total-students', dashboardData.totalStudents);
    animateNumber('total-faculty', dashboardData.totalFaculty);
    animateNumber('total-courses', dashboardData.totalCourses);
    animateNumber('average-attendance', dashboardData.averageAttendance, '%');
    
    // Update recent activities
    updateRecentActivities(dashboardData.recentActivities);
    
    // Update notifications
    updateNotifications(dashboardData.notifications);
}

// Animate Numbers
function animateNumber(elementId, target, suffix = '') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + suffix;
    }, 30);
}

// Update Recent Activities
function updateRecentActivities(activities) {
    const container = document.getElementById('recent-activities');
    if (!container) return;
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item d-flex align-items-center p-3 border-bottom">
            <div class="activity-icon me-3">
                <i class="fas fa-${getActivityIcon(activity.type)} text-${getActivityColor(activity.type)}"></i>
            </div>
            <div class="activity-content flex-grow-1">
                <p class="mb-0">${activity.message}</p>
                <small class="text-muted">${activity.time}</small>
            </div>
        </div>
    `).join('');
}

// Get Activity Icon
function getActivityIcon(type) {
    const icons = {
        enrollment: 'user-plus',
        grade: 'graduation-cap',
        attendance: 'clipboard-check',
        payment: 'credit-card',
        announcement: 'bullhorn'
    };
    return icons[type] || 'circle';
}

// Get Activity Color
function getActivityColor(type) {
    const colors = {
        enrollment: 'primary',
        grade: 'success',
        attendance: 'info',
        payment: 'warning',
        announcement: 'danger'
    };
    return colors[type] || 'secondary';
}

// Initialize Notifications
function initializeNotifications() {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;
    
    // Check for new notifications periodically
    setInterval(checkNewNotifications, 30000); // Check every 30 seconds
}

// Check New Notifications
async function checkNewNotifications() {
    try {
        const newNotifications = await fetchNewNotifications();
        if (newNotifications.length > 0) {
            showNotificationPopup(newNotifications[0]);
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

// Fetch New Notifications (Mock API)
async function fetchNewNotifications() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve([
                { type: 'info', message: 'New announcement posted', time: 'Just now' }
            ]);
        }, 500);
    });
}

// Show Notification Popup
function showNotificationPopup(notification) {
    const popup = document.createElement('div');
    popup.className = `alert alert-${notification.type} alert-dismissible fade show position-fixed`;
    popup.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    popup.innerHTML = `
        <i class="fas fa-${getActivityIcon(notification.type)} me-2"></i>
        ${notification.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(popup);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (popup.parentNode) {
            popup.parentNode.removeChild(popup);
        }
    }, 5000);
}

// Setup Navigation Active State
function setupNavigationActiveState() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Setup Form Submissions
function setupFormSubmissions() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

// Handle Form Submit
async function handleFormSubmit(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        return;
    }
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing...';
    }
    
    // Simulate form submission
    setTimeout(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit';
        }
        
        // Show success message
        showMessage('Form submitted successfully!', 'success');
    }, 1500);
}

// Setup Dynamic Content
function setupDynamicContent() {
    // Handle tab switching
    const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', loadTabContent);
    });
    
    // Handle modal loading
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', loadModalContent);
    });
}

// Load Tab Content
async function loadTabContent(e) {
    const target = e.target.getAttribute('data-bs-target');
    const contentPane = document.querySelector(target);
    
    if (contentPane && contentPane.dataset.url) {
        try {
            const response = await fetch(contentPane.dataset.url);
            const html = await response.text();
            contentPane.innerHTML = html;
        } catch (error) {
            console.error('Error loading tab content:', error);
            contentPane.innerHTML = '<p class="text-danger">Error loading content</p>';
        }
    }
}

// Load Modal Content
async function loadModalContent(e) {
    const modal = e.target;
    const modalBody = modal.querySelector('.modal-body');
    
    if (modalBody && modalBody.dataset.url) {
        try {
            const response = await fetch(modalBody.dataset.url);
            const html = await response.text();
            modalBody.innerHTML = html;
        } catch (error) {
            console.error('Error loading modal content:', error);
            modalBody.innerHTML = '<p class="text-danger">Error loading content</p>';
        }
    }
}

// Setup Search Functionality
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
}

// Handle Search
function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const searchResults = document.getElementById('search-results');
    
    if (!searchResults) return;
    
    if (query.length < 2) {
        searchResults.innerHTML = '';
        return;
    }
    
    // Simulate search
    const results = performSearch(query);
    displaySearchResults(results);
}

// Perform Search (Mock)
function performSearch(query) {
    const allItems = [
        { type: 'student', name: 'John Doe', id: 1 },
        { type: 'course', name: 'Computer Science 101', id: 2 },
        { type: 'faculty', name: 'Dr. Smith', id: 3 }
    ];
    
    return allItems.filter(item => 
        item.name.toLowerCase().includes(query)
    );
}

// Display Search Results
function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = '<p class="text-muted">No results found</p>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div class="search-result p-2 border-bottom">
            <div class="d-flex align-items-center">
                <i class="fas fa-${getSearchIcon(result.type)} me-2"></i>
                <div>
                    <div class="fw-bold">${result.name}</div>
                    <small class="text-muted">${result.type}</small>
                </div>
            </div>
        </div>
    `).join('');
}

// Get Search Icon
function getSearchIcon(type) {
    const icons = {
        student: 'user-graduate',
        course: 'book',
        faculty: 'chalkboard-teacher'
    };
    return icons[type] || 'search';
}

// Setup File Uploads
function setupFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileSelect);
    });
}

// Handle File Select
function handleFileSelect(e) {
    const input = e.target;
    const file = input.files[0];
    
    if (file) {
        const fileSize = formatFileSize(file.size);
        const fileName = file.name;
        
        // Display file info
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info mt-2';
        fileInfo.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file me-2"></i>
                <span>${fileName}</span>
                <small class="text-muted ms-2">(${fileSize})</small>
            </div>
        `;
        
        input.parentNode.appendChild(fileInfo);
    }
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Setup Print Functionality
function setupPrintFunctionality() {
    const printButtons = document.querySelectorAll('.btn-print');
    
    printButtons.forEach(button => {
        button.addEventListener('click', handlePrint);
    });
}

// Handle Print
function handlePrint(e) {
    const printArea = e.target.dataset.printArea;
    
    if (printArea) {
        const element = document.getElementById(printArea);
        if (element) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Print</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                        <link href="/static/css/modern-styles.css" rel="stylesheet">
                    </head>
                    <body>
                        ${element.innerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        }
    } else {
        window.print();
    }
}

// Setup Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Initialize Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Modals
function initializeModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

// Initialize Real-time Updates
function initializeRealTimeUpdates() {
    // Simulate real-time updates
    setInterval(() => {
        updateRealTimeData();
    }, 60000); // Update every minute
}

// Update Real-time Data
function updateRealTimeData() {
    // Update time displays
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    
    timeElements.forEach(element => {
        element.textContent = now.toLocaleTimeString();
    });
    
    // Update online status
    updateOnlineStatus();
}

// Update Online Status
function updateOnlineStatus() {
    const statusElements = document.querySelectorAll('.online-status');
    
    statusElements.forEach(element => {
        const isOnline = Math.random() > 0.3; // Simulate online status
        element.className = `online-status ${isOnline ? 'text-success' : 'text-muted'}`;
        element.innerHTML = `<i class="fas fa-circle me-1"></i> ${isOnline ? 'Online' : 'Offline'}`;
    });
}

// Show Message
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.SchoolManagement = {
    showMessage,
    loadDashboardData,
    updateDashboardUI,
    handleFormSubmit,
    handleSearch,
    handlePrint
};

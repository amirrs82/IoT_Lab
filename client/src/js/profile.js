import {
    axiosAgent,
    CheckHasAuthToken,
    NotifyErrors,
    NotificationModal,
    CreateNavSide
} from "./utils.js";
import './axios.min.js';

let userProfile = null;

function loadUserProfile() {
    // Show loading overlay
    $('#loadingOverlay').show();
    
    axiosAgent.get('/api/auth/profile/')
        .then(response => {
            userProfile = response.data;
            displayProfile(userProfile);
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error loading user profile:', error);
            NotifyErrors(error, 'خطا در بارگذاری اطلاعات پروفایل');
            $('#loadingOverlay').hide();
        });
}

function displayProfile(profile) {
    // Display profile information
    $('#display-username').text(profile.username || '-');
    $('#display-email').text(profile.email || '-');
    $('#display-first-name').text(profile.first_name || '-');
    $('#display-last-name').text(profile.last_name || '-');
    
    // Format date joined
    if (profile.date_joined) {
        const dateJoined = new Date(profile.date_joined);
        const persianDateObj = new persianDate(dateJoined);
        $('#display-date-joined').text(persianDateObj.format('YYYY/MM/DD'));
    } else {
        $('#display-date-joined').text('-');
    }
    
    // Display account status
    $('#display-is-active').text(profile.is_active ? 'فعال' : 'غیرفعال');
    
    // Populate edit form (email is not editable)
    $('#edit-first-name').val(profile.first_name || '');
    $('#edit-last-name').val(profile.last_name || '');
    $('#edit-display-email').text(profile.email || '-');
}

function updateProfile(profileData) {
    // Show loading overlay
    $('#loadingOverlay').show();
    
    axiosAgent.put('/api/auth/profile/', profileData)
        .then(response => {
            userProfile = response.data;
            displayProfile(userProfile);
            
            // Switch back to display mode
            $('#profile-display').show();
            $('#profile-edit').hide();
            $('#edit-profile-btn').show();
            
            NotificationModal('success', 'موفقیت', 'اطلاعات پروفایل با موفقیت بروزرسانی شد');
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error updating profile:', error);
            NotifyErrors(error, 'خطا در بروزرسانی پروفایل');
            $('#loadingOverlay').hide();
        });
}

function initializeEventHandlers() {
    // Edit profile button handler
    $('#edit-profile-btn').on('click', function() {
        $('#profile-display').hide();
        $('#profile-edit').show();
        $(this).hide();
    });

    // Cancel edit button handler
    $('#cancel-edit-btn').on('click', function() {
        // Reset form values to original profile data
        if (userProfile) {
            displayProfile(userProfile);
        }
        
        $('#profile-edit').hide();
        $('#profile-display').show();
        $('#edit-profile-btn').show();
    });

    // Profile form submit handler
    $('#profile-form').on('submit', function(e) {
        e.preventDefault();
        
        const profileData = {
            first_name: $('#edit-first-name').val().trim(),
            last_name: $('#edit-last-name').val().trim()
            // Email is not included as it cannot be changed
        };

        // Basic validation
        if (!profileData.first_name) {
            NotificationModal('error', 'خطا', 'نام نمی‌تواند خالی باشد');
            return;
        }

        if (!profileData.last_name) {
            NotificationModal('error', 'خطا', 'نام خانوادگی نمی‌تواند خالی باشد');
            return;
        }

        updateProfile(profileData);
    });

    // Logout button handler
    $('#logout-button').on('click', function() {
        axiosAgent.post('/api/auth/logout/')
            .then((response) => {
                localStorage.removeItem('token');
                NotificationModal("success", "خروج با موفقیت انجام شد", "لطفا کمی منتظر بمانید...");
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            })
            .catch((error) => {
                console.error(error);
                // Even if logout fails on server, remove token locally
                localStorage.removeItem('token');
                NotificationModal("success", "خروج انجام شد", "");
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            });
    });

    // Navigation to crypto page
    $('#brand-logo').on('click', function(e) {
        e.preventDefault();
        window.location.href = 'crypto.html';
    });
}

// Main initialization function
function initializePage() {
    const freshLogin = localStorage.getItem('freshLogin');
    
    if (freshLogin === 'true') {
        // Fresh login - assume token is valid and clear the flag
        localStorage.removeItem('freshLogin');
        const token = localStorage.getItem('token');
        
        if (token) {
            // Initialize page immediately for fresh login
            CreateNavSide("profile.html");
            initializeEventHandlers();
            loadUserProfile();
            return;
        }
    }
    
    // Normal authentication check for page reload or direct access
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                CreateNavSide("profile.html");
                initializeEventHandlers();
                loadUserProfile();
            } else {
                window.location.href = "login.html";
            }
        })
        .catch((error) => {
            console.error("Error checking authentication:", error);
            window.location.href = "login.html";
        });
}

// Initialize when DOM is ready
$(document).ready(function() {
    initializePage();
});

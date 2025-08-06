import {
    axiosAgent,
    CheckHasAuthToken,
    NotifyErrors,
    NotificationModal,
    CreateNavSide
} from "./utils.js";
import './axios.min.js';

let cryptoTable;

function initializeCryptoTable() {
    cryptoTable = $('#crypto-table').DataTable({
        "paging": true,
        "lengthChange": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "responsive": true,
        "language": {
            "lengthMenu":     "نشان دادن _MENU_ ردیف",
            "loadingRecords": "Loading...",
            "search":         "جستجو:",
            "zeroRecords":    "داده ای یافت نشد",
            "emptyTable": "هیچ داده‌ای در جدول وجود ندارد",
            "info": "نمایش _START_ تا _END_ از _TOTAL_ رکورد",
            "infoEmpty": "نمایش 0 تا 0 از 0 رکورد",
            "infoFiltered": "(فیلتر شده از _MAX_ رکورد)",
            "infoPostFix": "",
            "infoThousands": ",",
            "processing": "در حال پردازش...",
            "paginate": {
                "sFirst": "ابتدا",
                "sLast": "انتها",
                "sNext": "بعدی",
                "sPrevious": "قبلی"
            },
            "oAria": {
                "sSortAscending": ": فعال سازی نمایش به صورت صعودی",
                "sSortDescending": ": فعال سازی نمایش به صورت نزولی"
            }
        },
        "columns": [
            {"data": "name"},
            {"data": "key"},
            {
                "data": "last_price",
                "render": function(data, type, row) {
                    if (!data) return 'N/A';
                    const price = parseFloat(data);
                    // Format price based on value - more decimals for smaller values
                    if (price >= 1) {
                        return `$${price.toFixed(2)}`;
                    } else if (price >= 0.01) {
                        return `$${price.toFixed(4)}`;
                    } else {
                        return `$${price.toFixed(8)}`;
                    }
                }
            },
            {
                "data": "last_day_change",
                "render": function(data, type, row) {
                    if (data === null || data === undefined) return 'N/A';
                    const value = parseFloat(data).toFixed(2);
                    const className = data >= 0 ? 'text-success' : 'text-danger';
                    const icon = data >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                    return `<span class="${className}"><i class="fa ${icon}"></i> ${value}%</span>`;
                }
            },
            {
                "data": "last_price_update",
                "render": function(data, type, row) {
                    if (!data) return 'N/A';
                    const date = new Date(data);
                    return date.toLocaleString('fa-IR', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                }
            },
            {
                "data": null,
                "orderable": false,
                "render": function(data, type, row) {
                    return `<button class="btn btn-primary btn-sm view-crypto-btn" data-crypto-id="${row.uuid}">
                        <i class="fa fa-eye"></i> مشاهده
                    </button>`;
                }
            }
        ]
    });
}

function loadCryptocurrencies() {
    // Show loading overlay
    $('#loadingOverlay').show();
    
    axiosAgent.get('/api/crypto/currencies/')
        .then(response => {
            console.log('API Response:', response.data); // Debug log
            
            // Handle paginated response structure
            const responseData = response.data;
            const results = responseData.results || responseData;
            
            // Ensure results is an array
            if (Array.isArray(results)) {
                cryptoTable.clear();
                
                // Validate and clean data before adding to table
                const validData = results.filter(item => {
                    return item && item.uuid && item.name && item.key;
                });
                
                if (validData.length > 0) {
                    cryptoTable.rows.add(validData);
                    cryptoTable.draw();
                } else {
                    NotificationModal('warning', 'هشدار', 'هیچ داده معتبری دریافت نشد');
                }
            } else {
                console.error('Expected array response, got:', typeof results);
                NotificationModal('error', 'خطا', 'ساختار داده‌های دریافتی نامعتبر است');
            }
            
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error loading cryptocurrencies:', error);
            
            // Handle specific error cases
            if (error.response) {
                // Server responded with error status
                const status = error.response.status;
                const message = error.response.data?.detail || error.response.data?.message || 'خطا در دریافت داده‌ها';
                
                if (status === 401) {
                    NotificationModal('error', 'عدم احراز هویت', 'لطفاً مجدداً وارد شوید');
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        window.location.href = 'login.html';
                    }, 2000);
                } else if (status === 403) {
                    NotificationModal('error', 'عدم دسترسی', 'شما مجوز دسترسی به این بخش را ندارید');
                } else {
                    NotificationModal('error', 'خطا در بارگذاری', message);
                }
            } else if (error.request) {
                // Network error
                NotificationModal('error', 'خطای شبکه', 'لطفاً اتصال اینترنت خود را بررسی کنید');
            } else {
                // Other error
                NotificationModal('error', 'خطا', 'خطای غیرمنتظره‌ای رخ داد');
            }
            
            $('#loadingOverlay').hide();
        });
}

function initializeEventHandlers() {
    // Refresh button handler
    $('#refresh-btn').on('click', function() {
        loadCryptocurrencies();
    });

    // View crypto button handler (delegated event)
    $('#crypto-table').on('click', '.view-crypto-btn', function() {
        const cryptoId = $(this).data('crypto-id');
        // TODO: Navigate to crypto details page
        console.log('View crypto details for ID:', cryptoId);
        NotificationModal('info', 'اطلاعات ارز دیجیتال', `صفحه جزئیات ارز ${cryptoId} بعداً پیاده‌سازی خواهد شد.`);
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
            CreateNavSide("crypto.html");
            initializeCryptoTable();
            initializeEventHandlers();
            loadCryptocurrencies();
            return;
        }
    }
    
    // Normal authentication check for page reload or direct access
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                CreateNavSide("crypto.html");
                initializeCryptoTable();
                initializeEventHandlers();
                loadCryptocurrencies();
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
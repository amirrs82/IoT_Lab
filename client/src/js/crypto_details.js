import {
    axiosAgent,
    CheckHasAuthToken,
    NotifyErrors,
    NotificationModal,
    CreateNavSide
} from "./utils.js";
import './axios.min.js';

let subscriptionsTable;
let currentCurrencyUuid;
let currentCurrency;

function initializeSubscriptionsTable() {
    subscriptionsTable = $('#subscriptions-table').DataTable({
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
            {
                "data": null,
                "render": function(data, type, row) {
                    return row.floor ? 'Floor' : 'Ceiling';
                }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    const price = row.floor || row.ceiling;
                    const numPrice = parseFloat(price);
                    if (numPrice >= 1) {
                        return `$${numPrice.toFixed(2)}`;
                    } else if (numPrice >= 0.01) {
                        return `$${numPrice.toFixed(4)}`;
                    } else {
                        return `$${numPrice.toFixed(8)}`;
                    }
                }
            },
            {
                "data": "status",
                "render": function(data, type, row) {
                    let statusClass = '';
                    let statusText = '';
                    switch(data) {
                        case 'waiting':
                            statusClass = 'badge-warning';
                            statusText = 'در انتظار';
                            break;
                        case 'done':
                            statusClass = 'badge-success';
                            statusText = 'انجام شده';
                            break;
                        case 'cancelled':
                            statusClass = 'badge-danger';
                            statusText = 'لغو شده';
                            break;
                        default:
                            statusClass = 'badge-secondary';
                            statusText = data;
                    }
                    return `<span class="badge ${statusClass}">${statusText}</span>`;
                }
            },
            {
                "data": "created_at",
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
                    if (row.status === 'waiting') {
                        return `<button class="btn btn-danger btn-sm cancel-subscription-btn" data-subscription-id="${row.uuid}">
                            <i class="fa fa-times"></i> لغو
                        </button>`;
                    }
                    return '<span class="text-muted">-</span>';
                }
            }
        ]
    });
}

function loadCurrencyDetails() {
    if (!currentCurrencyUuid) {
        NotificationModal('error', 'خطا', 'شناسه ارز یافت نشد');
        return;
    }

    $('#loadingOverlay').show();
    
    axiosAgent.get(`/api/crypto/currencies/${currentCurrencyUuid}/`)
        .then(response => {
            currentCurrency = response.data;
            $('#currency-title').text(`جزئیات ${currentCurrency.name} (${currentCurrency.key})`);
            
            // Update current price
            if (currentCurrency.last_price) {
                const price = parseFloat(currentCurrency.last_price);
                let formattedPrice;
                if (price >= 1) {
                    formattedPrice = `$${price.toFixed(2)}`;
                } else if (price >= 0.01) {
                    formattedPrice = `$${price.toFixed(4)}`;
                } else {
                    formattedPrice = `$${price.toFixed(8)}`;
                }
                $('#current-price').text(formattedPrice);
            } else {
                $('#current-price').text('N/A');
            }
            
            // Update daily change
            if (currentCurrency.last_day_change !== null && currentCurrency.last_day_change !== undefined) {
                const change = parseFloat(currentCurrency.last_day_change).toFixed(2);
                const changeElement = $('#daily-change');
                const changeClass = currentCurrency.last_day_change >= 0 ? 'text-success' : 'text-danger';
                const changeIcon = currentCurrency.last_day_change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                changeElement.html(`<span class="${changeClass}"><i class="fa ${changeIcon}"></i> ${change}%</span>`);
            } else {
                $('#daily-change').text('N/A');
            }
            
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error loading currency details:', error);
            NotifyErrors(error, 'خطا در بارگذاری جزئیات ارز');
            $('#loadingOverlay').hide();
        });
}

function loadSubscriptions() {
    $('#loadingOverlay').show();
    
    axiosAgent.get('/api/crypto/subscriptions/')
        .then(response => {
            console.log('Subscriptions Response:', response.data);
            
            const responseData = response.data;
            const results = responseData.results || responseData;
            
            if (Array.isArray(results)) {
                // Filter subscriptions for current currency
                const currencySubscriptions = results.filter(sub => 
                    sub.currency === currentCurrencyUuid
                );
                
                subscriptionsTable.clear();
                
                if (currencySubscriptions.length > 0) {
                    subscriptionsTable.rows.add(currencySubscriptions);
                    subscriptionsTable.draw();
                }
            } else {
                console.error('Expected array response, got:', typeof results);
                NotificationModal('error', 'خطا', 'ساختار داده‌های دریافتی نامعتبر است');
            }
            
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error loading subscriptions:', error);
            NotifyErrors(error, 'خطا در بارگذاری اشتراک‌ها');
            $('#loadingOverlay').hide();
        });
}

function createSubscription() {
    const type = $('#type-selector').val();
    const price = $('#price-input').val();

    if (!type) {
        NotificationModal('warning', 'هشدار', 'لطفاً نوع هشدار را انتخاب کنید');
        return;
    }

    if (!price || price <= 0) {
        NotificationModal('warning', 'هشدار', 'لطفاً قیمت معتبری وارد کنید');
        return;
    }

    const data = {
        currency: currentCurrencyUuid
    };

    if (type === 'floor') {
        data.floor = parseFloat(price);
    } else {
        data.ceiling = parseFloat(price);
    }

    $('#loadingOverlay').show();

    axiosAgent.post('/api/crypto/subscriptions/create/', data)
        .then(response => {
            NotificationModal('success', 'موفقیت', 'اشتراک با موفقیت ایجاد شد');
            
            // Clear form
            $('#type-selector').val('');
            $('#price-input').val('');
            
            // Reload subscriptions
            loadSubscriptions();
        })
        .catch(error => {
            console.error('Error creating subscription:', error);
            NotifyErrors(error, 'خطا در ایجاد اشتراک');
            $('#loadingOverlay').hide();
        });
}

function cancelSubscription(subscriptionUuid) {
    Swal.fire({
        title: "تایید لغو اشتراک",
        text: "آیا از لغو این اشتراک اطمینان دارید؟",
        icon: "warning",
        showDenyButton: true,
        confirmButtonText: "تایید",
        denyButtonText: "انصراف",
        showLoaderOnConfirm: true,
        allowOutsideClick: () => !Swal.isLoading(),
    }).then((result) => {
        if (result.isConfirmed) {
            $('#loadingOverlay').show();
            
            axiosAgent.put(`/api/crypto/subscriptions/${subscriptionUuid}/cancel/`)
                .then(response => {
                    NotificationModal('success', 'موفقیت', 'اشتراک با موفقیت لغو شد');
                    loadSubscriptions();
                })
                .catch(error => {
                    console.error('Error cancelling subscription:', error);
                    NotifyErrors(error, 'خطا در لغو اشتراک');
                    $('#loadingOverlay').hide();
                });
        }
    });
}

function initializeEventHandlers() {
    // Create subscription button handler
    $('#create-subscription-btn').on('click', function() {
        createSubscription();
    });

    // Refresh subscriptions button handler
    $('#refresh-subscriptions-btn').on('click', function() {
        loadSubscriptions();
    });

    // Cancel subscription button handler (delegated event)
    $('#subscriptions-table').on('click', '.cancel-subscription-btn', function() {
        const subscriptionId = $(this).data('subscription-id');
        cancelSubscription(subscriptionId);
    });

    // ICT Strategy Analysis button handler
    $('#ict-strategy-btn').on('click', function() {
        NotificationModal('info', 'تحلیل استراتژی ICT', 'این بخش بعداً پیاده‌سازی خواهد شد');
    });

    // Market Analysis button handler
    $('#market-analysis-btn').on('click', function() {
        NotificationModal('info', 'تحلیل تکنیکال بازار', 'این بخش بعداً پیاده‌سازی خواهد شد');
    });

    // Logout button handler
    $('#logout-button').on('click', function() {
        axiosAgent.post('/api/auth/logout/')
            .then((response) => {
                localStorage.removeItem('token');
                localStorage.removeItem('crypto_uuid');
                NotificationModal("success", "خروج با موفقیت انجام شد", "لطفا کمی منتظر بمانید...");
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            })
            .catch((error) => {
                console.error(error);
                localStorage.removeItem('token');
                localStorage.removeItem('crypto_uuid');
                NotificationModal("success", "خروج انجام شد", "");
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            });
    });
}

// Main initialization function
function initializePage() {
    // Get currency UUID from localStorage
    currentCurrencyUuid = localStorage.getItem('crypto_uuid');
    
    if (!currentCurrencyUuid) {
        NotificationModal('error', 'خطا', 'شناسه ارز یافت نشد. به صفحه اصلی منتقل می‌شوید.');
        setTimeout(() => {
            window.location.href = 'crypto.html';
        }, 2000);
        return;
    }

    const freshLogin = localStorage.getItem('freshLogin');
    
    if (freshLogin === 'true') {
        localStorage.removeItem('freshLogin');
        const token = localStorage.getItem('token');
        
        if (token) {
            CreateNavSide("crypto_details.html");
            initializeSubscriptionsTable();
            initializeEventHandlers();
            loadCurrencyDetails();
            loadSubscriptions();
            return;
        }
    }
    
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                CreateNavSide("crypto_details.html");
                initializeSubscriptionsTable();
                initializeEventHandlers();
                loadCurrencyDetails();
                loadSubscriptions();
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

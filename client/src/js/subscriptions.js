import {
    axiosAgent,
    CheckHasAuthToken,
    NotifyErrors,
    NotificationModal,
    CreateNavSide
} from "./utils.js";
import './axios.min.js';

let subscriptionsTable;

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
                "data": "currency_name",
                "render": function(data, type, row) {
                    return data || 'N/A';
                }
            },
            {
                "data": "currency_key", 
                "render": function(data, type, row) {
                    return data || 'N/A';
                }
            },
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
                    let buttons = '';
                    
                    // View currency details button
                    buttons += `<button class="btn btn-info btn-sm ml-2 view-currency-btn" data-currency-id="${row.currency}" title="مشاهده جزئیات ارز">
                        <i class="fa fa-eye"></i> مشاهده ارز
                    </button>`;
                    
                    // Cancel subscription button (only for waiting subscriptions)
                    if (row.status === 'waiting') {
                        buttons += `<button class="btn btn-danger btn-sm cancel-subscription-btn" data-subscription-id="${row.uuid}" title="لغو اشتراک">
                            <i class="fa fa-times"></i> لغو
                        </button>`;
                    }
                    
                    return buttons || '<span class="text-muted">-</span>';
                }
            }
        ]
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
                subscriptionsTable.clear();
                
                if (results.length > 0) {
                    subscriptionsTable.rows.add(results);
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

function viewCurrencyDetails(currencyUuid) {
    localStorage.setItem('crypto_uuid', currencyUuid);
    window.location.href = 'crypto_details.html';
}

function initializeEventHandlers() {
    // Refresh subscriptions button handler
    $('#refresh-subscriptions-btn').on('click', function() {
        loadSubscriptions();
    });

    // View currency button handler (delegated event)
    $('#subscriptions-table').on('click', '.view-currency-btn', function() {
        const currencyId = $(this).data('currency-id');
        viewCurrencyDetails(currencyId);
    });

    // Cancel subscription button handler (delegated event)
    $('#subscriptions-table').on('click', '.cancel-subscription-btn', function() {
        const subscriptionId = $(this).data('subscription-id');
        cancelSubscription(subscriptionId);
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
    const freshLogin = localStorage.getItem('freshLogin');
    
    if (freshLogin === 'true') {
        localStorage.removeItem('freshLogin');
        const token = localStorage.getItem('token');
        
        if (token) {
            CreateNavSide("subscriptions.html");
            initializeSubscriptionsTable();
            initializeEventHandlers();
            loadSubscriptions();
            return;
        }
    }
    
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                CreateNavSide("subscriptions.html");
                initializeSubscriptionsTable();
                initializeEventHandlers();
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

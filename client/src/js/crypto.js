import {
    axiosAgent,
    CheckHasAuthToken,
    NotifyErrors,
    NotificationModal
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
            "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Persian.json"
        },
        "columns": [
            {"data": "name"},
            {"data": "symbol"},
            {
                "data": "current_price",
                "render": function(data, type, row) {
                    return data ? `$${parseFloat(data).toFixed(2)}` : 'N/A';
                }
            },
            {
                "data": "price_change_percentage_24h",
                "render": function(data, type, row) {
                    if (data === null || data === undefined) return 'N/A';
                    const value = parseFloat(data).toFixed(2);
                    const className = data >= 0 ? 'text-success' : 'text-danger';
                    const icon = data >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                    return `<span class="${className}"><i class="fa ${icon}"></i> ${value}%</span>`;
                }
            },
            {
                "data": "total_volume",
                "render": function(data, type, row) {
                    return data ? `$${parseFloat(data).toLocaleString()}` : 'N/A';
                }
            },
            {
                "data": null,
                "orderable": false,
                "render": function(data, type, row) {
                    return `<button class="btn btn-primary btn-sm view-crypto-btn" data-crypto-id="${row.id}">
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
            cryptoTable.clear();
            cryptoTable.rows.add(response.data);
            cryptoTable.draw();
            $('#loadingOverlay').hide();
        })
        .catch(error => {
            console.error('Error loading cryptocurrencies:', error);
            NotifyErrors(error, 'خطا در بارگذاری ارزهای دیجیتال');
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

function initializeNavbar() {
    const currentDate = new persianDate();
    const formattedDate = currentDate.format('YYYY/MM/DD');
    $('#date-time').text(formattedDate);
}

// Main initialization function
function initializePage() {
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                initializeNavbar();
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
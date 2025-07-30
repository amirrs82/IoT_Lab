import {
    axiosAgent,
    CreateNavSide,
    GetCurrentUser,
    NotifyErrors,
    parseGregorianDateToPersian, parsePersianDateToGregorian,
    RetrieveNameIDListData
} from "./utils.js";
import './axios.min.js';

function initializeSelectors() {
    function designSelect2(selector) {
        selector.select2()
        $(".select2-selection").each(function () {
            $(this).css({
                'border': 'none'
            });
        });
        $(".selection").each(function () {
            $(this).addClass('form-control');
        });
    }

    let selectors = ["title", "branch", "user", "hashtag", "budget"]
    let current_user_access_level = "کاربر"

    GetCurrentUser()
        .then((user) => {
            current_user_access_level = user.access_level

            for (let item of selectors) {
                let selector = $(`#${item}-filter`).empty()
                axiosAgent.get(`/list/${item}/`)
                    .then(RetrieveNameIDListData)
                    .then((data) => {
                        selector.append($('<option>', {
                            value: -1,
                            text: "هیچ کدام"
                        }));
                        for (let record of data) {
                            selector.append($('<option>', {
                                value: record.id,
                                text: record.text
                            }));
                        }

                        switch (item) {
                            case "user":
                                if (current_user_access_level === "کاربر")
                                    selector.prop('disabled', true).val(user.id)
                                else
                                    designSelect2(selector)
                                break;
                            case "title":
                                if (current_user_access_level === "معاونت سرفصل")
                                    selector.prop('disabled', true).val(user.access_level_data.title)
                                else
                                    designSelect2(selector)
                                break;
                            case "branch":
                                if (current_user_access_level === "مسئول واحد")
                                    selector.prop('disabled', true).val(user.access_level_data.branch)
                                else
                                    designSelect2(selector)
                                break;
                            default:
                                designSelect2(selector);
                                break;
                        }
                    })
                    .catch((error) => {
                        console.error(error)
                        NotifyErrors(error, `خطا در واکشی ${item} ها`)
                    })
            }
        })
}

function initializeDataTable(table_data) {
    let table = $('#contract-table').DataTable({
        language: {
            "lengthMenu":     "نشان دادن _MENU_ ردیف",
            "loadingRecords": "Loading...",
            "search":         "جستجو:",
            "zeroRecords":    "داده ای یافت نشد",
            "emptyTable":     "داده ای موجود نیست"
        },
        info : false,
        retrieve: true,
        data: table_data,
        order: [[6, 'desc']],
        columns: [
            {
                data: 'contract',
                render: function(data, type, row) {
                    return data.contractor;
                }
            },
            { data: 'title' },
            { data: 'branch' },
            {
                data: 'hashtag',
                render: function(data, type, row) {
                    return data ? data : '- - - -'
                }
            },
            {
                data: 'contract_id',
                render: function(data, type, row) {
                    return data ? data : '- - - -'
                }
            },
            {
                data: 'contract_state',
                type: 'contractState-pre' // Apply custom sorting
            },
            {
                data: 'request_date',
                render: function(data, type, row) {
                    return parseGregorianDateToPersian(data);
                }
            },
            {
                data: 'arrangement_date',
                render: function(data, type, row) {
                    return data ? parseGregorianDateToPersian(data) : '- - - -'
                }
            },
            {
                data: 'start_date',
                render: function(data, type, row) {
                    return parseGregorianDateToPersian(data);
                }
            },
            {
                data: 'end_date',
                render: function(data, type, row) {
                    return data ? parseGregorianDateToPersian(data) : '- - - -'
                }
            },
            {
                data: 'done',
                render: function(data, type, row) {
                    return data.toLocaleString();
                }
            },
            {
                data: 'price',
                render: function(data, type, row) {
                    return data.toLocaleString();
                }
            },
            {
                data: null,
                orderable: false,
                defaultContent: '<button class="btn btn-success">نمایش</button>',
                targets: -1
            },
        ],
        footerCallback: function (row, data, start, end, display) {
            let api = this.api();
            let total_cost = 0;
            let total_done = 0;

            // Iterate over the data and sum the prices
            data.forEach(function(rowData) {
                total_cost += rowData.price
                total_done += rowData.done
            });

            // Update the footer with the total
            $(api.column(10).footer()).text(total_done.toLocaleString());
            $(api.column(11).footer()).text(total_cost.toLocaleString());


            let badge = $(api.column(12).footer()).find('span').empty().removeClass();
            let percent = Math.floor(100 * total_done / total_cost)
            if (total_cost !== 0) {
                badge.text(`${percent}%`).addClass('badge');
                if (percent < 50)
                    badge.addClass('bg-success')
                else if (percent < 80)
                    badge.addClass('bg-warning')
                else
                    badge.addClass('bg-danger')
            } else {
                badge.text('- - - -').addClass('badge').addClass('bg-dark')
            }
        }
    });

    // event handler to the profile buttons
    table.on('click', 'button', function (event) {
        let row_data = table.row($(this).closest('tr')).data();
        localStorage.setItem('contract', row_data.contract.id)
        window.location.href = "contract_detail.html"
    });
}

function updateDataTable(query_param_str) {
    axiosAgent.get(`/contract/?${query_param_str}`)
        .then((response) => {
            let data = response.data.map(contract => ({
                "contract": contract,
                "branch": contract.branch,
                "title": contract.title,
                "hashtag": contract.hashtag,
                "contract_id": contract.contract_ID,
                "contract_state": contract.contract_state,
                "start_date": contract.start_date,
                "request_date": contract.request_date,
                "end_date": contract.end_date,
                "arrangement_date": contract.arrangement_date,
                "done": contract.done,
                "price": contract.price
            }));
            let table = $("#contract-table").DataTable();
            table.clear();
            table.rows.add(data);
            table.draw();
        })
        .catch((error) => {
            console.error(error);
            NotifyErrors(error, "خطا در واکشی قراردادها");
        });
}

function initializeTable() {
    $("#loadingOverlay").show()

    axiosAgent.get('/contract/')
        .then((response) => {
            let data = response.data.map(contract => ({
                "contract": contract,
                "branch": contract.branch,
                "title": contract.title,
                "hashtag": contract.hashtag,
                "contract_id": contract.contract_ID,
                "contract_state": contract.contract_state,
                "start_date": contract.start_date,
                "request_date": contract.request_date,
                "end_date": contract.end_date,
                "arrangement_date": contract.arrangement_date,
                "done": contract.done,
                "price": contract.price
            }));
            initializeDataTable(data)
            $("#loadingOverlay").hide()
        })
        .catch((error) => {
            console.error(error);
            $("#loadingOverlay").hide()
            NotifyErrors(error, "خطا در واکشی قراردادها");
        });
}

function AddEventListener() {
    $("#filter-btn").click(function (event) {
        let queryData = {
            user: $("#user-filter").val() === '-1' ? '' : parseInt($("#user-filter").val()),
            title: $("#title-filter").val() === '-1' ? '' : parseInt($("#title-filter").val()),
            branch: $("#branch-filter").val() === '-1' ? '' : parseInt($("#branch-filter").val()),
            hashtag: $("#hashtag-filter").val() === '-1' ? '' : parseInt($("#hashtag-filter").val()),
            contract_state: $("#contract_state-filter").val() === '-1' ? '' : $("#contract_state-filter").val(),
            contract_ID: $("#contract_ID-filter").val().trim() === '' ? '' :
                (parseInt($("#contract_ID-filter").val().trim()) ? parseInt($("#contract_ID-filter").val().trim()) : ''),
            budget: $("#budget-filter").val() === '-1' ? '' : parseInt($("#budget-filter").val()),
            date: $("#date-filter").val() === '-1' ? '' : $("#date-filter").val(),
            date_from: $("#date_from-filter").val() ? parsePersianDateToGregorian($("#date_from-filter").val()) : '',
            date_to: $("#date_to-filter").val() ? parsePersianDateToGregorian($("#date_to-filter").val()) : ''
        }
        const queryParams = new URLSearchParams(queryData);

        updateDataTable(queryParams.toString())
    })
}

CreateNavSide('contracts.html')
$(document).ready(() => {
    initializeSelectors()
    initializeTable()
    AddEventListener()
});
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


function AddEventListener() {
    $("#filter-btn").click(function (event) {
        $("#loadingOverlay").show()

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

        axiosAgent.get(`/export/contract/?${queryParams}`, {
            responseType: 'blob' // Ensure response is handled as a file
        })
            .then((response) => {
                $("#loadingOverlay").hide();

                // Create a URL for the blob
                const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
                const url = window.URL.createObjectURL(blob);

                // Create a temporary anchor element and trigger download
                const a = document.createElement("a");
                a.href = url;
                a.download = "Contracts.xlsx"; // Set the file name
                document.body.appendChild(a);
                a.click();

                // Cleanup
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch((error) => {
                console.error(error);
                $("#loadingOverlay").hide()
                NotifyErrors(error, "خطا در واکشی قراردادها");
            });
    })
}

CreateNavSide('export.html')
$(document).ready(() => {
    initializeSelectors()
    AddEventListener()
});
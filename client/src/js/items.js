import {
    axiosAgent,
    CreateNavSide,
    NotificationModal,
    NotifyErrors,
    RetrieveNameIDListData
} from "./utils.js";

let overlay_counter = 0

function InitiateSelectors() {
    $("#loadingOverlay").show()

    let items = ["title", "branch", "unit", "hashtag"]
    for (let item of items) {
        let selector = $(`#${item}-selector`).empty()
        axiosAgent.get(`/list/${item}/`)
            .then(RetrieveNameIDListData)
            .then((data) => {
                for (let name of data) {
                    selector.append($('<option>', {
                        value: name.id,
                        text: name.text
                    }));
                }
                if (overlay_counter === 4)
                    $("#loadingOverlay").hide()
                else
                    overlay_counter += 1
            })
            .catch((error) => {
                console.error(error)
                $("#loadingOverlay").hide()
                NotifyErrors(error, `خطا در واکشی ${item} ها`)
            })
    }
}

function addEventListener() {
    let items = ["title", "branch", "unit", "hashtag"]
    for (let item of items) {
        let edit_btn = $(`#edit-${item}-btn`)
        let new_btn = $(`#new-${item}-btn`)
        let delete_btn = $(`#delete-${item}-btn`)

        edit_btn.click((event) => {
            let new_value = $(`#new-${item}-input`).val()
            if (!new_value)
                NotificationModal("error", "ادیت ناموفق", "یک نام جدید وارد کنید.")
            else {
                let selected_item = $(`#${item}-selector :selected`).text()
                let selected_item_id = $(`#${item}-selector`).val()
                if (!selected_item_id)
                    NotificationModal("error", "ادیت ناموفق", "آیتمی انتخاب نشده است.")
                else {
                    axiosAgent.put(`/retrieve/${item}/${selected_item_id}/`, {name: new_value})
                        .then((response) => {
                            NotificationModal("success", "ادیت موفق", `آیتم انتخاب شده با موفقیت ادیت شد و از "${selected_item}" به "${new_value}" تغییر نام داد.`)
                            InitiateSelectors()
                            $(`#new-${item}-input`).val('')
                        })
                        .catch((error) => {
                            console.error(error)
                            NotifyErrors(error, "خطا در ادیت آیتم")
                        })
                }
            }
        })

        new_btn.click((event) => {
            let new_value = $(`#new-${item}-input`).val()
            if (!new_value)
                NotificationModal("error", "ساخت ناموفق", "یک نام جدید وارد کنید.")
            else {
                axiosAgent.post(`/create/${item}/`, {name: new_value})
                    .then((response) => {
                        NotificationModal("success", "ساخت موفق", `آیتم جدید با نام "${new_value}" ساخته شد.`)
                        InitiateSelectors()
                        $(`#new-${item}-input`).val('')
                    })
                    .catch((error) => {
                        console.error(error)
                        NotifyErrors(error, "خطا در ساخت آیتم")
                    })
            }
        })

        delete_btn.click(() => {
            let selected_item = $(`#${item}-selector :selected`).text()
            let selected_item_id = $(`#${item}-selector`).val()
            if (!selected_item_id)
                NotificationModal("error", "حذف ناموفق", "آیتمی انتخاب نشده است.")
            else {
                axiosAgent.delete(`/retrieve/${item}/${selected_item_id}/`)
                    .then((response) => {
                        NotificationModal("success", "حذف موفق", `آیتم "${selected_item}" با موفقیت حذف شد.`)
                        InitiateSelectors()
                        $(`#new-${item}-input`).val('')
                    })
                    .catch((error) => {
                        console.error(error)
                        NotifyErrors(error, "خطا در حذف آیتم")
                    })
            }
        })
    }

    if (overlay_counter === 1)
        $("#loadingOverlay").hide()
    else
        overlay_counter += 1
}

CreateNavSide("items.html")
InitiateSelectors()
addEventListener()
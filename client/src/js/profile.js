import {axiosAgent, CreateNavSide, NotificationModal, NotifyErrors} from "./utils.js";
import $ from './jquery.module.js';
import './axios.min.js';

function InitiateProfile() {
    $("#loadingOverlay").show()

    axiosAgent.get('/api/auth/profile/')
        .then((response) => {
            let profile = response.data
            // Display basic user info using the correct field IDs from profile.html
            $("#username-input").val(profile.username || '')
            $("#email-input").val(profile.email || '')
            $("#first_name-input").val(profile.first_name || '')
            $("#last_name-input").val(profile.last_name || '')
            
            // Set simple user status
            $("#access-level").text('"کاربر عادی"')
            $("#branch").text("- - - -")
            $("#title").text("- - - -")

            $("#loadingOverlay").hide()
        })
        .catch((error) => {
            console.error(error)
            $("#loadingOverlay").hide()
            NotificationModal("error", "خطا در واکشی پروفایل", `وضعیت: ${error.response ? error.response.status : 'نامشخص'}`)
        })
}

function addEventListener() {
    let profile_save_btn = $("#profile-save-btn")
    let profile_edit_btn = $("#profile-edit-btn")

    function toggleEditEnable() {
        if ($(profile_edit_btn).hasClass('btn-success')) {
            $(profile_edit_btn).removeClass('btn-success').addClass('btn-danger').text("انصراف");
        } else {
            $(profile_edit_btn).removeClass('btn-danger').addClass('btn-success').text("ویرایش");
            InitiateProfile()
        }

        $("#profile-card-body input, #profile-save-btn").prop("disabled", function (i, val) {
            return !val;
        });
    }

    profile_edit_btn.click(
        function (event) {
            event.preventDefault(); // Prevent the default form submission behavior
            toggleEditEnable();
        }
    )

    profile_save_btn.click(
        function (event) {
            event.preventDefault()

            let firstName = $("#first_name-input");
            let lastName = $("#last_name-input");
            let email = $("#email-input");

            let data = {
                first_name: firstName.val(),
                last_name: lastName.val(),
                email: email.val()
            };

            axiosAgent.put("/api/auth/profile/", data)
                .then((response) => {
                    NotificationModal("success", "ویرایش موفق", "ویرایش پروفایل با موفقیت انجام شد")
                    InitiateProfile()
                    toggleEditEnable();
                })
                .catch((error) => {
                    console.error(error)
                    NotifyErrors(error, "ویرایش ناموفق")
                });

        }
    )
}

CreateNavSide('profile.html')
InitiateProfile();
addEventListener();

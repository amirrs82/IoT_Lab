import {
    axiosAgent,
    CheckHasAuthToken,
    NotificationModal,
    NotifyErrors
} from "./utils.js";
import $ from './jquery.module.js';
import './axios.min.js';

function addEventListeners() {
    let username = $("#username-input");
    let password = $("#password-input");
    let firstName = $("#first-name-input");
    let lastName = $("#last-name-input");
    let email = $("#email-input");
    let signupButton = $("#signup-button");

    signupButton.on("click", function (event) {
        event.preventDefault(); // Prevent the default form submission behavior

        // Basic validation
        if (!username.val() || !password.val() || !email.val() || !firstName.val() || !lastName.val()) {
            NotificationModal("error", "خطا در ثبت نام", "لطفا تمام فیلدهای ضروری را تکمیل کنید");
            return;
        }

        let data = {
            username: username.val(),
            password: password.val(),
            email: email.val(),
            first_name: firstName.val(),
            last_name: lastName.val()
        };

        axiosAgent.post("/api/auth/register/", data)
            .then((response) => {
                Swal.fire({
                    icon: "success",
                    title: "ثبت نام با موفقیت انجام شد",
                    text: "اکنون می‌توانید وارد شوید",
                })
                    .then((result) => {
                        window.location.href = 'login.html';
                    });
            })
            .catch((error) => {
                NotifyErrors(error, "ثبت نام ناموفق")
        })
    });

    let cornerButton = $("#corner-button");
    cornerButton.on("click", function () {
        window.location.href = "login.html";
    });
}

CheckHasAuthToken()
    .then((hasAuth) => {
        if (hasAuth)
            window.location.href = "crypto.html"
        else
            addEventListeners();
    })
    .catch((error) => {
        console.error("Error checking authentication:", error);
    });

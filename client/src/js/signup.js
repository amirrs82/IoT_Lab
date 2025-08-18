import {
    axiosAgent,
    CheckHasAuthToken,
    NotificationModal,
    NotifyErrors
} from "./utils.js";
import $ from './jquery.module.js';
import './axios.min.js';

// Store user data for the verification step
let userSignupData = {};

function addEventListeners() {
    let username = $("#username-input");
    let password = $("#password-input");
    let firstName = $("#first-name-input");
    let lastName = $("#last-name-input");
    let email = $("#email-input");
    let verificationCode = $("#verification-code-input");
    
    let requestVerificationButton = $("#request-verification-button");
    let completeSignupButton = $("#complete-signup-button");
    let backToInfoButton = $("#back-to-info-button");
    let resendCodeButton = $("#resend-code-button");

    // Step 1: Request verification code
    requestVerificationButton.on("click", function (event) {
        event.preventDefault();

        // Basic validation
        if (!username.val() || !password.val() || !email.val() || !firstName.val() || !lastName.val()) {
            NotificationModal("error", "خطا در ثبت نام", "لطفا تمام فیلدهای ضروری را تکمیل کنید");
            return;
        }

        // Store user data for later use
        userSignupData = {
            username: username.val(),
            password: password.val(),
            email: email.val(),
            first_name: firstName.val(),
            last_name: lastName.val()
        };

        // Show loading state
        requestVerificationButton.val("در حال ارسال...");
        requestVerificationButton.prop("disabled", true);

        axiosAgent.post("/api/auth/request-verification/", userSignupData)
            .then((response) => {
                // Hide user info form and show verification form
                $(".signup-form").addClass("verification-form-visible");
                
                NotificationModal("success", "کد تایید ارسال شد", "کد تایید به ایمیل شما ارسال شد. لطفا ایمیل خود را بررسی کنید.");
            })
            .catch((error) => {
                NotifyErrors(error, "خطا در ارسال کد تایید");
            })
            .finally(() => {
                // Reset button state
                requestVerificationButton.val("درخواست کد تایید");
                requestVerificationButton.prop("disabled", false);
            });
    });

    // Step 2: Complete signup with verification code
    completeSignupButton.on("click", function (event) {
        event.preventDefault();

        if (!verificationCode.val()) {
            NotificationModal("error", "خطا در تایید", "لطفا کد تایید را وارد کنید");
            return;
        }

        if (verificationCode.val().length !== 8) {
            NotificationModal("error", "خطا در تایید", "کد تایید باید 8 رقم باشد");
            return;
        }

        let verificationData = {
            email: userSignupData.email,
            verification_code: verificationCode.val()
        };

        // Show loading state
        completeSignupButton.val("در حال تایید...");
        completeSignupButton.prop("disabled", true);

        axiosAgent.post("/api/auth/register/", verificationData)
            .then((response) => {
                // Store the token if provided
                if (response.data.token) {
                    localStorage.setItem('auth_token', response.data.token);
                }
                
                Swal.fire({
                    icon: "success",
                    title: "ثبت نام با موفقیت انجام شد",
                    text: "اکنون می‌توانید از خدمات استفاده کنید",
                })
                .then((result) => {
                    window.location.href = 'crypto.html';
                });
            })
            .catch((error) => {
                NotifyErrors(error, "خطا در تکمیل ثبت نام");
            })
            .finally(() => {
                // Reset button state
                completeSignupButton.val("تکمیل ثبت نام");
                completeSignupButton.prop("disabled", false);
            });
    });

    // Back to user info form
    backToInfoButton.on("click", function (event) {
        event.preventDefault();
        $(".signup-form").removeClass("verification-form-visible");
        verificationCode.val(""); // Clear verification code
    });

    // Resend verification code
    resendCodeButton.on("click", function (event) {
        event.preventDefault();
        
        if (!userSignupData.email) {
            NotificationModal("error", "خطا", "لطفا ابتدا اطلاعات خود را وارد کنید");
            return;
        }

        // Show loading state
        resendCodeButton.text("در حال ارسال...");
        resendCodeButton.prop("disabled", true);

        axiosAgent.post("/api/auth/request-verification/", userSignupData)
            .then((response) => {
                NotificationModal("success", "کد تایید مجدداً ارسال شد", "کد تایید جدید به ایمیل شما ارسال شد.");
                verificationCode.val(""); // Clear previous code
            })
            .catch((error) => {
                NotifyErrors(error, "خطا در ارسال مجدد کد تایید");
            })
            .finally(() => {
                // Reset button state
                resendCodeButton.text("ارسال مجدد کد تایید");
                resendCodeButton.prop("disabled", false);
            });
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

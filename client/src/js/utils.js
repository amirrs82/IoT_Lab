import $ from './jquery.module.js';
import './axios.min.js';

// export const SERVER_URL = "https://api.kardad.rahmag.ir";
export const SERVER_URL = "http://localhost:10003";


export const axiosAgent = axios.create({
    baseURL: SERVER_URL,
});

// Add a request interceptor
axiosAgent.interceptors.request.use(
    function(config) {
        // Check if token exists in localStorage
        const token = localStorage.getItem('token');
        // If token exists, set authorization header
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    function(error) {
        // Do something with request error
        return Promise.reject(error);
    }
);

export const ContractTitle = {
    TOLID: "تولید"
}

export async function NotificationModal(icon, title, text) {
    await Swal.fire({
        icon: icon,
        title: title,
        text: text,
    });
}

async function AlertErrors(errors, errors_fields) {
    for (let i = 0; i < errors_fields.length; i++) {
        if (Array.isArray(errors[errors_fields[i]])) {
            for (let error_decribtion of errors[errors_fields[i]])
                await NotificationModal("error", getFieldNameInPersian(errors_fields[i]),
                    getErrorInPersian(error_decribtion));
        } else {
            await NotificationModal("error", getFieldNameInPersian(errors_fields[i]),
                getErrorInPersian(errors[errors_fields[i]]));
        }
    }
}

export function NotifyErrors(error, common_title) {
    if (error.response && error.response.status === 400) {
        let errors = error.response.data;
        let errors_fields = Object.keys(errors);
        AlertErrors(errors, errors_fields);
    } else {
        NotificationModal("error", common_title, `status:${error.response ? error.response.status : 'unknown'}, message:${error.response ? error.response.data.detail : 'unknown'}`);
    }
}



export function CheckHasAuthToken() {
    return new Promise((resolve, reject) => {
        if (localStorage.getItem("token")) {
            // Check if token is valid by trying to access profile endpoint
            axiosAgent.get("/api/auth/profile/")
                .then((response) => {
                    resolve(true);
                })
                .catch((error) => {
                    localStorage.removeItem("token");
                    resolve(false);
                });
        } else {
            resolve(false);
        }
    });
}

export function GetCurrentUser() {
    return axiosAgent.get("retrieve/current_user/")
        .then((response) => {
            return response.data; // Return the user's information
        })
        .catch((error) => {
            console.error("Error fetching current user:", error);
            throw error;
        });
}

export function RetrieveNameListData(response) {
    let data = []
    for (let item of response.data) {
        data.push({
            id: item.name,
            text: item.name
        })
    }
    return data
}

export function RetrieveNameIDListData(response) {
    let data = []
    for (let item of response.data) {
        data.push({
            id: item.id,
            text: item.name
        })
    }
    return data
}



function getFieldNameInPersian(field_name) {
    const fieldTranslations = {
        first_name: "نام",
        last_name: "نام خانوادگی",
        email: "ایمیل",
        national_ID: "کد ملی",
        mobile_phone_number: "شماره موبایل",
        address: "آدرس",
        bank_account_number: "شماره حساب بانکی",
        landline_phone_number: "تلفن ثابت",
        name: "نام",
        postal_code: "کد پستی",
        major: "رشته تحصیلی",
        educational_level: "آخرین مدرک تحصیلی",
        new_password: "رمز عبور جدید",
        current_password: "رمز عبور فعلی",
        new_username: "نام کاربری جدید",
        period: "دوره ی بودجه",
        accepting_title: "سرفصل",
        branch: "واحد",
        title: "سرفصل",
        prices: "حجم قرارداد",
        contractor: "طرف قرارداد",
        start_date: "تاریخ شروع",
        end_date: "تاریخ پایان",
        _contract_state: "وضعیت قرارداد",
        contract_state: "وضعیت قرارداد",
        contract_ID: "شناسه قرارداد",
        contract: "قرارداد",
        done: 'حجم انجام شده جدید',
        report_state: 'وضعیت گزارش',
        PermissionDenied: 'عدم دسترسی',
        maximum: 'حجم قرارداد',
    };

    return fieldTranslations[field_name] || field_name;
}

function getErrorInPersian(error_describtion) {
    const errorTranslations = {
        "[object Object]": "مشکل در جزییات داده ها.",
        "This field is required.": "این فیلد الزامی است",
        "This field may not be blank.": "این فیلد الزامی است",
        "This field may not be null.": "این فیلد الزامی است",
        "Cannot be empty!": "این فیلد الزامی است",
        "profile with this email already exists.": "با این ایمیل یک پروفایل دیگر ساخته شده است",
        "profile with this mobile phone number already exists.": "با این شماره همراه یک پروفایل دیگر ساخته شده است",
        "profile with this national ID already exists.": "با این کدملی یک پروفایل دیگر ساخته شده است",
        "profile with this bank account number already exists.": "با این شماره حساب بانکی یک پروفایل دیگر ساخته شده است",
        "Ensure this field has at least 11 characters.": "این فیلد باید حتما 11 کاراکتر داشته باشد",
        "Ensure this field has no more than 11 characters.": "این فیلد باید حتما 11 کاراکتر داشته باشد",
        "Ensure this field has at least 10 characters.": "این فیلد باید حتما 10 کاراکتر داشته باشد",
        "Enter a valid email address.": "فرمت ایمیل اشتباه است.",
        "This password is too short. It must contain at least 8 characters.": "رمز عبور باید حداقل 8 کاراکتر داشته باشد",
        "Enter a valid username. This value may contain only unaccented lowercase a-z and uppercase A-Z letters, numbers, and @/./+/-/_ characters.": "نام کاربری باید فقط شامل حروف انگلیسی، اعداد و کاراکترهای (@/./+/-/_) باشد",
        "This password is too common.": "پسوورد پیچیدگی لازم را ندارد. پسوورد باید شامل ارقام و حروف انگلیسی باشد",
        "This password is entirely numeric.": "پسوورد نمیتواند فقط از اعداد تشکیل شده باشد.",
        "budget with this period already exists.": "یک بودجه برای این دوره قبلا ساخته شده است.",
        "hashtag with this name already exists.": "یک هشتگ با این نام قبلا ساخته شده است.",
        "title with this name already exists.": "یک سرفصل با این نام قبلا ساخته شده است.",
        "branch with this name already exists.": "یک واحد با این نام قبلا ساخته شده است.",
        "unit with this name already exists.": "یک واحد حجمی با این نام قبلا ساخته شده است.",
        "You do not have permission to perform this action.": "شما دسترسی یه این عملیات یا بخش را ندارید.",
        "user with this branch already exists.": "یک کاربر دیگر مسئول این واحد است. نمی توان دو مسئول برای یک واحد انتخاب کرد.",
        "user with this accepting title already exists.": "یک کاربر دیگر مسئول این سرفصل است. نمی توان دو مسئول برای یک سرفصل انتخاب کرد.",
        "Your (branch's) budget isn't enough!": "بودجه واحد انتخابی کافی نیست.",
        "Your (title's) budget isn't enough!": "بودجه سرفصل انتخابی کافی نیست.",
        "Invalid date, bigger than start date": "تاریخ پایان حتما باید بعد از تاریخ شروع باشد.",
        "Invalid date, the contract is not ended but the end_date you entered is before now": "وضعیت قرارداد \"پایان یافته\" یا \"فسخ شده\" نیست، به همین دلیل تاریخ پایان نباید قبل از تاریخ فعلی باشد.",
        "Contract id must be initialized before the confirmation of the contract": "شناسه قرارداد باید قبل از تایید و تکمیل قرارداد وارد شود.",
        "Invalid date, the contract is started but the start_date you entered is after now": "قرارداد شروع شده نمیتواند تاریخ شروع ش در آینده باشد.",
        "Invalid time to make a report! Contract finished or not started yet!": "زمان نامناسبی برای ایجاد گزارش است. قرارداد به پایان رسیده است یا هنوز شروع نشده است!",
        "Cannot make a report for canceled contract!": "برای قراردادهای فسخ شده یا رد شده، نمی توان گزارشی ثبت کرد.",
        "The contract's left volume isn't enough (unpaid reports considered)": "حجم باقی مانده از این واحد در قرارداد کمتر از مقدار حجم انجام شده جدید است.",
        "Cannot make a change in paid or denied report": "امکان ویرایش گزارش های پرداخت شده یا رد شده وجود ندارد.",
        "You cannot access this report for editing": "شما برای ویرایش کردن این گزارش، دسترسی ندارید.",
        "Maximum must be greater than the total done volume": "حجم یک واحد در قرارداد نمیتواند از مقدار انجام شده آن کمتر باشد.",
        "contract title with this name already exists.": "سرفصلی با این نام وجود دارد.",
        "status:403, message:You do not have permission to perform this action.": "شما دسترسی انجام این عملیات راد ندارید.",
    };

    return errorTranslations[error_describtion] || error_describtion;
}

function convertPersianDigitsToEnglish(str) {
    const charMap = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9'
    };

    return str.split('').map(char => charMap[char] || char).join('');
}

export function convertPersianMonthToDigit(str) {
    let months = {
        "فروردین": 1,
        "اردیبهشت": 2,
        "خرداد": 3,
        "تیر": 4,
        "مرداد": 5,
        "شهریور": 6,
        "مهر": 7,
        "آبان": 8,
        "آذر": 9,
        "دی": 10,
        "بهمن": 11,
        "اسفند": 12
    }

    return months[str];
}

export function persianMonthPeriodToGregorian(input_month, input_year) {
    const year = convertPersianDigitsToEnglish(input_year);
    const month = convertPersianMonthToDigit(input_month);
    if (!month || !year)
        throw new Error();
    persianDate.toLocale('en');
    const firstDay = new persianDate([year, month])
    const lastDay = new persianDate([year, month]).add('M', 1).subtract('d', 1)

    return [firstDay, lastDay];
}

export function parsePersianDateToGregorian(date) {
    date = convertPersianDigitsToEnglish(date)
    let [year, month, day] = date.split('/')

    persianDate.toLocale('en');
    persianDate.toCalendar('persian');
    const result = new persianDate([parseInt(year), parseInt(month), parseInt(day)]);

    return result.toCalendar('gregorian').format("YYYY-MM-DD")
}

export function parseGregorianDateToPersian(date) {
    let [year, month, day] = date.split('-');

    year = parseInt(year);
    month = parseInt(month);
    day = parseInt(day);

    persianDate.toLocale('fa');
    persianDate.toCalendar('gregorian');
    const result = new persianDate([year, month, day]);

    return result.toCalendar('persian').format("YYYY/MM/DD");
}


function CreateSideBar(user, page_link, sidebar, profile) {  // TODO: reports.html didn't implemented
    // Sidebar functionality removed - keeping function for backward compatibility
    // but not creating any sidebar items
    let html_body = "";
    sidebar.html(html_body)
    profile.text(user.name.split('-')[1] + ' ' + user.name.split('-')[0])
}

function InitiateNavbar(navbar) {
    let date_time = navbar.find('#date-box').find('#date-time')
    let logout_btn = navbar.find('#logout-button')

    logout_btn.on("click", function (event) {
        axiosAgent.post('/api/auth/logout/')
            .then((response) => {
                localStorage.removeItem('token')
                NotificationModal("success", "خروج با موفقیت انجام شد", "لطفا کمی منتظر بمانید...")
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            }, (error) => {
                console.error(error)
                // Even if logout fails on server, remove token locally
                localStorage.removeItem('token')
                NotificationModal("success", "خروج انجام شد", "")
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            })
    })

    const currentDate = new persianDate();
    const formattedDate = currentDate.format('YYYY/MM/DD');
    date_time.text(formattedDate);
}

export function CreateNavSide(page_link) {
    // Simplified navigation - no sidebar functionality
    CheckHasAuthToken()
        .then((hasAuth) => {
            if (hasAuth) {
                // Just initialize navbar without sidebar
                let navbar = $("#navbar")
                InitiateNavbar(navbar)
            } else
                window.location.href = "login.html"
        })
        .catch((error) => {
            console.error("Error checking authentication:", error);
        });
}
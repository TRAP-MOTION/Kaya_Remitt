// api.js

const BASE_URL = "http://127.0.0.1:5000/api/v1"; // For development environment

/**
 * Get JWT token from localStorage
 */
function getToken() {
    return localStorage.getItem("access_token");
}

/**
 * Generic API request helper
 */
async function request(endpoint, method = "GET", body = null, auth = false) {
    const headers = {
        "Content-Type": "application/json",
    };

    if (auth) {
        const token = getToken();

        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    const options = {
        method,
        headers,
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok || data.success === false) {
        throw new Error(data.message || "Something went wrong.");
    }

    return data;
}

/* =========================================================
   AUTHENTICATION
========================================================= */

const AuthAPI = {
    register(user) {
        return request("/auth/register", "POST", user);
    },

    login(credentials) {
        return request("/auth/login", "POST", credentials);
    }
};

/* =========================================================
   MERCHANTS
========================================================= */

const MerchantAPI = {
    getAll() {
        return request("/merchants");
    },

    getById(merchantId) {
        return request(`/merchants/${merchantId}`);
    },

    getServices(merchantId) {
        return request(`/merchants/${merchantId}/services`);
    }
};

/* =========================================================
   PAYMENTS
========================================================= */

const PaymentAPI = {
    create(payment) {
        return request("/payments", "POST", payment, true);
    },

    history() {
        return request("/payments/history", "GET", null, true);
    }
};

/* =========================================================
   VOUCHERS
========================================================= */

const VoucherAPI = {
    generate(paymentId) {
        return request(
            "/vouchers",
            "POST",
            {
                payment_id: paymentId
            },
            true
        );
    },

    verify(voucherId) {
        return request(
            "/vouchers/verify",
            "POST",
            {
                voucher_id: voucherId
            },
            true
        );
    },

    redeem(voucherId) {
        return request(
            `/vouchers/${voucherId}/redeem`,
            "PATCH",
            null,
            true
        );
    }
};

/* =========================================================
   MERCHANT DASHBOARD
========================================================= */

const MerchantDashboardAPI = {
    transactions() {
        return request("/merchant/transactions", "GET", null, true);
    }
};

/* =========================================================
   PROFILE
========================================================= */

const ProfileAPI = {
    get() {
        return request("/profile", "GET", null, true);
    },

    update(profile) {
        return request("/profile", "PUT", profile, true);
    }
};

/* =========================================================
   ADMIN
========================================================= */

const AdminAPI = {

    updateMerchantStatus(merchantId, payload) {
        return request(
            `/admin/merchants/${merchantId}/status`,
            "PATCH",
            payload,
            true
        );
    },

    deactivateUser(userId, payload = {}) {
        return request(
            `/admin/users/${userId}/deactivate`,
            "PATCH",
            payload,
            true
        );
    },

    activateUser(userId, payload = {}) {
        return request(
            `/admin/users/${userId}/activate`,
            "PATCH",
            payload,
            true
        );
    },

    sendWarning(payload) {
        return request(
            "/admin/warnings",
            "POST",
            payload,
            true
        );
    },

    listWarnings(userId = null) {
        const url = userId
            ? `/admin/warnings?user_id=${userId}`
            : "/admin/warnings";

        return request(url, "GET", null, true);
    },

    listSupportTickets(filters = {}) {
        const params = new URLSearchParams(filters).toString();

        const url = params
            ? `/admin/support?${params}`
            : "/admin/support";

        return request(url, "GET", null, true);
    },

    getSupportTicket(ticketId) {
        return request(
            `/admin/support/${ticketId}`,
            "GET",
            null,
            true
        );
    },

    updateSupportTicket(ticketId, payload) {
        return request(
            `/admin/support/${ticketId}`,
            "PATCH",
            payload,
            true
        );
    }
};
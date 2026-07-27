// api.js — KayaRemit frontend API client
// Override before this script loads if needed, e.g. local backend:
//   window.KAYA_API_BASE = "http://127.0.0.1:5000/";

window.KAYA_API_BASE = window.KAYA_API_BASE || "https://kayaremitt.pxxl.run/";

function resolveApiBase(base) {
  const trimmed = String(base || "").replace(/\/+$/, "");
  // Accept either host root or an already-qualified /api/v1 base.
  if (/\/api\/v\d+$/i.test(trimmed)) {
    return trimmed;
  }
  return `${trimmed}/api/v1`;
}

const BASE_URL = resolveApiBase(window.KAYA_API_BASE);

/* =========================================================
   SESSION / TOKEN HELPERS
========================================================= */

const Session = {
  getToken() {
    return localStorage.getItem("access_token");
  },

  setToken(token) {
    localStorage.setItem("access_token", token);
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem("kaya_user") || "null");
    } catch {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem("kaya_user", JSON.stringify(user));
  },

  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("kaya_user");
  },

  isAuthenticated() {
    return Boolean(this.getToken());
  },

  requireAuth(loginPage = "login.html") {
    if (!this.isAuthenticated()) {
      window.location.href = loginPage;
      return false;
    }
    return true;
  },

  requireRole(roles, fallbackPage = "login.html") {
    if (!this.requireAuth(fallbackPage)) return false;
    const user = this.getUser();
    const allowed = Array.isArray(roles) ? roles : [roles];
    if (!user || !allowed.includes(user.role)) {
      window.location.href = this.dashboardForRole(user?.role) || fallbackPage;
      return false;
    }
    return true;
  },

  dashboardForRole(role) {
    switch (role) {
      case "admin":
        return "admin-dashboard.html";
      case "merchant":
        return "merchant-dashboard.html";
      case "diaspora":
        return "dashboard.html";
      default:
        return "login.html";
    }
  },

  logout(loginPage = "login.html") {
    this.clear();
    window.location.href = loginPage;
  },
};

/**
 * Generic API request helper.
 * Throws Error with .status and .payload when the API returns an error.
 */
async function request(endpoint, method = "GET", body = null, auth = false) {
  const headers = {
    Accept: "application/json",
  };

  if (body !== null && body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = Session.getToken();
    if (!token) {
      const err = new Error("You must be signed in to continue.");
      err.status = 401;
      throw err;
    }
    headers.Authorization = `Bearer ${token}`;
  }

  const options = { method, headers };
  if (body !== null && body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, options);
  } catch {
    throw new Error("Unable to reach the server. Is the backend running?");
  }

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { success: false, message: text };
    }
  }

  if (response.status === 401 && auth) {
    Session.clear();
  }

  if (!response.ok || data?.success === false) {
    const err = new Error(
      data?.message || `Request failed (${response.status}).`
    );
    err.status = response.status;
    err.reason = data?.reason;
    err.payload = data;
    throw err;
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
  },

  /**
   * Login, store JWT, fetch profile, and return { token, user }.
   */
  async loginAndStore(credentials) {
    const loginRes = await this.login(credentials);
    const token = loginRes.data?.token;
    if (!token) {
      throw new Error("Login succeeded but no token was returned.");
    }
    Session.setToken(token);
    const profileRes = await ProfileAPI.get();
    Session.setUser(profileRes.data);
    return { token, user: profileRes.data };
  },
};

/* =========================================================
   MERCHANTS (public catalogue)
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
  },
};

/* =========================================================
   PAYMENTS
========================================================= */

const PaymentAPI = {
  /** Create a payment request (status: AwaitingAcceptance). */
  create(payment) {
    return request("/payments", "POST", payment, true);
  },

  /** Start PayChangu checkout for an Accepted payment. */
  checkout(paymentId) {
    return request(`/payments/${paymentId}/checkout`, "POST", null, true);
  },

  history() {
    return request("/payments/history", "GET", null, true);
  },
};

/* =========================================================
   VOUCHERS
========================================================= */

const VoucherAPI = {
  generate(paymentId) {
    return request("/vouchers", "POST", { payment_id: paymentId }, true);
  },

  verify(voucherId) {
    return request("/vouchers/verify", "POST", { voucher_id: voucherId }, true);
  },

  redeem(voucherId) {
    return request(`/vouchers/${voucherId}/redeem`, "PATCH", null, true);
  },
};

/* =========================================================
   MERCHANT DASHBOARD
========================================================= */

const MerchantDashboardAPI = {
  transactions() {
    return request("/merchant/transactions", "GET", null, true);
  },

  acceptPayment(paymentId) {
    return request(
      `/merchant/payments/${paymentId}/accept`,
      "PATCH",
      null,
      true
    );
  },

  denyPayment(paymentId) {
    return request(
      `/merchant/payments/${paymentId}/deny`,
      "PATCH",
      null,
      true
    );
  },
};

/* =========================================================
   NOTIFICATIONS
========================================================= */

const NotificationAPI = {
  list() {
    return request("/notifications", "GET", null, true);
  },

  markRead(notificationId) {
    return request(
      `/notifications/${notificationId}/read`,
      "PATCH",
      null,
      true
    );
  },

  markAllRead() {
    return request("/notifications/read-all", "PATCH", null, true);
  },
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
  },
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
    return request(`/admin/users/${userId}/activate`, "PATCH", payload, true);
  },

  sendWarning(payload) {
    return request("/admin/warnings", "POST", payload, true);
  },

  listWarnings(userId = null) {
    const url = userId
      ? `/admin/warnings?user_id=${encodeURIComponent(userId)}`
      : "/admin/warnings";
    return request(url, "GET", null, true);
  },

  listSupportTickets(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, value);
      }
    });
    const qs = params.toString();
    return request(qs ? `/admin/support?${qs}` : "/admin/support", "GET", null, true);
  },

  getSupportTicket(ticketId) {
    return request(`/admin/support/${ticketId}`, "GET", null, true);
  },

  updateSupportTicket(ticketId, payload) {
    return request(`/admin/support/${ticketId}`, "PATCH", payload, true);
  },
};

/* Export for modules / keep globals for classic script tags */
if (typeof window !== "undefined") {
  Object.assign(window, {
    Session,
    AuthAPI,
    MerchantAPI,
    PaymentAPI,
    VoucherAPI,
    MerchantDashboardAPI,
    NotificationAPI,
    ProfileAPI,
    AdminAPI,
    request,
  });
}

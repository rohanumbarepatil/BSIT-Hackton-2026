/**
 * auth.js — WasteWatchers
 * Handles JWT storage, session validation and live user data on every page.
 * Include this script on every page: <script src="auth.js"></script>
 */

const WW = {

  // ─────────────────────────────────────
  // TOKEN HELPERS
  // ─────────────────────────────────────

  saveToken(token) {
    localStorage.setItem('ww_token', token);
  },

  getToken() {
    return localStorage.getItem('ww_token');
  },

  clearToken() {
    localStorage.removeItem('ww_token');
    localStorage.removeItem('ww_user');
  },

  // ─────────────────────────────────────
  // USER CACHE (avoid repeated API calls)
  // ─────────────────────────────────────

  saveUser(user) {
    localStorage.setItem('ww_user', JSON.stringify(user));
  },

  getCachedUser() {
    try {
      return JSON.parse(localStorage.getItem('ww_user')) || null;
    } catch {
      return null;
    }
  },

  // ─────────────────────────────────────
  // AUTH HEADER — attach to every API call
  // ─────────────────────────────────────

  authHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + this.getToken()
    };
  },

  // ─────────────────────────────────────
  // FETCH LIVE USER DATA FROM BACKEND
  // GET /api/user/me
  // ─────────────────────────────────────

  async fetchUser() {
    const token = this.getToken();
    if (!token) return null;

    try {
      const res = await fetch('/api/user/me', {
        method: 'GET',
        headers: this.authHeaders()
      });

      if (res.status === 401 || res.status === 403) {
        // Token expired or invalid — clear and redirect to login
        this.clearToken();
        this.redirectToLogin();
        return null;
      }

      if (!res.ok) return this.getCachedUser(); // fallback to cache on other errors

      const data = await res.json();
      this.saveUser(data);
      return data;

    } catch (err) {
      // Network error — use cached user if available
      console.warn('[WW] Could not reach /api/user/me, using cache.', err);
      return this.getCachedUser();
    }
  },

  // ─────────────────────────────────────
  // UPDATE NAVBAR WITH LIVE DATA
  // Looks for: #navPoints, #navUsername
  // ─────────────────────────────────────

  updateNavbar(user) {
    if (!user) return;

    // Points pill (present on all pages)
    const pointsEl = document.getElementById('navPoints');
    if (pointsEl) {
      const pts = (user.points || 0).toLocaleString('en-IN');
      pointsEl.textContent = pts + ' pts';
    }

    // Username (present on camera.html)
    const userEl = document.getElementById('navUsername');
    if (userEl) {
      userEl.textContent = 'Hi ' + (user.username || 'User');
    }

    // Dashboard stat card (present on dashboard.html)
    const totalPtsEl = document.getElementById('totalPoints');
    if (totalPtsEl) {
      totalPtsEl.textContent = (user.points || 0).toLocaleString('en-IN');
    }

    const progressLabel = document.getElementById('progressLabel');
    if (progressLabel && user.points !== undefined) {
      const next = WW.nextLevelThreshold(user.points);
      progressLabel.textContent = user.points.toLocaleString('en-IN') + ' / ' + next.toLocaleString('en-IN');
    }

    const progressFill = document.getElementById('progressFill');
    if (progressFill && user.points !== undefined) {
      const pct = WW.levelProgressPct(user.points);
      setTimeout(() => { progressFill.style.width = pct + '%'; }, 400);
    }

    const levelBadge = document.getElementById('levelBadge');
    if (levelBadge && user.points !== undefined) {
      levelBadge.textContent = 'Level ' + WW.getLevel(user.points);
    }
  },

  // ─────────────────────────────────────
  // LEVEL HELPERS
  // ─────────────────────────────────────

  getLevel(points) {
    if (points >= 10000) return 6;
    if (points >= 6000)  return 5;
    if (points >= 3500)  return 4;
    if (points >= 1500)  return 3;
    if (points >= 500)   return 2;
    return 1;
  },

  levelThresholds: [0, 500, 1500, 3500, 6000, 10000, Infinity],

  nextLevelThreshold(points) {
    const thresholds = [500, 1500, 3500, 6000, 10000];
    return thresholds.find(t => t > points) || 10000;
  },

  levelProgressPct(points) {
    const thresholds = WW.levelThresholds;
    const level = WW.getLevel(points);
    const from  = thresholds[level - 1];
    const to    = thresholds[level];
    if (to === Infinity) return 100;
    return Math.min(100, Math.round((points - from) / (to - from) * 100));
  },

  // ─────────────────────────────────────
  // INIT — call on every protected page
  // Fetches user and updates navbar
  // Pass requireAuth=false on intro/about/terms
  // ─────────────────────────────────────

  async init(requireAuth = true) {
    const token = this.getToken();

    if (requireAuth && !token) {
      this.redirectToLogin();
      return null;
    }

    // Show cached data immediately (no flash)
    const cached = this.getCachedUser();
    if (cached) this.updateNavbar(cached);

    // Then fetch fresh data in background
    const user = await this.fetchUser();
    if (user) this.updateNavbar(user);

    return user;
  },

  // ─────────────────────────────────────
  // REDIRECT HELPERS
  // ─────────────────────────────────────

  redirectToLogin() {
    if (!window.location.pathname.includes('intro.html') &&
        !window.location.pathname.endsWith('/')) {
      window.location.href = 'intro.html';
    }
  },

  logout() {
    this.clearToken();
    window.location.href = 'intro.html';
  },

  // ─────────────────────────────────────
  // API HELPER — use this for all fetch calls
  // Automatically attaches JWT header
  // ─────────────────────────────────────

  async api(endpoint, options = {}) {
    const res = await fetch(endpoint, {
      ...options,
      headers: {
        ...this.authHeaders(),
        ...(options.headers || {})
      }
    });

    if (res.status === 401) {
      this.clearToken();
      this.redirectToLogin();
      return null;
    }

    return res;
  }

};
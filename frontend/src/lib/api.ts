const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001';

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${BASE_URL}${endpoint}`;
  
  let token = null;
  if (typeof window !== 'undefined') {
    try {
      const authData = localStorage.getItem('wastesense_auth');
      if (authData) {
        const parsed = JSON.parse(authData);
        token = parsed.access_token;
      }
    } catch (e) {}
  }

  const headers: HeadersInit = {
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    (headers as any)['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Your session has expired. Please sign in again.");
      }
      if (response.status === 403) {
        throw new Error("You don't have permission to access this section.");
      }
      if (response.status >= 500) {
        throw new Error("Server error. Please try again.");
      }

      let errorDetail = 'API Error';
      try {
        const errorData = await response.json();
        if (errorData.detail) errorDetail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      } catch (e) {
        errorDetail = response.statusText;
      }
      throw new Error(`Error ${response.status}: ${errorDetail}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error(`API Call failed: ${endpoint}`, error);
    if (error.message && (error.message.includes("Failed to fetch") || error.name === "TypeError")) {
      throw new Error("Backend unavailable. Make sure FastAPI is running on port 8001.");
    }
    throw error;
  }
}

// ----------------------------------------------------
// MODEL INFO
// ----------------------------------------------------
export async function getModelInfo() {
  return fetchAPI('/api/v1/model/info');
}

// ----------------------------------------------------
// CLASSIFICATION
// ----------------------------------------------------
export async function classifyWaste(file: File) {
  const formData = new FormData();
  formData.append('image', file);

  return fetchAPI('/api/v1/classify', {
    method: 'POST',
    body: formData,
    // Do not set Content-Type header manually when sending FormData,
    // the browser will automatically set it to multipart/form-data with boundary.
  });
}

// ----------------------------------------------------
// GREEN CREDITS & DISPOSAL
// ----------------------------------------------------
export async function startDisposal(userId: string, result: any) {
  return fetchAPI('/api/v1/disposal/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      classification: {
        class_name: result.class_name,
        category_group: result.category_group,
        confidence: result.confidence
      }
    }),
  });
}

export async function verifyDisposal(sessionId: string) {
  return fetchAPI(`/api/v1/disposal/${sessionId}/verify`, {
    method: 'POST'
  });
}

export async function getUserCredits(userId: string = "test_user_1") {
  return fetchAPI(`/api/v1/users/${userId}/credits`);
}

export async function getCreditHistory(userId: string = "test_user_1") {
  return fetchAPI(`/api/v1/users/${userId}/credit-history`);
}

// ----------------------------------------------------
// E-WASTE LIFECYCLE
// ----------------------------------------------------
export async function getEwasteDashboard() {
  return fetchAPI('/api/v1/ewaste/dashboard');
}

export async function getEwasteAssets() {
  return fetchAPI('/api/v1/ewaste/assets');
}

export async function getEwasteAudit(assetId: string) {
  return fetchAPI(`/api/v1/ewaste/assets/${assetId}/audit`);
}

// ----------------------------------------------------
// SMART BINS
// ----------------------------------------------------
export async function getBins() {
  return fetchAPI('/api/v1/bins');
}

export async function getBinAlerts() {
  return fetchAPI('/api/v1/bins/alerts');
}

export async function getBinPrediction(binId: string) {
  return fetchAPI(`/api/v1/bins/${binId}/prediction`);
}

export async function collectBin(binId: string) {
  return fetchAPI(`/api/v1/bins/${binId}/collect`, {
    method: 'POST',
  });
}

export async function getDashboardStats() {
  return fetchAPI('/api/v1/bins/dashboard/stats');
}

// ----------------------------------------------------
// ADMIN
// ----------------------------------------------------
export async function getAdminUsers() {
  return fetchAPI('/api/v1/admin/users');
}

export async function getAdminAuditLogs() {
  return fetchAPI('/api/v1/admin/audit-logs');
}

export async function getAdminCreditsOverview() {
  return fetchAPI('/api/v1/admin/credits/overview');
}

export async function getAdminCreditsStudents() {
  return fetchAPI('/api/v1/admin/credits/students');
}

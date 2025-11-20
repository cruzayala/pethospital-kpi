/**
 * Authentication Module for PetHospital KPI Service
 * Handles JWT tokens, refresh logic, and user session
 */

const Auth = {
    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    isAuthenticated() {
        const token = localStorage.getItem('access_token');
        return token !== null && token !== '';
    },

    /**
     * Get access token
     * @returns {string|null}
     */
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    /**
     * Get refresh token
     * @returns {string|null}
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    /**
     * Get current user data
     * @returns {object|null}
     */
    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                return JSON.parse(userStr);
            } catch (e) {
                return null;
            }
        }
        return null;
    },

    /**
     * Save authentication data
     * @param {string} accessToken
     * @param {string} refreshToken
     * @param {object} user
     */
    saveAuth(accessToken, refreshToken, user) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
    },

    /**
     * Clear authentication data
     */
    clearAuth() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    /**
     * Logout user
     */
    logout() {
        this.clearAuth();
        window.location.href = '/login';
    },

    /**
     * Redirect to login if not authenticated
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    },

    /**
     * Refresh access token
     * @returns {Promise<boolean>} Success or failure
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await axios.post('/auth/refresh', {
                refresh_token: refreshToken
            });

            // Update access token
            localStorage.setItem('access_token', response.data.access_token);
            return true;
        } catch (error) {
            console.error('Failed to refresh token:', error);
            // If refresh fails, logout
            this.logout();
            return false;
        }
    },

    /**
     * Setup Axios interceptors for automatic token refresh
     */
    setupAxiosInterceptors() {
        // Request interceptor - add Authorization header
        axios.interceptors.request.use(
            config => {
                const token = this.getAccessToken();
                if (token) {
                    config.headers['Authorization'] = `Bearer ${token}`;
                }
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        // Response interceptor - handle 401 errors
        axios.interceptors.response.use(
            response => {
                return response;
            },
            async error => {
                const originalRequest = error.config;

                // If 401 and not already retrying
                if (error.response && error.response.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    // Try to refresh token
                    const refreshed = await this.refreshAccessToken();

                    if (refreshed) {
                        // Retry original request with new token
                        originalRequest.headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
                        return axios(originalRequest);
                    } else {
                        // Refresh failed, redirect to login
                        this.logout();
                        return Promise.reject(error);
                    }
                }

                return Promise.reject(error);
            }
        );
    },

    /**
     * Check if user has specific role
     * @param {string} role
     * @returns {boolean}
     */
    hasRole(role) {
        const user = this.getCurrentUser();
        if (!user || !user.roles) {
            return false;
        }
        return user.roles.includes(role);
    },

    /**
     * Check if user is admin
     * @returns {boolean}
     */
    isAdmin() {
        const user = this.getCurrentUser();
        return user && (user.is_superuser === true || this.hasRole('admin'));
    },

    /**
     * Check if user is analyst
     * @returns {boolean}
     */
    isAnalyst() {
        return this.hasRole('analyst');
    },

    /**
     * Initialize auth module
     */
    init() {
        this.setupAxiosInterceptors();
    }
};

// Auto-initialize when script loads
if (typeof axios !== 'undefined') {
    Auth.init();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}

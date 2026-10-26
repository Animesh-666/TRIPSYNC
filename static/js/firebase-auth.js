/**
 * TripSync — Firebase Authentication Client Module
 * Manages Firebase JS SDK login and server-side session exchange.
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('login-btn');
    const loginSpinner = document.getElementById('login-spinner');
    const errorAlert = document.getElementById('login-error');
    const togglePassBtn = document.getElementById('toggle-password');

    // 1. Password Visibility Toggle
    if (togglePassBtn && passwordInput) {
        togglePassBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            const icon = togglePassBtn.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
            }
        });
    }

    // 3. Initialize Firebase Client SDK if configured
    let firebaseInitialized = false;
    const config = window.FIREBASE_CONFIG || {};

    if (config.apiKey && config.projectId && window.firebase) {
        try {
            if (!firebase.apps.length) {
                firebase.initializeApp(config);
            }
            firebaseInitialized = true;
            console.log('Firebase Web SDK initialized successfully.');
        } catch (err) {
            console.warn('Firebase client initialization warning:', err);
        }
    }

    function showError(msg) {
        if (errorAlert) {
            errorAlert.textContent = msg;
            errorAlert.classList.remove('d-none');
        }
    }

    function hideError() {
        if (errorAlert) {
            errorAlert.classList.add('d-none');
            errorAlert.textContent = '';
        }
    }

    function setLoading(isLoading) {
        if (loginBtn) loginBtn.disabled = isLoading;
        if (loginSpinner) {
            if (isLoading) loginSpinner.classList.remove('d-none');
            else loginSpinner.classList.add('d-none');
        }
    }

    // 4. Form Submission Handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();

            const email = (emailInput ? emailInput.value : '').trim();
            const password = passwordInput ? passwordInput.value : '';
            const csrfToken = window.CSRF_TOKEN || (loginForm.querySelector('input[name="_csrf_token"]') || {}).value;

            if (!email || !password) {
                showError('Please enter both email and password.');
                return;
            }

            setLoading(true);

            // Path A: Firebase Web SDK is initialized and active
            if (firebaseInitialized && config.apiKey) {
                try {
                    await firebase.auth().setPersistence(firebase.auth.Auth.Persistence.NONE);
                    const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
                    const idToken = await userCredential.user.getIdToken(true);

                    // Send ID Token to Flask server
                    const response = await fetch('/session/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-Token': csrfToken,
                        },
                        body: JSON.stringify({ idToken: idToken }),
                    });

                    const result = await response.json();
                    if (response.ok && result.status === 'success') {
                        // Clear temporary client-side persistence if desired
                        try {
                            await firebase.auth().signOut();
                        } catch (e) {}

                        window.location.href = result.redirect || '/dashboard';
                    } else {
                        showError(result.message || 'Authentication failed. Please verify your credentials.');
                        setLoading(false);
                    }
                } catch (authErr) {
                    console.error('Firebase Auth Error:', authErr);
                    let errMsg = 'Failed to sign in. Please verify your email and password.';
                    if (authErr.code === 'auth/user-not-found' || authErr.code === 'auth/wrong-password' || authErr.code === 'auth/invalid-credential') {
                        errMsg = 'Invalid email or password.';
                    } else if (authErr.code === 'auth/too-many-requests') {
                        errMsg = 'Too many failed login attempts. Please try again later.';
                    } else if (authErr.message) {
                        errMsg = authErr.message;
                    }
                    showError(errMsg);
                    setLoading(false);
                }
            } else {
                showError('Firebase login is not configured. Contact your administrator.');
                setLoading(false);
            }
        });
    }
});

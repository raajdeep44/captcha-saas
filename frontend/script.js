// Global variables
let currentUser = null;
let websites = [];
let selectedWebsite = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('[INIT] DOM Loaded. Initializing App...');
    initializeApp();
    setupEventListeners();
    
});

function initializeApp() {
    console.log('[INIT] Initializing application...');
    checkAuthStatus();
    displayWebsites();
}

function setupEventListeners() {
    console.log('[INIT] Setting up form event listeners...');
    const loginForm = document.getElementById('loginFormElement');
    const signupForm = document.getElementById('signupFormElement');
    const websiteForm = document.getElementById('websiteForm');

    if (loginForm) {
        console.log('[LISTENER] Login form ready');
        loginForm.addEventListener('submit', handleLogin);
    }
    if (signupForm) {
        console.log('[LISTENER] Signup form ready');
        signupForm.addEventListener('submit', handleSignup);
    }
    if (websiteForm) {
        console.log('[LISTENER] Website form ready');
        websiteForm.addEventListener('submit', addWebsite);
    }
}

function checkAuthStatus() {
    try {
        console.log('[AUTH] Checking auth status...');
        const userData = localStorage.getItem('captcha_user');
        if (userData) {
            currentUser = JSON.parse(userData);
            console.log('[AUTH] User logged in:', currentUser.name);
            showDashboard();
            loadUserData();
        } else {
            console.log('[AUTH] No user session found. Showing auth forms.');
            showAuth();
        }
    } catch (error) {
        console.error('[AUTH] Error reading auth status:', error);
        showAuth();
    }
}

function showAlert(message, type = 'success') {
    console.log(`[ALERT] (${type.toUpperCase()})`, message);
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;

    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';

    alertContainer.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
        </div>
    `;

    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert && alert.classList.contains('show')) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    }, 3000);
}

function clearAlert() {
    console.log('[UI] Clearing alerts');
    const alertContainer = document.getElementById('alertContainer');
    if (alertContainer) {
        alertContainer.innerHTML = '';
    }
}

function showLoginForm() {
    console.log('[UI] Showing login form');
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
    clearAlert();
}

function showSignupForm() {
    console.log('[UI] Showing signup form');
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupForm').style.display = 'block';
    clearAlert();
}

function showDashboard() {
    console.log('[UI] Showing dashboard');
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';

    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.name;
        console.log(currentUser.name)
        console.log(currentUser.email)
    }

    // âœ… Attach listener only now
    const websiteForm = document.getElementById('websiteForm');
    if (websiteForm) {
        websiteForm.addEventListener('submit', addWebsite);
    }
}

function showAuth() {
    console.log('[UI] Showing auth section');
    document.getElementById('authSection').style.display = 'flex';
    document.getElementById('dashboardSection').style.display = 'none';
}

async function handleSignup(event) {
    event.preventDefault();
    console.log('[SIGNUP] Signup form submitted');
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;

    if (!name || !email || !password) {
        showAlert('Please fill in all fields!', 'error');
        return;
    }
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters!', 'error');
        return;
    }

    try {
        console.log('[SIGNUP] Sending request to backend');
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: name, email, password })
        });
        const data = await response.json();
        console.log('[SIGNUP] Response received:', data);

        if (response.ok) {
            showAlert('Account created successfully! Please log in.');
            showLoginForm();
        } else {
            showAlert(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('[SIGNUP] Error:', error);
        showAlert('Error creating account. Please try again.', 'error');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    console.log('[LOGIN] Login form submitted');
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('Please fill in all fields!', 'error');
        return;
    }

    try {
        console.log('[LOGIN] Sending request to backend');
        const response = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        console.log('[LOGIN] Response received:', data);

        if (response.ok) {
            localStorage.setItem('captcha_token', data.access_token);
            currentUser = { name: data.username, email :data.email };
            localStorage.setItem('captcha_user', JSON.stringify(currentUser));
            showAlert('Login successful! Welcome back!');
            setTimeout(() => {
                showDashboard();
                loadUserData();
            }, 1500);
        } else {
            showAlert(data.detail || 'Invalid email or password!', 'error');
        }
    } catch (error) {
        console.error('[LOGIN] Error:', error);
        showAlert('Error during login. Please try again.', 'error');
    }
}

function handleLogout() {
    console.log('[LOGOUT] User logging out...');
    try {
        localStorage.removeItem('captcha_user');
        currentUser = null;
        websites = [];
        showAuth();
    } catch (error) {
        console.error('[LOGOUT] Error:', error);
    }
}

function loadUserData() {
    console.log('[DATA] Loading user websites...');
    try {
        const userWebsites = JSON.parse(localStorage.getItem(`websites_${currentUser.id}`) || '[]');
        websites = userWebsites;
        updateDashboardStats();
        displayWebsites();
    } catch (error) {
        console.error('[DATA] Error loading websites:', error);
        websites = [];
        updateDashboardStats();
        displayEmptyWebsites();
    }
}

function updateDashboardStats() {
    const websiteCount = websites.length;
    console.log('[STATS] Total websites:', websiteCount);
    document.getElementById('websiteCount').textContent = websiteCount;
    document.getElementById('apiKeyCount').textContent = websiteCount;
    document.getElementById('totalWebsites').textContent = `${websiteCount} website${websiteCount !== 1 ? 's' : ''}`;
}

function generateApiKey() {
    const apiKey = 'ck_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    console.log('[API] Generated API key:', apiKey);
    return apiKey;
}
function addWebsite(event) {
    event.preventDefault();
    console.log('[FORM] Add website form submitted');
    const name = document.getElementById('websiteName').value.trim();
    const url = document.getElementById('websiteUrl').value.trim();
    const type = document.getElementById('captchaType').value;

    if (!name || !url) {
        alert('Please fill in all fields!');
        return;
    }

    try {
        const newWebsite = {
            id: Date.now().toString(),
            name,
            url,
            type,
            apiKey: generateApiKey(),
            createdAt: new Date().toISOString()
        };

        websites.push(newWebsite);
        localStorage.setItem(`websites_${currentUser.email}`, JSON.stringify(websites));
        console.log('[FORM] Website added:', newWebsite);

        updateDashboardStats();
        displayWebsites();

        document.getElementById('websiteName').value = '';
        document.getElementById('websiteUrl').value = '';
        showIntegrationCode(newWebsite);
    } catch (error) {
        console.error('[FORM] Error adding website:', error);
        alert('Error adding website. Please try again.');
    }
}

function displayEmptyWebsites() {
    const container = document.getElementById('websitesList');
    console.log('[UI] Displaying empty state for websites');
    if (container) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-globe fa-4x text-muted mb-3"></i>
                <h6 class="text-muted">No websites added yet</h6>
                <p class="text-muted">Add your first website above to get started with CAPTCHA protection!</p>
            </div>
        `;
    }
}

function displayWebsites(){
    const container = document.getElementById('websitesList')
    if(!container) return;

    if(websites.length === 0){
        displayEmptyWebsites();
        return;
    }

    container.innerHTML = websites.map((site,idx) => `
        <div class="card mb-2">
            <div class="card-body">
                <h5>${idx + 1}. ${escapeHtml(site.name)}</h5>
                <p><strong>URL:</strong> ${escapeHtml(site.url)}</p>
                
                <p><strong>API Key:</strong> ${escapeHtml(site.apiKey)}</p>
                <small>Added: ${new Date(site.createdAt).toLocaleString()}</small>
                <div class="mt-3">
                    <button class="btn btn-outline-primary btn-sm" onclick="showIntegrationCode(websites[${idx}])">
                        <i class="fas fa-code me-1"></i> Show Code
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyCode(elementId) {
    try {
        const codeElement = document.getElementById(elementId);
        if (!codeElement) {
            alert('Code element not found.');
            return;
        }

        const text = codeElement.textContent;
        console.log('[COPY] Copying code from element:', elementId);

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showCopySuccess(codeElement);
            }).catch((err) => {
                console.error('[COPY] Clipboard API failed:', err);
                fallbackCopyText(text);
            });
        } else {
            fallbackCopyText(text);
        }
    } catch (error) {
        console.error('[COPY] Error copying code:', error);
        alert('Failed to copy code. Please try selecting and copying manually.');
    }
}

function fallbackCopyText(text) {
    try {
        console.log('[COPY] Using fallback copy method');
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);

        if (successful) {
            alert('Code copied to clipboard!');
        } else {
            alert('Failed to copy. Please select and copy the code manually.');
        }
    } catch (err) {
        console.error('[COPY] Fallback copy failed:', err);
        alert('Copy failed. Please select and copy the code manually.');
    }
}

function showCopySuccess(codeElement) {
    const copyBtn = codeElement.parentElement.querySelector('.copy-btn');
    if (copyBtn) {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        copyBtn.style.background = '#10b981';

        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = 'rgba(255,255,255,0.1)';
        }, 2000);
    }
}

function showIntegrationCode(website) {
    const code = generateCaptchaCode(website);

    document.getElementById('htmlCode').textContent = code.html;
    document.getElementById('jsCode').textContent = code.js;
    document.getElementById('cssCode').textContent = code.css;

    document.getElementById('apiKeyDisplay').textContent = website.apiKey;
    document.getElementById('websiteNameDisplay').textContent = website.name;

    // Show the modal (Bootstrap 5)
    const modal = new bootstrap.Modal(document.getElementById('codeModal'));
    modal.show();
}

function generateCaptchaCode(website) {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Captcha Demo</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Your CAPTCHA widget -->
        <img id="captchaImage" alt="Loading CAPTCHA...">
        <input type="text" id="captchaAnswer" placeholder="Enter CAPTCHA" required>
        <button type="button" onclick="loadCaptcha()">ðŸ”„</button>
        <br><br>
</body>
</html>`;

  const js = `
<script>
const API_KEY = "abc123"; // Your provided API key
        let captchaId = null;

        // 1ï¸âƒ£ Load CAPTCHA when page opens
        async function loadCaptcha() {
            const res = await fetch("http://127.0.0.1:8000/generate-captcha?api_key=" + API_KEY);
            captchaId = res.headers.get("captcha-id");
            console.log("loaded captchaID:",captchaId);
            const blob = await res.blob();
            document.getElementById("captchaImage").src = URL.createObjectURL(blob);
        }
        
        // 2ï¸âƒ£ Handle form submit
        document.getElementById("loginForm").addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const captchaAnswer = document.getElementById("captchaAnswer").value;
            console.log("captchaId before submit:", captchaId);
            if (!captchaId) {
            alert("CAPTCHA not loaded yet!");
            return;
            }

            const res = await fetch("http://127.0.0.1:8002/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    captcha_id: captchaId,
                    captcha_answer: captchaAnswer
                })
            });
            console.log("captcha id after :",captchaId)
            const result = await res.json();
            document.getElementById("result").textContent = result.message || result.detail;
            console.log("Submitting with captchaId:", captchaId, "and answer:", captchaAnswer);

        });


        loadCaptcha();
</script>`;

  const css = `
body {
  font-family: Arial, sans-serif;
  text-align: center;
  margin-top: 50px;
  background-color: #f5f5f5;
}

.container {
  background-color: #fff;
  padding: 20px;
  display: inline-block;
  border-radius: 10px;
  box-shadow: 0px 0px 10px gray;
}

input {
  padding: 5px;
  margin: 5px;
}`;

  return { html, js, css };
}





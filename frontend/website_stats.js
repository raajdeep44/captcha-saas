const API_BASE = 'http://127.0.0.1:8000'; // replace with your backend URL
const token = localStorage.getItem('captcha_token');
const websiteId = localStorage.getItem('selected_website_id'); // <-- get saved website ID

if (!token || !websiteId) {
    showAlert('You must be logged in and select a website first. Redirecting...','error');
    handleLogout();
    throw new Error("Missing token or websiteId");
}

async function fetchStatsAndActivity() {
  try {
    console.log(`[API] Fetching stats for website ID: ${websiteId}`);

    // Fetch stats for this website
    const statsRes = await fetch(`${API_BASE}/stats/${websiteId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });

    if (!statsRes.ok) throw new Error("Failed to fetch stats");
    const stats = await statsRes.json();

    // Fill DOM with stats
    
    document.getElementById('siteCaptchaCount').innerText = stats.total_generated || 0;
    const rate = stats.success_rate;
    document.getElementById('siteSuccessRate').innerText = Math.round(rate) ? Math.round(rate) + '%' : '0';

    // Fetch recent activity for this website
    const activityRes = await fetch(`${API_BASE}/attempts/daily/${websiteId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });

    if (!activityRes.ok) throw new Error("Failed to fetch activity");
    const data = await activityRes.json();
    const activities = data.daily_statistics;

    // Render activity table
    const tbody = document.getElementById('activityTable').querySelector('tbody');
    tbody.innerHTML = ''; // clear old rows

    activities.forEach((activity, index) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${activity.date}</td> 
        <td>${activity.total}</td>
        <td>${activity.success}</td>
        <td>${activity.failed}</td>
        <td>${activity.success_rate}</td>
      `;
      tbody.appendChild(row);
    });

  } catch (error) {
    console.error('Error fetching stats/activity:', error);
    showAlert('Error fetching stats or activity', 'error');
  }
}

// Call the function on page load
window.addEventListener('DOMContentLoaded', fetchStatsAndActivity);

async function getCaptchaAttemptsLast30Days(){
  try {
    const response = await fetch(`${API_BASE}/attempts/last-30-days/${websiteId}`,{
        headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) throw new Error("Failed to fetch stats");
    const data = await response.json();

    document.getElementById('last30days').innerText = data.captcha_attempts_last_30_days || 0;
  }
  catch(err) {
      console.error('[ERROR] Fetching captcha attempts failed:', err);
      showAlert('Failed to fetch captcha attempts. Please try again.', 'error');
  }
}

window.addEventListener('DOMContentLoaded', getCaptchaAttemptsLast30Days);
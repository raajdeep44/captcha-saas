const API_BASE = 'http://localhost:8000'; // replace with your backend URL
const token = localStorage.getItem('captcha_token')
    if(!token){
        showAlert('You must be logged in to add a website. Redirecting to login...','error');
        handleLogout();
        return;
    }
async function fetchStatsAndActivity() {
  try {
    // Fetch stats
    const statsRes = await fetch(`${API_BASE}/stats/`);
    const stats = await statsRes.json();
    
    document.getElementById('websiteCount').innerText = stats.websiteCount || 0;
    document.getElementById('captchaCount').innerText = stats.captchaCount || 0;
    document.getElementById('successRate').innerText = stats.successRate ? stats.successRate + '%' : '0';

    // Fetch recent activity
    const activityRes = await fetch(`${API_BASE}/api/activity`);
    const activities = await activityRes.json();

    const tbody = document.getElementById('activityTable').querySelector('tbody');
    tbody.innerHTML = ''; // clear existing rows

    activities.forEach((activity, index) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${activity.website}</td>
        <td>${activity.ip}</td>
        <td><span class="status ${activity.status.toLowerCase()}">${activity.status}</span></td>
        <td>${activity.time}</td>
      `;
      tbody.appendChild(row);
    });

  } catch (error) {
    console.error('Error fetching stats/activity:', error);
  }
}

// Call the function on page load
window.addEventListener('DOMContentLoaded', fetchStatsAndActivity);


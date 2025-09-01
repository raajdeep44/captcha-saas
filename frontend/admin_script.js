const API_BASE = "http://127.0.0.1:8000";
let usersData = [];
let websitesData = [];

let captchaInteractions = {
    labels: ['pass','fail'],
    data: []
};

let captchaOutcomes = {
    labels: [],
    data: []
};

document.addEventListener("DOMContentLoaded", () => {
    const adminName = localStorage.getItem("username"); // or from backend response
    document.getElementById("welcomeMsg").textContent = `Welcome, ${adminName}`;
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem('captcha_user');   // clear token
    // localStorage.removeItem("username"); // clear username
    window.location.href = "index.html"; // redirect to login page
});

// Simulate API data
async function updateCards() {
    const token = localStorage.getItem('captcha_token')
    console.log("this is token",token)
    const response = await fetch("http://127.0.0.1:8000/stats-admin/total-users-websites",{
        headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });
    const res = await response.json();
    console.log(res);
    document.getElementById('totalUsers').innerHTML = res.total_users;
    document.getElementById('totalWebsites').innerHTML = res.total_websites;

    const successData = await fetch("http://127.0.0.1:8000/stats-admin/catpcha",{
        headers: { "Authorization": `Bearer ${token}` }
    })
    const data = await successData.json();
    // Calculate captcha success rate
    document.getElementById('captchaRate').innerHTML = data.success_rate + '%';
}

// Chart.js initialization
async function initCharts() {
    // Captcha Interactions Chart
    const token = localStorage.getItem('captcha_token');
    const response = await fetch("http://127.0.0.1:8000/stats-admin/captcha-completions",{
       headers: { "Authorization": `Bearer ${token}` }
    })
    const res = await response.json()
    console.log(res);
    captchaInteractions = res;
    
    const ctx1 = document.getElementById('interactionsChart1');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: captchaInteractions.labels,
            datasets: [{
                label: 'Completed Verifications',
                data: captchaInteractions.data,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });

    // Captcha Outcomes Chart
    const outcome_data = await fetch(`${API_BASE}/stats-admin/captcha-pass-fail`,{
        headers: { "Authorization": `Bearer ${token}` }
    })
    const data = await outcome_data.json();
    console.log(data);
    captchaOutcomes = {
        labels: ['Pass', 'Fail'],
        data: [data.pass, data.fail]
    };
    const ctx2 = document.getElementById('outcomesChart');
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: captchaOutcomes.labels,
            datasets: [{
                data: captchaOutcomes.data,
                backgroundColor: [
                    'rgba(46, 204, 113, 0.7)',
                    'rgba(231, 76, 60, 0.7)'
                ],
                borderColor: [
                    'rgba(46, 204, 113, 1)',
                    'rgba(231, 76, 60, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
    // third chart pass fail 
    const outcome_res = await fetch("http://127.0.0.1:8000/stats-admin/captcha-pass-fail-daywise",{
        headers: { "Authorization": `Bearer ${token}` }
    })
    const outcome_json = await outcome_res.json()
    console.log(outcome_json)

    const labels3 = outcome_json.map(d => d.date);
    const passedData = outcome_json.map(d => d.passed);
    const failedData = outcome_json.map(d => d.failed);

    const ctx3 = document.getElementById('interactionsChart3');
    new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: labels3,
            datasets: [
                {
                    label: 'Passed',
                    data: passedData,
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Failed',
                    data: failedData,
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Detailed tables for Users/Websites
async function showUsers() {
    const token = localStorage.getItem('captcha_token')
    const response = await fetch(`${API_BASE}/stats-admin/total-users-data`,{
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await response.json();
    console.log(data);
    const detailsEl = document.getElementById('detailsTable');
    let html = `<h3>User Details</h3><table><thead><tr>
        <th>Email</th><th>Username</th><th>City</th>
        <th>Region</th><th>IP Address</th><th>Country</th>
    </tr></thead><tbody>`;
    data.forEach(res => {
        html += `<tr>
            <td>${res.email}</td><td>${res.username}</td><td>${res.city}</td>
            <td>${res.region}</td><td>${res.ip}</td><td>${res.country}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    detailsEl.innerHTML = html;
}

async function showWebsites() {

    const token = localStorage.getItem('captcha_token');
    const response = await fetch(`${API_BASE}/stats-admin/total-websites-data`,{
        headers : {"Authorization" : `Bearer ${token}`}
    })

    const res = await response.json();
    console.log(res);

    const detailsEl = document.getElementById('detailsTable');
    let html = `<h3>Registered Websites</h3><table><thead><tr>
        <th>Username</th><th>Website URL</th><th>Website Name</th>
    </tr></thead><tbody>`;
    res.forEach(site => {
        html += `<tr>
            <td>${site.username}</td><td>${site.website_url}</td><td>${site.website_name}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    detailsEl.innerHTML = html;
}

// Initialize dashboard
window.onload = async function() {
    updateCards();
    initCharts();
};

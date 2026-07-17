const API_BASE = '/api';

const statusColors = {
    'healthy': '#10b981',
    'degraded': '#f59e0b',
    'critical': '#ef4444'
};

async function fetchDashboardSummary() {
    try {
        const response = await fetch(`${API_BASE}/system/dashboard-summary`);
        const data = await response.json();
        renderSummary(data);
        updateStatusIndicator(data);
    } catch (error) {
        console.error('Error fetching summary:', error);
    }
}

function renderSummary(data) {
    const html = `
        <div class="summary-card">
            <div class="summary-card-label">Total Transactions Today</div>
            <div class="summary-card-value">${data.total_transactions_today.toLocaleString()}</div>
            <div class="summary-card-subtext">24-hour period</div>
        </div>
        <div class="summary-card">
            <div class="summary-card-label">Success Rate</div>
            <div class="summary-card-value">${data.successful_rate.toFixed(1)}%</div>
            <div class="summary-card-subtext" style="color: ${data.successful_rate > 95 ? '#10b981' : data.successful_rate > 90 ? '#f59e0b' : '#ef4444'}">
                ${data.successful_rate > 95 ? '✓ Excellent' : data.successful_rate > 90 ? '⚠ Good' : '✗ Poor'}
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-card-label">Avg Latency</div>
            <div class="summary-card-value">${data.avg_latency_ms.toFixed(0)}ms</div>
            <div class="summary-card-subtext">P99: ${data.p99_latency_ms.toFixed(0)}ms</div>
        </div>
        <div class="summary-card">
            <div class="summary-card-label">Active Merchants</div>
            <div class="summary-card-value">${data.active_merchants}</div>
            <div class="summary-card-subtext">Processing transactions</div>
        </div>
        <div class="summary-card">
            <div class="summary-card-label">Unresolved Anomalies</div>
            <div class="summary-card-value" style="color: ${data.unresolved_anomalies > 0 ? '#ef4444' : '#10b981'}">
                ${data.unresolved_anomalies}
            </div>
            <div class="summary-card-subtext">${data.unresolved_anomalies > 0 ? '⚠ Needs attention' : '✓ All clear'}</div>
        </div>
    `;
    document.getElementById('summaryGrid').innerHTML = html;
}

function updateStatusIndicator(data) {
    let status = 'healthy';
    if (data.successful_rate < 95) status = 'degraded';
    if (data.successful_rate < 85) status = 'critical';
    if (data.unresolved_anomalies > 5) status = 'critical';

    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    dot.className = `status-dot ${status}`;
    text.textContent = status.charAt(0).toUpperCase() + status.slice(1);
}

async function refreshTransactions() {
    try {
        const response = await fetch(`${API_BASE}/transactions/recent?limit=50`);
        const transactions = await response.json();
        renderTransactions(transactions);
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

function renderTransactions(transactions) {
    if (transactions.length === 0) {
        document.getElementById('transactionList').innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No transactions yet</p>';
        return;
    }

    const html = transactions.map(t => `
        <div class="transaction-item ${t.status.toLowerCase()}">
            <div class="transaction-cell">
                <div class="transaction-cell-label">ID</div>
                <div class="transaction-cell-value" title="${t.transaction_id}">${t.transaction_id.substring(0, 12)}...</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Merchant</div>
                <div class="transaction-cell-value">${t.merchant_id}</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Amount</div>
                <div class="transaction-cell-value">$${t.amount.toFixed(2)}</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Latency</div>
                <div class="transaction-cell-value">${t.latency_ms.toFixed(1)}ms</div>
            </div>
            <div style="text-align: center;">
                <span class="status-badge ${t.status.toLowerCase()}">${t.status}</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('transactionList').innerHTML = html;
}

async function refreshMerchants() {
    try {
        const response = await fetch(`${API_BASE}/merchants/?limit=100`);
        const merchants = await response.json();
        renderMerchants(merchants);
    } catch (error) {
        console.error('Error fetching merchants:', error);
    }
}

function renderMerchants(merchants) {
    if (merchants.length === 0) {
        document.getElementById('merchantGrid').innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No merchant data available</p>';
        return;
    }

    const html = merchants.map(m => `
        <div class="merchant-card">
            <div class="merchant-name">${m.merchant_name}</div>
            <div class="merchant-stat">
                <span class="merchant-stat-label">Total Transactions</span>
                <span class="merchant-stat-value">${m.total_transactions.toLocaleString()}</span>
            </div>
            <div class="merchant-stat">
                <span class="merchant-stat-label">Success Rate</span>
                <span class="merchant-stat-value" style="color: ${m.total_transactions > 0 ? '#10b981' : '#cbd5e1'}">
                    ${m.total_transactions > 0 ? ((m.successful_transactions / m.total_transactions) * 100).toFixed(1) : '0'}%
                </span>
            </div>
            <div class="merchant-stat">
                <span class="merchant-stat-label">Avg Latency</span>
                <span class="merchant-stat-value">${m.avg_latency_ms.toFixed(1)}ms</span>
            </div>
            <div class="merchant-stat">
                <span class="merchant-stat-label">Total Volume</span>
                <span class="merchant-stat-value">$${m.total_volume.toFixed(2)}</span>
            </div>
            <div class="merchant-stat">
                <span class="merchant-stat-label">Last Activity</span>
                <span class="merchant-stat-value">${new Date(m.last_activity).toLocaleTimeString()}</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('merchantGrid').innerHTML = html;
}

async function refreshAnomalies() {
    try {
        const response = await fetch(`${API_BASE}/system/dashboard-summary`);
        const summary = await response.json();
        
        if (summary.unresolved_anomalies === 0) {
            document.getElementById('anomalyList').innerHTML = '<p style="text-align: center; color: #10b981; padding: 40px 20px;">✓ No anomalies detected. System operating normally.</p>';
            return;
        }

        const anomalies = await fetch(`${API_BASE}/merchants/?limit=1`).then(r => r.json());
        renderAnomalies(anomalies);
    } catch (error) {
        console.error('Error fetching anomalies:', error);
    }
}

function renderAnomalies(anomalies) {
    const html = `
        <div class="anomaly-item critical">
            <div class="anomaly-type">Latency Spike</div>
            <div class="anomaly-desc">Transaction latency increased by 45% compared to baseline. P99 latency at 342ms.</div>
            <div class="anomaly-meta">
                <span>Severity: CRITICAL</span>
                <span>2 hours ago</span>
            </div>
        </div>
        <div class="anomaly-item high">
            <div class="anomaly-type">Error Rate Surge</div>
            <div class="anomaly-desc">Error rate increased from 2.1% to 5.3% in the last hour.</div>
            <div class="anomaly-meta">
                <span>Severity: HIGH</span>
                <span>45 minutes ago</span>
            </div>
        </div>
        <div class="anomaly-item">
            <div class="anomaly-type">Merchant Performance Degradation</div>
            <div class="anomaly-desc">Merchant tech_startup_001 experiencing 15% failure rate on transactions.</div>
            <div class="anomaly-meta">
                <span>Severity: MEDIUM</span>
                <span>30 minutes ago</span>
            </div>
        </div>
    `;
    
    document.getElementById('anomalyList').innerHTML = html;
}

async function refreshQueries() {
    try {
        const response = await fetch(`${API_BASE}/system/queries/slow?threshold_ms=50&limit=50`);
        const queries = await response.json();
        renderQueries(queries);
    } catch (error) {
        console.error('Error fetching queries:', error);
    }
}

function renderQueries(queries) {
    if (queries.length === 0) {
        document.getElementById('queryList').innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No slow queries detected</p>';
        return;
    }

    const html = queries.map((q, idx) => `
        <div class="transaction-item" style="border-left-color: ${q.execution_time_ms > 200 ? '#ef4444' : '#f59e0b'}">
            <div class="transaction-cell">
                <div class="transaction-cell-label">Query Hash</div>
                <div class="transaction-cell-value">${q.query_hash}</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Type</div>
                <div class="transaction-cell-value">${q.query_type}</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Execution Time</div>
                <div class="transaction-cell-value" style="color: ${q.execution_time_ms > 200 ? '#ef4444' : '#f59e0b'}">${q.execution_time_ms.toFixed(2)}ms</div>
            </div>
            <div class="transaction-cell">
                <div class="transaction-cell-label">Rows Affected</div>
                <div class="transaction-cell-value">${q.rows_affected.toLocaleString()}</div>
            </div>
            <div style="text-align: center;">
                <span class="status-badge ${q.execution_time_ms > 200 ? 'failed' : 'completed'}">${q.execution_time_ms > 100 ? 'SLOW' : 'OK'}</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('queryList').innerHTML = html;
}

async function refreshHealth() {
    try {
        const response = await fetch(`${API_BASE}/system/health`);
        const health = await response.json();
        renderHealth(health);
    } catch (error) {
        console.error('Error fetching health:', error);
    }
}

function renderHealth(health) {
    const html = `
        <div class="metric-row">
            <div class="metric-label">Total Transactions (1h)</div>
            <div class="metric-value">${health.total_transactions_hour.toLocaleString()}</div>
        </div>
        <div class="metric-row">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value" style="color: ${health.successful_rate > 95 ? '#10b981' : health.successful_rate > 90 ? '#f59e0b' : '#ef4444'}">
                ${health.successful_rate.toFixed(2)}%
            </div>
        </div>
        <div class="metric-row">
            <div class="metric-label">Average Latency</div>
            <div class="metric-value">${health.avg_latency_ms.toFixed(2)}ms</div>
        </div>
        <div class="metric-row">
            <div class="metric-label">P50 Latency</div>
            <div class="metric-value">${health.p50_latency_ms.toFixed(2)}ms</div>
        </div>
        <div class="metric-row">
            <div class="metric-label">P95 Latency</div>
            <div class="metric-value">${health.p95_latency_ms.toFixed(2)}ms</div>
        </div>
        <div class="metric-row">
            <div class="metric-label">P99 Latency</div>
            <div class="metric-value" style="color: ${health.p99_latency_ms > 300 ? '#ef4444' : '#f59e0b'}">${health.p99_latency_ms.toFixed(2)}ms</div>
        </div>
        <div class="metric-row">
            <div class="metric-label">System Status</div>
            <div class="metric-value" style="color: ${statusColors[health.status] || '#cbd5e1'}">
                ${health.status.toUpperCase()}
            </div>
        </div>
    `;
    
    document.getElementById('healthMetrics').innerHTML = html;
}

function setupTabNavigation() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            if (tabName === 'transactions') refreshTransactions();
            else if (tabName === 'merchants') refreshMerchants();
            else if (tabName === 'anomalies') refreshAnomalies();
            else if (tabName === 'performance') refreshQueries();
            else if (tabName === 'health') refreshHealth();
        });
    });
}

function startAutoRefresh() {
    fetchDashboardSummary();
    refreshTransactions();
    refreshMerchants();
    refreshAnomalies();
    refreshHealth();
    
    setInterval(fetchDashboardSummary, 10000);
    setInterval(refreshTransactions, 15000);
    setInterval(refreshMerchants, 30000);
    setInterval(refreshAnomalies, 20000);
    setInterval(refreshHealth, 10000);
}

document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    startAutoRefresh();
});

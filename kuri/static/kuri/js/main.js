// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
const CSRF_TOKEN = getCookie('csrftoken');

function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ---------------------------------------------------------------------------
// Sidebar toggle (mobile)
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 900 && sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Render server-side Django messages as toasts
  document.querySelectorAll('[data-server-message]').forEach((el) => {
    showToast(el.dataset.serverMessage, el.dataset.messageType || 'success');
  });

  // Generic modal open/close via data attributes
  document.querySelectorAll('[data-modal-target]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const modal = document.querySelector(btn.dataset.modalTarget);
      if (modal) modal.classList.add('open');
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach((btn) => {
    btn.addEventListener('click', () => {
      btn.closest('.modal-overlay').classList.remove('open');
    });
  });
  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
  });

  initTrackingGrid();
});

// ---------------------------------------------------------------------------
// 40-Month Tracking grid: click a cell to cycle its status via AJAX
// ---------------------------------------------------------------------------
const STATUS_CYCLE = ['paid', 'pending', 'overdue', 'future'];
const STATUS_LABEL_CLASS = {
  paid: 'cell-paid',
  pending: 'cell-pending',
  overdue: 'cell-overdue',
  future: 'cell-future',
};

function initTrackingGrid() {
  document.querySelectorAll('.tracking-table td.cell-status[data-payment-id]').forEach((cell) => {
    cell.addEventListener('click', () => cyclePaymentStatus(cell));
  });
}

function cyclePaymentStatus(cell) {
  const paymentId = cell.dataset.paymentId;
  const current = cell.dataset.status;
  const nextIndex = (STATUS_CYCLE.indexOf(current) + 1) % STATUS_CYCLE.length;
  const nextStatus = STATUS_CYCLE[nextIndex];

  fetch(`/payments/${paymentId}/ajax-update/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN,
    },
    body: JSON.stringify({ status: nextStatus }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (!data.ok) {
        showToast(data.error || 'Could not update payment', 'error');
        return;
      }
      cell.dataset.status = data.status;
      cell.className = `cell-status ${STATUS_LABEL_CLASS[data.status]}`;
      cell.textContent = data.status === 'paid' ? '✓' : data.status === 'future' ? '-' : '✗';

      const row = cell.closest('tr');
      if (row) {
        const paidEl = row.querySelector('[data-member-total-paid]');
        const pendingEl = row.querySelector('[data-member-total-pending]');
        const progressEl = row.querySelector('[data-member-progress]');
        if (paidEl) paidEl.textContent = '₹' + Number(data.member_total_paid).toLocaleString('en-IN');
        if (pendingEl) pendingEl.textContent = '₹' + Number(data.member_total_pending).toLocaleString('en-IN');
        if (progressEl) progressEl.style.width = data.member_progress + '%';
      }
      showToast(`Updated to ${data.status_label}`, 'success');
    })
    .catch(() => showToast('Network error while updating payment', 'error'));
}

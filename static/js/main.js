/**
 * MindBridge Interactive JavaScript
 * Supports Chat, Breathing Guide, Sensory Grounding, Mood Slider, and CSRF AJAX.
 *
 * v2 adds: a toast system, accessible confirmation dialogs, a theme manager,
 * password reveal + strength feedback, form loading states, and mobile chat drawer.
 */

(function () {
  'use strict';

  // Helper to get CSRF token from cookie or DOM
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken') ||
    (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '');

  window.getCookie = getCookie;
  window.csrftoken = csrftoken;

  /* =========================================================
   * Theme manager (light / dark / system)
   * ========================================================= */
  const THEME_KEY = 'mb-theme';
  const themeToggle = document.getElementById('themeToggle');

  function readStoredTheme() {
    try { return localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) { return 'auto'; }
  }

  function resolveTheme(theme) {
    if (theme === 'dark' || theme === 'light') return theme;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    const resolved = resolveTheme(theme);
    document.documentElement.setAttribute('data-bs-theme', resolved);
    if (themeToggle) {
      themeToggle.setAttribute('aria-label', resolved === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      themeToggle.setAttribute('title', resolved === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  function setTheme(theme) {
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* storage blocked */ }
    applyTheme(theme);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-bs-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // Follow the OS preference while the user has not chosen explicitly.
  if (window.matchMedia) {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = function () { if (readStoredTheme() === 'auto') applyTheme('auto'); };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  /* =========================================================
   * Toast system
   * ========================================================= */
  const TOAST_ICONS = {
    success: 'bi-check-circle-fill',
    danger: 'bi-exclamation-triangle-fill',
    warning: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill'
  };

  function toastStack() {
    let stack = document.getElementById('mbToastStack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'mbToastStack';
      stack.className = 'mb-toast-stack';
      stack.setAttribute('role', 'region');
      stack.setAttribute('aria-live', 'polite');
      stack.setAttribute('aria-label', 'Notifications');
      document.body.appendChild(stack);
    }
    return stack;
  }

  function mbToast(type, message, title, duration) {
    const kind = TOAST_ICONS[type] ? type : 'info';
    const stack = toastStack();

    const el = document.createElement('div');
    el.className = 'mb-toast mb-toast-' + kind;
    el.setAttribute('role', kind === 'danger' ? 'alert' : 'status');

    const icon = document.createElement('span');
    icon.className = 'mb-toast-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = '<i class="bi ' + TOAST_ICONS[kind] + '"></i>';

    const body = document.createElement('div');
    body.className = 'mb-toast-body';
    if (title) {
      const t = document.createElement('strong');
      t.className = 'mb-toast-title';
      t.textContent = title;
      body.appendChild(t);
    }
    const msg = document.createElement('span');
    msg.textContent = message;
    body.appendChild(msg);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'mb-toast-close';
    close.setAttribute('aria-label', 'Dismiss notification');
    close.innerHTML = '<i class="bi bi-x-lg" aria-hidden="true"></i>';

    el.appendChild(icon);
    el.appendChild(body);
    el.appendChild(close);
    stack.appendChild(el);

    let removed = false;
    function dismiss() {
      if (removed) return;
      removed = true;
      el.classList.add('is-leaving');
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 220);
    }

    close.addEventListener('click', dismiss);
    setTimeout(dismiss, duration || (kind === 'danger' ? 7000 : 4200));

    return { dismiss: dismiss, el: el };
  }

  window.mbToast = mbToast;

  /* =========================================================
   * Confirmation dialog (replaces native confirm())
   * ========================================================= */
  let confirmResolver = null;

  function confirmDialog(options) {
    const opts = options || {};
    const modalEl = document.getElementById('mbConfirmModal');
    if (!modalEl || !window.bootstrap) return Promise.resolve(window.confirm(opts.message || 'Are you sure?'));

    const titleEl = document.getElementById('mbConfirmTitle');
    const bodyEl = document.getElementById('mbConfirmBody');
    const iconEl = document.getElementById('mbConfirmIcon');
    const confirmBtn = document.getElementById('mbConfirmAccept');
    const cancelBtn = document.getElementById('mbConfirmCancel');

    titleEl.textContent = opts.title || 'Please confirm';
    bodyEl.textContent = opts.message || 'Are you sure you want to continue?';

    const variant = opts.variant === 'danger' ? 'danger' : 'primary';
    iconEl.className = 'confirm-icon is-' + variant;
    iconEl.innerHTML = '<i class="bi ' + (variant === 'danger' ? 'bi-exclamation-triangle-fill' : 'bi-question-circle-fill') + '"></i>';

    confirmBtn.textContent = opts.confirmText || 'Confirm';
    confirmBtn.className = 'btn ' + (variant === 'danger' ? 'btn-danger' : 'btn-primary-mb');
    cancelBtn.textContent = opts.cancelText || 'Cancel';

    const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);

    return new Promise(function (resolve) {
      function onHidden() {
        modalEl.removeEventListener('hidden.bs.modal', onHidden);
        confirmBtn.removeEventListener('click', onAccept);
        if (confirmResolver) { confirmResolver(null); confirmResolver = null; }
      }
      function onAccept() {
        modalEl.removeEventListener('hidden.bs.modal', onHidden);
        confirmBtn.removeEventListener('click', onAccept);
        modal.hide();
        if (confirmResolver) { confirmResolver(true); confirmResolver = null; }
      }
      confirmBtn.addEventListener('click', onAccept);
      modalEl.addEventListener('hidden.bs.modal', onHidden);
      confirmResolver = resolve;
      modal.show();
    });
  }

  window.mbConfirm = confirmDialog;

  /* =========================================================
   * Form enhancements: reveal password, strength meter, loading state
   * ========================================================= */
  function initPasswordToggles(root) {
    (root || document).querySelectorAll('[data-password-toggle]').forEach(function (btn) {
      if (btn.dataset.mbBound) return;
      btn.dataset.mbBound = '1';
      btn.addEventListener('click', function () {
        const input = btn.parentElement.querySelector('input');
        if (!input) return;
        const showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';
        btn.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
        btn.innerHTML = '<i class="bi ' + (showing ? 'bi-eye' : 'bi-eye-slash') + '" aria-hidden="true"></i>';
        input.focus();
      });
    });
  }

  function scorePassword(value) {
    if (!value) return 0;
    let score = 0;
    if (value.length >= 8) score++;
    if (value.length >= 12) score++;
    if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++;
    if (/\d/.test(value) || /[^A-Za-z0-9]/.test(value)) score++;
    return Math.min(score, 4);
  }

  function initPasswordStrength(root) {
    (root || document).querySelectorAll('[data-strength-for]').forEach(function (meter) {
      if (meter.dataset.mbBound) return;
      meter.dataset.mbBound = '1';
      const input = document.getElementById(meter.dataset.strengthFor);
      if (!input) return;
      const bar = meter.querySelector('.pw-strength-bar');
      const label = meter.querySelector('.pw-strength-label');
      const words = ['Too short', 'Weak', 'Fair', 'Good', 'Strong'];

      input.addEventListener('input', function () {
        const level = scorePassword(input.value);
        meter.dataset.level = String(level);
        if (bar) bar.style.width = (level / 4) * 100 + '%';
        if (label) label.textContent = input.value ? words[level] : words[0];
      });
    });
  }

  function initFormLoading(root) {
    (root || document).querySelectorAll('form[data-loading-label]').forEach(function (form) {
      if (form.dataset.mbBound) return;
      form.dataset.mbBound = '1';
      form.addEventListener('submit', function () {
        const btn = form.querySelector('button[type="submit"]');
        if (!btn || btn.dataset.mbBusy) return;
        btn.dataset.mbBusy = '1';
        btn.classList.add('is-loading');
        btn.setAttribute('aria-busy', 'true');
        const label = btn.dataset.loadingLabel || form.dataset.loadingLabel || 'Working…';
        const spinner = document.createElement('span');
        spinner.className = 'btn-spinner me-2';
        spinner.setAttribute('aria-hidden', 'true');
        const previous = btn.innerHTML;
        btn.dataset.mbPreviousHtml = previous;
        btn.innerHTML = '';
        btn.appendChild(spinner);
        btn.appendChild(document.createTextNode(label));
      });
    });
  }

  /* =========================================================
   * Copy to clipboard (shared by chat + resource cards)
   * ========================================================= */
  function copyToClipboard(btn, text) {
    const done = function () {
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i class="bi bi-check2" aria-hidden="true"></i> Copied';
      setTimeout(function () { btn.innerHTML = originalText; }, 2000);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function (err) {
        console.error('Could not copy text: ', err);
        mbToast('warning', 'Your browser blocked copying. Select the text and copy manually.');
      });
    } else {
      mbToast('warning', 'Your browser blocked copying. Select the text and copy manually.');
    }
  }
  window.copyToClipboard = copyToClipboard;

  /* =========================================================
   * Report message modal (chat)
   * ========================================================= */
  function openReportModal(messageId) {
    const modalElem = document.getElementById('reportMessageModal');
    if (modalElem && window.bootstrap) {
      document.getElementById('report_message_id').value = messageId;
      window.bootstrap.Modal.getOrCreateInstance(modalElem).show();
    }
  }
  window.openReportModal = openReportModal;

  function submitMessageReport() {
    const messageId = document.getElementById('report_message_id').value;
    const reason = document.getElementById('report_reason_input').value;
    const submitBtn = document.getElementById('submitReportBtn');

    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Sending…';

    fetch('/api/messages/' + messageId + '/report/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') || csrftoken || ''
      },
      body: JSON.stringify({ reason: reason })
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        mbToast('success', data.status || 'Report submitted. Thank you for keeping MindBridge safe.', 'Report received');
        const modalElem = document.getElementById('reportMessageModal');
        const modal = window.bootstrap.Modal.getInstance(modalElem);
        if (modal) modal.hide();
        document.getElementById('report_reason_input').value = '';
      })
      .catch(function (err) {
        console.error(err);
        mbToast('danger', 'Something went wrong while submitting your report. Please try again.');
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Submit Report';
      });
  }
  window.submitMessageReport = submitMessageReport;

  /* =========================================================
   * Destructive-action confirmations (data-confirm)
   * ========================================================= */
  function initConfirmForms(root) {
    (root || document).querySelectorAll('form[data-confirm]').forEach(function (form) {
      if (form.dataset.mbBound) return;
      form.dataset.mbBound = '1';

      const handler = function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        confirmDialog({
          title: form.dataset.confirmTitle || 'Please confirm',
          message: form.dataset.confirm,
          confirmText: form.dataset.confirmText || 'Yes, continue',
          variant: form.dataset.confirmVariant || 'danger'
        }).then(function (ok) {
          if (ok) {
            // Detach the guard and let the form submit natively.
            form.removeEventListener('submit', handler);
            form.submit();
          }
        });
      };

      form.addEventListener('submit', handler);
    });
  }

  /* =========================================================
   * Option cards (radio tiles)
   * ========================================================= */
  function initOptionCards(root) {
    (root || document).querySelectorAll('.option-card').forEach(function (card) {
      const input = card.querySelector('input');
      if (!input) return;

      function sync() {
        card.classList.toggle('is-selected', input.checked);
      }

      if (!input.dataset.mbBound) {
        input.dataset.mbBound = '1';
        input.addEventListener('change', sync);
      }
      sync();
    });
  }

  /* =========================================================
   * Back to top
   * ========================================================= */
  function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    let ticking = false;

    function update() {
      const y = window.scrollY || document.documentElement.scrollTop;
      btn.classList.toggle('is-visible', y > 500);
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    update();
  }

  /* =========================================================
   * Chat: mobile drawer + scroll to bottom
   * ========================================================= */
  function initChatDrawer() {
    const sidebar = document.getElementById('chatSidebar');
    const openBtn = document.getElementById('chatDrawerOpen');
    const closeBtn = document.getElementById('chatDrawerClose');
    const backdrop = document.getElementById('chatDrawerBackdrop');
    if (!sidebar) return;

    function setOpen(open) {
      sidebar.classList.toggle('is-open', open);
      if (backdrop) backdrop.classList.toggle('is-open', open);
      if (openBtn) openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      sidebar.setAttribute('aria-hidden', open ? 'false' : 'true');
      document.body.classList.toggle('chat-drawer-open', open);
    }

    if (openBtn) openBtn.addEventListener('click', function () { setOpen(!sidebar.classList.contains('is-open')); });
    if (closeBtn) closeBtn.addEventListener('click', function () { setOpen(false); });
    if (backdrop) backdrop.addEventListener('click', function () { setOpen(false); });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('is-open')) setOpen(false);
    });

    // Reset state when returning to the desktop layout.
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 768) setOpen(false);
    });
  }

  function initChatScroll() {
    const area = document.getElementById('chatMessagesArea');
    const btn = document.getElementById('chatScrollBottom');
    if (!area || !btn) return;
    let ticking = false;

    function update() {
      const distance = area.scrollHeight - area.scrollTop - area.clientHeight;
      btn.classList.toggle('is-visible', distance > 160);
      ticking = false;
    }

    area.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });

    btn.addEventListener('click', function () {
      area.scrollTo({ top: area.scrollHeight, behavior: 'smooth' });
    });
  }

  /* =========================================================
   * Mood slider display enhancer
   * ========================================================= */
  function initMoodSlider() {
    const stressSlider = document.getElementById('id_stress_level');
    const stressDisplay = document.getElementById('stressDisplay');
    if (stressSlider && stressDisplay) {
      const paint = function () {
        stressDisplay.textContent = this.value + ' / 10';
        const pct = ((this.value - this.min) / (this.max - this.min)) * 100;
        this.style.setProperty('--range-fill', pct + '%');
      };
      stressSlider.addEventListener('input', paint);
      paint.call(stressSlider);
    }
  }

  /* =========================================================
   * Mood sparkline (dependency-free inline SVG)
   * ========================================================= */
  function initMoodSpark() {
    document.querySelectorAll('[data-mood-spark]').forEach(function (el) {
      if (el.dataset.mbBound) return;
      el.dataset.mbBound = '1';

      const values = (el.dataset.values || '').split(',')
        .map(function (n) { return parseFloat(n); })
        .filter(function (n) { return !isNaN(n); });
      if (!values.length) return;

      const W = 720, H = 74, PAD = 8, MIN = 1, MAX = 5;
      const spanX = W - PAD * 2;
      const spanY = H - PAD * 2;

      const xAt = function (i) {
        // A single point is centred so the chart never looks empty.
        if (values.length === 1) return W / 2;
        return PAD + (i * spanX) / (values.length - 1);
      };
      const yAt = function (v) {
        const ratio = Math.max(0, Math.min(1, (v - MIN) / (MAX - MIN)));
        return H - PAD - ratio * spanY;
      };

      const pts = values.map(function (v, i) { return [xAt(i), yAt(v)]; });
      const line = values.length === 1
        ? 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1)
        : pts.map(function (p, i) {
            return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
          }).join(' ');
      const base = H - PAD;
      const area = values.length === 1
        ? 'M' + (pts[0][0] - 24) + ' ' + pts[0][1].toFixed(1) +
          ' L' + (pts[0][0] + 24) + ' ' + pts[0][1].toFixed(1) +
          ' L' + (pts[0][0] + 24) + ' ' + base + ' L' + (pts[0][0] - 24) + ' ' + base + ' Z'
        : line + ' L' + xAt(values.length - 1).toFixed(1) + ' ' + base +
          ' L' + xAt(0).toFixed(1) + ' ' + base + ' Z';

      const grid = [];
      for (let v = MIN; v <= MAX; v++) {
        grid.push('<line class="spark-grid" x1="' + PAD + '" y1="' + yAt(v).toFixed(1) +
                  '" x2="' + (W - PAD) + '" y2="' + yAt(v).toFixed(1) + '"></line>');
      }

      const dots = pts.map(function (p) {
        return '<circle class="spark-dot" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="4"></circle>';
      }).join('');

      el.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" ' +
        'style="width:100%;height:100%;display:block" aria-hidden="true">' +
        grid.join('') +
        '<path class="spark-area" d="' + area + '"></path>' +
        '<path class="spark-line" d="' + line + '" vector-effect="non-scaling-stroke"></path>' +
        dots + '</svg>';
    });
  }

  /* =========================================================
   * Breathing engine
   * ========================================================= */
  let breathingInterval = null;
  let breathingState = 0; // 0: Inhale, 1: Hold, 2: Exhale, 3: Hold
  let breathingTimer = 4;
  let isBreathingActive = false;

  function toggleBreathing() {
    const box = document.getElementById('breathingCircle');
    const label = document.getElementById('breathingLabel');
    const counter = document.getElementById('breathingCounter');
    const toggleBtn = document.getElementById('breathingToggleBtn');

    if (!box || !label || !counter) return;

    if (isBreathingActive) {
      clearInterval(breathingInterval);
      isBreathingActive = false;
      toggleBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Breathing';
      label.innerText = 'Ready';
      counter.innerText = '4';
      box.className = 'breathing-box';
      return;
    }

    isBreathingActive = true;
    toggleBtn.innerHTML = '<i class="bi bi-pause-fill"></i> Pause Exercise';
    breathingState = 0;
    breathingTimer = 4;

    const phases = [
      { name: 'Inhale Slowly...', class: 'breathing-box inhale' },
      { name: 'Gently Hold...', class: 'breathing-box hold' },
      { name: 'Exhale Smoothly...', class: 'breathing-box exhale' },
      { name: 'Rest & Be Still...', class: 'breathing-box' }
    ];

    function runCycle() {
      label.innerText = phases[breathingState].name;
      box.className = phases[breathingState].class;
      counter.innerText = breathingTimer;

      breathingTimer--;
      if (breathingTimer < 0) {
        breathingTimer = 4;
        breathingState = (breathingState + 1) % 4;
      }
    }

    runCycle();
    breathingInterval = setInterval(runCycle, 1000);
  }
  window.toggleBreathing = toggleBreathing;

  /* =========================================================
   * Bootstrap init + global wiring
   * ========================================================= */
  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(readStoredTheme());

    if (window.bootstrap) {
      // Enable Bootstrap's own tooltips where the markup opts in.
      document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new window.bootstrap.Tooltip(el);
      });
    }

    initPasswordToggles();
    initPasswordStrength();
    initFormLoading();
    initConfirmForms();
    initOptionCards();
    initBackToTop();
    initChatDrawer();
    initChatScroll();
    initMoodSlider();
    initMoodSpark();
  });
})();

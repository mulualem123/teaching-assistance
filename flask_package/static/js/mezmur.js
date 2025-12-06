// Global Variables
let playlistModal = null;
let currentPlayer = {
    playlistId: null,
    currentIndex: 0,
    audioElement: null,
    songs: []
};
let masonry = null;

// Centralized filter state store
let filterState = {
    q: '',        // search query
    tags: [],     // array of tag names (original case)
    op: 'or',     // 'or' or 'and'
    page: 1,
    perPage: 24
};

// Fuse.js index for fuzzy search (created lazily for moderate dataset sizes)
let fuse = null;
const FUSE_INDEX_LIMIT = 1500; // only index up to this many items on client to avoid memory/CPU overhead

function ensureFuseIndex() {
    if (fuse) return fuse;

    const cards = Array.from(document.querySelectorAll('.mezmur-card-container'));
    if (cards.length === 0 || cards.length > FUSE_INDEX_LIMIT) return null;

    const list = cards.map(card => {
        const id = card.getAttribute('data-m-id');
        const titleEl = card.querySelector('.card-title');
        const title = titleEl ? titleEl.textContent.trim() : '';
        const lyrics = card.dataset.lyrics || '';
        const tags = Array.from(card.querySelectorAll('.tag-pill')).map(t => t.textContent.trim());

        // store original text for highlighting
        if (!card.dataset.originalTitle) card.dataset.originalTitle = title;
        if (!card.dataset.originalLyrics) card.dataset.originalLyrics = lyrics;

        return { id, title, lyrics, tags };
    });

    try {
        fuse = new Fuse(list, {
            keys: [
                { name: 'title', weight: 0.7 },
                { name: 'tags', weight: 0.2 },
                { name: 'lyrics', weight: 0.1 }
            ],
            includeMatches: true,
            threshold: 0.35,
            ignoreLocation: true
        });
    } catch (e) {
        console.warn('Failed to build Fuse index', e);
        fuse = null;
    }

    return fuse;
}

function applyHighlights(query) {
    if (!query) return clearHighlights();

    // Use split words to highlight - safe approach and low cost
    const words = query.toString().trim().split(/\s+/).filter(w => w.length > 1).map(w => w.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
    if (!words.length) return clearHighlights();

    const regex = new RegExp(`(${words.join('|')})`, 'ig');

    document.querySelectorAll('.mezmur-card-container:not(.filtered-out)').forEach(card => {
        const titleEl = card.querySelector('.card-title');
        const lyricsEl = card.querySelector('label.preserve-line-breaks');

        const originalTitle = card.dataset.originalTitle || (titleEl ? titleEl.textContent : '');
        const originalLyrics = card.dataset.originalLyrics || (lyricsEl ? lyricsEl.textContent : '');

        if (titleEl) {
            titleEl.innerHTML = originalTitle.replace(regex, '<mark>$1</mark>');
        }
        if (lyricsEl) {
            // only highlight a short snippet (avoid huge replacements)
            const snippet = originalLyrics.length > 300 ? originalLyrics.slice(0, 300) + '...' : originalLyrics;
            lyricsEl.innerHTML = snippet.replace(regex, '<mark>$1</mark>');
        }
    });
}

function clearHighlights() {
    document.querySelectorAll('.mezmur-card-container').forEach(card => {
        const titleEl = card.querySelector('.card-title');
        const lyricsEl = card.querySelector('label.preserve-line-breaks');
        if (titleEl && card.dataset.originalTitle) titleEl.innerHTML = card.dataset.originalTitle;
        if (lyricsEl && card.dataset.originalLyrics) lyricsEl.innerHTML = card.dataset.originalLyrics;
    });
}

// Enhanced Toast System with better UX
function showToast(message, type = 'info', duration = 4000) {
    // Remove existing toasts of same type to prevent spam
    const existingToasts = document.querySelectorAll(`.toast-${type}`);
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show position-fixed`;
    
    // Enhanced styling and positioning
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1060;
        max-width: 350px;
        background: ${getToastColor(type)};
        color: white;
        padding: 12px 16px;
        font-size: 0.9rem;
        line-height: 1.4;
    `;
    
    // Add icon and close button
    toast.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center">
                <i class="bi ${getToastIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button class="btn-close btn-close-white ms-2" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.style.transform = 'translateX(0)', 10);
    
    // Auto-remove with fade out
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getToastColor(type) {
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#007bff'
    };
    return colors[type] || colors.info;
}

function getToastIcon(type) {
    const icons = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-x-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill'
    };
    return icons[type?.toLowerCase()] || icons.info;
}

// Masonry Initialization - Disabled for responsive Bootstrap grid
function initMasonry() {
    // Disable Masonry to allow Bootstrap responsive grid to work properly
    return null;
}

document.addEventListener('DOMContentLoaded', function() {
    // Ensure all elements are present before adding event listeners
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        // Update state then apply filtering (preserve debounce in filterMezmurs)
        searchInput.addEventListener('input', function() {
            updateStateFromUI();
            filterMezmurs();
        });
    } 
    // else {
    //     console.error('Search input not found.');
    // }

    // Add event listeners for both desktop and mobile tag checkboxes
    document.querySelectorAll('.tag-list .form-check-input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // central state will be updated and then applied to other UIs and filtering will run
            updateStateFromUI();
            applyStateToUI();
            filterMezmurs();
        });
    });

    // Mobile tag dropdown event listeners
    document.querySelectorAll('.mobile-tag-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateStateFromUI();
            applyStateToUI();
            updateMobileTagsDisplay();
            filterMezmurs();
        });
    });

    // Mobile swipe interface tag checkboxes
    document.querySelectorAll('.mobile-tag-checkbox-swipe').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateStateFromUI();
            applyStateToUI();
            filterMezmurs();
        });
    });

    // Mobile operator radio buttons
    document.querySelectorAll('input[name="mobileOperator"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // update state and apply
            updateStateFromUI();
            applyStateToUI();
            filterMezmurs();
        });
    });

    // Prevent dropdown from closing when clicking on checkboxes
    document.querySelectorAll('.mobile-tags-dropdown .form-check').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });

    // Operator change listeners
    document.querySelectorAll('input[name="operator"]').forEach(radio => {
        radio.addEventListener('change', function() {
            updateStateFromUI();
            applyStateToUI();
            filterMezmurs();
        });
    });
    
    // Initialize mobile swipe interface
    initMobileSwipe();
    
    // Initialize pull-to-refresh for mobile
    if (window.innerWidth < 992) {
        initPullToRefresh();
    }
    
    // Initialize keyboard navigation
    initKeyboardNavigation();
    
    // Initialize smart search
    initSmartSearch();
    
    // Initialize audio enhancements
    initAudioEnhancements();
    
    // Read filters from URL (if present) and apply to state + UI
    readFiltersFromURL();
    // Skip Masonry initialization - use Bootstrap grid instead
    filterMezmurs(); // Initial filter

    // Share current filter URL
    const shareBtn = document.getElementById('shareFilterBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(location.href);
                showToast('Filter link copied to clipboard', 'success');
            } catch (e) {
                // fallback
                const dummy = document.createElement('textarea');
                dummy.value = location.href;
                document.body.appendChild(dummy);
                dummy.select();
                document.execCommand('copy');
                dummy.remove();
                showToast('Filter link copied to clipboard', 'success');
            }
        });
    }

    // Save filter (if logged-in) - button in modal
    const confirmSaveBtn = document.getElementById('confirmSaveFilterBtn');
    if (confirmSaveBtn) {
        confirmSaveBtn.addEventListener('click', async () => {
            const nameInput = document.getElementById('savedFilterName');
            const name = nameInput ? nameInput.value.trim() : '';
            if (!name) return showToast('Please give a name to save this filter', 'warning');

            // send to server
            try {
                    const isPublicCheckbox = document.getElementById('saveFilterIsPublic');
                    const payload = { name, q: filterState.q || '', tags: filterState.tags || [], op: filterState.op || 'or', is_public: !!(isPublicCheckbox && isPublicCheckbox.checked) };
                const res = await fetch('/api/saved_filters', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    // try to extract server message to show to user
                    let err = {};
                    try { err = await res.json(); } catch (e) { /* ignore */ }
                    const msg = err && err.message ? err.message : `Save failed (${res.status})`;
                    if (res.status === 401) {
                        showToast('Please log in to save filters', 'warning');
                        // close modal if open
                        const modal = bootstrap.Modal.getInstance(document.getElementById('saveFilterModal'));
                        if (modal) modal.hide();
                        // redirect to login preserving next
                        const next = encodeURIComponent(location.pathname + location.search);
                        window.location.href = `/login?next=${next}`;
                        return;
                    }
                    throw new Error(msg);
                }

                showToast('Filters saved', 'success');
                // close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('saveFilterModal'));
                if (modal) modal.hide();
            } catch (err) {
                console.error('Save filter error', err);
                showToast('Failed to save filters', 'error');
            }
        });
    }

    // When saved-filters modal is shown, load the saved filters list
    const savedFiltersModalEl = document.getElementById('savedFiltersListModal');
    if (savedFiltersModalEl) {
        savedFiltersModalEl.addEventListener('show.bs.modal', loadSavedFiltersIntoModal);
    }

    // Ensure Save / ViewSaved buttons redirect unauthenticated users to login
    const saveBtn = document.getElementById('saveFilterBtn');
    if (saveBtn && saveBtn.getAttribute('data-auth') === '0') {
        saveBtn.addEventListener('click', () => {
            // redirect to login preserving current url
            const next = encodeURIComponent(location.pathname + location.search);
            window.location.href = `/login?next=${next}`;
        });
    }

    const viewSavedBtn = document.getElementById('viewSavedFiltersBtn');
    if (viewSavedBtn && viewSavedBtn.getAttribute('data-auth') === '0') {
        viewSavedBtn.addEventListener('click', () => {
            const next = encodeURIComponent(location.pathname + location.search);
            window.location.href = `/login?next=${next}`;
        });
    }
});

// Read filters from URL and apply to UI (search input + tag checkboxes + operator)
function readFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q') || '';
    const tagsParam = params.get('tags') || '';
    const op = params.get('op') || 'or';

    let tags;
    // update central state
    filterState.q = q;
    filterState.tags = tags;
    filterState.op = op;

    // apply into UI controls
    applyStateToUI();

    // split tags
    tags = tagsParam ? tagsParam.split(',').map(t => t.trim()).filter(Boolean) : [];

    // apply tag selections across the three UIs
    // desktop
    document.querySelectorAll('.tag-list .form-check-input').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });
    // mobile dropdown
    document.querySelectorAll('.mobile-tag-checkbox').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });
    // mobile swipe
    document.querySelectorAll('.mobile-tag-checkbox-swipe').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });

    // apply operator
    if (op === 'and') {
        document.getElementById('operatorAnd')?.setAttribute('checked', '');
        document.getElementById('mobileOperatorAnd')?.setAttribute('checked', '');
        document.getElementById('operatorOr')?.removeAttribute('checked');
        document.getElementById('mobileOperatorOr')?.removeAttribute('checked');
    } else {
        document.getElementById('operatorOr')?.setAttribute('checked', '');
        document.getElementById('mobileOperatorOr')?.setAttribute('checked', '');
        document.getElementById('operatorAnd')?.removeAttribute('checked');
        document.getElementById('mobileOperatorAnd')?.removeAttribute('checked');
    }

    // update mobile displays
    updateMobileTagsDisplay();
    // keep synced swipe controls in sync
    syncOthersToMobileSwipe();
}

// Persist filters in the URL (and push to history)
function pushFiltersToURL() {
    const q = filterState.q?.trim() || '';
    const selectedTags = Array.isArray(filterState.tags) ? filterState.tags : [];
    const op = (filterState.op === 'and') ? 'and' : 'or';

    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (selectedTags.length) params.set('tags', selectedTags.join(','));
    if (op) params.set('op', op);

    const url = `${location.pathname}?${params.toString()}`;
    history.pushState({ q, tags: selectedTags, op }, '', url);
}

// Read DOM inputs, update filterState accordingly
function updateStateFromUI() {
    const searchInput = document.getElementById('searchInput');
    filterState.q = searchInput ? searchInput.value.trim() : '';

    // read tags from any UI (unify)
    const desktop = Array.from(document.querySelectorAll('.tag-list input:checked')).map(cb => cb.value.trim());
    const mobile = Array.from(document.querySelectorAll('.mobile-tag-checkbox:checked')).map(cb => cb.value.trim());
    const swipe = Array.from(document.querySelectorAll('.mobile-tag-checkbox-swipe:checked')).map(cb => cb.value.trim());

    const union = [...new Set([...(desktop || []), ...(mobile || []), ...(swipe || [])])];
    filterState.tags = union;

    // operator
    const opRadio = document.querySelector('input[name="operator"]:checked') || document.querySelector('input[name="mobileOperator"]:checked');
    if (opRadio) {
        filterState.op = opRadio.id?.toLowerCase().includes('and') ? 'and' : 'or';
    }

    // reset paging when filters change
    filterState.page = 1;
    // Update action buttons visibility when state changes
    try { updateActionButtonsVisibility(); } catch (e) { /* ignore in older contexts */ }
}

// Apply state to the UI elements (input, checkboxes, radios)
function applyStateToUI() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = filterState.q || '';

    const tags = Array.isArray(filterState.tags) ? filterState.tags : [];

    document.querySelectorAll('.tag-list .form-check-input').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });
    document.querySelectorAll('.mobile-tag-checkbox').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });
    document.querySelectorAll('.mobile-tag-checkbox-swipe').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });

    if ((filterState.op || 'or') === 'and') {
        document.getElementById('operatorAnd')?.setAttribute('checked', '');
        document.getElementById('mobileOperatorAnd')?.setAttribute('checked', '');
        document.getElementById('operatorOr')?.removeAttribute('checked');
        document.getElementById('mobileOperatorOr')?.removeAttribute('checked');
    } else {
        document.getElementById('operatorOr')?.setAttribute('checked', '');
        document.getElementById('mobileOperatorOr')?.setAttribute('checked', '');
        document.getElementById('operatorAnd')?.removeAttribute('checked');
        document.getElementById('mobileOperatorAnd')?.removeAttribute('checked');
    }

    // update mobile count text
    updateMobileTagsDisplay();
    // Update action buttons visibility when UI is updated from state
    try { updateActionButtonsVisibility(); } catch (e) { /* ignore in older contexts */ }
}

// Handle back/forward navigation for URL-based filters
window.addEventListener('popstate', (event) => {
    // When the user navigates via back/forward, re-read the URL and apply filters
    readFiltersFromURL();
    filterMezmurs();
});

// Enhanced Search with Smart Suggestions
function initSmartSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    let searchTimeout;
    const searchSuggestions = document.createElement('div');
    searchSuggestions.className = 'search-suggestions position-absolute w-100';
    searchSuggestions.style.cssText = `
        top: 100%;
        left: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 8px 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
    `;
    
    searchInput.parentElement.style.position = 'relative';
    searchInput.parentElement.appendChild(searchSuggestions);
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchSuggestions.style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            generateSearchSuggestions(query, searchSuggestions);
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.parentElement.contains(e.target)) {
            searchSuggestions.style.display = 'none';
        }
    });
}

function generateSearchSuggestions(query, container) {
    const f = ensureFuseIndex();
    const suggestions = new Set();

    if (f) {
        const results = f.search(query, { limit: 8 });
        results.forEach(r => {
            // Try to pick the first matching word or tag
            const item = r.item;
            if (item.title && item.title.toLowerCase().includes(query.toLowerCase())) {
                suggestions.add(query);
            }
            if (Array.isArray(item.tags)) {
                item.tags.forEach(t => { if (t.toLowerCase().includes(query.toLowerCase())) suggestions.add(t); });
            }
        });
    }

    // Fallback to lightweight DOM scan if fuse not available
    if (!suggestions.size) {
        const allMezmurs = Array.from(document.querySelectorAll('.mezmur-card-container'));
        allMezmurs.forEach(card => {
            const title = card.querySelector('.card-title')?.textContent || '';
            const tags = Array.from(card.querySelectorAll('.tag-pill')).map(tag => tag.textContent);
            const titleWords = title.toLowerCase().split(' ').filter(word => word.includes(query.toLowerCase()) && word.length > 2);
            titleWords.forEach(word => suggestions.add(word));
            tags.forEach(tag => { if (tag.toLowerCase().includes(query.toLowerCase())) suggestions.add(tag); });
        });
    }

    const suggestionArray = Array.from(suggestions).slice(0, 6);

    if (suggestionArray.length > 0) {
        container.innerHTML = suggestionArray.map(suggestion => `
            <div class="suggestion-item px-3 py-2 cursor-pointer" onclick="selectSuggestion('${suggestion}')">
                <i class="bi bi-search me-2 text-muted"></i>${suggestion}
            </div>
        `).join('');
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = suggestion;
    document.querySelector('.search-suggestions').style.display = 'none';
    filterMezmurs();
}

// Filter Functionality
async function filterMezmurs() {
    // Use centralized state
    const searchTerm = (filterState.q || '').trim().toLowerCase();
    
    // Get selected tags from desktop, mobile dropdown, and mobile swipe checkboxes
    // We collect original-case values for the server API, but use lower-case for local matching
    const desktopTags = Array.isArray(filterState.tags) ? filterState.tags.slice() : [];
    // mobile and swipe inputs are kept in sync via applyStateToUI — their current state mirrors filterState
    const mobileTags = [];
    const swipeTags = [];
    
    // Combine all sets of selected tags
    const selectedTags = [...new Set([...desktopTags, ...mobileTags, ...swipeTags])];
    // For local matching, use lowercase
    const selectedTagsLower = selectedTags.map(t => t.toLowerCase());
    
    // Operator is stored in filterState.op ('and' or 'or')
    const operator = filterState.op === 'and' ? 'operatorAnd' : 'operatorOr';

    // Prefer server-side filtered results (scalable). If API fails, fall back to local DOM filtering.
    try {
        const params = new URLSearchParams();
        if (filterState.q) params.set('q', filterState.q);
        if (selectedTags.length) params.set('tags', selectedTags.join(','));
        params.set('op', filterState.op === 'and' ? 'and' : 'or');
        // Request a large perPage so we get all matching IDs in one call for existing DOM
        params.set('perPage', '10000');

        const res = await fetch(`/api/mezmurs?${params.toString()}`);
        if (res.ok) {
            const data = await res.json();
            if (data && Array.isArray(data.items)) {
                const allowed = new Set(data.items.map(i => String(i.m_id)));
                document.querySelectorAll('.mezmur-card-container').forEach(card => {
                    const mid = card.getAttribute('data-m-id');
                    card.classList.toggle('filtered-out', !allowed.has(mid));
                });
                // Update URL and chips
                // make url match filterState and render chips
                pushFiltersToURL();
                renderActiveFilterChips();
                return; // done
            }
        }
    } catch (err) {
        // network or API error -> fallback to local filtering
        console.warn('Server-side filter failed, falling back to client-side filter', err);
    }

    // Local DOM-based filter fallback
    document.querySelectorAll('.mezmur-card-container').forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const tags = Array.from(card.querySelectorAll('.tag-pill'))
            .map(tag => tag.textContent.trim().toLowerCase());
        const lyrics = card.dataset.lyrics?.toLowerCase() || '';

        const matchesSearch = title.includes(searchTerm) || 
                            (searchTerm.length > 2 && lyrics.includes(searchTerm));
        const matchesTags = selectedTagsLower.length === 0 || 
            (filterState.op === 'and' ? 
                selectedTagsLower.every(tag => tags.includes(tag)) : 
                selectedTagsLower.some(tag => tags.includes(tag)));

        card.classList.toggle('filtered-out', !(matchesSearch && matchesTags));
    });

    // Update URL and active filter chips
    pushFiltersToURL();
    renderActiveFilterChips();
    applyHighlights(filterState.q);
}

// Render active filter chips UI and wire chip removal
function renderActiveFilterChips() {
    const container = document.getElementById('activeFiltersContainer');
    if (!container) return;

    // Use centralized store for chips
    const q = filterState.q || '';
    const tags = Array.isArray(filterState.tags) ? filterState.tags : [];
    const operator = filterState.op === 'and' ? 'AND' : 'OR';

    const chips = [];
    if (q) chips.push({ type: 'q', label: `"${q}"`, value: q });
    tags.forEach(t => chips.push({ type: 'tag', label: t, value: t }));

    // build html
    container.innerHTML = '';
    if (chips.length === 0) {
        container.classList.add('d-none');
        try { updateActionButtonsVisibility(); } catch (e) { /* ignore */ }
        return;
    }

    container.classList.remove('d-none');

    const info = document.createElement('div');
    info.className = 'mb-2 d-flex align-items-center gap-2 flex-wrap';

    // Operator indicator
    const opBadge = document.createElement('span');
    opBadge.className = 'badge bg-secondary small';
    opBadge.textContent = `Mode: ${operator}`;
    info.appendChild(opBadge);

    chips.forEach(chip => {
        const el = document.createElement('span');
        el.className = 'badge bg-primary text-white me-1 mb-1 active-filter-chip';
        el.style.cursor = 'pointer';
        el.setAttribute('data-filter-type', chip.type);
        el.setAttribute('data-filter-value', chip.value);
        el.innerHTML = `${chip.label} <i class="bi bi-x ms-1"></i>`;
        el.setAttribute('role','button');
        el.setAttribute('aria-label', `Remove filter ${chip.label}`);
        el.setAttribute('tabindex','0');
        el.addEventListener('click', () => removeFilterChip(chip.type, chip.value));
        el.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'Delete' || e.key === 'Backspace') {
                e.preventDefault();
                removeFilterChip(chip.type, chip.value);
            }
        });
        info.appendChild(el);
    });

    const clearBtn = document.createElement('button');
    clearBtn.className = 'btn btn-sm btn-outline-secondary ms-auto';
    clearBtn.textContent = 'Clear all filters';
    clearBtn.addEventListener('click', () => clearAllFilters());
    info.appendChild(clearBtn);

    container.appendChild(info);
    // Ensure action buttons reflect the presence of filters/chips
    try { updateActionButtonsVisibility(); } catch (e) { /* ignore */ }
}

// Update tag UI showing counts and disabling tags with zero results
function updateTagCounts(facets) {
    if (!Array.isArray(facets)) return;

    // facets: [{name, count}]
    // Update desktop list
    document.querySelectorAll('.tag-list .form-check').forEach(el => {
        const input = el.querySelector('input.form-check-input');
        const label = el.querySelector('label.form-check-label');
        if (!input || !label) return;
        const tag = input.value;
        const f = facets.find(x => x.name === tag) || { count: 0 };

        // add or update a small count badge
        let badge = el.querySelector('.tag-count-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'tag-count-badge ms-2 text-muted small';
            label.appendChild(badge);
        }
        badge.textContent = `(${f.count})`;

        // disable if count is zero and tag not currently selected
        if (f.count === 0 && !input.checked) {
            input.disabled = true;
            el.classList.add('disabled');
            input.setAttribute('aria-disabled', 'true');
        } else {
            input.disabled = false;
            el.classList.remove('disabled');
            input.removeAttribute('aria-disabled');
        }
    });

    // mobile dropdown
    document.querySelectorAll('.mobile-tags-dropdown .form-check').forEach(el => {
        const input = el.querySelector('input.mobile-tag-checkbox');
        const label = el.querySelector('label.form-check-label');
        if (!input || !label) return;
        const tag = input.value;
        const f = facets.find(x => x.name === tag) || { count: 0 };
        let badge = label.querySelector('.tag-count-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'tag-count-badge ms-2 text-muted small';
            label.appendChild(badge);
        }
        badge.textContent = `(${f.count})`;

        if (f.count === 0 && !input.checked) {
            input.disabled = true;
            el.classList.add('disabled');
            input.setAttribute('aria-disabled', 'true');
        } else {
            input.disabled = false;
            el.classList.remove('disabled');
            input.removeAttribute('aria-disabled');
        }
    });

    // mobile swipe list
    document.querySelectorAll('.tag-list-mobile .form-check').forEach(el => {
        const input = el.querySelector('input.mobile-tag-checkbox-swipe');
        const label = el.querySelector('label.form-check-label');
        if (!input || !label) return;
        const tag = input.value;
        const f = facets.find(x => x.name === tag) || { count: 0 };
        let badge = label.querySelector('.tag-count-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'tag-count-badge ms-2 text-muted small';
            label.appendChild(badge);
        }
        badge.textContent = `(${f.count})`;

        if (f.count === 0 && !input.checked) {
            input.disabled = true;
            el.classList.add('disabled');
            input.setAttribute('aria-disabled', 'true');
        } else {
            input.disabled = false;
            el.classList.remove('disabled');
            input.removeAttribute('aria-disabled');
        }
    });
}

// Compute tag counts locally (fallback) by simulating current search and operator
function computeLocalTagCounts() {
    // gather all tags
    const allTagInputs = Array.from(document.querySelectorAll('.tag-list .form-check-input'));
    if (!allTagInputs.length) return;

    // base matching sets: current search (filterState.q)
    const q = (filterState.q || '').toLowerCase();

    // precompute for each card the set of tags it has and whether it matches search
    const cards = Array.from(document.querySelectorAll('.mezmur-card-container'));
    const cardData = cards.map(card => {
        const id = card.getAttribute('data-m-id');
        const title = card.querySelector('.card-title')?.textContent?.toLowerCase() || '';
        const lyrics = card.dataset.lyrics?.toLowerCase() || '';
        const tags = Array.from(card.querySelectorAll('.tag-pill')).map(t => t.textContent.trim());
        const matchesSearch = (!q) || title.includes(q) || (q.length > 2 && lyrics.includes(q));
        return { id, tags, matchesSearch };
    });

    allTagInputs.forEach(input => {
        const tag = input.value;
        // effective tags = filterState.tags + [tag] (unique)
        const effectiveTags = [...new Set([...(filterState.tags || []), tag])];
        let count = 0;

        cardData.forEach(cd => {
            if (!cd.matchesSearch) return;

            if (filterState.op === 'and') {
                // card must have all effectiveTags
                const hasAll = effectiveTags.every(t => cd.tags.map(x => x.toLowerCase()).includes(t.toLowerCase()));
                if (hasAll) count++;
            } else {
                // or: card must have any of effectiveTags
                if (effectiveTags.some(t => cd.tags.map(x => x.toLowerCase()).includes(t.toLowerCase()))) count++;
            }
        });

        // update UI element for this tag similar to updateTagCounts
        const el = document.querySelector(`.tag-list .form-check input[value="${CSS.escape(tag)}"]`)?.closest('.form-check');
        if (el) {
            let badge = el.querySelector('.tag-count-badge');
            if (!badge) {
                const label = el.querySelector('label.form-check-label');
                badge = document.createElement('span');
                badge.className = 'tag-count-badge ms-2 text-muted small';
                label.appendChild(badge);
            }
            badge.textContent = `(${count})`;

            if (count === 0 && !(filterState.tags || []).includes(tag)) {
                const inputEl = el.querySelector('.form-check-input');
                inputEl.disabled = true;
                el.classList.add('disabled');
                inputEl.setAttribute('aria-disabled', 'true');
            } else {
                const inputEl = el.querySelector('.form-check-input');
                inputEl.disabled = false;
                el.classList.remove('disabled');
                inputEl.removeAttribute('aria-disabled');
            }
        }
    });
}

function removeFilterChip(type, value) {
    if (type === 'q') {
        filterState.q = '';
    } else if (type === 'tag') {
        filterState.tags = (filterState.tags || []).filter(t => t !== value);
    }

    // apply state to UI and run filter
    applyStateToUI();
    filterMezmurs();
}

function clearAllFilters() {
    // reset central state
    filterState.q = '';
    filterState.tags = [];
    filterState.op = 'or';
    filterState.page = 1;

    applyStateToUI();
    filterMezmurs();
}

// Mobile Tag Dropdown Functionality
function updateMobileTagsDisplay() {
    const selectedCheckboxes = document.querySelectorAll('.mobile-tag-checkbox:checked');
    const selectedTagsTextElement = document.getElementById('selectedTagsText');
    
    if (!selectedTagsTextElement) return;

    if (selectedCheckboxes.length === 0) {
        selectedTagsTextElement.textContent = 'Select Tags';
        selectedTagsTextElement.classList.add('text-muted');
    } else if (selectedCheckboxes.length === 1) {
        selectedTagsTextElement.textContent = selectedCheckboxes[0].value;
        selectedTagsTextElement.classList.remove('text-muted');
    } else {
        selectedTagsTextElement.textContent = `${selectedCheckboxes.length} tags selected`;
        selectedTagsTextElement.classList.remove('text-muted');
    }
}


function syncTagSelections() {
    // Legacy function - now calls the specific sync functions
    syncMobileToDesktop();
    updateMobileTagsDisplay();
    filterMezmurs();
}

function clearAllTags() {
    // Clear all mobile checkboxes
    document.querySelectorAll('.mobile-tag-checkbox').forEach(cb => {
        cb.checked = false;
    });
    
    // Clear all desktop checkboxes
    document.querySelectorAll('.tag-list .form-check-input').forEach(cb => {
        cb.checked = false;
    });
    
    // Clear mobile swipe checkboxes
    document.querySelectorAll('.mobile-tag-checkbox-swipe').forEach(cb => {
        cb.checked = false;
    });
    
    // Update display and apply filters
    updateMobileTagsDisplay();
    filterMezmurs();
}

function clearAllTagsMobile() {
    // Clear all tag checkboxes from mobile swipe interface
    document.querySelectorAll('.mobile-tag-checkbox-swipe').forEach(cb => {
        cb.checked = false;
    });
    
    // Sync with desktop and dropdown
    syncMobileSwipeToOthers();
    filterMezmurs();
}

// Mobile Pull-to-Refresh
function initPullToRefresh() {
    let startY = 0;
    let pullDistance = 0;
    const pullThreshold = 80;
    
    const mainContent = document.querySelector('.container-fluid');
    if (!mainContent) return;
    
    let refreshIndicator = document.createElement('div');
    refreshIndicator.className = 'pull-refresh-indicator';
    refreshIndicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Pull to refresh';
    refreshIndicator.style.cssText = `
        position: fixed;
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        background: #007bff;
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        z-index: 1060;
        transition: top 0.3s ease;
    `;
    document.body.appendChild(refreshIndicator);
    
    mainContent.addEventListener('touchstart', (e) => {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
        }
    });
    
    mainContent.addEventListener('touchmove', (e) => {
        if (startY > 0 && window.scrollY === 0) {
            pullDistance = e.touches[0].clientY - startY;
            if (pullDistance > 0) {
                e.preventDefault();
                refreshIndicator.style.top = Math.min(pullDistance - 60, 20) + 'px';
                
                if (pullDistance >= pullThreshold) {
                    refreshIndicator.innerHTML = '<i class="bi bi-check-circle"></i> Release to refresh';
                    refreshIndicator.style.background = '#28a745';
                }
            }
        }
    });
    
    mainContent.addEventListener('touchend', () => {
        if (pullDistance >= pullThreshold) {
            refreshIndicator.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Refreshing...';
            setTimeout(() => location.reload(), 500);
        } else {
            refreshIndicator.style.top = '-60px';
        }
        startY = 0;
        pullDistance = 0;
    });
}

// Mobile Swipe Interface Functions
function initMobileSwipe() {
    const wrapper = document.getElementById('mobileSwipeWrapper');
    const indicators = document.querySelectorAll('.indicator');
    
    if (!wrapper || !indicators.length) return;
    
    let currentSlide = 0;
    
    // Handle indicator clicks
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentSlide = index;
            scrollToSlide(currentSlide);
            updateIndicators(currentSlide);
        });
    });
    
    // Handle scroll events
    wrapper.addEventListener('scroll', () => {
        const slideWidth = wrapper.offsetWidth;
        const newSlide = Math.round(wrapper.scrollLeft / slideWidth);
        if (newSlide !== currentSlide) {
            currentSlide = newSlide;
            updateIndicators(currentSlide);
        }
    });
    
    function scrollToSlide(slideIndex) {
        const slideWidth = wrapper.offsetWidth;
        wrapper.scrollTo({
            left: slideIndex * slideWidth,
            behavior: 'smooth'
        });
    }
    
    function updateIndicators(activeIndex) {
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === activeIndex);
        });
    }
    
    // Add touch support for better mobile experience
    let startX = 0;
    let startY = 0;
    let isDragging = false;
    
    wrapper.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isDragging = false;
    });
    
    wrapper.addEventListener('touchmove', (e) => {
        if (!startX || !startY) return;
        
        const deltaX = Math.abs(e.touches[0].clientX - startX);
        const deltaY = Math.abs(e.touches[0].clientY - startY);
        
        // Improved touch sensitivity and haptic feedback
        if (deltaX > deltaY && deltaX > 20) { // Minimum swipe distance
            isDragging = true;
            e.preventDefault();
            
            // Add haptic feedback for supported devices
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        }
    });
    
    wrapper.addEventListener('touchend', () => {
        startX = 0;
        startY = 0;
        isDragging = false;
    });
}

// Sync functions for mobile swipe interface
function syncMobileSwipeToOthers() {
    const swipeCheckboxes = document.querySelectorAll('.mobile-tag-checkbox-swipe');
    const desktopCheckboxes = document.querySelectorAll('.tag-list .form-check-input');
    const dropdownCheckboxes = document.querySelectorAll('.mobile-tag-checkbox');
    
    swipeCheckboxes.forEach((swipeCheckbox, index) => {
        if (desktopCheckboxes[index]) {
            desktopCheckboxes[index].checked = swipeCheckbox.checked;
        }
        if (dropdownCheckboxes[index]) {
            dropdownCheckboxes[index].checked = swipeCheckbox.checked;
        }
    });
    
    updateMobileTagsDisplay();
}

function syncOthersToMobileSwipe() {
    const desktopCheckboxes = document.querySelectorAll('.tag-list .form-check-input');
    const swipeCheckboxes = document.querySelectorAll('.mobile-tag-checkbox-swipe');
    
    desktopCheckboxes.forEach((desktopCheckbox, index) => {
        if (swipeCheckboxes[index]) {
            swipeCheckboxes[index].checked = desktopCheckbox.checked;
        }
    });
}

// Keyboard Navigation for Accessibility
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Only handle when not in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        switch(e.key) {
            case 'f':
            case 'F':
                if (e.ctrlKey || e.metaKey) return; // Don't interfere with Ctrl+F
                e.preventDefault();
                document.getElementById('searchInput')?.focus();
                break;
                
            case 'n':
            case 'N':
                if (e.ctrlKey || e.metaKey) return;
                e.preventDefault();
                document.querySelector('[data-bs-target="#createPlaylistModal"]')?.click();
                break;
                
            case 'Escape':
                // Close any open modals
                document.querySelectorAll('.modal.show').forEach(modal => {
                    bootstrap.Modal.getInstance(modal)?.hide();
                });
                // Close sidebar on mobile
                document.querySelector('.playlist-sidebar')?.classList.remove('active');
                break;
                
            case 'ArrowLeft':
            case 'ArrowRight':
                // Navigate mobile swipe interface
                if (window.innerWidth < 992) {
                    const wrapper = document.getElementById('mobileSwipeWrapper');
                    if (wrapper) {
                        const currentSlide = Math.round(wrapper.scrollLeft / wrapper.offsetWidth);
                        const nextSlide = e.key === 'ArrowLeft' ? 
                            Math.max(0, currentSlide - 1) : 
                            Math.min(2, currentSlide + 1);
                        
                        wrapper.scrollTo({
                            left: nextSlide * wrapper.offsetWidth,
                            behavior: 'smooth'
                        });
                        
                        // Update indicators
                        document.querySelectorAll('.indicator').forEach((indicator, index) => {
                            indicator.classList.toggle('active', index === nextSlide);
                        });
                    }
                }
                break;
        }
    });
    
    // Add visual focus indicators
    document.querySelectorAll('.mezmur-card, .playlist-card').forEach(card => {
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

// Consolidated sync functions to handle all tag interfaces
function syncMobileToDesktop() {
    // Sync mobile checkboxes with desktop checkboxes and swipe interface
    const mobileCheckboxes = document.querySelectorAll('.mobile-tag-checkbox');
    const desktopCheckboxes = document.querySelectorAll('.tag-list .form-check-input');
    const swipeCheckboxes = document.querySelectorAll('.mobile-tag-checkbox-swipe');
    
    mobileCheckboxes.forEach((mobileCheckbox, index) => {
        if (desktopCheckboxes[index]) {
            desktopCheckboxes[index].checked = mobileCheckbox.checked;
        }
        if (swipeCheckboxes[index]) {
            swipeCheckboxes[index].checked = mobileCheckbox.checked;
        }
    });
}

function syncDesktopToMobile() {
    // Sync desktop checkboxes with mobile checkboxes and swipe interface
    const desktopCheckboxes = document.querySelectorAll('.tag-list .form-check-input');
    const mobileCheckboxes = document.querySelectorAll('.mobile-tag-checkbox');
    const swipeCheckboxes = document.querySelectorAll('.mobile-tag-checkbox-swipe');
    
    desktopCheckboxes.forEach((desktopCheckbox, index) => {
        if (mobileCheckboxes[index]) {
            mobileCheckboxes[index].checked = desktopCheckbox.checked;
        }
        if (swipeCheckboxes[index]) {
            swipeCheckboxes[index].checked = desktopCheckbox.checked;
        }
    });
    
    updateMobileTagsDisplay();
}

// Playlist Management
// Toggle sidebar on mobile
function toggleSidebar() {
    document.querySelector('.playlist-sidebar').classList.toggle('active');
}

// Loading state management
function showLoadingSpinner(element, text = 'Loading...') {
    if (!element) return;
    
    element.disabled = true;
    const originalHTML = element.innerHTML;
    element.dataset.originalHtml = originalHTML;
    
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        ${text}
    `;
}

function hideLoadingSpinner(element) {
    if (!element || !element.dataset.originalHtml) return;
    
    element.disabled = false;
    element.innerHTML = element.dataset.originalHtml;
    delete element.dataset.originalHtml;
}

async function loadPlaylist(playlistId, forceReload = false) {
    const loadButton = document.querySelector(`[onclick="loadPlaylist(${playlistId})"]`);
    
    try {
        showLoadingSpinner(loadButton, 'Opening...');
        
        const response = await fetch(`/api/playlists/${playlistId}${forceReload ? '?t=' + Date.now() : ''}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error(`Playlist not found. It may have been deleted or you don't have access.`);
            } else if (response.status === 403) {
                throw new Error(`Access denied. Please make sure you're logged in and own this playlist.`);
            } else if (response.status === 401) {
                throw new Error(`Please log in to access your playlists.`);
            } else {
                throw new Error(`Failed to load playlist (Error ${response.status})`);
            }
        }

        const playlist = await response.json();
        
        if (playlist.status === 'error') {
            throw new Error(playlist.message || 'Failed to load playlist');
        }
        
        if (!playlist?.songs) {
            throw new Error('Invalid playlist data received from server');
        }
        
        console.log('Loaded playlist:', playlist.name, 'with', playlist.songs.length, 'songs');
        
        const songsContainer = document.getElementById('playlistSongs');
        
        // Update UI
        document.getElementById('playlistName').textContent = playlist.name;
        songsContainer.innerHTML = playlist.songs.map(song => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>${song.title}</div>
                <button class="btn btn-sm btn-outline-danger" 
                        data-remove-song data-playlist-id="${playlistId}" data-song-id="${song.id}">
                    Remove
                </button>
            </div>
        `).join('');

        // Initialize audio player state
        currentPlayer = {
            playlistId: playlistId,
            currentIndex: 0,
            audioElement: null,
            songs: playlist.songs.map(song => ({
                ...song,
                audio_url: song.audio_url || `/audio/${song.id}`
            }))
        };
        
        console.log('currentPlayer updated with', currentPlayer.songs.length, 'songs');

        playlistModal.show();
        playlistModal._element.addEventListener('shown.bs.modal', () => {
            // No longer need masonry layout
        });
        
        showToast(`Playlist "${playlist.name}" loaded successfully`, 'success');
    } catch (error) {
        console.error('Playlist loading error:', error);
        
        // Show culturally appropriate error handling
        showPlaylistErrorFallback(playlistId, error.message);
        
        // Also show toast for immediate feedback
        showToast(`ዝተመርሐ ዝማሬ ኣይተረኽበን: ${error.message}`, 'error');
    } finally {
        hideLoadingSpinner(loadButton);
    }
}

function showPlaylistErrorFallback(playlistId, errorMessage) {
    const playlistModal = bootstrap.Modal.getInstance(document.getElementById('playlistModal')) || 
                         new bootstrap.Modal(document.getElementById('playlistModal'));
    
    // Update modal content with Ethiopian Orthodox-inspired error UI
    document.getElementById('playlistName').innerHTML = `
        <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>
        ዝተመርሐ ዝማሬ ኣይተረኽበን
    `;
    
    const songsContainer = document.getElementById('playlistSongs');
    songsContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="mb-4">
                <i class="bi bi-music-note-beamed display-1 text-muted" style="font-size: 4rem;"></i>
            </div>
            <h4 class="text-muted mb-3">ዝተመርሐ ዝማሬ ኣይተረኽበን</h4>
            <p class="text-muted mb-4">${errorMessage}</p>
            
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6 class="card-title mb-3">
                                <i class="bi bi-lightbulb me-2 text-warning"></i>
                                እንታይ ክንገብር ንኽእል?
                            </h6>
                            <div class="list-group list-group-flush">
                                <button class="list-group-item list-group-item-action border-0 bg-transparent" 
                                        onclick="refreshPlaylistList()">
                                    <i class="bi bi-arrow-clockwise me-2 text-primary"></i>
                                    ዝማሬታት ዳግማይ ምጽዓን
                                </button>
                                <a href="/playlists" class="list-group-item list-group-item-action border-0 bg-transparent">
                                    <i class="bi bi-collection me-2 text-success"></i>
                                    ናይ ግዴል ዝማሬታት ምርኣይ
                                </a>
                                <button class="list-group-item list-group-item-action border-0 bg-transparent" 
                                        onclick="showPopularTags()">
                                    <i class="bi bi-tags me-2 text-info"></i>
                                    ተፈታውነ መውሰብታት ምርኣይ
                                </button>
                                <a href="/playlist/create" class="list-group-item list-group-item-action border-0 bg-transparent">
                                    <i class="bi bi-plus-circle me-2 text-warning"></i>
                                    ሓድሽ ዝማሬ ምፍጣር
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <small class="text-muted">
                    <i class="bi bi-info-circle me-1"></i>
                    ነዚ ጸገም ንምፍታሕ፡ ንድሕሪት ተመለስ ወይ ሓድሽ ዝማሬ መረጽ
                </small>
            </div>
        </div>
    `;
    
    playlistModal.show();
}

function refreshPlaylistList() {
    // Close the error modal
    const playlistModal = bootstrap.Modal.getInstance(document.getElementById('playlistModal'));
    if (playlistModal) {
        playlistModal.hide();
    }
    
    // Refresh the playlist section
    if (typeof loadPlaylistsPanel === 'function') {
        loadPlaylistsPanel();
    } else {
        // Fallback: reload the page
        window.location.reload();
    }
    
    showToast('ዝማሬታት እተሓዱ እዮም...', 'info');
}

// Load and render saved filters into the modal
async function loadSavedFiltersIntoModal() {
    const container = document.getElementById('savedFiltersListBody');
    if (!container) return;

    container.innerHTML = document.getElementById('savedFiltersLoading')?.outerHTML || '<p>Loading...</p>';

    try {
        const res = await fetch('/api/saved_filters');
        if (!res.ok) throw new Error('Failed to load');

        const items = await res.json();
        if (!Array.isArray(items) || items.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-bookmark-x display-4 text-muted"></i>
                    <p class="mt-3 text-muted">No saved filters yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(s => `
            <div class="card mb-2">
                <div class="card-body d-flex align-items-start justify-content-between gap-3">
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <h6 class="mb-1">${escapeHtml(s.name)}</h6>
                            <small class="text-muted">${s.created_at ? new Date(s.created_at).toLocaleString() : ''}</small>
                        </div>
                        <div class="small text-muted mb-2">${buildFilterSummary(s.query)}</div>
                        <div class="d-flex gap-2">
                            <button data-apply-id="${s.id}" aria-label="Apply saved filter ${escapeHtml(s.name)}" class="btn btn-sm btn-outline-primary apply-saved-filter">Apply</button>
                            <button data-delete-id="${s.id}" aria-label="Delete saved filter ${escapeHtml(s.name)}" class="btn btn-sm btn-outline-danger delete-saved-filter">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // attach handlers
        container.querySelectorAll('.apply-saved-filter').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = btn.getAttribute('data-apply-id');
                const item = items.find(it => String(it.id) === String(id));
                if (!item) return showToast('Saved filter not found', 'error');

                // apply state
                const payload = (typeof item.query === 'string') ? JSON.parse(item.query) : item.query || {};
                filterState.q = payload.q || '';
                filterState.tags = payload.tags || [];
                filterState.op = payload.op || 'or';

                applyStateToUI();
                pushFiltersToURL();
                filterMezmurs();

                // close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('savedFiltersListModal'));
                if (modal) modal.hide();
            });
        });

        container.querySelectorAll('.delete-saved-filter').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = btn.getAttribute('data-delete-id');
                if (!confirm('Delete this saved filter?')) return;
                try {
                    const res = await fetch(`/api/saved_filters/${id}`, { method: 'DELETE' });
                    if (!res.ok) throw new Error('Failed');
                    showToast('Saved filter deleted', 'success');
                    loadSavedFiltersIntoModal();
                } catch (err) {
                    console.error('Delete failed', err);
                    showToast('Failed to delete filter', 'error');
                }
            });
        });

    } catch (err) {
        console.error('Failed to load saved filters', err);
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-exclamation-triangle display-4 text-warning"></i>
                <p class="mt-3 text-muted">Could not load saved filters.</p>
            </div>
        `;
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function buildFilterSummary(qobj) {
    try {
        const obj = (typeof qobj === 'string') ? JSON.parse(qobj) : (qobj || {});
        const parts = [];
        if (obj.q) parts.push(`Search: "${escapeHtml(obj.q)}"`);
        if (obj.tags && obj.tags.length) parts.push(`Tags: ${escapeHtml(obj.tags.join(', '))}`);
        if (obj.op) parts.push(`Mode: ${obj.op.toUpperCase()}`);
        return parts.join(' • ');
    } catch (e) {
        return '';
    }
}

function showPopularTags() {
    // Close the error modal
    const playlistModal = bootstrap.Modal.getInstance(document.getElementById('playlistModal'));
    if (playlistModal) {
        playlistModal.hide();
    }
    
    // Show popular tags or scroll to tags section
    const tagsSection = document.querySelector('.tag-filters, .tags-section, [data-tags]');
    if (tagsSection) {
        tagsSection.scrollIntoView({ behavior: 'smooth' });
        showToast('ተፈታውነ መውሰብታት ተመርሒ', 'success');
    } else {
        // Fallback: show available tags
        showAvailableTagsModal();
    }
}

function showAvailableTagsModal() {
    // Create a modal to show available tags
    const existingModal = document.getElementById('tagsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const tagsModalHtml = `
        <div class="modal fade" id="tagsModal" tabindex="-1" aria-labelledby="tagsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="tagsModalLabel">
                            <i class="bi bi-tags me-2"></i>ተፈታውነ መውሰብታት
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">መውሰብታት እተጻዕኑ እዮም...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', tagsModalHtml);
    const tagsModal = new bootstrap.Modal(document.getElementById('tagsModal'));
    tagsModal.show();
    
    // Load tags data
    loadAvailableTags();
}

function loadAvailableTags() {
    fetch('/api/tags')
        .then(response => response.json())
        .then(tags => {
            const modalBody = document.querySelector('#tagsModal .modal-body');
            
            if (tags && tags.length > 0) {
                modalBody.innerHTML = `
                    <div class="row">
                        <div class="col-12 mb-3">
                            <p class="text-muted">ብመሰረት እዞም መውሰብታዊ ዝማሬታት ምረጽ:</p>
                        </div>
                        ${tags.map(tag => `
                            <div class="col-md-4 col-sm-6 mb-2">
                                <button class="btn btn-outline-primary btn-sm w-100" 
                                        onclick="filterByTag('${tag.name}')">
                                    <i class="bi bi-tag me-1"></i>${tag.name}
                                    <span class="badge bg-secondary ms-1">${tag.count || 0}</span>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <div class="text-center mt-4">
                        <button class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle me-1"></i>ዕጽወት
                        </button>
                    </div>
                `;
            } else {
                modalBody.innerHTML = `
                    <div class="text-center py-4">
                        <i class="bi bi-tags display-4 text-muted"></i>
                        <h5 class="mt-3 text-muted">መውሰብታት ኣይተረኽቡን</h5>
                        <p class="text-muted">ኣብዚ እዋን እዚ ዝምታሕ መውሰብታት ኣይብሉን።</p>
                        <button class="btn btn-primary" data-bs-dismiss="modal">
                            <i class="bi bi-arrow-left me-1"></i>ተመለስ
                        </button>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading tags:', error);
            const modalBody = document.querySelector('#tagsModal .modal-body');
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-exclamation-triangle display-4 text-warning"></i>
                    <h5 class="mt-3 text-muted">መውሰብታት ክጻዓኑ ኣይከኣሉን</h5>
                    <p class="text-muted">ተመሳሳሊ ጸገም ፍሰትን። ቀልጢፍካ እንደገና ፈርቂ።</p>
                    <button class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-circle me-1"></i>ዕጽወት
                    </button>
                </div>
            `;
        });
}

function filterByTag(tagName) {
    // Close the tags modal
    const tagsModal = bootstrap.Modal.getInstance(document.getElementById('tagsModal'));
    if (tagsModal) {
        tagsModal.hide();
    }
    
    // Apply the tag filter
    const searchInput = document.querySelector('input[name="search_term"], .search-input');
    if (searchInput) {
        searchInput.value = tagName;
        // Trigger search
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.submit();
        } else {
            // Manual search trigger
            performSearch(tagName);
        }
    } else {
        // Fallback: navigate to search with tag
        window.location.href = `/search?search_term=${encodeURIComponent(tagName)}`;
    }
    
    showToast(`"${tagName}" መውሰብታት ዝመሰሎም ዝማሬታት እተፍልዩ እዮም`, 'info');
}

function performSearch(searchTerm) {
    // This function should integrate with your existing search functionality
    // For now, we'll use a simple approach
    window.location.href = `/search?search_term=${encodeURIComponent(searchTerm)}`;
}

async function deletePlaylist(playlistId) {
    if (!confirm('Are you sure you want to delete this playlist?')) return;
    
    try {
        const response = await fetch(`/api/playlists/${playlistId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Failed to delete playlist');

        // Remove playlist card from both sidebar and shared section
        document.querySelectorAll(`[data-playlist-id="${playlistId}"]`).forEach(el => el.remove());

        if (playlistModal._element.classList.contains('show') && currentPlayer.playlistId === playlistId) {
            playlistModal.hide();
        }
        showToast('Playlist deleted successfully', 'success');
    } catch (error) {
        showToast(`Error deleting playlist: ${error.message}`, 'error');
    }
}
async function removeFromPlaylist(playlistId, songId) {
    try {
        const response = await fetch(`/api/playlists/${playlistId}/songs/${songId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        // Refresh the modal content without closing
        await loadPlaylist(playlistId, true);
        
        showToast('Song removed successfully', 'success');

    } catch (error) {
        showToast(`Error removing song: ${error.message}`, 'error');
    }
}

async function addToPlaylist(event, mezmurId, playlistId) {
    try {
        event.preventDefault();

        const response = await fetch(`/playlist/${playlistId}/add/${mezmurId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        loadInitialPlaylists();

        const result = await response.json();

        if (!response.ok) {
            throw new Error(`${result.status}: ${result.message}`);
        }

        if (!result.song || !result.song.title || !result.playlist || !result.playlist.name) {
            throw new Error('Invalid data received from the server');
        }

        showToast(`${result.song.title} added to ${result.playlist.name}`, 'success');

        // Update UI counters
        const badge = document.querySelector(`[data-playlist-id="${playlistId}"] .badge`);
        if (badge) {
            badge.textContent = `${result.playlist.song_count} hymns`;
        }

        // Close the modal
        const modalId = `collectionsModal${mezmurId}`;
        const modalElement = document.getElementById(modalId);

        // Correctly get the existing modal instance to hide it.
        // Do not create a new one if it doesn't exist.
        if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    } catch (error) {
        showToast(error.message, 'error');
        console.error('Playlist Error:', error);
    }
}

async function toggleSharePlaylist(playlistId, buttonElement) {
    try {
        const response = await fetch(`/api/playlist/${playlistId}/share`, {
            method: 'POST'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message);
        }

        showToast(result.message, 'success');

        // A simple page reload is the easiest way to update the shared list and button text.
        location.reload();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function loadInitialPlaylists() {
    try {
        const response = await fetch('/api/playlists');
        const playlists = await response.json();
        refreshPlaylistSidebar(playlists);
    } catch (error) {
        console.error('Failed to load playlists:', error);
        showToast('Failed to load playlists', 'error');
    }
}
// Function to refresh the sidebar
function refreshPlaylistSidebar(playlists) {
    const sidebar = document.querySelector('.playlist-sidebar .playlist-list');
    sidebar.innerHTML = ''; // Clear existing content

    playlists.forEach(playlist => {
        const playlistCard = document.createElement('div');
        playlistCard.className = 'playlist-card';
        playlistCard.dataset.playlistId = playlist.id;
        playlistCard.innerHTML = `
            <div class="card-body"
                 data-playlist-id="${ playlist.id }"
                 onclick="loadPlaylist(${ playlist.id })" 
                 style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-start">
                    <!-- Playlist Info -->
                    <div class="flex-grow-1">
                        <h5 class="mb-1">${ playlist.name }</h5>
                        <p class="text-muted small mb-0">${ playlist.description }</p>
                        <span class="badge bg-secondary">${playlist.song_count} hymns</span>
                    </div>
                    <!-- Three-dot Menu -->
                    <div class="dropdown ms-2" onclick="event.stopPropagation()">
                        <button class="btn btn-link p-0 text-muted" 
                                type="button" 
                                data-bs-toggle="dropdown">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <!-- Open Button -->
                            <li>
                                <button class="dropdown-item" 
                                        data-load-playlist
                                        onclick="loadPlaylist(${ playlist.id })"  
                                        data-playlist-id="${ playlist.id }">
                                    <i class="bi bi-folder2-open me-2"></i>Open
                                </button>
                            </li>                           
                            <!-- Delete Option -->
                            <li>
                                <button class="dropdown-item text-danger" 
                                        onclick="event.stopPropagation(); deletePlaylist(${ playlist.id })">
                                    <i class="bi bi-trash me-2"></i>Delete
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        `;  
        sidebar.appendChild(playlistCard);
    });
}
// Font Size Adjustment for Modals
const FONT_STEP = 1; // Adjust font size by 1px per click
const MIN_FONT_SIZE = 10; // Minimum font size in pixels
const MAX_FONT_SIZE = 28; // Maximum font size in pixels

function adjustModalFontSize(buttonElement, direction) {
    const modal = buttonElement.closest('.modal'); // Find the parent modal
    if (!modal) {
        console.error("Could not find parent modal for font size adjustment.");
        return;
    }

    const lyricElements = modal.querySelectorAll('.modal-lyrics-content'); // Find lyrics within this specific modal
    if (!lyricElements || lyricElements.length === 0) {
        console.warn("No elements with class 'modal-lyrics-content' found in this modal.");
        return;
    }

    lyricElements.forEach(element => {
        const currentSizeStyle = window.getComputedStyle(element, null).getPropertyValue('font-size');
        let currentSize = parseFloat(currentSizeStyle); // Get current size in pixels

        if (isNaN(currentSize)) {
            console.error("Could not parse current font size:", currentSizeStyle);
            currentSize = 16; // Default to 16px if parsing fails
        }

        let newSize;
        if (direction === 'increase') {
            newSize = Math.min(currentSize + FONT_STEP, MAX_FONT_SIZE);
        } else if (direction === 'decrease') {
            newSize = Math.max(currentSize - FONT_STEP, MIN_FONT_SIZE);
        } else {
            return; // Invalid direction
        }

        element.style.fontSize = `${newSize}px`;
    });
}

// Enhanced Audio Management with better error handling
function initAudioEnhancements() {
    // Global audio session management
    let globalAudioSession = null;
    
    // Add global audio error handler
    document.addEventListener('error', (e) => {
        if (e.target.tagName === 'AUDIO') {
            console.warn('Audio loading failed:', e.target.src);
            showToast('Audio file not available for this hymn', 'warning', 3000);
            
            // Hide the audio element or show a placeholder
            e.target.style.display = 'none';
            
            // Add a fallback message
            const fallbackMsg = document.createElement('div');
            fallbackMsg.className = 'audio-fallback text-muted small';
            fallbackMsg.innerHTML = '<i class="bi bi-volume-x me-1"></i>Audio not available';
            e.target.parentNode.insertBefore(fallbackMsg, e.target.nextSibling);
        }
    }, true);
    
    // Enhanced audio element creation with error handling
    function createAudioElement(audioUrl, songTitle) {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.preload = 'metadata';
        audio.className = 'audio-player w-100';
        
        // Add error handling
        audio.addEventListener('error', function(e) {
            console.error(`Audio error for "${songTitle}":`, e);
            this.style.display = 'none';
            
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-warning mt-2';
            errorMsg.innerHTML = `
                <i class="bi bi-exclamation-triangle me-2"></i>
                Audio not available for "${songTitle}"
            `;
            this.parentNode.insertBefore(errorMsg, this.nextSibling);
        });
        
        // Add loading state
        audio.addEventListener('loadstart', function() {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'audio-loading text-muted small';
            loadingIndicator.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Loading audio...';
            this.parentNode.insertBefore(loadingIndicator, this);
        });
        
        audio.addEventListener('canplay', function() {
            const loadingIndicator = this.parentNode.querySelector('.audio-loading');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        });
        
        if (audioUrl && audioUrl !== 'null' && !audioUrl.includes('/audio/NA')) {
            audio.src = audioUrl;
        } else {
            // Don't set src for invalid URLs
            audio.style.display = 'none';
            return null;
        }
        
        return audio;
    }
    
    // Preload next audio in playlists
    function preloadNextAudio(currentIndex, songs) {
        if (currentIndex + 1 < songs.length) {
            const nextSong = songs[currentIndex + 1];
            if (nextSong.audio_url && nextSong.audio_url !== 'null') {
                const preloadAudio = new Audio();
                preloadAudio.preload = 'metadata';
                preloadAudio.src = nextSong.audio_url;
            }
        }
    }
    
    // Enhanced audio player with better error handling
    function createEnhancedAudioPlayer(audioUrl, onLoad, onError) {
        const audio = new Audio();
        audio.preload = 'metadata';
        
        // Add loading state
        const loadingPromise = new Promise((resolve, reject) => {
            audio.addEventListener('loadedmetadata', () => {
                resolve(audio);
                if (onLoad) onLoad(audio);
            });
            
            audio.addEventListener('error', (e) => {
                const errorMsg = `Failed to load audio: ${e.target.error?.message || 'Unknown error'}`;
                reject(new Error(errorMsg));
                if (onError) onError(errorMsg);
            });
            
            // Timeout for slow connections
            setTimeout(() => {
                if (audio.readyState === 0) {
                    reject(new Error('Audio loading timeout'));
                }
            }, 10000);
        });
        
        audio.src = audioUrl;
        return { audio, loadingPromise };
    }
    
    // Media session API for better mobile control
    if ('mediaSession' in navigator) {
        function updateMediaSession(songTitle, artist = 'Ethiopian Orthodox Hymns') {
            navigator.mediaSession.metadata = new MediaMetadata({
                title: songTitle,
                artist: artist,
                album: 'Teaching Assistance Collection',
                artwork: [
                    { src: '/static/logo.png', sizes: '96x96', type: 'image/png' }
                ]
            });
        }
        
        // Set up media session action handlers
        navigator.mediaSession.setActionHandler('play', () => {
            if (currentPlayer.audioElement) {
                currentPlayer.audioElement.play();
            }
        });
        
        navigator.mediaSession.setActionHandler('pause', () => {
            if (currentPlayer.audioElement) {
                currentPlayer.audioElement.pause();
            }
        });
        
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            skipToNextSong();
        });
        
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            if (currentPlayer.currentIndex > 0) {
                currentPlayer.currentIndex -= 2; // Will be incremented in playNextSong
                playNextSong();
            }
        });
    }
    
    return { preloadNextAudio, createEnhancedAudioPlayer };
}

function playAll() {
    console.log('Play All clicked');
    
    // Check if the playlist modal is actually visible (playlist is loaded)
    const playlistModal = document.getElementById('playlistModal');
    if (!playlistModal || !playlistModal.classList.contains('show')) {
        showToast('Please open a playlist first before playing.', 'warning');
        return;
    }
    
    // Check if playlist is loaded
    if (!currentPlayer.playlistId) {
        showToast('No playlist loaded. Please open a playlist first.', 'warning');
        return;
    }
    
    // Check if playlist has songs
    if (!currentPlayer.songs || currentPlayer.songs.length === 0) {
        console.log('No songs found in currentPlayer.songs');
        showToast('This playlist is empty. Add some songs to start playing.', 'info');
        return;
    }

    console.log('Starting playback with', currentPlayer.songs.length, 'songs in playlist');
    showToast(`Starting playlist: ${currentPlayer.songs.length} songs`, 'success');

    // Stop and remove any existing audio element to ensure a fresh start
    if (currentPlayer.audioElement) {
        currentPlayer.audioElement.pause();
        // Remove listeners before removing element
        currentPlayer.audioElement.onended = null;
        currentPlayer.audioElement.onerror = null;
        currentPlayer.audioElement.ontimeupdate = null;
        currentPlayer.audioElement.onloadedmetadata = null;
        currentPlayer.audioElement.remove();
        currentPlayer.audioElement = null; // Nullify the reference
        console.log("Removed previous audio element for Play All.");
    }

    // Reset index and start playback from the beginning
    currentPlayer.currentIndex = -1; // Set to -1 so skipToNextSong starts correctly at 0
    skipToNextSong(); // Use skipToNextSong to initialize and play the first song
}


function highlightCurrentSong(index) {
    document.querySelectorAll('#playlistSongs .list-group-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
}

// Share Functionality
function generateShareLink(playlistId) {
    return `${window.location.origin}/playlist/shared/${playlistId}`;
}

function copyShareLink() {
    const shareInput = document.getElementById('shareLink');
    shareInput.select();
    document.execCommand('copy');
    showToast('Link copied to clipboard', 'success');
}

function shareOnFacebook() {
    const url = encodeURIComponent(generateShareLink(currentPlayer.playlistId));
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
}

function shareOnTwitter() {
    const url = encodeURIComponent(generateShareLink(currentPlayer.playlistId));
    const text = encodeURIComponent(`Check out this spiritual playlist: ${document.getElementById('playlistName').textContent}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
}

function shareOnWhatsApp() {
    const url = encodeURIComponent(generateShareLink(currentPlayer.playlistId));
    const text = encodeURIComponent(`Check out this spiritual playlist: ${document.getElementById('playlistName').textContent} - ${url}`);
    window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
}

// Lyrics Highlighting System
let currentLyrics = {
    geez: [],
    latin: [],
    english: []
};

function parseTimedLyrics(lyrics) {
    if (!lyrics) return [];
    return lyrics.split('\n').filter(line => line.trim()).map(line => {
        const match = line.match(/^\[(\d+:\d+)\]\s*(.*)/);
        return match ? {
            time: convertToSeconds(match[1]),
            text: match[2]
        } : { time: 0, text: line };
    });
}

function convertToSeconds(timeString) {
    const [minutes, seconds] = timeString.split(':').map(Number);
    return minutes * 60 + seconds;
}

function displayLyrics(lyrics, containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.error(`Lyrics container not found: #${containerId}`);
        return;
    }

    try {
        container.innerHTML = lyrics.map(line => 
            `<div class="lyric-line" data-time="${line.time}">${line.text}</div>`
        ).join('');
    } catch (error) {
        console.error('Error rendering lyrics:', error);
        showToast('Failed to display lyrics', 'error');
    }
}

function highlightLyrics(currentTime) {
    ['geez', 'latin', 'english'].forEach(lang => {
        const container = document.getElementById(`colap${lang.charAt(0).toUpperCase() + lang.slice(1)}`);
        if (!container) return;

        const lines = container.querySelectorAll('.lyric-line');
        let activeLine = null;

        lines.forEach(line => {
            const lineTime = parseFloat(line.dataset.time) || 0;
            const nextTime = line.nextElementSibling?.dataset.time || Infinity;
            
            line.classList.toggle('active', 
                currentTime >= lineTime && 
                currentTime < nextTime
            );
            
            if (line.classList.contains('active')) {
                activeLine = line;
            }
        });

        if (activeLine) {
            activeLine.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'nearest'
            });
        }
    });
}

// Replace the existing playNextSong function with this one
async function playNextSong() {
    try {
        // Check if playlist is valid and index is within bounds
        if (!currentPlayer.songs || currentPlayer.songs.length === 0) {
            showToast('Playlist is empty.', 'info');
            highlightCurrentSong(-1);
            
            // Safely hide lyrics controls if they exist
            const lyricsControls = document.getElementById('lyricsControls');
            if (lyricsControls) {
                lyricsControls.classList.add('d-none');
            }
            
            if (currentPlayer.audioElement) currentPlayer.audioElement.pause();
            return;
        }
        // Ensure index is valid after potential advancement/looping
        if (currentPlayer.currentIndex < 0 || currentPlayer.currentIndex >= currentPlayer.songs.length) {
             console.warn(`Invalid index ${currentPlayer.currentIndex}, resetting to 0.`);
             currentPlayer.currentIndex = 0;
             if (currentPlayer.songs.length === 0) { // Double check after reset
                 showToast('Playlist is empty.', 'info');
                 return;
             }
        }
 
        const song = currentPlayer.songs[currentPlayer.currentIndex];
        if (!song) {
            console.error(`No song data found for index: ${currentPlayer.currentIndex}`);
            showToast('Error: Could not load song data.', 'error');
            // Attempt to skip to the next valid one
            setTimeout(skipToNextSong, 500);
            return;
        }
 
        console.log(`Attempting to play song: ${song.title} at index ${currentPlayer.currentIndex}`);
 
        // --- Update Lyrics Display ---
        currentLyrics = {
            geez: parseTimedLyrics(song.timed_geez || song.lyrics || ''),
            latin: parseTimedLyrics(song.timed_latin || ''),
            english: parseTimedLyrics(song.timed_english || '')
        };
 
        ['geez', 'latin', 'english'].forEach(lang => {
            const containerId = `colap${lang.charAt(0).toUpperCase() + lang.slice(1)}`;
            const container = document.getElementById(containerId);
            if (container) container.innerHTML = ''; // Clear first
        });
 
        displayLyrics(currentLyrics.geez, 'colapGeez');
        displayLyrics(currentLyrics.latin, 'colapLatin');
        displayLyrics(currentLyrics.english, 'colapEnglish');
 
        highlightCurrentSong(currentPlayer.currentIndex);
        
        // Safely show lyrics controls if they exist
        const lyricsControls = document.getElementById('lyricsControls');
        if (lyricsControls) {
            lyricsControls.classList.remove('d-none');
        }
        // --- End Lyrics Update ---
 
 
        // --- Handle Audio ---
        // Ensure audio element exists and is in the DOM, create if necessary
        if (!currentPlayer.audioElement || !document.body.contains(currentPlayer.audioElement)) {
             if (currentPlayer.audioElement) currentPlayer.audioElement.remove(); // Clean up old one if detached
             console.log("Creating new Audio element");
             currentPlayer.audioElement = new Audio();
             currentPlayer.audioElement.controls = true;
             currentPlayer.audioElement.style.width = '100%';
             currentPlayer.audioElement.preload = "auto"; // Important for loading
             // Add the new audio element to the DOM *before* setting src
             document.getElementById('playlistSongs').prepend(currentPlayer.audioElement);
        }
 
        // Remove previous listeners before adding new ones
        currentPlayer.audioElement.onended = null;
        currentPlayer.audioElement.onerror = null;
        currentPlayer.audioElement.ontimeupdate = null;
        currentPlayer.audioElement.onloadedmetadata = null;
 
 
        if (song.audio_url && song.audio_url !== 'null' && song.audio_url.trim() !== '' && !song.audio_url.includes('/audio/NA')) {
            console.log(`Audio URL found: ${song.audio_url}`);
            currentPlayer.audioElement.src = song.audio_url;

            // Setup event listeners for the *current* track
            currentPlayer.audioElement.onloadedmetadata = () => {
                console.log(`Metadata loaded for: ${song.title}`);
            };
            currentPlayer.audioElement.ontimeupdate = () => {
                highlightLyrics(currentPlayer.audioElement.currentTime);
            };
            currentPlayer.audioElement.onended = () => {
                console.log(`Song ended: ${song.title}. Advancing.`);
                skipToNextSong(); // Use skip function for consistent advancement
            };
            currentPlayer.audioElement.onerror = (e) => {
                const errorMsg = e.target.error ? `Error ${e.target.error.code}: ${e.target.error.message}` : 'Audio file not found or corrupted';
                showToast(`Cannot play "${song.title}": ${errorMsg}`, 'error');
                console.error('Audio Element Error:', e.target.error);
                
                // Hide the broken audio element
                currentPlayer.audioElement.style.display = 'none';
                
                // Add fallback message
                const fallbackMsg = document.createElement('div');
                fallbackMsg.className = 'audio-fallback';
                fallbackMsg.innerHTML = `<i class="bi bi-volume-x me-2"></i>Audio not available for "${song.title}"`;
                currentPlayer.audioElement.parentNode.insertBefore(fallbackMsg, currentPlayer.audioElement.nextSibling);
                
                // Optionally skip to next song after a delay
                setTimeout(skipToNextSong, 2000);
            };            try {
                console.log(`Playing audio: ${song.title}`);
                await currentPlayer.audioElement.play();
                console.log(`Playback started for: ${song.title}`);
            } catch (playError) {
                console.error(`Error starting playback for ${song.title}:`, playError);
                showToast(`Could not play "${song.title}": ${playError.message}`, 'error');
                // Maybe skip if playback fails immediately?
                // setTimeout(skipToNextSong, 500);
            }
 
        } else {
            // --- No Audio Available ---
            console.log(`No audio URL for: ${song.title}`);
            showToast(`"${song.title}" has no audio. Skipping to next.`, 'info');
            
            // Ensure player is stopped if previous track had audio
            if (currentPlayer.audioElement && !currentPlayer.audioElement.paused) {
                currentPlayer.audioElement.pause();
            }
            
            // Clear src and hide audio controls
            if (currentPlayer.audioElement) {
                currentPlayer.audioElement.removeAttribute('src');
                currentPlayer.audioElement.style.display = 'none';
                
                // Add a message indicating no audio
                const noAudioMsg = document.createElement('div');
                noAudioMsg.className = 'audio-fallback';
                noAudioMsg.innerHTML = `<i class="bi bi-music-note-beamed me-2"></i>Lyrics only - no audio available for "${song.title}"`;
                // Avoid adding multiple messages
                const existingMsg = currentPlayer.audioElement.parentNode.querySelector('.audio-fallback');
                if (!existingMsg) {
                    currentPlayer.audioElement.parentNode.insertBefore(noAudioMsg, currentPlayer.audioElement.nextSibling);
                }
            }
            
            // Automatically skip to the next song after a short delay
            setTimeout(skipToNextSong, 1000); // 1 second delay
        }
        // --- End Audio Handling ---
 
    } catch (error) {
        showToast(`Playback error: ${error.message || 'Unknown error'}`, 'error');
        console.error('General Playback Error in playNextSong:', error);
        // Attempt to recover?
        // setTimeout(skipToNextSong, 1000);
    }
 }

// Add this new function
function skipToNextSong() {
    if (!currentPlayer.songs || currentPlayer.songs.length === 0) {
        showToast('Playlist is empty or not loaded.', 'warning');
        return;
    }

    console.log(`Skipping from index: ${currentPlayer.currentIndex}`);

    // Stop current playback forcefully
    if (currentPlayer.audioElement && !currentPlayer.audioElement.paused) {
        currentPlayer.audioElement.pause();
        // Remove event listeners to prevent potential conflicts from the stopped track
        currentPlayer.audioElement.onended = null;
        currentPlayer.audioElement.onerror = null;
        currentPlayer.audioElement.ontimeupdate = null;
        console.log('Paused current audio.');
    }

    // Advance index
    currentPlayer.currentIndex++;

    // Handle playlist wrap-around
    if (currentPlayer.currentIndex >= currentPlayer.songs.length) {
        currentPlayer.currentIndex = 0; // Loop back to the start
        showToast('Reached end of playlist, starting over.', 'info');
    }
    console.log(`Advanced to index: ${currentPlayer.currentIndex}`);

    // Play the song at the new index
    playNextSong(); // playNextSong uses the updated currentPlayer.currentIndex
}

// Event Handlers
function setupEventListeners() {
    // Filtering
    let filterTimeout;
    document.getElementById('searchInput').addEventListener('input', () => {
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(filterMezmurs, 300);
    });

    document.querySelectorAll('.tag-cloud input, input[name="operator"]').forEach(el => {
        el.addEventListener('change', () => {
            clearTimeout(filterTimeout);
            filterTimeout = setTimeout(filterMezmurs, 200);
        });
    });

    // Playlist Actions
    document.addEventListener('click', (e) => {
        // PRIORITY 1: Always allow shared playlist links to navigate naturally
        if (e.target.matches('a.shared-playlist-link') || 
            e.target.closest('a.shared-playlist-link') ||
            e.target.matches('a[href*="/playlist/shared/"]') || 
            e.target.closest('a[href*="/playlist/shared/"]')) {
            console.log('Allowing natural navigation for shared playlist link');
            // Let the browser handle the navigation naturally
            return true;
        }

        // PRIORITY 2: Skip any elements with data-no-intercept or shared playlist types
        if (e.target.hasAttribute('data-no-intercept') ||
            e.target.closest('[data-no-intercept]') ||
            (e.target.hasAttribute('data-playlist-type') && e.target.getAttribute('data-playlist-type') === 'shared') ||
            e.target.closest('[data-playlist-type="shared"]')) {
            console.log('Skipping JavaScript handling due to data-no-intercept or shared type');
            return true;
        }
        
        // PRIORITY 3: Handle shared playlist cards (but not their buttons/links)
        const sharedCard = e.target.closest('.shared-playlist-card') || e.target.closest('.shared-playlist-card-mobile');
        if (sharedCard && !e.target.closest('button') && !e.target.closest('a')) {
            const playlistId = sharedCard.dataset.sharedPlaylistId;
            if (playlistId) {
                console.log('Navigating to shared playlist from card click:', playlistId);
                window.location.href = `/playlist/shared/${playlistId}`;
                return false;
            }
        }
        
        // PRIORITY 4: Only handle data-load-playlist elements (user's own playlists)
        if (e.target.matches('[data-load-playlist]')) {
            e.preventDefault();
            console.log('Loading user playlist:', e.target.dataset.playlistId);
            loadPlaylist(e.target.dataset.playlistId);
            return false;
        }
        if (e.target.matches('[data-remove-song]')) {
            e.preventDefault();
            removeFromPlaylist(e.target.dataset.playlistId, e.target.dataset.songId);
            return false;
        }
        if(window.innerWidth < 1200 && 
            !e.target.closest('.playlist-sidebar') && 
            !e.target.closest('.sidebar-toggle')) {
             document.querySelector('.playlist-sidebar').classList.remove('active');
         }
    });

    // Modal Handling
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', () => {
            const audioElements = modal.querySelectorAll('audio');
            audioElements.forEach(audio => {
                audio.pause();
                audio.currentTime = 0; // Optional: Reset to the beginning
            });
        });
    });

    document.getElementById('playlistModal').addEventListener('hidden.bs.modal', () => {
        if (currentPlayer.audioElement) {
            currentPlayer.audioElement.pause();
            currentPlayer.audioElement.remove();
        }
        
        // Safely hide lyrics controls if they exist
        const lyricsControls = document.getElementById('lyricsControls');
        if (lyricsControls) {
            lyricsControls.classList.add('d-none');
        }
    });

    document.getElementById
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    playlistModal = new bootstrap.Modal(document.getElementById('playlistModal'));
    setupEventListeners();
    
    // Setup event listeners
    playlistModal._element.addEventListener('shown.bs.modal', () => {
        // Now we're sure modal DOM elements exist
        initMasonry();
        // Don't call setupEventListeners again to avoid duplicate listeners
    });

    document.addEventListener('show.bs.modal', (event) => {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            if (modal !== event.target) {
                bootstrap.Modal.getInstance(modal).hide();
            }
        });
    });

    loadInitialPlaylists()
    // Initial setup
    //filterMezmurs(); // Removed this line
    window.addEventListener('resize', () => {
        // No longer need masonry layout
        if(window.innerWidth >= 1200) {
            document.querySelector('.playlist-sidebar').classList.remove('active');
        }
    });

    var dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(function(dropdown) {
        var instance = new bootstrap.Dropdown(dropdown);
    });

    // Handle modal transition
    document.getElementById('createPlaylistModal').addEventListener('hidden.bs.modal', function() {
        const collectionModals = document.querySelectorAll('.modal[id^="collectionsModal"]');
        collectionModals.forEach(modal => {
            bootstrap.Modal.getInstance(modal).show();
        });
    });

    // Accessibility fix: Return focus to the body when any modal is closed.
    // This prevents the "aria-hidden" warning where focus gets trapped in a hidden modal.
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            // Set a brief timeout to ensure the modal is fully hidden before shifting focus.
            setTimeout(() => {
                document.body.focus();
            }, 10);
        });
    });
    
    // Initialize modals
    const mezmurModals = document.querySelectorAll('.mezmur-modal');
    mezmurModals.forEach(modal => {
        const audio = modal.querySelector('.audio-player');
        const lyricsContainer = modal.querySelector('.lyrics-container');
        
        modal.addEventListener('shown.bs.modal', () => {
            setupLyricsHighlighting(audio, lyricsContainer);
        });

        modal.addEventListener('hidden.bs.modal', () => {
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
        });
    });
    // No longer using Masonry - Bootstrap grid handles responsiveness
    filterMezmurs(); // Initial filter

});

// Add mezmur model handler
const addMezmurForm = document.getElementById('addMezmurForm');
if (addMezmurForm) {
    addMezmurForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);
        console.log("1")
        try {
            const response = await fetch('/add_mezmur', {
                method: 'POST',
                body: formData
            });
            console.log("2")
            if (!response.ok) {
                const errorData = await response.json();
                showToast(`Error: ${errorData.error || 'Failed to add Mezmur'}`, 'error');
                return; // Stop further execution if there's an error
            }
            console.log("3")
            const data = await response.json();
            console.log("4")
            showToast(data.message, 'success');
            // Optionally, reload the page or update the mezmur list
            console.log("5")
            event.target.reset(); // Clear the form
            console.log("6")
            document.getElementById('addMezmurModal').style.display = 'none';// Close the modal
            location.reload();
        } catch (error) {
            showToast(`Error: ${error.message}`, 'error');
            console.error('Error adding Mezmur:', error);
        }
    });
}

// ... other JavaScript code ...

function handleAddTagSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const tagName = formData.get('tag_name');

    if (!tagName || tagName.trim() === '') {
        showToast('Tag name cannot be empty.', 'warning');
        return;
    }

    fetch('/add_tag', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Failed to add tag'); });
        }
        return response.json();
    })
    .then(data => {
        showToast(data.message, 'success');
        form.reset(); // Clear the form

        // Reload the page to ensure all tag lists (desktop, mobile, swipe) are updated consistently.
        // This is the simplest and most reliable way to reflect the new tag everywhere.
        location.reload();
    })
    .catch(error => {
        showToast(`Error: ${error.message}`, 'error');
        console.error('Error adding tag:', error);
    });
}

// Attach event listeners to both "add tag" forms
document.addEventListener('DOMContentLoaded', () => {
    const addTagForms = document.querySelectorAll('.add-tag-form');
    addTagForms.forEach(form => {
        form.addEventListener('submit', handleAddTagSubmit);
    });
});

// Add at the end of mezmur.js
window.addEventListener('error', function(e) {
    showToast(`Unexpected error: ${e.message}`, 'error');
    console.error('Global Error:', e);
});


// Mezmur Sharing Functions
function copyMezmurLyrics(mezmurId) {
    const textarea = document.getElementById(`lyrics-${mezmurId}`);
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showToast('Lyrics copied to clipboard!', 'success');
    } else {
        showToast('Could not find lyrics to copy.', 'error');
    }
}

function shareOnWhatsApp(mezmurId) {
    const textarea = document.getElementById(`lyrics-${mezmurId}`);
    if (textarea) {
        const text = encodeURIComponent(textarea.value);
        const audioUrl = encodeURIComponent(`${window.location.origin}/audio/${mezmurId}`);
        const shareText = `${text}\n\nListen to the audio: ${audioUrl}`;
        
        const whatsappUrl = `https://api.whatsapp.com/send?text=${shareText}`;
        window.open(whatsappUrl, '_blank');
    } else {
        showToast('Could not find content to share.', 'error');
    }
}

function shareOnTelegram(mezmurId) {
    const textarea = document.getElementById(`lyrics-${mezmurId}`);
    if (textarea) {
        const text = textarea.value;
        const audioUrl = `${window.location.origin}/audio/${mezmurId}`;
        const shareText = `${text}\n\nListen to the audio: ${audioUrl}`;

        const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(audioUrl)}&text=${encodeURIComponent(text)}`;
        window.open(telegramUrl, '_blank');
    } else {
        showToast('Could not find content to share.', 'error');
    }
}

// Show/hide Save + Share action buttons based on whether any filters are active
function updateActionButtonsVisibility() {
    const saveBtn = document.getElementById('saveFilterBtn');
    const shareBtn = document.getElementById('shareFilterBtn');

    const hasQuery = !!(filterState.q && String(filterState.q).trim().length > 0);
    const hasTags = Array.isArray(filterState.tags) && filterState.tags.length > 0;
    const hasFilters = hasQuery || hasTags;

    [saveBtn, shareBtn].forEach(btn => {
        if (!btn) return;
        if (hasFilters) {
            btn.classList.remove('d-none');
            btn.removeAttribute('aria-hidden');
            btn.disabled = false;
        } else {
            btn.classList.add('d-none');
            btn.setAttribute('aria-hidden', 'true');
            btn.disabled = true;
        }
    });
}

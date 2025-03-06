// Global Variables
let playlistModal = null;
let currentPlayer = {
    playlistId: null,
    currentIndex: 0,
    audioElement: null,
    songs: []
};

// Toast System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Masonry Initialization
function initMasonry() {
    return new Masonry('#mezmurGrid', {
        itemSelector: '.mezmur-card-container',
        columnWidth: '.col',
        percentPosition: true,
        gutter: 24,
        transitionDuration: '0.3s',
        horizontalOrder: true
    });
}

// Filter Functionality
function filterMezmurs() {
    const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
    const selectedTags = Array.from(document.querySelectorAll('.tag-cloud input:checked'))
        .map(cb => cb.value.trim().toLowerCase());
    const operator = document.querySelector('input[name="operator"]:checked').id;
    const masonry = Masonry.data(document.querySelector('#mezmurGrid'));

    document.querySelectorAll('.mezmur-card-container').forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const tags = Array.from(card.querySelectorAll('.tag-pill'))
            .map(tag => tag.textContent.trim().toLowerCase());
        const lyrics = card.dataset.lyrics?.toLowerCase() || '';

        const matchesSearch = title.includes(searchTerm) || 
                            (searchTerm.length > 2 && lyrics.includes(searchTerm));
        const matchesTags = selectedTags.length === 0 || 
            (operator === 'operatorAnd' ? 
                selectedTags.every(tag => tags.includes(tag)) : 
                selectedTags.some(tag => tags.includes(tag)));

        card.classList.toggle('filtered-out', !(matchesSearch && matchesTags));
    });

    setTimeout(() => {
        masonry.reloadItems();
        masonry.layout();
    }, 300);
}

// Playlist Management
// Toggle sidebar on mobile
function toggleSidebar() {
    document.querySelector('.playlist-sidebar').classList.toggle('active');
}


async function loadPlaylist(playlistId, forceReload = false) {
    try {
        const response = await fetch(`/api/playlists/${playlistId}${forceReload ? '?t=' + Date.now() : ''}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const playlist = await response.json();
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

        playlistModal.show();

    } catch (error) {
        showToast(`Failed to load playlist: ${error.message}`, 'error');
    }
}

async function deletePlaylist(playlistId) {
    if (!confirm('Are you sure you want to delete this playlist?')) return;
    
    try {
        const response = await fetch(`/api/playlists/${playlistId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error(await response.text());

        document.querySelector(`[data-playlist-id="${playlistId}"]`)?.remove();
        playlistModal.hide();
        showToast('Playlist deleted successfully', 'success');
        loadInitialPlaylists()
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

        if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            modalInstance.hide();

            // Remove modal backdrop if needed
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
        }
    } catch (error) {
        showToast(error.message, 'error');
        console.error('Playlist Error:', error);
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
// Play All Functionality
function playAll() {
    if (currentPlayer.songs.length === 0) {
        showToast('No songs in this playlist', 'warning');
        return;
    }

    // Stop any existing playback
    if (currentPlayer.audioElement) {
        currentPlayer.audioElement.pause();
        currentPlayer.audioElement.remove();
    }

    // Create new audio element
    currentPlayer.audioElement = new Audio();
    currentPlayer.audioElement.controls = true;
    currentPlayer.audioElement.style.width = '100%';
    
    // Add player to modal
    const playerContainer = document.getElementById('playlistSongs');
    playerContainer.prepend(currentPlayer.audioElement);
    
    // Start playback
    currentPlayer.currentIndex = 0;
    playNextSong();
}
//Play Next Mezmur
function playNextSong() {
    if (currentPlayer.currentIndex >= currentPlayer.songs.length) {
        showToast('Playlist playback completed', 'success');
        return;
    }

    const song = currentPlayer.songs[currentPlayer.currentIndex];
    currentPlayer.audioElement.src = song.audio_url;
    // Reveal the lyrics controls.
    const lyricsControls = document.getElementById('lyricsControls');
    if (lyricsControls.classList.contains('d-none')) {
       lyricsControls.classList.remove('d-none');
    } 
    //Display lyrics of mezmur        
    document.getElementById("colapMezmur").innerText = song.lyrics || "Lyrics not available.";
    // Update UI
    highlightCurrentSong(currentPlayer.currentIndex);
    
    currentPlayer.audioElement.play();
    
    // Set up next song
    currentPlayer.audioElement.onended = () => {
        currentPlayer.currentIndex++;
        playNextSong();
    };
    
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
        if (e.target.matches('[data-load-playlist]')) {
            loadPlaylist(e.target.dataset.playlistId);
        }
        if (e.target.matches('[data-remove-song]')) {
            removeFromPlaylist(e.target.dataset.playlistId, e.target.dataset.songId);
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
        document.getElementById('lyricsControls').classList.add('d-none');
    });

    document.getElementById
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    playlistModal = new bootstrap.Modal(document.getElementById('playlistModal'));
    //const masonry = initMasonry();
    
    // Setup event listeners
    setupEventListeners();
    loadInitialPlaylists()
    // Initial setup
    filterMezmurs();
    window.addEventListener('resize', () => masonry.layout());
    window.addEventListener('resize', () => {
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

});
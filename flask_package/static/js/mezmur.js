// Global Variables
let playlistModal = null;
let currentPlayer = {
    playlistId: null,
    currentIndex: 0,
    audioElement: null,
    songs: []
};
let masonry = null;

// Toast System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Masonry Initialization
// Update initMasonry function
function initMasonry() {
    masonry = new Masonry('#mezmurGrid', {
        itemSelector: '.mezmur-card-container',
        columnWidth: '.card',
        percentPosition: true,
        gutter: 24,
        transitionDuration: '0.3s',
        horizontalOrder: true
    });
    return masonry;
}

// Filter Functionality
function filterMezmurs() {
    const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
    const selectedTags = Array.from(document.querySelectorAll('.tag-cloud input:checked'))
        .map(cb => cb.value.trim().toLowerCase());
    const operator = document.querySelector('input[name="operator"]:checked').id;

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

    // Force Masonry update
    if (masonry) {
        masonry.reloadItems();
        masonry.layout();
    }
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
        if (!playlist?.songs) {
            throw new Error('Invalid playlist data received from server');
        }
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
        playlistModal._element.addEventListener('shown.bs.modal', () => {
            if (masonry) {
                masonry.layout();
            }
        });
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

function playAll() {
    console.log('Play All clicked');
    if (!currentPlayer.songs?.length) {
        showToast('No songs in this playlist', 'warning');
        return;
    }

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
            document.getElementById('lyricsControls').classList.add('d-none');
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
        document.getElementById('lyricsControls').classList.remove('d-none');
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
 
 
        if (song.audio_url && song.audio_url !== 'null' && song.audio_url.trim() !== '') {
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
                const errorMsg = e.target.error ? `${e.target.error.code}; ${e.target.error.message}` : 'Unknown audio error';
                showToast(`Audio error for "${song.title}": ${errorMsg}`, 'error');
                console.error('Audio Element Error:', e.target.error);
                // Optionally skip to next on error after a delay
                // setTimeout(skipToNextSong, 1000);
            };
 
            try {
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
            showToast(`"${song.title}" has no audio. Displaying lyrics only.`, 'info');
            // Ensure player is stopped if previous track had audio
            if (currentPlayer.audioElement && !currentPlayer.audioElement.paused) {
                currentPlayer.audioElement.pause();
            }
            // Clear src to avoid potential issues with the old source
            if (currentPlayer.audioElement) {
                currentPlayer.audioElement.removeAttribute('src');
                // Consider hiding or disabling the controls visually
                // currentPlayer.audioElement.style.display = 'none';
            }
            // Do not set up 'onended' or 'timeupdate' if there's no audio.
            // User must click "Play Next" or "Play All" again.
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
    setupEventListeners();
    // Setup event listeners
    playlistModal._element.addEventListener('shown.bs.modal', () => {
        // Now we're sure modal DOM elements exist
        initMasonry();
        setupEventListeners();
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
        if (masonry) masonry.layout();
        if(window.innerWidth >= 1200) {
            document.querySelector('.playlist-sidebar').classList.remove('active');
        }
    });
    window.addEventListener('resize', () => {
        if (masonry) masonry.layout();
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
    // Initialize Masonry after images load
    imagesLoaded('#mezmurGrid', function() {
        initMasonry();
        filterMezmurs(); // Initial filter
        window.dispatchEvent(new Event('resize')); // Trigger initial layout
    });

});

// Add mezmur model handler
document.getElementById('addMezmurForm').addEventListener('submit', async (event) => {
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

// ... other JavaScript code ...

document.addEventListener('submit', (event) => {
    if (event.target.classList.contains('add-tag-form')) {
        event.preventDefault();
        const formData = new FormData(event.target);
        (async () => {
            try {
                const response = await fetch('/add_tag', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    showToast(`Error: ${errorData.error}`, 'error');
                    return;
                }
                const data = await response.json();
                showToast(data.message, 'success');
                // Update the UI to show the new tag
                const tagCloud = document.querySelector('.tag-cloud');
                if (tagCloud) {
                    const newInput = document.createElement('input');
                    newInput.type = 'checkbox';
                    newInput.name = 'tag';
                    newInput.value = data.tag.toLowerCase();
                    newInput.id = `tag-${data.tag.toLowerCase().replace(/\s/g, '-')}`;

                    const newLabel = document.createElement('label');
                    newLabel.htmlFor = newInput.id;
                    newLabel.appendChild(newInput);
                    newLabel.appendChild(document.createTextNode(data.tag));

                    tagCloud.appendChild(newLabel);
                }
                event.target.reset(); // Clear the form
            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
                console.error('Error adding tag:', error);
            }
        })();
    }
});

// Add at the end of mezmur.js
window.addEventListener('error', function(e) {
    showToast(`Unexpected error: ${e.message}`, 'error');
    console.error('Global Error:', e);
});

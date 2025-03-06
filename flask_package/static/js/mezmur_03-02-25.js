// Store modal instance globally
let playlistModal = null;
// Initialize modal on page load
function initializeModals(){
    playlistModal = new bootstrap.Modal(document.getElementById('playlistModal'));
};
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    // Your existing filter code
    function filterMezmurs() {
        const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
        const selectedTags = Array.from(document.querySelectorAll('.tag-cloud input:checked')).map(cb => cb.value.trim().toLowerCase());
        const operator = document.querySelector('input[name="operator"]:checked').id;
        const masonry = Masonry.data(document.querySelector('#mezmurGrid'));
    
        document.querySelectorAll('.mezmur-card-container').forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const tags = Array.from(card.querySelectorAll('.tag-pill')).map(tag => 
                tag.textContent.trim().toLowerCase()
            );
            const lyrics = card.dataset.lyrics ? card.dataset.lyrics.toLowerCase() : '';
    
            const matchesSearch = title.includes(searchTerm) || 
                                (searchTerm.length > 2 && lyrics.includes(searchTerm));
            const matchesTags = selectedTags.length === 0 || 
                (operator === 'operatorAnd' ? 
                    selectedTags.every(tag => tags.includes(tag)) : 
                    selectedTags.some(tag => tags.includes(tag)));
    
            // Use classList instead of direct style manipulation
            if (matchesSearch && matchesTags) {
                card.classList.remove('filtered-out');
            } else {
                card.classList.add('filtered-out');
            }
        });
    
        // Wait for CSS transitions before layout
        setTimeout(() => {
            masonry.reloadItems();
            masonry.layout();
        }, 300);
    }

    // Event Listeners with debounce
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

    function initMasonry() {
        return new Masonry('#mezmurGrid', {
            itemSelector: '.mezmur-card-container',
            columnWidth: '.col', // Use Bootstrap column as base
            percentPosition: true,
            gutter: 24, // Match Bootstrap's gutter (1.5rem = 24px)
            transitionDuration: '0.3s',
            horizontalOrder: true
        });
    }

    //const masonry = initMasonry();

    // Add resize handler
    // window.addEventListener('resize', () => {
    //     masonry.layout();
    // });

    // Initial filter
    //filterMezmurs();


    function showToast(message) {
        // Your code to display a toast notification
        alert(message); // Example implementation, replace with actual toast code
    }
    function showToast(message, type) {
        // Your code to display a toast notification
        // Example implementation (replace with actual toast code)
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3000); // Adjust the duration as needed
    }
    
    
    // Modified removeFromPlaylist function
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
    
    // AJAX Operations
    async function addToPlaylist(mezmurId, playlistId) {
        try {
            const response = await fetch(`/playlist/${playlistId}/add/${mezmurId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
    
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(`${result.status}: ${result.message}`);
            }
    
            showToast(`${result.song.title} added to ${result.playlist.name}`, 'success');
            
            // Optional: Update UI counters
            const badge = document.querySelector(`[data-playlist-id="${playlistId}"] .badge`);
            if(badge) {
                badge.textContent = `${result.playlist.song_count} hymns`;
            }
        } catch (error) {
            showToast(error.message, 'error');
            console.error('Playlist Error:', error);
        }
    }
    
    // Playlist Player State
    let currentPlayer = {
        playlistId: null,
        currentIndex: 0,
        audioElement: null,
        songs: []
    }
    
    // Fetch and display playlists on page load
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

        // Add this to mezmur.js
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-load-playlist]')) {
            const playlistId = e.target.dataset.playlistId;
            loadPlaylist(playlistId);
        }
    });
        
    // Updated loadPlaylist function
    async function loadPlaylist(playlistId, forceReload = false) {
        try {
            // Always fetch fresh data when forced
            const response = await fetch(`/api/playlists/${playlistId}${forceReload ? '?t=' + Date.now() : ''}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const playlist = await response.json();
            
            // Update DOM elements
            document.getElementById('playlistName').textContent = playlist.name;
            const songsContainer = document.getElementById('playlistSongs');
            
            // Clear previous content
            songsContainer.innerHTML = '';
    
            // Repopulate songs
            playlist.songs.forEach(song => {
                const songElement = document.createElement('div');
                songElement.className = 'list-group-item d-flex justify-content-between align-items-center';
                songElement.innerHTML = `
                    <div>${song.title}</div>
                    <div>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="removeFromPlaylist(${playlistId}, ${song.id})">
                            Remove
                        </button>
                    </div>
                `;
                songElement.draggable = true;
                songElement.ondragstart = (e) => dragMezmur(e, song.id);
                songsContainer.appendChild(songElement);
            });

            // Show modal using Bootstrap's proper method
            playlistModal.show();
    
            // Store songs with proper audio URLs
            currentPlayer = {
                playlistId: playlistId,
                currentIndex: 0,
                audioElement: null,
                songs: playlist.songs.map(song => ({
                    ...song,
                    // Ensure audio_url is properly formatted
                    audio_url: song.audio_url || `/audio/${song.id}`
                }))
            };
    
        } catch (error) {
            console.error('Playlist load error:', error);
            showToast(`Failed to load playlist: ${error.message}`, 'error');
        }

        // Your implementation here
        console.log('Loading playlist:', playlistId);
    }
    //Delete a playlist    
    async function deletePlaylist(playlistId) {
        try {
            const confirmation = confirm('Are you sure you want to delete this playlist? This action cannot be undone.');
            if (!confirmation) return;
    
            const response = await fetch(`/api/playlists/${playlistId}`, {
                method: 'DELETE'
            });
    
            const result = await response.json();
    
            if (!response.ok) {
                throw new Error(result.message);
            }
    
            // Remove playlist card from UI
            const playlistCard = document.querySelector(`[data-playlist-id="${playlistId}"]`);
            if (playlistCard) {
                playlistCard.remove();
            }
    
            // Refresh the sidebar with updated playlists
            refreshPlaylistSidebar(result.playlists);
    
            // Close modal if open
            if (playlistModal && playlistModal._element.classList.contains('show')) {
                playlistModal.hide();
            }
    
            showToast(result.message, 'success');
    
        } catch (error) {
            showToast(error.message, 'error');
            console.error('Delete Playlist Error:', error);
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
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h5 class="mb-1">${playlist.name}</h5>
                            <p class="text-muted small mb-0">${playlist.description}</p>
                            <span class="badge bg-secondary">${playlist.song_count} hymns</span>                    
                        </div>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="loadPlaylist(${playlist.id})">
                                Open
                            </button>
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="deletePlaylist(${playlist.id})">
                                ✕
                            </button>
                        </div>
                    </div>
                </div>
            `;
            sidebar.appendChild(playlistCard);
        });
    }
                                                //////////////////////END Sidebar////////////////////
                                                //////////////////Start Share Playlist//////////////
                                                
                                                //////////////////END Share Playlist//////////////
    // Toggle sidebar on mobile
    function toggleSidebar() {
        document.querySelector('.playlist-sidebar').classList.toggle('active');
    }
    
    // Auto-close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if(window.innerWidth < 1200 && 
           !e.target.closest('.playlist-sidebar') && 
           !e.target.closest('.sidebar-toggle')) {
            document.querySelector('.playlist-sidebar').classList.remove('active');
        }
    });
    
    // Responsive adjustment
    window.addEventListener('resize', () => {
        if(window.innerWidth >= 1200) {
            document.querySelector('.playlist-sidebar').classList.remove('active');
        }
    });
    
    
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

    // When the playlist modal is closed, stop the song and hide lyrics controls again.
    // var playlistModal = document.getElementById('playlistModal');
    document.getElementById('playlistModal').addEventListener('hidden.bs.modal', () => {
        if (currentPlayer.audioElement) {
            currentPlayer.audioElement.pause();
        }
        const lyricsControls = document.getElementById('lyricsControls');
        lyricsControls.classList.add('d-none');
    });
});
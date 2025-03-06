// Global audio controller
let audioController = {
    element: null,
    currentSongId: null,
    lyricsElement: null
};

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    // Create hidden audio element
    audioController.element = document.createElement('audio');
    audioController.element.controls = true;
    audioController.element.style.display = 'none';
    document.body.appendChild(audioController.element);

    // Lyrics container (add this to your modal HTML)
    audioController.lyricsElement = document.createElement('div');
    audioController.lyricsElement.id = 'lyricsContainer';
    audioController.lyricsElement.style.display = 'none';
    document.getElementById('playlistSongs').appendChild(audioController.lyricsElement);

    // Handle modal close
    const playlistModal = document.getElementById('playlistModal');
    playlistModal.addEventListener('hidden.bs.modal', () => {
        audioController.element.pause();
        audioController.element.currentTime = 0;
        audioController.lyricsElement.style.display = 'none';
        audioController.currentSongId = null;
    });
});

// Modified loadPlaylist function
async function loadPlaylist(playlistId) {
    try {
        // Clear previous state
        audioController.element.pause();
        audioController.element.currentTime = 0;
        audioController.lyricsElement.style.display = 'none';
        audioController.currentSongId = null;

        const response = await fetch(`/api/playlists/${playlistId}`);
        const playlist = await response.json();

        const songsContainer = document.getElementById('playlistSongs');
        songsContainer.innerHTML = ''; // Clear previous content

        playlist.songs.forEach((song, index) => {
            const songElement = document.createElement('div');
            songElement.className = 'list-group-item d-flex justify-content-between align-items-center';
            songElement.innerHTML = `
                <div>${song.title}</div>
                <div>
                    <button class="btn btn-sm btn-primary play-button">
                        ▶ Play
                    </button>
                    <button class="btn btn-sm btn-info lyrics-button" style="display: none;">
                        📜 Lyrics
                    </button>
                </div>
            `;

            // Add event listeners
            songElement.querySelector('.play-button').addEventListener('click', () => {
                playSong(song.id, song.audio_url, song.lyrics);
            });
            
            songsContainer.appendChild(songElement);
        });

        new bootstrap.Modal('#playlistModal').show();

    } catch (error) {
        console.error('Playlist load error:', error);
        showToast(`Failed to load playlist: ${error.message}`, 'error');
    }
}

function playSong(songId, audioUrl, lyrics) {
    // Stop previous song
    audioController.element.pause();
    
    // Set new song
    audioController.currentSongId = songId;
    audioController.element.src = audioUrl;
    audioController.element.play();
    
    // Update lyrics
    audioController.lyricsElement.innerHTML = lyrics;
    audioController.lyricsElement.style.display = 'none';
    
    // Show lyrics button for this song
    document.querySelectorAll('.lyrics-button').forEach(btn => btn.style.display = 'none');
    event.target.closest('.list-group-item').querySelector('.lyrics-button').style.display = 'inline-block';
}

// Add to your existing code
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('lyrics-button')) {
        audioController.lyricsElement.style.display = 
            audioController.lyricsElement.style.display === 'none' ? 'block' : 'none';
    }
});
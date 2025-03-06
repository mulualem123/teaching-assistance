
function checkCreateNewPlaylist(select) {
    if (select.value === 'create_new') {
        var createPlaylistModal = new bootstrap.Modal(document.getElementById('createPlaylistModal'), {});
        createPlaylistModal.show();
        // Reset the select dropdown to its default state
        select.value = 'Add to playlist...';
    }
}
        // Drag & Drop Implementation
function allowDrop(ev) {
    ev.preventDefault();
}

function dragMezmur(ev, mezmurId) {
    ev.dataTransfer.setData("mezmurId", mezmurId);
}

function dropToPlaylist(ev) {
    ev.preventDefault();
    const playlistId = ev.target.closest('.playlist-card').dataset.playlistId;
    const mezmurId = ev.dataTransfer.getData("mezmurId");
    addToPlaylist(mezmurId, playlistId);
}


////////////////////////////////////////////////
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






////////////////////////////////////////////////////////////////    
document.getElementById('searchInput').addEventListener('keyup', function() {
    var input = document.getElementById('searchInput');
    var filter = input.value.toLowerCase();
    var table = document.getElementById('myTable');
    var tr = table.getElementsByTagName('tr');

    for (var i = 1; i < tr.length; i++) {
        var td = tr[i].getElementsByTagName('td');
        var showRow = false;
        for (var j = 0; j < td.length; j++) {
            if (td[j]) {
                if (td[j].innerHTML.toLowerCase().indexOf(filter) > -1) {
                    showRow = true;
                    break;
                }
            }
        }
        tr[i].style.display = showRow ? '' : 'none';
    }
});

////////////////////////////////playlist.playlist////////////////////////////////
// Playlist Player State
let currentPlayer = {
    playlistId: null,
    currentIndex: 0,
    audioElement: null,
    songs: []
};

// Updated loadPlaylist function
async function loadPlaylist(playlistId) {
    try {
        const response = await fetch(`/api/playlists/${playlistId}`);
        const playlist = await response.json();

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

        // Rest of your loadPlaylist implementation...
        
    } catch (error) {
        console.error('Failed to load playlist:', error);
        showToast(`Error loading playlist: ${error.message}`, 'error');
    }
}

// Modified playAll function
function playAll() {
    // Use the songs from currentPlayer
    const availableSongs = currentPlayer.songs.filter(song => song.audio_url);
    
    if (availableSongs.length === 0) {
        showToast('No playable songs in this playlist', 'warning');
        return;
    }

    // Clear existing audio element
    if (currentPlayer.audioElement) {
        currentPlayer.audioElement.pause();
        currentPlayer.audioElement.remove();
    }

    // Create new audio element
    const audioElement = new Audio();
    audioElement.controls = true;
    audioElement.style.width = '100%';
    document.getElementById('playlistSongs').prepend(audioElement);

    // Update player state
    currentPlayer = {
        ...currentPlayer,
        currentIndex: 0,
        audioElement: audioElement,
        songs: availableSongs
    };

    // Start playback
    playNextSong();
}

// Modified playNextSong function
function playNextSong() {
    if (!currentPlayer.audioElement || currentPlayer.currentIndex >= currentPlayer.songs.length) {
        showToast('Playlist playback completed', 'success');
        return;
    }

    const song = currentPlayer.songs[currentPlayer.currentIndex];
    
    try {
        currentPlayer.audioElement.src = song.audio_url;
        highlightCurrentSong(currentPlayer.currentIndex);
        
        currentPlayer.audioElement.play();
        
        currentPlayer.audioElement.onended = () => {
            currentPlayer.currentIndex++;
            playNextSong();
        };

    } catch (error) {
        console.error('Error playing song:', error);
        showToast(`Error playing ${song.title}`, 'error');
        currentPlayer.currentIndex++;
        playNextSong();
    }
}

function highlightCurrentSong(index) {
    console.log(`Now playing: ${currentPlayer.songs[index].title}`);
    document.querySelectorAll('#playlistSongs .list-group-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
}



////////////////////////////////////////////////////////////////////////////////////////////////
async function loadPlaylist(playlistID) {
    try {
        const response = await fetch(`/api/playlists/${playlistID}`);
        const data = await response.json();
        
        const playlist = data;

        // Store songs with proper audio URLs
        currentPlayer = {
            playlistId: playlistID, 
            currentIndex: 0, 
            audioElement: null, 
            songs: playlist.songs.map(song => ({
                ...song,
                // Ensure audio_url is properly formatted
                audio_url: song.audio_url || `/audio/${song.id}`
            }))
        };
        
        // Additional logic to play the first song or handle the playlist
        playSong(currentPlayer.songs[0]);

    } catch (error) {
        console.error('Failed to load playlist:', error);
    }
}

function playSong(song) {
    const audioElement = new Audio(song.audio_url);
    audioElement.play();
    currentPlayer.audioElement = audioElement;
}

// Call the function with the desired playlist ID
loadPlaylist(somePlaylistID);

////////////////////////////////////////////////////////////////

async function loadPlaylist(playlistID) {
    try {
        const response = await fetch(`https://api/playlists/${playlistID}`);
        const data = await response.json();

        //Store songs with proper audio URLs
        currentPlayer = {
            playlistId: playlistID, 
            currentIndex: 0, 
            audioElement: null, 
            songs: playlist.songs.map(song=>({
                ...song,
                // Ensure audio_url is properly formatted 
                audio_url: song.audio_url || '/audio/${song.id}'
            }))
        };

        // Rest of your loadPlaylist implementation...

    } catch (error) {
        console.error('Failed to load playlist:',error);
        showToast('Errorr loading playlist: ${error.message}', 'error');
    }
    

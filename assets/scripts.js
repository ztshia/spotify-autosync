async function fetchPlaylist() {
    const response = await fetch('./liked_tracks.json');
    const playlist = await response.json();
    const playlistBody = document.getElementById('playlist-body');

    // Sort the playlist by added_at in descending order
    playlist.sort((a, b) => new Date(b.added_at) - new Date(a.added_at));

    playlist.forEach((song, index) => {
        const row = document.createElement('tr');

        const cellIndex = document.createElement('td');
        cellIndex.textContent = index + 1;
        row.appendChild(cellIndex);

        const cellSongInfo = document.createElement('td');
        const songInfoDiv = document.createElement('div');
        songInfoDiv.className = 'song-info';

        const albumCoverContainer = document.createElement('div');
        albumCoverContainer.className = 'album-cover-container';

        const albumCoverImg = document.createElement('img');
        albumCoverImg.src = song.album_cover_url;
        albumCoverImg.alt = song.album_name;
        albumCoverImg.className = 'album-cover';
        albumCoverContainer.appendChild(albumCoverImg);

        const popularityOverlay = document.createElement('div');
        popularityOverlay.className = 'popularity-overlay';
        popularityOverlay.textContent = song.popularity;
        albumCoverContainer.appendChild(popularityOverlay);

        songInfoDiv.appendChild(albumCoverContainer);

        const songDetailsDiv = document.createElement('div');
        songDetailsDiv.className = 'song-details';

        const songNameDiv = document.createElement('div');
        songNameDiv.className = 'song-name';
        const songLink = document.createElement('a');
        songLink.href = song.track_url;
        songLink.textContent = song.song_name;
        songLink.target = "_blank";
        songNameDiv.appendChild(songLink);
        songDetailsDiv.appendChild(songNameDiv);

        const singerNameDiv = document.createElement('div');
        singerNameDiv.className = 'singer-name';
        singerNameDiv.textContent = song.singer_name;
        songDetailsDiv.appendChild(singerNameDiv);

        songInfoDiv.appendChild(songDetailsDiv);
        cellSongInfo.appendChild(songInfoDiv);
        row.appendChild(cellSongInfo);

        const cellAlbumName = document.createElement('td');
        cellAlbumName.textContent = song.album_name;
        cellAlbumName.className = 'album-name';
        row.appendChild(cellAlbumName);

        const cellAddedAt = document.createElement('td');
        cellAddedAt.textContent = formatRelativeTime(song.added_at);
        cellAddedAt.className = 'relative-time';
        row.appendChild(cellAddedAt);

        const cellDuration = document.createElement('td');
        cellDuration.textContent = formatDuration(song.track_duration_ms);
        cellDuration.className = 'track-duration';
        row.appendChild(cellDuration);

        playlistBody.appendChild(row);
    });
}

function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

function formatRelativeTime(datetime) {
    const now = new Date();
    const then = new Date(datetime);
    const diffInSeconds = Math.floor((now - then) / 1000);

    const minutes = Math.floor(diffInSeconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return `${days}天前`;
    } else if (hours > 0) {
        return `${hours}小时前`;
    } else if (minutes > 0) {
        return `${minutes}分钟前`;
    } else {
        return '刚刚';
    }
}

fetchPlaylist();

async function fetchTasteAnalysis() {
    try {
        const response = await fetch('./taste.json');
        const taste = await response.json();
        const container = document.getElementById('taste-summary');

        const content = `
            <p><strong>总结：</strong> ${taste.summary || ''}</p>
            <p><strong>风格：</strong> ${taste.genres?.join(', ') || ''}</p>
            <p><strong>情绪：</strong> ${taste.moods?.join(', ') || ''}</p>
            <p><strong>详细描述：</strong> ${taste.description || ''}</p>
        `;

        container.innerHTML = content;
    } catch (error) {
        console.error('无法加载 taste.json:', error);
    }
}

document.addEventListener('DOMContentLoaded', fetchTasteAnalysis);


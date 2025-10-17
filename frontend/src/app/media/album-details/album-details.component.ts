import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../env/environment';

interface Song {
  id: string;
  title: string;
  duration?: number;
  audio_url?: string;
  track_number?: number;
  cover_url?: string;
}

interface Album {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  year?: number;
  description?: string;
  imageUrl?: string;
  songs: Song[];
  created_at?: string;
}

@Component({
  selector: 'app-album-details',
  standalone: false,
  templateUrl: './album-details.component.html',
  styleUrls: ['./album-details.component.css']
})
export class AlbumDetailsComponent implements OnInit {
  album?: Album;
  loading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    const albumId = this.route.snapshot.paramMap.get('id');
    if (!albumId) {
      this.error = 'Album ID not provided';
      this.loading = false;
      return;
    }

    this.loadAlbum(albumId);
  }

  private loadAlbum(albumId: string): void {
    this.http.get<Album>(`${environment.apiHost}/albums/${albumId}`).subscribe({
      next: (album) => {
        console.log(album);
        this.album = album;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load album:', err);
        this.error = 'Failed to load album. Please try again later.';
        this.loading = false;
      }
    });
  }

  getArtistsString(): string {
    console.log(this.album);
    if (!this.album?.artists || this.album.artists.length === 0) {
      return 'Unknown Artist';
    }
    return this.album.artists.join(', ');
  }

  getTotalDuration(): string {
    if (!this.album?.songs) return '0:00';

    const totalSeconds = this.album.songs.reduce((sum, song) => {
      return sum + (song.duration || 0);
    }, 0);

    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

}

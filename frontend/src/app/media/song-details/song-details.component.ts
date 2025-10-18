import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../env/environment';
import { MediaService } from '../media.service';
import { MatSnackBar } from '@angular/material/snack-bar';

interface Song {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  duration: number;
  track_number?: number;
  description: string;
  audio_url: string;
  cover_url?: string;
  album?: {
    id: string;
    title: string;
    year: number;
    cover_url: string;
  };
  created_at: string;
  related_songs: any[];
}

@Component({
  selector: 'app-song-details',
  templateUrl: './song-details.component.html',
  standalone: false,
  styleUrls: ['./song-details.component.css'],
})
export class SongDetailsComponent implements OnInit, OnDestroy {
  song?: Song;
  id?: string;
  loading = true;
  error?: string;

  isPlaying = false;
  currentTime = 0;
  duration = 0;
  volume = 1;

  audio?: HTMLAudioElement;

  constructor(
    private route: ActivatedRoute,
    private service: MediaService,
    private snackBar: MatSnackBar,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? undefined;
    if (this.id) this.loadSong(this.id);
  }

  loadSong(songId: string): void {
    this.loading = true;
    this.error = undefined;

    this.http.get<Song>(`${environment.apiHost}/songs/${songId}`).subscribe({
      next: (song) => {
        this.song = song;
        this.loading = false;
        this.initializeAudioPlayer();
      },
      error: (err) => {
        console.error('Error loading song:', err);
        this.error = 'Failed to load song. Please try again.';
        this.loading = false;
      },
    });
  }

  initializeAudioPlayer(): void {
    if (!this.song?.audio_url) return;

    this.audio = new Audio(this.song.audio_url);

    this.audio.addEventListener('loadedmetadata', () => {
      this.duration = this.audio!.duration;
    });

    this.audio.addEventListener('timeupdate', () => {
      this.currentTime = this.audio!.currentTime;
    });

    this.audio.addEventListener('ended', () => {
      this.isPlaying = false;
      this.currentTime = 0;
    });

    this.audio.addEventListener('error', (e) => {
      console.error('Audio error:', e);
      this.error = 'Failed to load audio file.';
    });
  }

  togglePlay(): void {
    if (!this.audio) return;

    if (this.isPlaying) {
      this.audio.pause();
    } else {
      this.audio.play();
    }
    this.isPlaying = !this.isPlaying;
  }

  seek(event: any): void {
    if (!this.audio) return;
    const value = event.target.value;
    this.audio.currentTime = value;
    this.currentTime = value;
  }

  changeVolume(event: any): void {
    if (!this.audio) return;
    const value = event.target.value;
    this.audio.volume = value;
    this.volume = value;
  }

  formatTime(seconds: number): string {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  getArtistsString(): string {
    return this.song?.artists.join(', ') ?? 'Unknown Artist';
  }

  getGenresString(): string {
    return this.song?.genres.join(', ') ?? '';
  }

  onDelete(): void {
    if (!this.id) return;
    console.log(this.song);
    this.service.deleteSong(this.id).subscribe({
      next: () => {
        this.snackBar.open('Song successfully deleted', 'Close', {
          duration: 3000,
        });
        this.router.navigate(['/home']);
      },
      error: () => {
        this.snackBar.open('Failed to delete song', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  ngOnDestroy(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.src = '';
      this.audio = undefined;
    }
  }
}

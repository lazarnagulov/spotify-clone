import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {HttpClient, HttpContext, HttpResponse} from '@angular/common/http';
import { environment } from '../../../env/environment';
import { MediaService } from '../media.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../auth/auth.service';
import {OfflineStorageService} from '../offline-storage.service';
import {catchError, filter, from, of, Subject, switchMap, takeUntil, tap} from 'rxjs';
import {SKIP_AUTH} from '../../auth/auth.interceptor';

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
  transcript?: string | null;
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
  userRoles: string[] = [];
  userRating: number = 0;

  isPlaying = false;
  currentTime = 0;
  duration = 0;
  volume = 1;

  audio?: HTMLAudioElement;
  audioInitialized = false;
  showLyrics = false;
  isOfflineAvailable = false;
  isDownloading = false;
  downloadProgress: number = 0;

  private destroy$ = new Subject<void>();


  constructor(
    private route: ActivatedRoute,
    private service: MediaService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private router: Router,
    private offlineStorage: OfflineStorageService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? undefined;
    if (this.id) {
      this.loadSong(this.id);
      this.pollTranscript();
    }
    this.userRoles = this.authService.getRoles();
  }

  loadSong(songId?: string): void {
    this.loading = true;
    this.error = undefined;

    this.http.get<Song>(`${environment.apiHost}/songs/${songId}`).subscribe({
      next: (song) => {
        this.song = song;
        this.loading = false;
        this.checkOfflineAvailability();

        if (!this.audioInitialized) {
          this.initializeAudioPlayer();
          this.audioInitialized = true;
        }
      },
      error: (err) => {
        console.error('Error loading song:', err);
        this.error = 'Failed to load song. Please try again.';
        this.loading = false;
      },
    });
  }

  pollTranscript() {
    if (!this.id) return;

    const interval = setInterval(() => {
      if (this.song?.transcript) {
        clearInterval(interval);
        console.log('Transcript available, stopping polling.');
        return;
      }


      this.service.getTranscription(this.id!).subscribe({
        next: (res) => {
          if (res.transcript) {
            this.song!.transcript = res.transcript;
            console.log('Transcript fetched:', res.transcript);
          }
        },
        error: (err) => {
          console.warn('Error polling transcript:', err);
        }
      });
      }, 5000);
  }

  toggleLyrics() {
    this.showLyrics = !this.showLyrics;
  }

  onRate(rating: number): void {
    if (!this.id || !this.song) return;

    const ratingData = {
      content_id: this.id,
      content_type: 'song',
      rating: rating,
      artistIds: this.song.artists,
      albumIds: this.song.album ? [this.song.album.id] : [],
      genres: this.song.genres
    };

    this.http.post(`${environment.apiHost}/ratings`, ratingData).subscribe({
      next: () => {
        this.userRating = rating;
        this.snackBar.open(`Rated ${rating} stars!`, 'Close', {
          duration: 2000,
        });
      },
      error: (err) => {
        console.error('Failed to submit rating:', err);
        this.snackBar.open('Failed to submit rating', 'Close', {
          duration: 3000,
        });
      },
    });
  }

  initializeAudioPlayer(): void {
    if (!this.song) return;

    this.offlineStorage.getSong(this.song.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe(offlineData => {
        if (offlineData) {
          console.log('Playing offline version');
          const url = URL.createObjectURL(offlineData.blob);
          this.audio = new Audio(url);
        } else if (this.song!.audio_url) {
          this.audio = new Audio(this.song!.audio_url);
        }

        this.setupAudioListeners();
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

  toggleOffline(): void {
    if (this.isOfflineAvailable) {
      this.removeOffline();
    } else {
      this.downloadOffline();
    }
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

  checkOfflineAvailability(): void {
    if (!this.song?.id) return;

    this.offlineStorage.isAvailableOffline(this.song.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe(isAvailable => {
        this.isOfflineAvailable = isAvailable;
      });
  }

  downloadOffline(): void {
    if (!this.id || !this.song) return;

    this.isDownloading = true;
    this.downloadProgress = 0;

    this.http.get<any>(`${environment.apiHost}/songs/${this.id}/offline_url`)
      .pipe(
        switchMap(res =>
          this.http.get(res.offline_url, {
            responseType: 'blob',
            reportProgress: true,
            observe: 'events',
            context: new HttpContext().set(SKIP_AUTH, true)
          })
        ),
        tap(event => {
          if (event.type === 1 && event.total) {
            this.downloadProgress = Math.round((event.loaded / event.total) * 100);
          }
        }),
        filter((event): event is HttpResponse<Blob> => event.type === 4),
        switchMap(response =>
          this.offlineStorage.saveSong({
            id: this.song!.id,
            blob: response.body!,
            downloadedAt: Date.now(),
            title: this.song!.title,
            artists: this.song!.artists,
            coverUrl: this.song!.cover_url,
            duration: this.song!.duration
          })
        ),
        tap(() => {
          this.isOfflineAvailable = true;
          this.snackBar.open('Song downloaded for offline playback!', 'Close', {
            duration: 3000,
          });
        }),
        catchError(err => {
          console.error('Download failed:', err);
          this.snackBar.open('Failed to download song for offline use.', 'Close', {
            duration: 3000,
          });
          return of(null);
        }),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.isDownloading = false;
        this.downloadProgress = 0;
      });
  }

  removeOffline(): void {
    if (!this.id) return;

    this.offlineStorage.deleteSong(this.id)
      .pipe(
        tap(() => {
          this.isOfflineAvailable = false;
          this.snackBar.open('Removed from offline storage', 'Close', {
            duration: 2000,
          });

          if (this.audio) {
            const wasPlaying = this.isPlaying;
            const currentTimeBackup = this.currentTime;

            this.audio.pause();
            this.audio.src = '';
            this.audio = undefined;

            this.initializeAudioPlayer();

            setTimeout(() => {
              if (wasPlaying && this.audio) {
                this.audio.currentTime = currentTimeBackup;
                this.audio.play();
                this.isPlaying = true;
              }
            }, 100);
          }
        }),
        catchError(err => {
          console.error('Failed to remove offline song:', err);
          this.snackBar.open('Failed to remove offline version', 'Close', {
            duration: 3000,
          });
          return of(null);
        }),
        takeUntil(this.destroy$)
      )
      .subscribe();
  }

  private setupAudioListeners(): void {
    if (!this.audio) return;

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

  ngOnDestroy(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.src = '';
      this.audio = undefined;
    }
  }
}

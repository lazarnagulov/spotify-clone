import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../env/environment';
import { MediaService } from '../media.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../auth/auth.service';
import {Album} from '../../shared/model/media/album.model';

@Component({
  selector: 'app-album-details',
  standalone: false,
  templateUrl: './album-details.component.html',
  styleUrls: ['./album-details.component.css'],
})
export class AlbumDetailsComponent implements OnInit {
  album?: Album;
  id?: string;
  loading = true;
  error: string | null = null;
  userRoles: string[] = [];
  userRating: number = 0;

  constructor(
    private router: Router,
    private service: MediaService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? undefined;
    if (!this.id) {
      this.error = 'Album ID not provided';
      this.loading = false;
      return;
    }

    this.userRoles = this.authService.getRoles();
    this.loadAlbum(this.id);
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
      },
    });
  }

  onRate(rating: number): void {
    if (!this.id || !this.album) return;

    const ratingData = {
      content_id: this.id,
      content_type: 'album',
      rating: rating,
      artistIds: this.album.artists,
      genres: this.album.genres,
    };

    console.log(ratingData);

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

  getArtistsString(): string {
    console.log(this.album);
    if (!this.album?.artists || this.album.artists.length === 0) {
      return 'Unknown';
    }
    return this.album.artists.join(', ');
  }

  getTotalDuration(): string {
    if (!this.album?.songs) return '0:00';

    const totalSeconds = this.album.songs.reduce((sum, song) => {
      return sum + (song.duration ?? 0);
    }, 0);

    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  onDelete(): void {
    if (!this.id) return;

    this.service.deleteAlbum(this.id).subscribe({
      next: () => {
        this.snackBar.open('Album successfully deleted', 'Close', {
          duration: 3000,
        });
        void this.router.navigate(['/home']);
      },
      error: () => {
        this.snackBar.open('Failed to delete album', 'Close', {
          duration: 3000,
        });
      },
    });
  }
}

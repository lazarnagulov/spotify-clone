import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { switchMap, EMPTY } from 'rxjs';
import { Artist } from '../model/artist.model';
import { ArtistService } from '../artist.service';
import { AuthService } from '../../auth/auth.service';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../env/environment';

@Component({
  selector: 'app-artist-details',
  standalone: false,
  templateUrl: './artist-details.component.html',
  styleUrls: ['./artist-details.component.css']
})
export class ArtistDetailsComponent implements OnInit {
  id?: string;
  artist?: Artist;
  loading = true;
  error?: string;
  isSubscribed = false;
  checkingSubscription = true;
  userRoles: string[] = [];
  userRating: number = 0;

  constructor(
    private http: HttpClient,
    private artistService: ArtistService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userRoles = this.authService.getRoles();

    this.route.paramMap
      .pipe(
        switchMap((params) => {
          const id = params.get('id');
          if (!id) return EMPTY;
          this.id = id;
          this.loading = true;
          return this.artistService.getDetails(id);
        })
      )
      .subscribe({
        next: (artist) => {
          this.artist = artist;
          this.loading = false;
          if (this.id) {
            this.checkSubscription(this.id);
          }
        },
        error: (err) => {
          console.error('Error loading artist:', err);
          this.error = 'Failed to load artist.';
          this.loading = false;
        }
      });
  }

  onRate(rating: number): void {
    if (!this.id || !this.artist) return;

    const ratingData = {
      content_id: this.id,
      content_type: 'artist',
      rating: rating,
      genres: this.artist?.genres,
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

  onDelete(): void {
    if (!this.id) return;
    this.artistService.deleteArtist(this.id).subscribe({
      next: () => {
        this.snackBar.open('Artist successfully deleted', 'Close', { duration: 3000 });
        void this.router.navigate(['/home']);
      },
      error: () => {
        this.snackBar.open('Failed to delete artist', 'Close', { duration: 3000 });
      }
    });
  }

  checkSubscription(artistId: string): void {
    this.checkingSubscription = true;
    this.isSubscribed = false;
    this.http.get<{ subscribed: boolean }>(
      `${environment.apiHost}/subscription`,
      { params: { content_id: artistId } }
    ).subscribe({
      next: (response) => {
        this.isSubscribed = response.subscribed;
        this.checkingSubscription = false;
      },
      error: (err) => {
        console.error('Error checking subscription:', err);
        this.checkingSubscription = false;
      }
    });
  }

  toggleSubscription(): void {
    if (!this.id) return;
    if (this.isSubscribed)
      this.unsubscribe();
    else
      this.subscribe();
  }

  private unsubscribe(): void {
    this.http.request('DELETE', `${environment.apiHost}/subscription`, {
      body: {
        content_id: this.id,
        content_type: 'artist'
      }
    }).subscribe({
      next: () => {
        this.isSubscribed = false;
      },
      error: (err) => {
        console.error('Error unsubscribing:', err);
        this.error = 'Failed to unsubscribe. Please try again.';
      }
    });
  }

  private subscribe(): void {
    this.http.post(
      `${environment.apiHost}/subscription`,
      {
        content_id: this.id,
        content_type: 'artist'
      }
    ).subscribe({
      next: () => {
        this.isSubscribed = true;
      },
      error: (err) => {
        console.error('Error subscribing:', err);
        this.error = 'Failed to subscribe. Please try again.';
      }
    });
  }
}

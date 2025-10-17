import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../env/environment';
import { Artist } from '../model/artist.model';

@Component({
  selector: 'app-artist-details',
  standalone: false,
  templateUrl: './artist-details.component.html',
  styleUrls: ['./artist-details.component.css']
})
export class ArtistDetailsComponent implements OnInit {
  artist?: Artist;
  loading = true;
  error?: string;
  isSubscribed = false;
  checkingSubscription = true;
  artistId = '';

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.artistId = this.route.snapshot.paramMap.get('id') ?? '';
    if (this.artistId) {
      this.loadArtist(this.artistId);
      this.checkSubscription(this.artistId);
    }
  }

  loadArtist(artistId: string): void {
    this.loading = true;
    this.error = undefined;

    this.http.get<Artist>(`${environment.apiHost}/artists/${artistId}`)
      .subscribe({
        next: (artist) => {
          this.artist = artist;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading artist:', err);
          this.error = 'Failed to load artist. Please try again.';
          this.loading = false;
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
    if (!this.artist || !this.artistId) return;

    if (this.isSubscribed) {
      this.http.request('DELETE', `${environment.apiHost}/subscription`, {
        body: {
          content_id: this.artistId,
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
    } else {
      this.http.post(
        `${environment.apiHost}/subscription`,
        {
          content_id: this.artistId,
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
}

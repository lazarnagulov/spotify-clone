import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../env/environment';
import { SubscriptionDisplay } from '../model/subscription.model';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-subscriptions',
  standalone: false,
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.css']
})
export class SubscriptionsComponent implements OnInit {
  artistSubscriptions: SubscriptionDisplay[] = [];
  genreSubscriptions: SubscriptionDisplay[] = [];
  availableGenres: string[] = [];
  loading = true;
  loadingGenres = false;
  error?: string;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadGenres();
    this.loadSubscriptions();
  }

  loadGenres(): void {
    this.loadingGenres = true;

    this.http.get<{ genres: string[] }>(`${environment.apiHost}/genres`)
      .pipe(map(response => response.genres || []))
      .subscribe({
        next: (genres) => {
          console.log('Loaded genres:', genres);
          this.availableGenres = genres;
          this.loadingGenres = false;
        },
        error: (err) => {
          console.error('Error loading genres:', err);
          this.loadingGenres = false;
        }
      });
  }

  loadSubscriptions(): void {
    this.loading = true;
    this.error = undefined;

    this.http.get<SubscriptionDisplay[]>(
      `${environment.apiHost}/subscriptions`,
    ).subscribe({
      next: (subscriptions) => {
        console.log('Loaded subscriptions:', subscriptions);

        this.artistSubscriptions = subscriptions.filter(sub => sub.type === 'artist');
        this.genreSubscriptions = subscriptions.filter(sub => sub.type === 'genre');

        console.log('Artist subscriptions:', this.artistSubscriptions);
        console.log('Genre subscriptions:', this.genreSubscriptions);

        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading subscriptions:', err);
        this.error = 'Failed to load subscriptions. Please try again.';
        this.loading = false;
      }
    });
  }

  unsubscribeArtist(subscription: SubscriptionDisplay): void {
    const request = {
      content_id: subscription.contentId,
      content_type: 'artist'
    };
    console.log('Unsubscribing from artist:', request);

    this.http.request('DELETE', `${environment.apiHost}/subscription`, {
      body: request
    }).subscribe({
      next: () => {
        console.log('Successfully unsubscribed from artist');
        this.artistSubscriptions = this.artistSubscriptions.filter(
          s => s.contentId !== subscription.contentId
        );
      },
      error: (err) => {
        console.error('Error unsubscribing from artist:', err);
        this.error = 'Failed to unsubscribe from artist. Please try again.';
      }
    });
  }

  unsubscribeGenre(subscription: SubscriptionDisplay): void {
    const request = {
      content_id: subscription.contentId,
      content_type: 'genre'
    };
    console.log('Unsubscribing from genre:', request);

    this.http.request('DELETE', `${environment.apiHost}/subscription`, {
      body: request
    }).subscribe({
      next: () => {
        console.log('Successfully unsubscribed from genre');
        this.genreSubscriptions = this.genreSubscriptions.filter(
          s => s.contentId !== subscription.contentId
        );
      },
      error: (err) => {
        console.error('Error unsubscribing from genre:', err);
        this.error = 'Failed to unsubscribe from genre. Please try again.';
      }
    });
  }

  subscribeToGenre(genre: string): void {
    const request = {
      content_id: genre,
      content_type: 'genre'
    };
    console.log('Subscribing to genre:', request);

    this.http.post(
      `${environment.apiHost}/subscription`,
      request,
    ).subscribe({
      next: () => {
        console.log('Successfully subscribed to genre');
        this.genreSubscriptions.push({
          contentId: genre,
          type: 'genre',
          name: genre
        });
      },
      error: (err) => {
        console.error('Error subscribing to genre:', err);
        this.error = 'Failed to subscribe to genre. Please try again.';
      }
    });
  }

  isSubscribedToGenre(genre: string): boolean {
    return this.genreSubscriptions.some(sub => sub.contentId === genre);
  }

}

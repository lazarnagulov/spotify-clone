import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../env/environment';


@Component({
  selector: 'app-subscriptions',
  standalone: false,
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.css']
})
export class SubscriptionsComponent implements OnInit {
  subscriptions: SubscriptionDisplay[] = [];
  loading = true;
  error?: string;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadSubscriptions();
  }

  loadSubscriptions(): void {
    this.loading = true;
    this.error = undefined;

    const headers = this.getAuthHeaders();

    this.http.get<Subscription[]>(
      `${environment.apiHost}/subscriptions`,
      { headers }
    ).subscribe({
      next: (subscriptions) => {
        // Transform backend format to display format
        this.subscriptions = subscriptions.map(sub => ({
          contentId: sub.SK,
          type: sub.type,
          name: this.getDisplayName(sub),
          email: sub.email
        }));
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading subscriptions:', err);
        this.error = 'Failed to load subscriptions. Please try again.';
        this.loading = false;
      }
    });
  }

  unsubscribe(subscription: SubscriptionDisplay): void {
    const headers = this.getAuthHeaders();

    this.http.request('DELETE', `${environment.apiHost}/subscription`, {
      headers,
      body: {
        content_id: subscription.contentId,
        content_type: subscription.type
      }
    }).subscribe({
      next: () => {
        this.subscriptions = this.subscriptions.filter(
          s => s.contentId !== subscription.contentId
        );
      },
      error: (err) => {
        console.error('Error unsubscribing:', err);
        this.error = 'Failed to unsubscribe. Please try again.';
      }
    });
  }

  private getDisplayName(sub: Subscription): string {
    // You'll need to fetch actual names from artist/genre endpoints
    // For now, return the ID as placeholder
    return sub.SK;
  }

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('authToken');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }
}

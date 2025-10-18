import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../env/environment';
import { SubscriptionDisplay } from '../model/subscription.model';

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

    this.http.get<SubscriptionDisplay[]>(
      `${environment.apiHost}/subscriptions`,
      { headers: this.getAuthHeaders() }
    ).subscribe({
      next: (subscriptions) => {
        console.log('Loaded subscriptions:', subscriptions);
        this.subscriptions = subscriptions;
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
    const request = {
      content_id: subscription.contentId,
      content_type: subscription.type
    };
    console.log('Unsubscribing:', request);

    this.http.request('DELETE', `${environment.apiHost}/subscription`, {
      headers: this.getAuthHeaders(),
      body: request
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

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('authToken');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }
}

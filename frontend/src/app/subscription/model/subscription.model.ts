interface Subscription {
  PK: string;          // user_id
  SK: string;          // content_id
  type: string;        // 'artist' | 'genre'
  email?: string;
  username?: string;
}

interface SubscriptionDisplay {
  contentId: string;
  type: string;
  name: string;
  email?: string;
}

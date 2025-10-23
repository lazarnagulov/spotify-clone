export interface CreateListeningHistoryRequest {
  songId: string;
  albumId?: string;
  genres: string[];
  artists: string[];
}

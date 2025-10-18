export interface Song {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  duration: number;
  track_number?: number;
  description: string;
  audioUrl: string;
  coverUrl: string;
  album?: {
    id: string;
    title: string;
    year: number;
    cover_url: string;
  };
  created_at: string;
  related_songs: any[];
}

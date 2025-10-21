export interface Song {
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

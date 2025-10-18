import { Song } from './song.model';

export interface Album {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  year?: number;
  description?: string;
  cover_url: string;
  songs: Song[];
  created_at?: string;
  coverUrl?: string;
}

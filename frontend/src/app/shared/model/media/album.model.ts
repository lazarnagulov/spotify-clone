import {Song} from './song.model';

export interface Album {
  id: string;
  title: string;
  artists: string[];
  artist_ids: string[];
  genres: string[];
  year?: number;
  description?: string;
  songs: Song[];
  coverUrl?: string;
}

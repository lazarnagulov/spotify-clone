import { Song } from './song.model';

export interface Album {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  year?: number;
  description?: string;
  songs: Song[];
  coverUrl?: string;
}

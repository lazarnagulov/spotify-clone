export interface OfflineSongData {
  id: string;
  blob: Blob;
  downloadedAt: number;
  title: string;
  artists: string[];
  coverUrl?: string;
  duration: number;
}

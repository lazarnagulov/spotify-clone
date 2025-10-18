import { Artist } from "../../artist/model/create-artist.model";
import { Album } from "../../shared/model/media/album.model";
import { Song } from "../../shared/model/media/song.model";

export interface DiscoverResponse {
  songs: Song[];
  albums: Album[];
  artists: Artist[];
}
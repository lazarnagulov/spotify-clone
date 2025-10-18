import { Component, OnInit } from '@angular/core';
import { Album } from '../../shared/model/media/album.model';
import { Song } from '../../shared/model/media/song.model';
import { Artist } from '../../artist/model/artist-details.model';
import { DiscoverService } from '../discover.service';
import { GenreService } from '../../shared/genre.service';

@Component({
  selector: 'app-discover',
  standalone: false,
  templateUrl: './discover.component.html',
  styleUrl: './discover.component.css'
})
export class DiscoverComponent implements OnInit {
  genres: string[] = [];
  albums: Album[] = [];
  songs: Song[] = [];
  artists: Artist[] = [];

  selectedGenre: string | null = null;

  constructor(
    private discoverService: DiscoverService,
    private genreService: GenreService
  ) { }

  ngOnInit(): void {
    this.genreService.getGenres().subscribe({
      next: (genres) => this.genres = genres,
      error: (err) => console.error('Error fetching genres', err)
    });
  }

  navigateToArtist(artistId: string): void {
    // TODO: navigate to artist details page
  }

  onGenreChange() {
    if (!this.selectedGenre) return;
    this.discoverService.getGenreData(this.selectedGenre).subscribe(response => {
      this.songs = response.songs;
      this.albums = response.albums;
      this.artists = response.artists;
    });
  }


}

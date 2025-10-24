import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../env/environment';

interface Album {
  id: string;
  title: string;
  artists: string[];
  genres: string[];
  year?: number;
  cover_url?: string;
}

interface Song {
  id: string;
  title: string;
  artists: string[];
  cover_url?: string;
}

interface Artist {
  id: string;
  name: string;
  genres: string[];
}

interface HomeData {
  albums: Album[];
  songs: Song[];
  artists: Artist[];
}

@Component({
  selector: 'app-home',
  standalone: false,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  albums: Album[] = [];
  songs: Song[] = [];
  artists: Artist[] = [];
  loading = true;
  error: string | null = null;

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.loadHomeData();
  }

  private loadHomeData(): void {
    this.http.get<HomeData>(`${environment.apiHost}/feed`).subscribe({
      next: (data) => {
        console.log(data);
        this.albums = data.albums || [];
        this.songs = data.songs || [];
        this.artists = data.artists || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load home data:', err);
        this.error = 'Failed to load content. Please try again later.';
        this.loading = false;
      }
    });
  }

  getArtistString(artists: string[]): string {
    return artists && artists.length > 0 ? artists.join(', ') : 'Unknown Artist';
}

  navigateToArtist(artistId: string): void {
    this.router.navigate(['/artist', artistId]);
  }
}

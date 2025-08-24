import { Component } from '@angular/core';

@Component({
  selector: 'app-album-details',
  standalone: false,
  templateUrl: './album-details.component.html',
  styleUrl: './album-details.component.css'
})
export class AlbumDetailsComponent {
  album = {
    id: 11,
    title: 'Code Symphony',
    artistName: 'The Rolling Codes',
    year: 2025,
    imageUrl: 'https://placehold.co/400x400?text=Album',
    songs: [
      { id: 201, title: 'Binary Dreams', duration: '3:45' },
      { id: 202, title: 'Refactor Rhapsody', duration: '4:12' },
      { id: 203, title: 'Infinite Loop', duration: '5:05' }
    ]
  };
}

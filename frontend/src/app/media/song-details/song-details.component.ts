import { Component } from '@angular/core';

@Component({
  selector: 'app-song-details',
  standalone: false,
  templateUrl: './song-details.component.html',
  styleUrl: './song-details.component.css'
})
export class SongDetailsComponent {
  song = {
    id: 101,
    title: 'Hello World Anthem',
    artistName: 'The Rolling Codes',
    albumName: 'Code Symphony',
    duration: '3:45',
    imageUrl: 'https://placehold.co/400x400?text=Song',
    relatedSongs: [
      { id: 301, title: 'Syntax Sonata', imageUrl: 'https://placehold.co/300x300?text=Song+3' },
      { id: 302, title: 'Compiler Concerto', imageUrl: 'https://placehold.co/300x300?text=Song+4' }
    ]
  };
}

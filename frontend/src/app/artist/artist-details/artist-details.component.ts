import { Component } from '@angular/core';

@Component({
  selector: 'app-artist-details',
  standalone: false,
  templateUrl: './artist-details.component.html',
  styleUrl: './artist-details.component.css'
})
export class ArtistDetailsComponent {
  artist = {
    id: 1,
    name: 'The Rolling Codes',
    bio: 'A legendary coding rock band known for their complex riffs and bug-free jams.',
    imageUrl: 'https://placehold.co/600x400?text=Artist',
    albums: [
      { id: 11, title: 'Code Symphony', imageUrl: 'https://placehold.co/300x300?text=Album+1' },
      { id: 12, title: 'Debugging Blues', imageUrl: 'https://placehold.co/300x300?text=Album+2' }
    ],
    songs: [
      { id: 101, title: 'Hello World Anthem', imageUrl: 'https://placehold.co/300x300?text=Song+1' },
      { id: 102, title: 'Null Pointer Serenade', imageUrl: 'https://placehold.co/300x300?text=Song+2' }
    ]
  };
}

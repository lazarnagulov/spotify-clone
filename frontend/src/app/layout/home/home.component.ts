import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  standalone: false,
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  mediaItems = [
    {
      title: 'Imagine Dragons',
      subtitle: 'Artist',
      description: 'Popular alternative rock band known for energetic performances.',
      imageUrl: 'https://i.scdn.co/image/ab6761610000e5eb6b5b5b5b5b5b5b5b5b5b5b5'
    },
    {
      title: 'Evolve',
      subtitle: 'Album',
      description: 'Released in 2017 with hits like "Believer" and "Thunder".',
      imageUrl: 'https://i.scdn.co/image/ab67616d0000b2732b2b2b2b2b2b2b2b2b2b2b2b'
    },
    {
      title: 'Believer',
      subtitle: 'Song',
      description: 'One of Imagine Dragons’ most streamed tracks worldwide.',
      imageUrl: 'https://i.scdn.co/image/ab67616d00004851a3a3a3a3a3a3a3a3a3a3a3a3'
    },
    {
      title: 'Adele',
      subtitle: 'Artist',
      description: 'Grammy-winning singer with timeless ballads.',
      imageUrl: 'https://i.scdn.co/image/ab6761610000e5ebb3b3b3b3b3b3b3b3b3b3b3b3'
    },
    {
      title: '25',
      subtitle: 'Album',
      description: 'Award-winning album featuring "Hello".',
      imageUrl: 'https://i.scdn.co/image/ab67616d0000b273c4c4c4c4c4c4c4c4c4c4c4c4'
    },
    {
      title: 'Hello',
      subtitle: 'Song',
      description: 'Iconic single that broke multiple streaming records.',
      imageUrl: 'https://i.scdn.co/image/ab67616d00004851d5d5d5d5d5d5d5d5d5d5d5d5'
    }
  ];
}

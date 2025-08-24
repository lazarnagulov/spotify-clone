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
      cardType: "artist",
      title: 'Imagine Dragons',
      subtitle: 'Artist',
      description: 'Popular alternative rock band known for energetic performances.',
      imageUrl: 'https://i.scdn.co/image/ab67616100005174ab47d8dae2b24f5afe7f9d38'
    },
    {
      cardType: "album",
      title: 'Evolve',
      subtitle: 'Album',
      description: 'Released in 2017 with hits like "Believer" and "Thunder".',
      imageUrl: 'https://upload.wikimedia.org/wikipedia/en/1/11/Evolve_Box_Art.png'
    },
    {
      cardType: "song",
      title: 'Believer',
      subtitle: 'Song',
      description: 'One of Imagine Dragons’ most streamed tracks worldwide.',
      imageUrl: 'https://i.scdn.co/image/ab67616d0000b2735675e83f707f1d7271e5cf8a'
    },
    {
      cardType: "artist",
      title: 'Adele',
      subtitle: 'Artist',
      description: 'Grammy-winning singer with timeless ballads.',
      imageUrl: 'https://i.scdn.co/image/ab6761610000e5ebb3b3b3b3b3b3b3b3b3b3b3b3'
    },
    {
      cardType: "album",
      title: '25',
      subtitle: 'Album',
      description: 'Award-winning album featuring "Hello".',
      imageUrl: 'https://i.scdn.co/image/ab67616d0000b273c4c4c4c4c4c4c4c4c4c4c4c4'
    },
    {
      cardType: "song",
      title: 'Hello',
      subtitle: 'Song',
      description: 'Iconic single that broke multiple streaming records.',
      imageUrl: 'https://i.scdn.co/image/ab67616d00004851d5d5d5d5d5d5d5d5d5d5d5d5'
    }
  ];
}

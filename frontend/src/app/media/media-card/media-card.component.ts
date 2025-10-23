import { Component, EventEmitter, Input, Output, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-media-card',
  standalone: false,
  templateUrl: './media-card.component.html',
  styleUrl: './media-card.component.css'
})
export class MediaCardComponent implements OnDestroy {
  @Input() cardType: string = 'album';
  @Input() id!: string;
  @Input() title!: string;
  @Input() subtitle!: string;
  @Input() description?: string;
  @Input() imageUrl!: string;
  @Input() audioUrl?: string;

  @Output() play = new EventEmitter<void>();
  @Output() cardClick = new EventEmitter<void>();

  private audio: HTMLAudioElement | null = null;
  isPlaying = false;

  constructor(private router: Router) {}

  onPlayClick(event: MouseEvent) {
    event.stopPropagation();

    if (this.cardType === 'song' && this.audioUrl) {
      this.togglePlayback();
    } else {
      this.play.emit();
    }
  }

  onCardClick() {
    let id = this.id.split("#")[1];
    if (!id) id = this.id;
    
    if (this.cardType === 'song' && id) {
      void this.router.navigate(['/song', id]);
    } else if (this.cardType === 'album' && id) {
      void this.router.navigate(['/album', id]);
    } else {
      this.cardClick.emit();
    }
  }

  private togglePlayback() {
    if (!this.audioUrl) return;

    if (this.isPlaying) {
      this.pauseAudio();
    } else {
      this.playAudio();
    }
  }

  private playAudio() {
    if (!this.audio) {
      this.audio = new Audio(this.audioUrl);
      this.audio.onended = () => {
        this.isPlaying = false;
      };
    }

    this.audio.play();
    this.isPlaying = true;
  }

  private pauseAudio() {
    if (this.audio) {
      this.audio.pause();
      this.isPlaying = false;
    }
  }

  ngOnDestroy() {
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }
  }
}

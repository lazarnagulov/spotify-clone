import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-media-card',
  standalone: false,
  templateUrl: './media-card.component.html',
  styleUrl: './media-card.component.css'
})
export class MediaCardComponent {
  @Input() title!: string;
  @Input() subtitle!: string;
  @Input() description?: string;
  @Input() imageUrl!: string;
}

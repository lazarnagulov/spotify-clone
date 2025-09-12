import {Component, OnInit} from '@angular/core';
import {ArtistService} from '../artist.service';
import {ActivatedRoute} from '@angular/router';
import {EMPTY, switchMap} from 'rxjs';
import {Artist} from '../model/create-artist.model';

@Component({
  selector: 'app-artist-details',
  standalone: false,
  templateUrl: './artist-details.component.html',
  styleUrl: './artist-details.component.css'
})
export class ArtistDetailsComponent implements OnInit {
  id?: string;
  artist?: Artist;

  constructor(
    private artistService: ArtistService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.paramMap.pipe(
      switchMap(params => {
        const id = params.get('id');
        this.id = id ?? undefined;
        return id ? this.artistService.getDetails(id) : EMPTY;
      })
    ).subscribe(artist => this.artist = artist);
  }
}

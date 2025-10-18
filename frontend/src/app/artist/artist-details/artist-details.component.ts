import { Component, OnInit } from '@angular/core';
import { ArtistService } from '../artist.service';
import { ActivatedRoute, Router } from '@angular/router';
import { EMPTY, switchMap } from 'rxjs';
import { Artist } from '../model/create-artist.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-artist-details',
  standalone: false,
  templateUrl: './artist-details.component.html',
  styleUrl: './artist-details.component.css',
})
export class ArtistDetailsComponent implements OnInit {
  id?: string;
  artist?: Artist;
  userRoles: string[] = [];

  constructor(
    private artistService: ArtistService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap
      .pipe(
        switchMap((params) => {
          const id = params.get('id');
          this.id = id ?? undefined;
          return id ? this.artistService.getDetails(id) : EMPTY;
        })
      )
      .subscribe(artist => this.artist = artist);

    this.userRoles = this.authService.getRoles();
  }

  onDelete(): void {
    if (!this.id) return;
    this.artistService.deleteArtist(this.id).subscribe({
      next: () => {
        this.snackBar.open('Artist successfully deleted', 'Close', { duration: 3000 });
        this.router.navigate(['/']);
      },
      error: () => {
        this.snackBar.open('Failed to delete artist', 'Close', { duration: 3000 });
      }
    });
  }
}

import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ArtistService } from '../artist.service';
import { GenreService } from '../../shared/genre.service';

@Component({
  selector: 'app-artist-editing',
  standalone: false,
  templateUrl: './artist-editing.component.html',
  styleUrls: ['./artist-editing.component.css'],
})
export class ArtistEditingComponent implements OnInit {
  artistForm!: FormGroup;
  allGenres: string[] = [];
  id!: string;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private artistService: ArtistService,
    private genreService: GenreService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.artistForm = this.fb.group({
      name: ['', Validators.required],
      bio: [
        '',
        [
          Validators.required,
          Validators.minLength(10),
          Validators.maxLength(500),
        ],
      ],
      genres: [[], Validators.required],
    });

    this.genreService.getGenres().subscribe({
      next: (genres) => (this.allGenres = genres),
      error: (err) => console.error('Error fetching genres', err),
    });

    this.id = this.route.snapshot.paramMap.get('id')!;
    this.loadArtistData();
  }

  loadArtistData(): void {
    this.artistService.getDetails(this.id).subscribe({
      next: (artist) => {
        this.artistForm.patchValue({
          name: artist.name,
          bio: artist.bio,
          genres: artist.genres,
        });
      },
      error: () => {
        this.snackBar.open('Error loading artist data', 'Close', {
          duration: 3000,
          panelClass: ['snackbar-error'],
        });
      },
    });
  }

  onSubmit(): void {
    if (this.artistForm.invalid) return;

    this.artistService.updateArtist(this.id, this.artistForm.value).subscribe({
      next: () => {
        this.snackBar.open('Artist successfully edited', 'Close', {
          duration: 3000,
        });
        void this.router.navigate(['/home']);
      },
      error: () => {
        this.snackBar.open('Failed to edit artist', 'Close', {
          duration: 3000,
        });
      },
    });
  }
}

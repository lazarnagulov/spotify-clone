import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { GenreService } from '../../shared/genre.service';
import { ArtistService } from '../artist.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-artist-creation',
  templateUrl: './artist-creation.component.html',
  styleUrls: ['./artist-creation.component.css'],
  standalone: false
})
export class ArtistCreationComponent implements OnInit {
  artistForm: FormGroup;
  allGenres: string[] = [];

  constructor(
    private fb: FormBuilder,
    private genreService: GenreService,
    private artistService: ArtistService,
    private router: Router
  ) {
    this.artistForm = this.fb.group({
      name: ['', Validators.required],
      bio: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(500)]],
      genres: [[], this.atLeastOneGenreSelected]
    });
  }

  ngOnInit(): void {
    this.genreService.getGenres().subscribe({
      next: (genres) => this.allGenres = genres,
      error: (err) => console.error('Error fetching genres', err)
    });
  }

  atLeastOneGenreSelected(control: AbstractControl): ValidationErrors | null {
    const value: string[] = control.value;
    return value && value.length > 0 ? null : { required: true };
  }

  onSubmit() {
    if (this.artistForm.valid) {
      console.log('Artist created:', this.artistForm.value);
      this.artistService.createArtist(this.artistForm.value).subscribe({
        next: (response) => {
          console.log('Artist successfully created:', response)
          void this.router.navigate(['/home']);
        },
        error: (err) => console.error('Error creating artist:', err)
      });
      this.artistForm.reset();
    } else {
      this.artistForm.markAllAsTouched();
    }
  }
}

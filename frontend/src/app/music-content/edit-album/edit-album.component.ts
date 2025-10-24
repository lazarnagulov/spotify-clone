import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { GenreService } from '../../shared/genre.service';
import { UploadService } from '../upload.service';
import { ArtistService } from '../../artist/artist.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Album } from '../../shared/model/media/album.model';
import { MusicContentService } from '../music-content.service';
import { Artist } from '../../artist/model/artist.model';
import { catchError, EMPTY, of, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-edit-album',
  standalone: false,
  templateUrl: './edit-album.component.html',
  styleUrl: './edit-album.component.css'
})
export class EditAlbumComponent implements OnInit{
  id?: string;
  albumForm: FormGroup;
  genres: string[] = [];
  album?: Album;
  error: string | null = null;
  coverFile?: File;
  coverPreviewUrl?: string;
  serverError?: string;
  loading = false;
  artists: Artist[] = [];

  constructor(
    private fb: FormBuilder,
    private service: MusicContentService,
    private genreService: GenreService,
    private artistService: ArtistService,
    private uploadService: UploadService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.albumForm = this.fb.group({
      title: ['', Validators.required],
      artists: [[], Validators.required],
      genres: [[], Validators.required],
      year: [new Date().getFullYear(), [Validators.required, Validators.min(1900), Validators.max(new Date().getFullYear())]],
      description: ['']
    });
  }

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? undefined;
    if (!this.id) {
      this.error = 'Album ID not provided';
      this.loading = false;
      return;
    }

    this.fetchGenres();
    this.fetchArtists();
  }

  onCoverSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.coverFile = file;
      const reader = new FileReader();
      reader.onload = () => this.coverPreviewUrl = reader.result as string;
      reader.readAsDataURL(file);
    }
  }

  private fetchGenres(): void {
    this.genreService.getGenres().subscribe({
      next: (genres: string[]) => this.genres = genres
    });
  }

  private fetchArtists(): void {
    this.artistService.getArtists().subscribe({
      next: (response) => {
        this.artists = response.artists
        this.loadAlbum(this.id!);
      }
    });
  }

  loadAlbum(albumId: string): void {
    this.service.getAlbum(albumId).subscribe({
      next: (album: Album) => {
        this.album = album;
        this.albumForm.patchValue({
          title: album.title,
          artists: album.artist_ids,
          genres: album.genres,
          year: album.year,
          description: album.description
        });
        this.coverPreviewUrl = album.coverUrl;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load album:', err);
        this.error = 'Failed to load album. Please try again later.';
        this.loading = false;
      },
    });
  }

  onSubmit(): void {
    if (this.albumForm.invalid || !this.album) {
      this.serverError = 'Please fill all required fields';
      return;
    }

    this.loading = true;
    this.serverError = undefined;

    const formValue = this.albumForm.value;

    const updatedData = {
      title: formValue.title,
      artists: formValue.artists,
      genres: formValue.genres,
      year: formValue.year,
      description: formValue.description || '',
      coverType: this.coverFile ? this.coverFile.type : undefined
    };

    console.log('Updating album with data:', updatedData);

    this.service.updateAlbum(this.id, updatedData).pipe(
      switchMap(response => {
        console.log('Album update response:', response);
        console.log('Cover file to upload:', this.coverFile);
        if (this.coverFile && response.presignedCoverUrl) {
          console.log('Uploading new album cover...');
          console.log('Presigned URL:', response.presignedCoverUrl);
          return this.uploadService.uploadFileToS3(
            response.presignedCoverUrl,
            this.coverFile,
            this.coverFile.type
          ).pipe(
            tap(() => console.log('Album cover uploaded'))
          );
        }
        return of(null);
      }),
      tap(() => {
        console.log('Album updated successfully!');
        this.loading = false;
        void this.router.navigate(['/album', this.id]);
      }),
      catchError(err => {
        console.error('Album update failed:', err);
        this.serverError = err.error?.message || 'Album update failed. Please try again.';
        this.loading = false;
        return EMPTY;
      })
    ).subscribe();
  }

}

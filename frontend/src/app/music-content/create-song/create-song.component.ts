import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {GenreService} from '../../shared/genre.service';
import {UploadService} from '../upload.service';
import {HttpClient} from '@angular/common/http';
import {catchError, EMPTY, finalize, switchMap, tap, forkJoin} from 'rxjs';
import {environment} from '../../../env/environment';
import {ArtistService} from '../../artist/artist.service';
import {Artist} from '../../artist/model/create-artist.model';
import {Router} from '@angular/router';

@Component({
  selector: 'app-create-song',
  templateUrl: './create-song.component.html',
  standalone: false,
  styleUrls: ['./create-song.component.css']
})
export class CreateSongComponent implements OnInit {
  songForm: FormGroup;
  genres: string[] = [];
  artists: Artist[] = [];

  previewUrl?: string;
  audioPreviewUrl?: string;
  coverFile?: File;
  audioFile?: File;
  metadata?: any;
  serverError?: string;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private genreService: GenreService,
    private uploadService: UploadService,
    private artistService: ArtistService,
    private router: Router,
    private http: HttpClient
  ) {
    this.songForm = this.fb.group({
      title: ['', Validators.required],
      genres: [[], Validators.required],
      artists: [[], Validators.required],
      description: [''],
      file: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.fetchGenres();
    this.fetchArtists();
  }

  onImageSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.coverFile = file;
      const reader = new FileReader();
      reader.onload = () => this.previewUrl = reader.result as string;
      reader.readAsDataURL(file);
    }
  }

  onFileSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.audioFile = file;
      this.songForm.patchValue({file});
      this.audioPreviewUrl = URL.createObjectURL(file);
      this.metadata = {
        filename: file.name,
        type: file.type,
        size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
        createdAt: new Date().toLocaleString(),
        modifiedAt: new Date(file.lastModified).toLocaleString()
      };

      console.log('Audio file selected - Raw type:', file.type);
    }
  }

  onSubmit(): void {
    if (this.songForm.invalid || !this.audioFile) return;

    this.loading = true;
    this.serverError = undefined;

    const formValue = this.songForm.value;

    let audioContentType = this.audioFile.type || 'audio/mpeg';

    if (audioContentType === 'audio/mp3' || audioContentType === 'audio/mpeg3') {
      audioContentType = 'audio/mpeg';
    }

    const requestBody = {
      title: formValue.title,
      genres: formValue.genres,
      artists: formValue.artists,
      album_id: formValue.albumId || undefined,
      description: formValue.description || '',
      cover_type: this.coverFile?.type ?? 'image/jpeg',
      audio_type: audioContentType
    };

    console.log('Audio file details:', {
      name: this.audioFile.name,
      rawType: this.audioFile.type,
      normalizedType: audioContentType,
      size: this.audioFile.size
    });

    this.http.post<{
      coverUploadPresignedUrl: string;
      audioUploadPresignedUrl: string;
    }>(`${environment.apiHost}/songs`, requestBody).pipe(
      switchMap(response => {
        console.log('Presigned URLs received:', {
          cover: response.coverUploadPresignedUrl,
          audio: response.audioUploadPresignedUrl
        });
        const uploads = [];

        uploads.push(
          this.uploadService.uploadFileToS3(
            response.audioUploadPresignedUrl,
            this.audioFile!,
            audioContentType
          ).pipe(
            tap(() => console.log('Audio upload successful')),
            catchError(err => {
              console.error('Audio upload failed:', err);
              throw err;
            })
          )
        );

        if (this.coverFile) {
          uploads.push(
            this.uploadService.uploadFileToS3(
              response.coverUploadPresignedUrl,
              this.coverFile,
              this.coverFile.type
            ).pipe(
              tap(() => console.log('Cover upload successful')),
              catchError(err => {
                console.error('Cover upload failed:', err);
                throw err;
              })
            )
          );
        }

        return forkJoin(uploads);
      }),
      tap(() => {
        console.log('Song created and files uploaded successfully');
        this.songForm.reset();
        this.previewUrl = undefined;
        this.audioPreviewUrl = undefined;
        this.coverFile = undefined;
        this.audioFile = undefined;
        this.metadata = undefined;
        void this.router.navigate(["/home"]);
      }),
      catchError(err => {
        console.error('Upload failed', err);
        this.serverError = err.error?.message || 'Upload failed. Please try again.';
        return EMPTY;
      }),
      finalize(() => {
        this.loading = false;
      })
    ).subscribe();
  }

  private fetchGenres(): void {
    this.genreService.getGenres().subscribe({
      next: (genres: string[]) => this.genres = genres
    });
  }

  private fetchArtists(): void {
    this.artistService.getArtists().subscribe({
      next: (response) => this.artists = response.artists,
    });
  }
}

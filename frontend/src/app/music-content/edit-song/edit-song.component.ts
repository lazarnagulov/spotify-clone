import { Component, OnInit } from '@angular/core';
import { Song } from '../../shared/model/media/song.model';
import { ActivatedRoute, Router } from '@angular/router';
import { MediaService } from '../../media/media.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { GenreService } from '../../shared/genre.service';
import { UploadService } from '../upload.service';
import { ArtistService } from '../../artist/artist.service';
import { Artist } from '../../artist/model/artist.model';
import { MusicContentService } from '../music-content.service';
import { catchError, EMPTY, finalize, forkJoin, of, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-edit-song',
  standalone: false,
  templateUrl: './edit-song.component.html',
  styleUrl: './edit-song.component.css'
})
export class EditSongComponent implements OnInit {
  id?: string;
  song?: Song;
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
    private route: ActivatedRoute,
    private service: MusicContentService,
    private mediaService: MediaService,
    private uploadService: UploadService,
    private fb: FormBuilder,
    private genreService: GenreService,
    private artistService: ArtistService,
    private router: Router,
  )
  {
    this.songForm = this.fb.group({
      title: ['', Validators.required],
      genres: [[], Validators.required],
      artists: [[], Validators.required],
      description: [''],
      file: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? undefined;
    if (this.id) {
      this.loadSong(this.id)
      this.fetchGenres();
      this.fetchArtists();
    }
  }

  loadSong(songId?: string): void {
    if (!songId) return;

    this.mediaService.getSong(songId).subscribe({
      next: (song) => {
        this.song = song;
        const cacheBuster = `?v=${Date.now()}`;
        console.log('Loaded song: ', song);
        this.songForm.patchValue({
          title: song.title,
          genres: song.genres || [],
          artists: song.artist_ids || [],
          description: song.description || ''
        });

        if (song.cover_url) this.previewUrl = `${song.cover_url}${cacheBuster}`;
        if (song.audio_url) this.audioPreviewUrl = `${song.audio_url}${cacheBuster}`;

      },
      error: (err) => console.error('Error loading song: ', err)
    });
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
    console.log(this.songForm.value);

    this.loading = true;
    this.serverError = undefined;

    const formValue = this.songForm.value;
    const hasNewAudio = !!this.audioFile;
    const hasNewCover = !!this.coverFile;

    const audioContentType = this.audioFile?.type || 'audio/mpeg';
    const coverContentType = this.coverFile?.type || 'image/jpeg';

    const requestBody: any = {
      title: formValue.title,
      genres: formValue.genres,
      artists: formValue.artists,
      description: formValue.description || '',
      album_id: formValue.albumId || undefined,
      size: this.metadata.size || undefined,
    };

    if (hasNewAudio || hasNewCover) {
      requestBody.coverType = hasNewCover ? coverContentType : undefined;
      requestBody.audioType = hasNewAudio ? audioContentType : undefined;
    }

    this.service
      .updateSong(this.id!, requestBody)
      .pipe(
        switchMap((response) => {
          const uploads = [];

          console.log('has new audio:', hasNewAudio);
          console.log("response from updateSong: ", response);

          if (response.audioUploadPresignedUrl && hasNewAudio) {
            uploads.push(
              this.uploadService
                .uploadFileToS3(
                  response.audioUploadPresignedUrl,
                  this.audioFile!,
                  audioContentType
                )
                .pipe(tap(() => console.log('Audio updated')))
            );
          }

          if (response.coverUploadPresignedUrl && hasNewCover) {
            uploads.push(
              this.uploadService
                .uploadFileToS3(
                  response.coverUploadPresignedUrl,
                  this.coverFile!,
                  coverContentType
                )
                .pipe(tap(() => console.log('Cover updated')))
            );
          }

          return uploads.length ? forkJoin(uploads) : of(null);
        }),
        tap(() => {
          console.log('Song updated successfully');
          void this.router.navigate(['/song', this.id]);
        }),
        catchError((err) => {
          console.error('Update failed:', err);
          this.serverError = err.error?.message || 'Update failed. Please try again.';
          return EMPTY;
        }),
        finalize(() => (this.loading = false))
      )
      .subscribe();
  }

}

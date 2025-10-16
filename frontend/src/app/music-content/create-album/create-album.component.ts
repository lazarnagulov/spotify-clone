import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {GenreService} from '../../shared/genre.service';
import {UploadService} from '../upload.service';
import {HttpClient} from '@angular/common/http';
import {catchError, EMPTY, finalize, switchMap, tap, forkJoin} from 'rxjs';
import {environment} from '../../../env/environment';
import {ArtistService} from '../../artist/artist.service';

interface SongFile {
  file: File;
  title: string;
  duration?: number;
  description?: string;
  coverFile?: File;
  coverPreviewUrl?: string;
}

@Component({
  selector: 'app-create-album',
  templateUrl: './create-album.component.html',
  standalone: false,
  styleUrls: ['./create-album.component.css']
})
export class CreateAlbumComponent implements OnInit {
  albumForm: FormGroup;
  genres: string[] = [];
  artists: {id: string, name:string}[] = [];

  coverFile?: File;
  coverPreviewUrl?: string;
  songFiles: SongFile[] = [];

  serverError?: string;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private genreService: GenreService,
    private uploadService: UploadService,
    private artistService: ArtistService,
    private http: HttpClient
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

  onSongsSelected(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    if (files) {
      this.songFiles = [];

      Array.from(files).forEach((file, index) => {
        const title = this.extractSongTitle(file.name);

        const songFile: SongFile = {
          file: file,
          title: title,
          duration: undefined
        };

        this.songFiles.push(songFile);

        const audio = new Audio();
        audio.src = URL.createObjectURL(file);

        audio.addEventListener('loadedmetadata', () => {
          this.songFiles[index].duration = Math.round(audio.duration);
          URL.revokeObjectURL(audio.src);
        });
      });
    }
  }

  onSongTitleChange(event: Event, index: number): void {
    const input = event.target as HTMLInputElement;
    this.updateSongTitle(index, input.value);
  }

  extractSongTitle(filename: string): string {
    return filename
      .replace(/\.[^/.]+$/, '')
      .replace(/[_-]/g, ' ')
      .trim();
  }

  removeSong(index: number): void {
    this.songFiles.splice(index, 1);
  }

  updateSongTitle(index: number, newTitle: string): void {
    this.songFiles[index].title = newTitle;
  }

  onSubmit(): void {
    if (this.albumForm.invalid || this.songFiles.length === 0) {
      this.serverError = 'Please fill all required fields and add at least one song';
      return;
    }

    if (!this.coverFile) {
      this.serverError = 'Album cover is required';
      return;
    }

    this.loading = true;
    this.serverError = undefined;

    const formValue = this.albumForm.value;

    const albumData = {
      title: formValue.title,
      artists: formValue.artists,
      genres: formValue.genres,
      year: formValue.year,
      description: formValue.description || '',
      cover_type: this.coverFile.type,
      songs: this.songFiles.map(sf => ({
        title: sf.title,
        audio_type: sf.file.type ?? 'audio/mpeg',
        duration: sf.duration ?? 0,
        description: sf.description ?? '',
        cover_type: sf.coverFile?.type ?? null
      }))
    };

    console.log('Creating album with data:', albumData);

    this.http.post<{
      album_id: string;
      album_cover_upload_url: string;
      songs: Array<{
        song_id: string;
        title: string;
        track_number: number;
        upload_url: string;
        cover_upload_url?: string;
      }>;
    }>(`${environment.apiHost}/albums`, albumData).pipe(
      switchMap(response => {
        console.log('Album created, uploading files...', response);

        const uploads = [];

        console.log('Uploading album cover...');
        uploads.push(
          this.uploadService.uploadFileToS3(
            response.album_cover_upload_url,
            this.coverFile!,
            this.coverFile!.type
          ).pipe(
            tap(() => console.log('Album cover uploaded'))
          )
        );

        response.songs.forEach((songInfo, index) => {
          const songFile = this.songFiles.find(sf => sf.title === songInfo.title);

          if (songFile) {
            console.log(`Uploading song ${songInfo.track_number}: ${songInfo.title}...`);
            uploads.push(
              this.uploadService.uploadFileToS3(
                songInfo.upload_url,
                songFile.file,
                songFile.file.type || 'audio/mpeg'
              ).pipe(
                tap(() => console.log(`Song ${songInfo.track_number} uploaded: ${songInfo.title}`))
              )
            );

            if (songFile.coverFile && songInfo.cover_upload_url) {
              console.log(`Uploading cover for song ${songInfo.track_number}: ${songInfo.title}...`);
              uploads.push(
                this.uploadService.uploadFileToS3(
                  songInfo.cover_upload_url,
                  songFile.coverFile,
                  songFile.coverFile.type
                ).pipe(
                  tap(() => console.log(`Cover uploaded for song ${songInfo.track_number}: ${songInfo.title}`))
                )
              );
            }
          }
        });

        return forkJoin(uploads);
      }),
      tap(() => {
        console.log('Album created and all files uploaded successfully!');
        this.albumForm.reset({ year: new Date().getFullYear() });
        this.coverFile = undefined;
        this.coverPreviewUrl = undefined;
        this.songFiles = [];
      }),
      catchError(err => {
        console.error('Album creation failed:', err);
        this.serverError = err.error?.message || 'Album creation failed. Please try again.';
        return EMPTY;
      }),
      finalize(() => {
        this.loading = false;
      })
    ).subscribe();
  }


  onSongDescriptionChange(event: Event, index: number): void {
    const input = event.target as HTMLTextAreaElement;
    this.songFiles[index].description = input.value;
  }

  onSongCoverSelected(event: Event, index: number): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.songFiles[index].coverFile = file;
      const reader = new FileReader();
      reader.onload = () =>
        this.songFiles[index].coverPreviewUrl = reader.result as string;
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
      next: (response) => this.artists = response.artists,
    });
  }
}

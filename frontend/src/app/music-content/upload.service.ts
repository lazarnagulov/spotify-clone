import { Injectable } from '@angular/core';
import {from, of, switchMap, throwError} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {

  uploadFileToS3(presignedUrl: string, file: File, contentType?: string) {
    const actualContentType = contentType || file.type;

    console.log('Uploading file:', {
      name: file.name,
      fileType: file.type,
      actualContentType: actualContentType,
      size: file.size,
      url: presignedUrl.substring(0, 100) + '...'
    });

    const blob = new Blob([file], { type: actualContentType });

    return from(fetch(presignedUrl, {
      method: 'PUT',
      body: blob
    })).pipe(
      switchMap(response => {
        if (!response.ok) {
          return throwError(() => new Error('Upload failed with status ' + response.status));
        }
        return of(response);
      })
    );
  }
}

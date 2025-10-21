import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import {OfflineSongData} from './model/offline-song-data.model';

@Injectable({
  providedIn: 'root'
})
export class OfflineStorageService {
  private dbName = 'OfflineSongsDB';
  private dbVersion = 2;
  private db$: Observable<IDBDatabase>;

  constructor() {
    this.db$ = this.initDB();
  }

  private initDB(): Observable<IDBDatabase> {
    return new Observable<IDBDatabase>(observer => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = (e) => {
        const db = (e.target as IDBOpenDBRequest).result;

        if (!db.objectStoreNames.contains('songs')) {
          const songStore = db.createObjectStore('songs', { keyPath: 'id' });
          songStore.createIndex('downloadedAt', 'downloadedAt', { unique: false });
        }
      };

      request.onsuccess = () => {
        observer.next(request.result);
        observer.complete();
      };

      request.onerror = () => {
        observer.error(request.error);
      };
    });
  }

  saveSong(data: OfflineSongData): Observable<void> {
    return this.db$.pipe(
      switchMap(db => {
        return new Observable<void>(observer => {
          const tx = db.transaction('songs', 'readwrite');
          const store = tx.objectStore('songs');
          const request = store.put(data);

          request.onsuccess = () => {
            observer.next();
            observer.complete();
          };

          request.onerror = () => {
            observer.error(request.error);
          };
        });
      }),
      catchError(err => {
        console.error('Error saving song:', err);
        return throwError(() => new Error('Failed to save song offline'));
      })
    );
  }

  getSong(id: string): Observable<OfflineSongData | null> {
    return this.db$.pipe(
      switchMap(db => {
        return new Observable<OfflineSongData | null>(observer => {
          const tx = db.transaction('songs', 'readonly');
          const store = tx.objectStore('songs');
          const request = store.get(id);

          request.onsuccess = () => {
            observer.next(request.result || null);
            observer.complete();
          };

          request.onerror = () => {
            observer.error(request.error);
          };
        });
      }),
      catchError(err => {
        console.error('Error getting song:', err);
        return of(null);
      })
    );
  }

  deleteSong(id: string): Observable<void> {
    return this.db$.pipe(
      switchMap(db => {
        return new Observable<void>(observer => {
          const tx = db.transaction('songs', 'readwrite');
          const store = tx.objectStore('songs');
          const request = store.delete(id);

          request.onsuccess = () => {
            observer.next();
            observer.complete();
          };

          request.onerror = () => {
            observer.error(request.error);
          };
        });
      })
    );
  }

  isAvailableOffline(id: string): Observable<boolean> {
    return this.getSong(id).pipe(
      map(song => song !== null)
    );
  }

  getAllOfflineSongs(): Observable<OfflineSongData[]> {
    return this.db$.pipe(
      switchMap(db => {
        return new Observable<OfflineSongData[]>(observer => {
          const tx = db.transaction('songs', 'readonly');
          const store = tx.objectStore('songs');
          const request = store.getAll();

          request.onsuccess = () => {
            observer.next(request.result);
            observer.complete();
          };

          request.onerror = () => {
            observer.error(request.error);
          };
        });
      })
    );
  }

  getStorageSize(): Observable<number> {
    return this.getAllOfflineSongs().pipe(
      map(songs => songs.reduce((total, song) => total + song.blob.size, 0))
    );
  }

  clearAll(): Observable<void> {
    return this.db$.pipe(
      switchMap(db => {
        return new Observable<void>(observer => {
          const tx = db.transaction('songs', 'readwrite');
          const store = tx.objectStore('songs');
          const request = store.clear();

          request.onsuccess = () => {
            observer.next();
            observer.complete();
          };

          request.onerror = () => {
            observer.error(request.error);
          };
        });
      })
    );
  }
}

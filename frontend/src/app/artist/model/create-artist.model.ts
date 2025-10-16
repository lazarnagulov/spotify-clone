export interface Artist {
  id: string,
  name: string,
  bio: string,
  genres: string[],
  // TODO: Change once songs and albums creation is implemented
  songs: any[];
  albums: any[];
}

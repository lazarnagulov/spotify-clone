export type CatalogItemType = "artist" | "album" | "song";

export interface GenreCatalogItem {
  genre: string;
  type: CatalogItemType;
  id: string;
  name: string;
}

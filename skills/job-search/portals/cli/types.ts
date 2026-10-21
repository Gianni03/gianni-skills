export type Job = {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  date: string | null;
  url: string;
  portal: string;
  modality?: string | null;
};

export type SearchParams = {
  query: string;
  location?: string;
  jobage: number;
  limit: number;
};

export type Source = {
  name: string;
  host: string;
  search: (params: SearchParams) => Promise<Job[]>;
};

export const ISO_DATE = (d: Date): string => d.toISOString().slice(0, 10);

export interface ValidationDetail {
  loc: string[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  status: number;
  error: string | ValidationDetail[];
  requestId?: string;
}

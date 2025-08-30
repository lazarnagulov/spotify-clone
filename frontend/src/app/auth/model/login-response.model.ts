export interface AuthenticationResult {
  AccessToken: string;
  ExpiresIn: number;
  TokenType: string;
  RefreshToken?: string;
  IdToken: string;
}

export interface LoginResponse {
  statusCode: number;
  body: AuthenticationResult;
}

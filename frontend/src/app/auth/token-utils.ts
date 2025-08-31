import {jwtDecode} from "jwt-decode";

export interface DecodedToken {
    sub: string;
    email: string;
    'cognito:groups'?: string[];
    exp: number;
    iat: number;
}

export function getUserRoles(idToken: string): string[] {
    const decoded = jwtDecode<DecodedToken>(idToken);
    return decoded['cognito:groups'] || [];
}

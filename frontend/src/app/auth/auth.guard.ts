import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  Router,
} from '@angular/router';
import {AuthService} from './auth.service';


@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
  ): boolean {
    const userRoles: string[] = this.authService.getRoles();
    const requiredRoles: string[] = route.data['roles'];

    if (userRoles.length === 0) {
      void this.router.navigate(['login']);
      return false;
    }
    if (!requiredRoles.some(role => userRoles.includes(role))) {
      void this.router.navigate(['home']);
      return false;
    }
    return true;
  }
}

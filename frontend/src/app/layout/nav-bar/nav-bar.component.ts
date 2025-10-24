import { Component } from '@angular/core';
import {AuthService} from '../../auth/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  standalone: false,
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.css'
})
export class NavBarComponent {

  constructor(private authService: AuthService, private router: Router) {
  }

  get userRoles(): string[] {
    return this.authService.getRoles();
  }

  logout(): void {
    this.authService.clearTokens();
    void this.router.navigate(['/login']);
  }
}

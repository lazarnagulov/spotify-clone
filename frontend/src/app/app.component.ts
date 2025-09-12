import {Component, OnInit} from '@angular/core';
import {AuthService} from './auth/auth.service';
import {LoginResponse} from './auth/model/login-response.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: false,
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {

  constructor(private authService: AuthService) {
  }

  ngOnInit(): void {
    // TODO: Uncomment if HTTPS is implemented
    // this.authService.refresh().subscribe({
    //   next: (response: LoginResponse) => {
    //     this.authService.setTokens(response);
    //   },
    //   error: () => {}
    // });
  }

}

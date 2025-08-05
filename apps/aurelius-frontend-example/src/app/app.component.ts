import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { DarkMode, Header } from "aurelius-ui";
import { AuthService } from "./services/auth.service";

@Component({
    imports: [CommonModule, DarkMode, Header, RouterOutlet],
    selector: "aurelius-frontend-example-root",
    templateUrl: "./app.component.html",
    styleUrl: "./app.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
    /**
     * The authentication service is injected to access the current authentication state.
     */
    protected readonly authService = inject(AuthService);
}

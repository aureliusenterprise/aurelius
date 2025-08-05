import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { faCircle as faCircleRegular } from "@fortawesome/free-regular-svg-icons";
import { faCircleHalfStroke, faCircle as faCircleSolid } from "@fortawesome/free-solid-svg-icons";
import { DarkModeService } from "./dark-mode.service";

@Component({
    selector: "aurelius-ui-dark-mode",
    imports: [FontAwesomeModule],
    templateUrl: "./dark-mode.component.html",
    styleUrl: "./dark-mode.component.scss",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DarkMode {
    /**
     * The dark mode service is injected to access the current mode and toggle it.
     */
    protected readonly darkModeService = inject(DarkModeService);

    /**
     * The FontAwesome icons used in the dark mode toggle.
     */
    protected readonly faCircleHalfStroke = faCircleHalfStroke;
    protected readonly faCircleRegular = faCircleRegular;
    protected readonly faCircleSolid = faCircleSolid;
}

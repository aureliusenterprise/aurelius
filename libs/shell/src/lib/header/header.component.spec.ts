import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
import { HeaderComponent } from './header.component';
import { I18nService } from '@models4insight/i18n';
import { AuthenticationService } from '@models4insight/authentication';
import { ShellService } from '../shell.service';
import { ShellConfig, ShellConfigService } from '../shell-config.service';
import { of } from 'rxjs';

describe('HeaderComponent', () => {
    let component: HeaderComponent;
    let fixture: ComponentFixture<HeaderComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [RouterTestingModule],
            declarations: [HeaderComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: I18nService, useValue: { select: (key: string) => of() } },
                { provide: AuthenticationService, useValue: { credentials: () => of() } },
                { provide: ShellService, useValue: { select: (key: string) => of(), applyUpdate: () => {} } },
                { provide: ShellConfigService, useValue: {} as ShellConfig },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(HeaderComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});

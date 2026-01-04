import { provideZonelessChangeDetection } from "@angular/core";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { DarkMode } from "./dark-mode.component";

describe("DarkMode", () => {
    let component: DarkMode;
    let fixture: ComponentFixture<DarkMode>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [DarkMode],
            providers: [provideZonelessChangeDetection()],
        }).compileComponents();

        fixture = TestBed.createComponent(DarkMode);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });
});

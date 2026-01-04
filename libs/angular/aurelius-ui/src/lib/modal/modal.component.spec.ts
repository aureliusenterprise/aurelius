import { provideZonelessChangeDetection } from "@angular/core";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Modal } from "./modal.component";

describe("Modal", () => {
    let component: Modal;
    let fixture: ComponentFixture<Modal>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [Modal],
            providers: [provideZonelessChangeDetection()],
        }).compileComponents();

        fixture = TestBed.createComponent(Modal);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });
});

import { provideZonelessChangeDetection } from "@angular/core";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Header } from "./header.component";

describe("Header", () => {
    let component: Header;
    let fixture: ComponentFixture<Header>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [Header],
            providers: [provideZonelessChangeDetection()],
        }).compileComponents();

        fixture = TestBed.createComponent(Header);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });
});

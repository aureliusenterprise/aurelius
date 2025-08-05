import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Accordion } from "./accordion.component";

describe("Accordion", () => {
    let component: Accordion;
    let fixture: ComponentFixture<Accordion>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [Accordion],
        }).compileComponents();

        fixture = TestBed.createComponent(Accordion);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });
});

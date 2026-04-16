import { ComponentFixture, TestBed } from "@angular/core/testing";

import { Pagination } from "./pagination.component";

describe("Pagination", () => {
    let fixture: ComponentFixture<Pagination>;
    let component: Pagination;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [Pagination],
        }).compileComponents();

        fixture = TestBed.createComponent(Pagination);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("uses defaults when no inputs are provided", () => {
        expect(component.pageSize()).toBe(10);
        expect(component.pageIndex()).toBe(0);
        expect(component.totalPages()).toBe(0);
        expect(component.currentPageDisplay()).toBe(0);
        expect(component.pageTokens()).toEqual([]);
        expect(component.hasPreviousPage()).toBe(false);
        expect(component.hasNextPage()).toBe(false);
    });

    it("computes total pages using ceiling division", () => {
        fixture.componentRef.setInput("totalItems", 21);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.totalPages()).toBe(3);
    });

    it("recomputes total pages when pageSize changes", () => {
        fixture.componentRef.setInput("totalItems", 25);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.totalPages()).toBe(3);

        fixture.componentRef.setInput("pageSize", 8);
        fixture.detectChanges();

        expect(component.totalPages()).toBe(4);
    });

    it("exposes 1-based current page display and caps to total pages", () => {
        fixture.componentRef.setInput("totalItems", 25);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.currentPageDisplay()).toBe(1);

        component.pageIndex.set(2);
        expect(component.currentPageDisplay()).toBe(3);

        component.pageIndex.set(10);
        expect(component.currentPageDisplay()).toBe(3);
    });

    it("updates hasPreviousPage and hasNextPage across boundaries", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.hasPreviousPage()).toBe(false);
        expect(component.hasNextPage()).toBe(true);

        component.pageIndex.set(1);
        expect(component.hasPreviousPage()).toBe(true);
        expect(component.hasNextPage()).toBe(true);

        component.pageIndex.set(2);
        expect(component.hasPreviousPage()).toBe(true);
        expect(component.hasNextPage()).toBe(false);
    });

    it("goToPage navigates to a valid index", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.goToPage(2);

        expect(component.pageIndex()).toBe(2);
        expect(component.currentPageDisplay()).toBe(3);
    });

    it("goToPage ignores negative indexes", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.goToPage(-1);

        expect(component.pageIndex()).toBe(0);
    });

    it("goToPage ignores indexes beyond the last page", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.pageIndex.set(1);
        component.goToPage(3);

        expect(component.pageIndex()).toBe(1);
    });

    it("nextPage moves forward and stops at the last page", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.nextPage();
        expect(component.pageIndex()).toBe(1);

        component.nextPage();
        expect(component.pageIndex()).toBe(2);

        component.nextPage();
        expect(component.pageIndex()).toBe(2);
    });

    it("previousPage moves backward and stops at the first page", () => {
        fixture.componentRef.setInput("totalItems", 30);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.pageIndex.set(2);

        component.previousPage();
        expect(component.pageIndex()).toBe(1);

        component.previousPage();
        expect(component.pageIndex()).toBe(0);

        component.previousPage();
        expect(component.pageIndex()).toBe(0);
    });

    it("returns sequential short-form tokens when totalPages is 7", () => {
        fixture.componentRef.setInput("totalItems", 70);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.totalPages()).toBe(7);
        expect(component.pageTokens()).toEqual([1, 2, 3, 4, 5, 6, 7]);
    });

    it("switches to long-form tokens when totalPages is greater than 7", () => {
        fixture.componentRef.setInput("totalItems", 80);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        expect(component.totalPages()).toBe(8);
        expect(component.pageTokens()).toEqual([1, 2, "ellipsis", 8]);
    });

    it("generates long-form tokens near the middle", () => {
        fixture.componentRef.setInput("totalItems", 100);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.pageIndex.set(4);

        expect(component.pageTokens()).toEqual([1, "ellipsis", 4, 5, 6, "ellipsis", 10]);
    });

    it("generates long-form tokens near the end", () => {
        fixture.componentRef.setInput("totalItems", 100);
        fixture.componentRef.setInput("pageSize", 10);
        fixture.detectChanges();

        component.pageIndex.set(9);

        expect(component.pageTokens()).toEqual([1, "ellipsis", 9, 10]);
    });
});

import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
    selector: 'models4insight-properties-item',
    templateUrl: './properties-item.component.html',
    styleUrls: ['./properties-item.component.scss'],
    providers: []
})
export class PropertiesItemComponent implements OnInit {

    @Input() data: any;

    isObjectLike: Array<object>;
    isStringLike: string;

    constructor(private readonly router: Router) { }

    ngOnInit() {
        this.defineTypes(this.data);
    }

    openDetails(guid: string) {
        this.router.navigate(['search/details', guid]);
    }
    ngOnDestroy() {
    }
    defineTypes(data: any) {
        if (typeof data === 'string') {
            this.isStringLike = data
        } else {
            this.isObjectLike = data
        }
    }

}

import { Component, OnInit } from '@angular/core';
import { ConsoleService } from './console.service';
import { trigger, state, style, transition, animate } from '@angular/animations';


@Component({
    selector: 'app-console',
    templateUrl: 'console.component.html',
    styleUrls: ['console.component.less'],
    animations: [
        trigger('logExpand',[
            transition(':enter', [
                style({opacity: 0, height: '0px', minHeight: '0'}),
                animate('0.3s', style({ opacity: 1, height: '*'})),
            ]),
            transition(':leave', [
                animate('0.2s', style({ opacity: 0, height: '0px', minHeight: '0'}))
            ])
        ]),
    ]
})
export class ConsoleComponent implements OnInit {
    


    constructor(private consoleService: ConsoleService) { }
    running = false;

    shouldShowLogs = false;

    ngOnInit(): void {
        this.consoleService.subscribeStatus();
    }

    runAutomaton() {
        this.consoleService.runAutomaton();
    }

}
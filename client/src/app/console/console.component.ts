import { Component, OnInit } from '@angular/core';
import { ConsoleService } from './console.service';
import { trigger, state, style, transition, animate } from '@angular/animations';



@Component({
    selector: 'app-console',
    templateUrl: 'console.component.html',
    styleUrls: ['console.component.less'],
    animations: [
        trigger('logExpand', [
            state('collapsed', style({ height: '0px', minHeight: '0', display: 'none', opacity: 0 })),
            state('expanded', style({ height: '*', opacity: 1 })),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)'))
        ]),
    ]
})
export class ConsoleComponent implements OnInit {
    
    


    constructor(private consoleService: ConsoleService) { }
    running = false;

    terminalState = 'collapsed';

    ngOnInit(): void {
        this.consoleService.subscribeStatus();
        this.consoleService.running$.subscribe(
            running => this.running=running
        )
    }

    runAutomaton() {
        this.consoleService.runAutomaton();
    }

}
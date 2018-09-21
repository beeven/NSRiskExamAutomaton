import { Component } from '@angular/core';
import { ConsoleService } from './console.service';


@Component({
    selector: 'app-console',
    templateUrl: 'console.component.html',
    styleUrls: ['console.component.less']
})
export class ConsoleComponent {


    constructor(private consoleService: ConsoleService) { }
    running = false;

    runAutomaton() {
        this.consoleService.runAutomaton();
    }

}
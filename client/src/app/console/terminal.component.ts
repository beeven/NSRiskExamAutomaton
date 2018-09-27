import { Component, OnInit, OnDestroy, ElementRef, ViewEncapsulation } from '@angular/core';
import { Terminal } from 'xterm';
import { fit } from 'xterm/lib/addons/fit/fit';
import { ConsoleService } from './console.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-terminal',
    template: ``,
    styles: [`
        :host {
            width: 100%;
            height: 100%;
            display: block;
        }

        :host ::ng-deep .xterm {
            padding: 5px;
        }
    `],
    // encapsulation: ViewEncapsulation.None,
})
export class TerminalComponent implements OnInit, OnDestroy {
    
    private term = new Terminal();
    private consoleSubscription: Subscription;

    constructor(private elem: ElementRef,
        private consoleService: ConsoleService) { }


    ngOnInit(): void {
        this.term.open(this.elem.nativeElement);
        fit(this.term);
        //this.term.write('Hello from \x1B[1;3;31mxterm.js\x1B[0m $ ');
        this.consoleSubscription = this.consoleService.console$.subscribe(
            data => {
                this.term.writeln(data)
            }
        )
    }


    ngOnDestroy(): void {
        if(this.consoleSubscription) {
            this.consoleSubscription.unsubscribe();
            this.consoleSubscription = null;
        }
    }
    
}
import { Component, OnInit, OnDestroy, ElementRef, ViewEncapsulation } from '@angular/core';
import { Terminal } from 'xterm';
import { ConsoleService } from './console.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-terminal',
    template: `<div></div>`,
    styles: [`
        .xterm ::-webkit-scrollbar {
            display: none;
        }
    `],
    encapsulation: ViewEncapsulation.None,
})
export class TerminalComponent implements OnInit, OnDestroy {
    
    constructor(private elem: ElementRef,
        private consoleService: ConsoleService) { }

    private term = new Terminal();
    private consoleSubscription: Subscription;

    ngOnInit(): void {
        this.term.open(this.elem.nativeElement);
        this.term.write('Hello from \x1B[1;3;31mxterm.js\x1B[0m $ ');
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
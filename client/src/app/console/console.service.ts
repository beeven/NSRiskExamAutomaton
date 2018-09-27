import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { fromEvent, BehaviorSubject, Subject } from 'rxjs';

@Injectable()
export class ConsoleService {

    constructor(private http: HttpClient) {
        this.getRunningStatus();
    }

    private runningSubject = new BehaviorSubject<boolean>(false);
    public running$ = this.runningSubject.asObservable();

    private consoleSubject = new Subject<string>();
    public console$ = this.consoleSubject.asObservable();

    runAutomaton() {
        this.http.post("/api/control/start", null).subscribe(
            data => {
                this.runningSubject.next(true);
            }
        )
    }

    getRunningStatus() {
        this.http.get("/api/control/status").subscribe(
            data => {
                if(data["status"] === "running") {
                    this.runningSubject.next(true);
                } else {
                    this.runningSubject.next(false);
                }
            }
        )
    }



    subscribeStatus(): void {
        let source = new EventSource('/api/control/subscribe');
        let statusSrc = fromEvent(source, 'message');
        statusSrc.subscribe(
            (ev: MessageEvent) => {
                let data = JSON.parse(ev.data)
                this.consoleSubject.next(data.message);
                this.runningSubject.next(data.running);
            }
        );
    }
}
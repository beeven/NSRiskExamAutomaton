import { DataSource, CollectionViewer } from "@angular/cdk/collections";
import { Log } from "./log";
import { BehaviorSubject, Observable, of } from "rxjs";
import { LogsService } from "./logs.service";
import { catchError, finalize } from "rxjs/operators";


export class LogsDataSource implements DataSource<Log> {

    private logsSubject = new BehaviorSubject<Log[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);

    public loading$ = this.loadingSubject.asObservable();

    constructor(private logService: LogsService) {}

    connect(collectionViewer: CollectionViewer): Observable<Log[]> {
        return this.logsSubject.asObservable();
    }    
    
    disconnect(collectionViewer: CollectionViewer): void {
        this.logsSubject.complete();
        this.loadingSubject.complete();
    }

    loadLogs(page=0, size=15, sort="exam_time", order="desc", filter="") {
        this.loadingSubject.next(true);
        this.logService.getLogs(page, size, sort, order, filter)
            .pipe(
                catchError(() => of([])),
                finalize(() => this.loadingSubject.next(false))
            )
            .subscribe( logs => this.logsSubject.next(logs));
    }

}
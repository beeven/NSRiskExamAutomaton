import { DataSource, CollectionViewer } from "@angular/cdk/collections";
import { Log } from "./log";
import { BehaviorSubject, Observable, of } from "rxjs";
import { LogsService } from "./logs.service";
import { catchError, finalize } from "rxjs/operators";


export class LogsDataSource implements DataSource<Log> {

    private logsSubject = new BehaviorSubject<Log[]>([]);
    private loadingSubject = new BehaviorSubject<boolean>(false);
    private totalSubject = new BehaviorSubject<number>(0);

    public loading$ = this.loadingSubject.asObservable();
    public total$ = this.totalSubject.asObservable();

    constructor(private logService: LogsService) {}

    connect(collectionViewer: CollectionViewer): Observable<Log[]> {
        return this.logsSubject.asObservable();
    }    
    
    disconnect(collectionViewer: CollectionViewer): void {
        this.logsSubject.complete();
        this.loadingSubject.complete();
    }

    loadLogs(page=0, size=10, sort="exam_time", order="desc", filter="") {
        this.loadingSubject.next(true);
        this.logService.getLogs(page, size, sort, order, filter)
            .pipe(
                catchError(() => of(null)),
                finalize(() => this.loadingSubject.next(false))
            )
            .subscribe( logBatch => {
                this.logsSubject.next(logBatch["data"]);
                this.totalSubject.next(logBatch["total"]);
            });
    }

}
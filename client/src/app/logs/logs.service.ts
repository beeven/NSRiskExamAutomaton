import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Log } from './log';


export class LogBatch {
    logs: Log[];
    total: number;
}

@Injectable()
export class LogsService {
    constructor(private http: HttpClient) { }

    getLogs(page = 0, size = 15, sort='exam_time', order='desc', filter = ''): Observable<LogBatch> {
        return this.http.get<LogBatch>("/api/logs", {
            params: new HttpParams()
                .set('page', page.toString())
                .set('size', size.toString())
                .set('sort', sort)
                .set('order', order)
                .set('filter', filter)
        });
    }
}   


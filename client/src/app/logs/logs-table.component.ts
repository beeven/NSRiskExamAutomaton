import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { LogsDataSource } from './logs.datasource';
import { LogsService } from './logs.service';
import { MatPaginator } from '@angular/material';
import { tap } from 'rxjs/operators';


@Component({
    selector: 'app-logs-table',
    templateUrl: 'logs-table.component.html',
    styleUrls: ['logs-table.component.less']
})
export class LogsTableComponent implements OnInit, AfterViewInit {
    
    
    dataSource: LogsDataSource;
    columnsToDisplay = ['id', 'entry_id', 'reason', 'req', 'note',
    'container_num', 'exam_req', 'exam_method', 'exam_container_num', 'exam_time']

    @ViewChild(MatPaginator) paginator: MatPaginator;

    constructor(private logsService: LogsService) {}
    ngOnInit(): void {
        this.dataSource = new LogsDataSource(this.logsService);
        this.dataSource.loadLogs();
    }

    ngAfterViewInit(): void {
        this.paginator.page.pipe(
            tap(() => this.loadLogsPage())
        )
        .subscribe();
    }


    loadLogsPage() {
        this.dataSource.loadLogs(this.paginator.pageIndex, this.paginator.pageSize)
    }
}
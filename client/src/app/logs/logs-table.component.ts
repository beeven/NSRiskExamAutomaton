import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { LogsDataSource } from './logs.datasource';
import { LogsService } from './logs.service';
import { MatPaginator } from '@angular/material';
import { tap } from 'rxjs/operators';
import { Log } from './log';
import { transition, trigger, state, style, animate } from '@angular/animations';


@Component({
    selector: 'app-logs-table',
    templateUrl: 'logs-table.component.html',
    styleUrls: ['logs-table.component.less'],
    animations: [
        trigger('detailExpand',[
            state('collapsed', style({height: '0px', minHeight: '0', display: 'none'})),
            state('expanded', style({height: '*'})),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)'))
        ]),
    ],
})
export class LogsTableComponent implements OnInit, AfterViewInit {
    
    
    dataSource: LogsDataSource;
    columnsToDisplay = ['id', 'entry_id', 
    'container_num', 'exam_method', 'exam_container_num', 'exam_time']
    expandedLog: Log;

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
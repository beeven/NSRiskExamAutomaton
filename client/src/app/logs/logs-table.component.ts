import { Component, OnInit, ViewChild, AfterViewInit, ElementRef } from '@angular/core';
import { LogsDataSource } from './logs.datasource';
import { LogsService } from './logs.service';
import { MatPaginator, MatSort } from '@angular/material';
import { tap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import {merge, fromEvent} from 'rxjs';
import { Log } from './log';
import { transition, trigger, state, style, animate } from '@angular/animations';


@Component({
    selector: 'app-logs-table',
    templateUrl: 'logs-table.component.html',
    styleUrls: ['logs-table.component.less'],
    animations: [
        trigger('detailExpand', [
            state('collapsed', style({ height: '0px', minHeight: '0', display: 'none' })),
            state('expanded', style({ height: '*' })),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)'))
        ]),
        trigger('loading',[
            transition(':enter', [
                style({opacity: 0}),
                animate('0.5s', style({ opacity: 1})),
            ]),
            transition(':leave', [
                animate('0.5s', style({ opacity: 0}))
            ])
        ]),
    ],
})
export class LogsTableComponent implements OnInit, AfterViewInit {


    dataSource: LogsDataSource;
    columnsToDisplay = ['id', 'entry_id',
        'container_num', 'exam_method', 'exam_container_num', 'exam_time']
    expandedLog: Log;

    @ViewChild(MatPaginator) paginator: MatPaginator;
    @ViewChild(MatSort) sort: MatSort;
    @ViewChild('input') input:ElementRef;


    constructor(private logsService: LogsService) { }
    ngOnInit(): void {
        this.dataSource = new LogsDataSource(this.logsService);
        this.dataSource.loadLogs();
    }

    ngAfterViewInit(): void {
        fromEvent(this.input.nativeElement,'keyup')
            .pipe(
                debounceTime(500),
                distinctUntilChanged(),
                tap(() => {
                    this.paginator.pageIndex = 0;
                    this.loadLogsPage();
                })
            )
            .subscribe();
        
        this.sort.sortChange.subscribe(()=> this.paginator.pageIndex = 0);
        merge(this.sort.sortChange, this.paginator.page)
            .pipe(
                tap(()=> this.loadLogsPage())
            )
            .subscribe();
    }


    loadLogsPage() {
        this.dataSource.loadLogs(this.paginator.pageIndex, 
            this.paginator.pageSize, this.sort.active, this.sort.direction,
            this.input.nativeElement.value);
    }


}
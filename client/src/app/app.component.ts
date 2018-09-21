import { Component, AfterViewInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, fromEvent } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent implements AfterViewInit{

  
  constructor(private http: HttpClient) { }

  title = 'RiskExamAutomaton';

  ngAfterViewInit(): void {
  }

  


}

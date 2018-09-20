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
  displayedColumns = [""]

  ngAfterViewInit(): void {
    this.subscribeStatus()
  }

  subscribeStatus(): void {
    let source = new EventSource('/api/control/subscribe');
    let statusSrc = fromEvent(source, 'message');
    statusSrc.subscribe(
      (ev: MessageEvent)=>{
        console.log("status:", ev.data)
      }
    );
  }

  runAutomaton() {
    this.http.post("/api/control/start", null).subscribe(
      data => {
        console.log(data)
      }
    )
  }

}

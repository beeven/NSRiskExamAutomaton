import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { MaterialModule } from './material.module';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LogsService } from './logs/logs.service';
import { LogsTableComponent } from './logs/logs-table.component';
import { ConsoleComponent } from './console/console.component';
import { ConsoleService } from './console/console.service';
import { TerminalComponent }  from './console/terminal.component';

@NgModule({
  declarations: [
    AppComponent,
    LogsTableComponent,
    ConsoleComponent,
    TerminalComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    MaterialModule
  ],
  providers: [
    LogsService,
    ConsoleService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

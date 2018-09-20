import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { MaterialModule } from './material.module';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LogsService } from './logs/logs.service';
import { LogsTableComponent } from './logs/logs-table.component';

@NgModule({
  declarations: [
    AppComponent,
    LogsTableComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    MaterialModule
  ],
  providers: [
    LogsService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

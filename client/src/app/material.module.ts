import {NgModule} from '@angular/core';
import {MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule} from '@angular/material';

@NgModule({
  imports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule],
  exports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule],
})
export class MaterialModule { }
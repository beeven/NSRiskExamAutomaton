import {NgModule} from '@angular/core';
import {MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule} from '@angular/material';

@NgModule({
  imports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule],
  exports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule],
})
export class MaterialModule { }
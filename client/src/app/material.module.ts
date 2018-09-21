import {NgModule} from '@angular/core';
import {MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule, MatFormFieldModule, MatInputModule} from '@angular/material';

@NgModule({
  imports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule, MatFormFieldModule, MatInputModule],
  exports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, MatProgressSpinnerModule, MatFormFieldModule, MatInputModule],
})
export class MaterialModule { }